"""
Ceryle - Cliente de la Microsoft Learn Catalog API.

La Catalog API (https://learn.microsoft.com/api/catalog/) es una REST
pública sin auth que devuelve la jerarquía completa del contenido de
MS Learn: learningPaths -> modules -> units, con UIDs estables,
títulos, niveles, duración y URLs.

El MCP de MS Learn da CONTENIDO (markdown) pero no ESTRUCTURA. Este
cliente da ESTRUCTURA pero no contenido. Se complementan: la ingesta
usa ambos para construir módulos completos en la BD.

Funciones principales:
  - fetch_catalog()       -> dict con learningPaths, modules, units
  - get_module_record(uid)-> metadata de un módulo desde el catálogo
  - get_unit_record(uid)  -> metadata de una unidad desde el catálogo
  - resolve_unit_urls(module_url) -> parsea el HTML del módulo y mapea
    cada unit UID a su URL real (los slugs no son predecibles desde
    el UID, hay que leerlos del <ul id="unit-list"> de la página).
  - build_module_units(module_uid) -> combina catalog + resolver para
    devolver [{uid, title, url, duration_minutes}] listo para persistir.
"""

import logging
import re
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

logger = logging.getLogger(__name__)


# ─── Configuración ───────────────────────────────────────────────────────────

CATALOG_URL = "https://learn.microsoft.com/api/catalog/"
CATALOG_TYPES = "learningPaths,modules,units"
DEFAULT_USER_AGENT = "Ceryle/0.1 (learning-platform)"
HTTP_TIMEOUT = 60.0

# Cache en memoria del catálogo (la ingesta lo llama muchas veces).
_catalog_cache: dict | None = None


# ─── Catalog fetch ───────────────────────────────────────────────────────────


async def fetch_catalog(force_refresh: bool = False) -> dict:
    """Descarga el catálogo de MS Learn (una sola llamada REST) y lo
    cachea en memoria.

    Returns:
        Dict con claves 'learningPaths', 'modules', 'units' (cada una
        una lista de records).

    Raises:
        httpx.HTTPError si la llamada falla.
    """
    global _catalog_cache
    if _catalog_cache is not None and not force_refresh:
        return _catalog_cache

    params = {"type": CATALOG_TYPES}
    async with httpx.AsyncClient(
        timeout=HTTP_TIMEOUT,
        headers={"User-Agent": DEFAULT_USER_AGENT},
        follow_redirects=True,
    ) as client:
        resp = await client.get(CATALOG_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    _catalog_cache = data
    n_mods = len(data.get("modules", []))
    n_units = len(data.get("units", []))
    n_paths = len(data.get("learningPaths", []))
    logger.info(
        f"Learn catalog fetched: {n_paths} learningPaths, "
        f"{n_mods} modules, {n_units} units"
    )
    return data


def _strip_query(url: str) -> str:
    """Elimina los query params de una URL (ej. ?WT.mc_id=...)."""
    if not url:
        return url
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))


# ─── Lookups por UID ─────────────────────────────────────────────────────────


async def get_module_record(uid: str) -> dict | None:
    """Busca un módulo por UID en el catálogo cacheado."""
    catalog = await fetch_catalog()
    for m in catalog.get("modules", []):
        if m.get("uid") == uid:
            return m
    return None


async def get_unit_record(uid: str) -> dict | None:
    """Busca una unidad por UID en el catálogo cacheado."""
    catalog = await fetch_catalog()
    for u in catalog.get("units", []):
        if u.get("uid") == uid:
            return u
    return None


# ─── Resolver de URLs de unidades ────────────────────────────────────────────

# Regex sobre el bloque <ul id="unit-list">...</ul>:
#   data-unit-uid="UID" ... <a ... href="RELATIVE" ...>TITLE</a>
_UNIT_LI_RE = re.compile(
    r'data-unit-uid="([^"]+)"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]*)</a>',
    re.DOTALL,
)
_UNIT_LIST_RE = re.compile(
    r'<ul id="unit-list"[^>]*>(.*?)</ul>',
    re.DOTALL,
)


async def resolve_unit_urls(
    module_url: str,
    client: httpx.AsyncClient | None = None,
) -> list[dict]:
    """Descarga la página HTML de un módulo y mapea cada unit UID a su
    URL absoluta real.

    Los slugs de las unidades NO se derivan del UID (ej. el UID
    ...introduction corresponde a /1-introduction), por lo que hay que
    leerlos del <ul id="unit-list"> embebido en la página del módulo.

    Returns:
        Lista de dicts [{uid, title, url}] en el orden en que aparecen
        en el módulo. Lista vacía si no se pudo parsear.
    """
    clean_url = _strip_query(module_url)
    if not clean_url:
        return []

    owns_client = client is None
    if owns_client:
        client = httpx.AsyncClient(
            timeout=HTTP_TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            follow_redirects=True,
        )

    try:
        resp = await client.get(clean_url)
        resp.raise_for_status()
        html = resp.text

        list_match = _UNIT_LIST_RE.search(html)
        if not list_match:
            logger.warning(
                f"resolve_unit_urls: <ul id=unit-list> not found in {clean_url}"
            )
            return []

        block = list_match.group(1)
        units: list[dict] = []
        for m in _UNIT_LI_RE.finditer(block):
            uid = m.group(1).strip()
            href = m.group(2).strip()
            title = m.group(3).strip()
            abs_url = urljoin(clean_url, href)
            units.append({"uid": uid, "title": title, "url": abs_url})

        return units
    except httpx.HTTPError as e:
        logger.warning(f"resolve_unit_urls: HTTP error for {clean_url}: {e}")
        return []
    finally:
        if owns_client:
            await client.aclose()


async def build_module_units(
    module_uid: str,
    client: httpx.AsyncClient | None = None,
) -> list[dict]:
    """Construye la lista completa de unidades de un módulo combinando:
      - metadata del catálogo (duration_in_minutes, título canónico)
      - URL real resuelta desde el HTML de la página del módulo

    Returns:
        Lista de dicts [{uid, title, url, duration_minutes}] en orden
        pedagógico (el orden del <ul id="unit-list">).
    """
    module = await get_module_record(module_uid)
    if not module:
        logger.warning(f"build_module_units: module {module_uid} not in catalog")
        return []

    resolved = await resolve_unit_urls(module.get("url", ""), client=client)
    if not resolved:
        return []

    # Indexar records del catálogo por UID para enriquecer con duration
    catalog = await fetch_catalog()
    unit_records_by_uid: dict[str, dict] = {
        u.get("uid"): u for u in catalog.get("units", [])
    }

    result: list[dict] = []
    for r in resolved:
        rec = unit_records_by_uid.get(r["uid"], {})
        result.append(
            {
                "uid": r["uid"],
                "title": r["title"] or rec.get("title", ""),
                "url": r["url"],
                "duration_minutes": rec.get("duration_in_minutes", 0) or 0,
            }
        )
    return result
