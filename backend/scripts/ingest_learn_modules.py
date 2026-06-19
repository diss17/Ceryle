"""
Ceryle - Script de ingesta de módulos de Microsoft Learn.

Pre-descarga módulos curados (ver app/learn_curriculum.py) a la tabla
LearnModule, incluyendo metadata del catálogo, markdown de cada unidad
(vía MCP) y code samples. Tras la ingesta, el runtime sirve las rutas
de aprendizaje desde la BD local, sin depender de que MS Learn esté
en línea.

Uso (desde backend/):
    python -m scripts.ingest_learn_modules            # ingesta todo
    python -m scripts.ingest_learn_modules --level beginner
    python -m scripts.ingest_learn_modules --force     # re-descarga todo
    python -m scripts.ingest_learn_modules --uid learn.wwl.fundamentals-generative-ai

Requisitos:
    - Paquete 'mcp' instalado (para microsoft_docs_fetch / code samples)
    - Conexión a internet (Catalog API + MCP de MS Learn)
"""

import argparse
import asyncio
import logging
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urljoin

import httpx
from sqlalchemy import select

from app.db import async_session, init_db
from app.db.models import LearnModule
from app.learn_curriculum import CURATED_MODULES, all_curated_uids
from app.services.learn_catalog import (
    build_module_units,
    fetch_catalog,
    get_module_record,
)
from app.services.mcp_learn_client import (
    fetch_learn_pages_batch,
    search_learn_code_samples,
)

logger = logging.getLogger("ingest")


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _curated_level_for(uid: str) -> str:
    """Retorna el nivel curado al que pertenece un UID, o '' si no está
    curado. Un módulo curado determina el nivel asignado en BD."""
    for level, uids in CURATED_MODULES.items():
        if uid in uids:
            return level
    return ""


async def _resolve_learning_path_uid(uid: str) -> str | None:
    """Busca en el catálogo el learning path que contiene este módulo."""
    catalog = await fetch_catalog()
    for lp in catalog.get("learningPaths", []):
        if uid in (lp.get("modules") or []):
            return lp.get("uid")
    return None


# ─── Normalización de contenido ──────────────────────────────────────────────

# Marcadores ::: zone de MS Learn. Cada unidad puede tener bloques
# pivot="video" (con un "Tip: See the Text and images tab...") y
# pivot="text" (con el contenido real + imágenes). Conservamos solo
# el contenido interior del text, sin los marcadores.
_ZONE_VIDEO_RE = re.compile(
    r':::\s*zone\s+pivot="video".*?:::\s*zone-end',
    re.DOTALL,
)
_ZONE_TEXT_OPEN_RE = re.compile(r':::\s*zone\s+pivot="text"\s*\n')
_ZONE_END_RE = re.compile(r':::\s*zone-end\s*\n?')
# Imágenes markdown con URL (cualquiera): ![alt](url)
_MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')


def _normalize_content(content: str, unit_url: str) -> str:
    """Limpia y absolutiza el markdown de una unidad de MS Learn.

    Transformaciones (en orden):
      1. Elimina bloques ::: zone pivot="video" ... ::: zone-end
         completos (contienen solo "Tip: See the Text and images
         tab for more details!", ruido para Ceryle).
      2. Conserva el contenido interior de ::: zone pivot="text"
         pero elimina las líneas marcadoras ::: zone / ::: zone-end.
      3. Absolutiza URLs relativas de imágenes usando urljoin(unit_url,
         rel) para que el navegador las resuelva contra
         learn.microsoft.com en vez de localhost. Las URLs ya
         absolutas (http(s)://, data:, #) se preservan.

    Args:
        content: Markdown crudo retornado por microsoft_docs_fetch.
        unit_url: URL absoluta de la unidad (base para urljoin).

    Returns:
        Markdown limpio con imágenes absolutas.
    """
    if not content:
        return ""

    # 1. Eliminar bloques video completos
    content = _ZONE_VIDEO_RE.sub("", content)

    # 2. Quitar marcadores de bloques text (conservar contenido interior)
    content = _ZONE_TEXT_OPEN_RE.sub("", content)
    content = _ZONE_END_RE.sub("", content)

    # 3. Absolutizar URLs de imágenes
    def _absolutize(match: re.Match[str]) -> str:
        alt = match.group(1)
        url = match.group(2).strip()
        # Preservar URLs ya absolutas o no-URL (data:, #, mailto:)
        if url.startswith(("http://", "https://", "data:", "#", "mailto:")):
            return match.group(0)
        # urljoin normaliza relativas: ../../path -> https://learn.../path
        absolute = urljoin(unit_url, url)
        return f"![{alt}]({absolute})"

    content = _MD_IMAGE_RE.sub(_absolutize, content)

    # Limpiar líneas vacías consecutivas excesivas dejadas por los
    # re.sub (máximo 2 saltos de línea seguidos).
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    return content.strip()


# ─── Ingesta de un módulo ────────────────────────────────────────────────────


