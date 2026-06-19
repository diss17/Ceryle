"""
Ceryle - Router de Learning Path.

Endpoints:
  - GET  /learning-path/{session_id}                  → Retorna la ruta existente o la construye
  - PATCH /learning-path/{session_id}/topic/{topic_id} → Marca un tópico como completado

El path se construye desde módulos curados de Microsoft Learn
pre-ingestados en la tabla LearnModule. El builder produce referencias
ligeras [{id, module_uid, status}]; este router las hidrata con el
contenido completo (markdown, unidades, code samples) antes de retornar.
Compatibilidad legacy: topics sin module_uid se retornan inline.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import LearningPath, QuizResult
from app.services.learning_path_builder import (
    ModulesNotIngestedError,
    build_learning_path_for_level,
    hydrate_topics,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/learning-path",
    tags=["learning-path"],
)


@router.get(
    "/{session_id}",
    summary="Get or generate learning path",
    description=(
        "Retorna la ruta de aprendizaje de la sesión. Si no existe, la construye "
        "desde módulos curados de Microsoft Learn pre-ingestados en BD, "
        "reordenándolos con LLM en progresión pedagógica según el nivel del quiz."
    ),
)
async def get_learning_path(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Flujo:
      1. Busca path existente en DB → si existe, hidrata y retorna
      2. Si no existe, busca el quiz result para obtener el nivel
      3. Construye el path (referencias ligeras) vía learning_path_builder
      4. Persiste las referencias
      5. Hidrata desde LearnModule y retorna
    """
    # 1. Path existente
    result = await db.execute(
        select(LearningPath).where(LearningPath.session_id == session_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        topics = await hydrate_topics(existing.topics, db)
        return {
            "session_id": existing.session_id,
            "level": existing.level,
            "topics": topics,
        }

    # 2. Quiz result requerido
    quiz_result = await db.execute(
        select(QuizResult).where(QuizResult.session_id == session_id)
    )
    quiz = quiz_result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(
            status_code=404,
            detail="No quiz result found. Complete the quiz first.",
        )

    # 3. Construir path desde módulos ingestate (referencias ligeras)
    logger.info(
        f"Generating learning path for session={session_id[:8]}... level={quiz.level}"
    )
    try:
        refs = await build_learning_path_for_level(quiz.level)
    except ModulesNotIngestedError as e:
        # No hay módulos en BD: instruir al operador ejecutar la ingesta.
        logger.error(f"Modules not ingested for level={quiz.level}: {e}")
        raise HTTPException(
            status_code=503,
            detail=(
                "Los módulos de aprendizaje aún no se han ingestado en la "
                "plataforma. Ejecuta el script de ingesta: "
                f"python -m scripts.ingest_learn_modules --level {quiz.level}"
            ),
        )

    # 4. Persistir referencias ligeras
    learning_path = LearningPath(
        session_id=session_id,
        level=quiz.level,
        topics=refs,
    )
    db.add(learning_path)
    await db.commit()

    # 5. Hidratar para la respuesta
    topics = await hydrate_topics(refs, db)

    logger.info(
        f"Learning path generated: {len(topics)} topics for level={quiz.level}"
    )

    return {"session_id": session_id, "level": quiz.level, "topics": topics}


@router.patch(
    "/{session_id}/topic/{topic_id}",
    summary="Update topic status",
    description="Marks a topic as completed.",
)
async def update_topic_status(
    session_id: str,
    topic_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Marca un tópico como completado actualizando el JSON de topics."""
    result = await db.execute(
        select(LearningPath).where(LearningPath.session_id == session_id)
    )
    learning_path = result.scalar_one_or_none()

    if not learning_path:
        raise HTTPException(status_code=404, detail="No learning path found.")

    topics = learning_path.topics
    updated = False
    for topic in topics:
        if topic["id"] == topic_id:
            topic["status"] = "completed"
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found.")

    # SQLAlchemy no detecta cambios en JSON mutado in-place, forzar update
    learning_path.topics = list(topics)
    await db.commit()

    return {"session_id": session_id, "topic_id": topic_id, "status": "completed"}
