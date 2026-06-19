"""
Ceryle - Constructor del Learning Path basado en módulos ingestaos.

Flujo:
  1. Recibe el nivel del quiz ("beginner" | "intermediate" | "advanced")
  2. Lee los UIDs curados para ese nivel (app.learn_curriculum)
  3. Consulta la tabla LearnModule en BD para obtener los módulos
     pre-ingestados (con content, units, code_samples).
  4. Si no hay módulos ingestate → ModulesNotIngestedError (503).
  5. Usa el LLM SOLO para reordenar los módulos en progresión
     pedagógica. Al LLM se le envía un payload LIVIANO
     {title, url, description}; tras recibir el orden, se reconstruyen
     los topics preservando TODOS los campos originales.
  6. Si el LLM falla → conserva el orden curado original.
  7. Retorna referencias ligeras [{id, module_uid, status}].

El contenido real (markdown, unidades, code samples) se hidrata desde
LearnModule en el router vía hydrate_topics(), evitando duplicar KBs
de markdown por sesión.

Errores:
  - ModulesNotIngestedError si no hay módulos en BD para el nivel.
    El router la mapea a HTTP 503 con instrucción de ejecutar la ingesta.

Incluye single-flight: si dos requests piden el mismo nivel al mismo
tiempo, solo se ejecuta el primero; el segundo espera el resultado.
"""

import asyncio
import json
import logging
from typing import Awaitable, Callable, TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import LEARNING_PATH_ORDER_PROMPT
from app.db import async_session
from app.db.models import LearnModule
from app.learn_curriculum import get_curated_uids
from app.services.llm_service import get_llm

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ─── Excepciones ─────────────────────────────────────────────────────────────


class ModulesNotIngestedError(RuntimeError):
    """No hay módulos ingestate en BD para el nivel solicitado.

    El router la mapea a HTTP 503 con instrucción de ejecutar el script
    de ingesta. No se cae al método de búsqueda legacy: la decisión de
    diseño es requerir pre-ingesta.
    """


# ─── Single-flight (evita builds concurrentes duplicados) ──────────────────

_in_flight: dict[str, asyncio.Future] = {}
_in_flight_lock = asyncio.Lock()


async def single_flight(key: str, coro_factory: Callable[[], Awaitable[T]]) -> T:
    """
    Ejecuta coro_factory una sola vez por key. Llamadas concurrentes con
    la misma key esperan el mismo Future en vez de duplicar el trabajo.
    """
    async with _in_flight_lock:
        if key in _in_flight:
            existing = _in_flight[key]
            logger.info(f"single-flight: joining in-flight build for key={key}")
            return await existing  # type: ignore[return-value]

        future: asyncio.Future = asyncio.get_running_loop().create_future()
        _in_flight[key] = future

    # Fuera del lock: ejecutar el trabajo
    try:
        result = await coro_factory()
        future.set_result(result)
        return result
    except Exception as exc:
        future.set_exception(exc)
        raise
    finally:
        async with _in_flight_lock:
            _in_flight.pop(key, None)


# ─── Helpers ───────────────────────────────────────────────────────────────


def _normalize_url(url: str) -> str:
    """Normaliza una URL para comparación robusta (trailing slash + case)."""
    return (url or "").strip().rstrip("/").lower()


def _module_to_topic(m: LearnModule) -> dict:
    """Construye un topic hidratado desde una fila de LearnModule."""
    return {
        "module_uid": m.uid,
        "title": m.title,
        "description": m.summary or "",
        "url": m.url or "",
        "duration_minutes": m.duration_minutes,
        "content": m.content or "",
        "code_samples": m.code_samples or [],
        "units": m.units or [],
        "icon_url": m.icon_url or "",
        "social_image_url": m.social_image_url or "",
    }


def _assign_ids(topics: list[dict]) -> list[dict]:
    """Asigna id secuencial y status='pending'."""
    return [
        {**t, "id": i + 1, "status": "pending"}
        for i, t in enumerate(topics)
    ]


async def _order_with_llm(topics: list[dict], level: str) -> list[dict] | None:
    """
    Pide al LLM reordenar los módulos en progresión pedagógica.

    Estrategia (preserva TODOS los campos originales):
      1. Envía al LLM un payload LIVIANO con solo {title, url, description}.
      2. El LLM devuelve el nuevo orden con esos mismos campos.
      3. Validamos tipo, count y URLs.
      4. Reconstruimos cada topic final tomando el original completo
         (module_uid, content, units, code_samples, duration_minutes, ...)
         según el orden indicado por el LLM.

    Returns:
        Lista reordenada con el shape completo, o None si el LLM no
        responde con un JSON parseable (el caller usa el orden curado).
    """
    try:
        llm = get_llm()

        system_prompt = LEARNING_PATH_ORDER_PROMPT.format(level=level)

        light_payload = [
            {
                "title": t.get("title", ""),
                "url": t.get("url", ""),
                "description": t.get("description", ""),
            }
            for t in topics
        ]
        user_payload = json.dumps(light_payload, ensure_ascii=False, indent=2)
        user_message = (
            "Reordena los siguientes recursos de Microsoft Learn en progresión "
            "pedagógica óptima para un estudiante de nivel "
            f'"{level}". Devuelve SOLO el JSON array, sin markdown.\n\n'
            f"Recursos:\n{user_payload}"
        )

        response = await llm.ainvoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]
        )

        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        ordered = json.loads(content)

        if not isinstance(ordered, list):
            logger.warning("LLM ordering returned non-list. Falling back to curated order.")
            return None

        if len(ordered) != len(topics):
            logger.warning(
                f"LLM ordering changed resource count ({len(ordered)} vs {len(topics)}). "
                "Falling back to curated order."
            )
            return None

        # Indexar topics originales por URL normalizada
        original_by_url: dict[str, dict] = {}
        for t in topics:
            key = _normalize_url(t.get("url", ""))
            if key:
                original_by_url[key] = t

        for r in ordered:
            key = _normalize_url(r.get("url", ""))
            if key not in original_by_url:
                logger.warning(
                    f"LLM ordering returned a URL not in the original set: {r.get('url')}. "
                    "Falling back to curated order."
                )
                return None

        # Reconstruir preservando el orden del LLM y TODOS los campos del original
        result: list[dict] = []
        for r in ordered:
            key = _normalize_url(r.get("url", ""))
            result.append(dict(original_by_url[key]))

        return result
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        logger.warning(f"LLM ordering parse failed: {e}. Falling back to curated order.")
        return None
    except Exception as e:
        logger.warning(f"LLM ordering unexpected error: {e}. Falling back to curated order.")
        return None