async def ingest_one(uid: str, client: httpx.AsyncClient, force: bool = False) -> bool:
    """Ingesta un único módulo. Retorna True si tuvo éxito.

    Pasos:
      1. Metadata del catálogo (incluye icon_url, social_image_url)
      2. Unidades (catalog + URLs resueltas del HTML del módulo)
      3. Batch-fetch del markdown de cada unidad (una sesión MCP)
      4. Normalización del contenido (zone cleanup + URLs absolutas)
      5. Code samples (una sesión MCP)
      6. Upsert en LearnModule
    """
    # Skip si ya existe y no hay force
    if not force:
        async with async_session() as db:
            existing = await db.execute(
                select(LearnModule).where(LearnModule.uid == uid)
            )
            if existing.scalar_one_or_none():
                logger.info(f"[skip] {uid} ya ingestado (usa --force para refrescar)")
                return True

    # 1. Metadata del catálogo
    module = await get_module_record(uid)
    if not module:
        logger.error(f"[fail] {uid} no encontrado en el catálogo")
        return False

    title = module.get("title", uid)
    logger.info(f"[start] {uid} :: {title}")

    # 2. Unidades (metadata + URLs reales)
    units_meta = await build_module_units(uid, client=client)
    if not units_meta:
        logger.error(f"[fail] {uid} sin unidades resolubles")
        return False
    logger.info(f"[units] {uid} :: {len(units_meta)} unidades resueltas")

    # 3. Batch-fetch markdown de todas las unidades
    unit_urls = [u["url"] for u in units_meta]
    pages = await fetch_learn_pages_batch(unit_urls)
    fetched = sum(1 for u in unit_urls if u in pages)
    logger.info(f"[fetch] {uid} :: {fetched}/{len(unit_urls)} unidades con markdown")

    # 4. Normalizar contenido de cada unidad (zone cleanup + URLs absolutas)
    units_full = []
    for u in units_meta:
        raw = pages.get(u["url"], "")
        clean = _normalize_content(raw, u["url"]) if raw else ""
        units_full.append({**u, "content": clean})

    # 5. Code samples
    code_samples = await search_learn_code_samples(title, max_results=3)
    logger.info(f"[code] {uid} :: {len(code_samples)} snippets")

    # 6. Contenido concatenado para RAG (unidades normalizadas)
    content_concat = "\n\n---\n\n".join(
        f"# {u['title']}\n\n{u['content']}" for u in units_full if u["content"]
    )

    # Nivel: priorizar la asignación curada sobre el declarado del módulo
    level = _curated_level_for(uid) or (module.get("levels") or [""])[0]
    lp_uid = await _resolve_learning_path_uid(uid)

    values = {
        "uid": uid,
        "title": title,
        "summary": module.get("summary", "") or "",
        "url": module.get("url", "") or "",
        "level": level,
        "duration_minutes": module.get("duration_in_minutes", 0) or 0,
        "learning_path_uid": lp_uid,
        "content": content_concat,
        "code_samples": code_samples,
        "units": units_full,
        "icon_url": module.get("icon_url", "") or "",
        "social_image_url": module.get("social_image_url", "") or "",
        "last_ingested_at": datetime.now(timezone.utc),
    }

    # 6. Upsert
    async with async_session() as db:
        existing = await db.execute(
            select(LearnModule).where(LearnModule.uid == uid)
        )
        row = existing.scalar_one_or_none()
        if row:
            for k, v in values.items():
                setattr(row, k, v)
        else:
            db.add(LearnModule(**values))
        await db.commit()

    logger.info(
        f"[done] {uid} :: {len(units_full)} unidades, "
        f"{len(content_concat)} chars de contenido, level={level}"
    )
    return True


# ─── Migración ligera (ALTER TABLE para SQLite) ──────────────────────────────


async def _ensure_columns() -> None:
    """Añade columnas nuevas a learn_modules si faltan.

    SQLite no agrega columnas con create_all; hay que ALTER TABLE
    explícito. Idempotente: si la columna ya existe, no hace nada.
    """
    from sqlalchemy import text

    async with async_session() as db:
        result = await db.execute(text("PRAGMA table_info(learn_modules)"))
        existing_cols = {row[1] for row in result.fetchall()}

        wanted = {
            "icon_url": "VARCHAR(500) DEFAULT ''",
            "social_image_url": "VARCHAR(500) DEFAULT ''",
        }
        for col, ddl in wanted.items():
            if col not in existing_cols:
                logger.info(f"[migrate] ALTER TABLE add {col}")
                await db.execute(
                    text(f"ALTER TABLE learn_modules ADD COLUMN {col} {ddl}")
                )
        await db.commit()


# ─── Entry point ─────────────────────────────────────────────────────────────


async def run(force: bool, level: str | None, uid: str | None) -> int:
    await init_db()
    await _ensure_columns()

    # Seleccionar UIDs a procesar
    if uid:
        uids = [uid]
    elif level:
        uids = list(CURATED_MODULES.get(level, []))
        if not uids:
            logger.error(f"Nivel desconocido: {level}")
            return 2
    else:
        uids = all_curated_uids()

    logger.info(f"Ingestando {len(uids)} módulo(s) (force={force})")

    # Pre-cargar el catálogo una vez (se cachea)
    await fetch_catalog()

    ok = 0
    failed = 0
    async with httpx.AsyncClient(
        timeout=60.0,
        headers={"User-Agent": "Ceryle/0.1 (ingest)"},
        follow_redirects=True,
    ) as client:
        for i, mod_uid in enumerate(uids, 1):
            logger.info(f"--- [{i}/{len(uids)}] ---")
            try:
                success = await ingest_one(mod_uid, client, force=force)
                if success:
                    ok += 1
                else:
                    failed += 1
            except Exception as e:
                logger.exception(f"[fail] {mod_uid}: {e}")
                failed += 1

    logger.info(f"Resumen: {ok} OK, {failed} fallidos, {len(uids)} total")
    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingiere módulos curados de MS Learn en la BD de Ceryle."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-descarga módulos ya ingestado.",
    )
    parser.add_argument(
        "--level",
        choices=["beginner", "intermediate", "advanced"],
        help="Ingesta solo los módulos de un nivel.",
    )
    parser.add_argument(
        "--uid",
        help="Ingesta un único módulo por UID.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    rc = asyncio.run(run(force=args.force, level=args.level, uid=args.uid))
    sys.exit(rc)


if __name__ == "__main__":
    main()
