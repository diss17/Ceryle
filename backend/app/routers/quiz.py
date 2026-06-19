"""
Ceryle - Router del Quiz de Madurez de IA.

Endpoints:
  - GET  /quiz/questions         → Retorna las preguntas (sin pesos)
  - POST /quiz/submit            → Recibe respuestas, calcula nivel, guarda en DB
  - GET  /quiz/result/{session_id} → Retorna resultado previo si existe
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import QuizResult
from app.models.schemas import QuizQuestionOut, QuizResultResponse, QuizSubmitRequest
from app.quiz.questions import QUESTIONS
from app.quiz.scoring import LEVEL_DESCRIPTIONS, calculate_score, determine_level

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"],
)


@router.get(
    "/questions",
    response_model=list[QuizQuestionOut],
    summary="Obtener preguntas del quiz",
    description="Retorna todas las preguntas del quiz sin revelar los pesos de cada opción.",
)
async def get_questions() -> list[QuizQuestionOut]:
    """Retorna las preguntas del quiz listas para renderizar en el frontend."""
    return [
        QuizQuestionOut(id=q.id, text=q.text, options=q.options)
        for q in QUESTIONS
    ]


@router.post(
    "/submit",
    response_model=QuizResultResponse,
    summary="Enviar respuestas del quiz",
    description="Recibe las respuestas, calcula el nivel de madurez y lo guarda en la base de datos.",
)
async def submit_quiz(
    request: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
) -> QuizResultResponse:
    """
    Flujo:
      1. Valida que no exista un resultado previo para este session_id
      2. Calcula el score sumando los pesos de las opciones seleccionadas
      3. Determina el nivel según umbrales (33%/66%)
      4. Guarda el resultado en la tabla quiz_results
      5. Retorna el nivel, score y descripción
    """
    # Verificar si ya existe un resultado para esta sesión
    existing = await db.execute(
        select(QuizResult).where(QuizResult.session_id == request.session_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="This session already has a quiz result. Use GET /quiz/result/{session_id} to retrieve it.",
        )

    # Calcular score y nivel
    score, total = calculate_score(request.answers)
    level = determine_level(score, total)

    logger.info(f"Quiz completed: session={request.session_id[:8]}... score={score}/{total} level={level}")

    # Guardar en base de datos
    quiz_result = QuizResult(
        session_id=request.session_id,
        level=level,
        score=score,
        total=total,
        answers=request.answers,
    )
    db.add(quiz_result)
    await db.commit()

    return QuizResultResponse(
        session_id=request.session_id,
        level=level,
        score=score,
        total=total,
        description=LEVEL_DESCRIPTIONS[level],
    )


@router.get(
    "/result/{session_id}",
    response_model=QuizResultResponse,
    summary="Obtener resultado previo",
    description="Retorna el resultado del quiz si el usuario ya lo completó.",
)
async def get_result(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> QuizResultResponse:
    """Busca un resultado existente por session_id."""
    result = await db.execute(
        select(QuizResult).where(QuizResult.session_id == session_id)
    )
    quiz_result = result.scalar_one_or_none()

    if not quiz_result:
        raise HTTPException(
            status_code=404,
            detail="No quiz result found for this session.",
        )

    return QuizResultResponse(
        session_id=quiz_result.session_id,
        level=quiz_result.level,
        score=quiz_result.score,
        total=quiz_result.total,
        description=LEVEL_DESCRIPTIONS[quiz_result.level],
    )