# ─── Hidratación pública (usada por el router) ─────────────────────────────


async def hydrate_topics(topics: list[dict], db: AsyncSession) -> list[dict]:
    """Hidrata referencias ligeras [{id, module_uid, status}] con el
    contenido completo desde LearnModule.

    Compatibilidad legacy: si un topic no tiene module_uid (formato
    viejo inline con content/url/etc.), se retorna tal cual.
    """
    uids = [t.get("module_uid") for t in topics if t.get("module_uid")]
    modules_by_uid: dict[str, LearnModule] = {}
    if uids:
        result = await db.execute(
            select(LearnModule).where(LearnModule.uid.in_(uids))
        )
        for m in result.scalars().all():
            modules_by_uid[m.uid] = m

    hydrated: list[dict] = []
    for t in topics:
        uid = t.get("module_uid")
        if uid and uid in modules_by_uid:
            m = modules_by_uid[uid]
            hydrated.append(
                {
                    "id": t.get("id"),
                    "module_uid": uid,
                    "title": m.title,
                    "description": m.summary or "",
                    "url": m.url or "",
                    "duration_minutes": m.duration_minutes,
                    "status": t.get("status", "pending"),
                    "content": m.content or "",
                    "code_samples": m.code_samples or [],
                    "units": m.units or [],
                    "icon_url": m.icon_url or "",
                    "social_image_url": m.social_image_url or "",
                }
            )
        else:
            # Legacy inline topic o módulo faltante en BD
            hydrated.append(t)
    return hydrated


# ─── Entry point público ────────────────────────────────────────────────────


async def _build_impl(level: str) -> list[dict]:
    """Implementación real del build. Retorna referencias ligeras
    [{id, module_uid, status}] ordenadas pedagógicamente.

    Raises:
        ModulesNotIngestedError: Si no hay módulos en BD para el nivel.
    """
    uids = get_curated_uids(level)
    if not uids:
        raise ModulesNotIngestedError(
            f"No hay módulos curados para el nivel '{level}'."
        )

    logger.info(f"[build start] level={level} curated_uids={len(uids)}")

    async with async_session() as db:
        result = await db.execute(
            select(LearnModule).where(LearnModule.uid.in_(uids))
        )
        modules = result.scalars().all()

    if not modules:
        raise ModulesNotIngestedError(
            f"No hay módulos ingestate en BD para level='{level}'. "
            f"Ejecuta: python -m scripts.ingest_learn_modules --level {level}"
        )

    # Preservar el orden curado (uids está en orden pedagógico curado)
    modules_by_uid = {m.uid: m for m in modules}
    topics: list[dict] = []
    missing: list[str] = []
    for uid in uids:
        m = modules_by_uid.get(uid)
        if not m:
            missing.append(uid)
            continue
        topics.append(_module_to_topic(m))

    if missing:
        logger.warning(
            f"[build] módulos curados no ingestate para {level}: {missing}"
        )

    if not topics:
        raise ModulesNotIngestedError(
            f"Ninguno de los módulos curados para level='{level}' está ingestado. "
            f"Ejecuta: python -m scripts.ingest_learn_modules --level {level}"
        )

    logger.info(
        f"[build] {len(topics)}/{len(uids)} módulos disponibles desde BD"
    )

    # Reordenar con LLM (preserva contenido, solo cambia orden)
    ordered = await _order_with_llm(topics, level)
    if ordered is None:
        logger.info("[build] usando orden curado original (LLM ordering unavailable)")
        ordered = topics
    else:
        logger.info("[build] usando orden pedagógico del LLM")

    final = _assign_ids(ordered)

    # Convertir a referencias ligeras para persistir
    refs = [
        {"id": t["id"], "module_uid": t["module_uid"], "status": t["status"]}
        for t in final
    ]

    logger.info(f"[build done] level={level} topics={len(refs)}")
    return refs


async def build_learning_path_for_level(level: str) -> list[dict]:
    """
    Construye un learning path para el nivel dado a partir de los
    módulos curados e ingestate en BD.

    Aplica single-flight: si hay un build en curso para el mismo nivel,
    los callers concurrentes reciben el mismo resultado.

    Args:
        level: "beginner" | "intermediate" | "advanced"

    Returns:
        Lista de referencias ligeras:
          [{"id": int, "module_uid": str, "status": "pending"}]

    Raises:
        ModulesNotIngestedError: Si no hay módulos ingestate en BD.
    """
    return await single_flight(
        key=f"build_path:{level}",
        coro_factory=lambda: _build_impl(level),
    )
