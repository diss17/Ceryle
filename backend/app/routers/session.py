"""
Ceryle - Router de Sesión.

Endpoints:
  - DELETE /session/{session_id} → Borra todos los datos de la sesión de la BD
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import LearningPath, QuizResult, TopicMessage

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/session",
    tags=["session"],
)


@router.delete(
    "/{session_id}",
    summary="Resetear sesión completa",
    description="Elimina todos los datos asociados a una sesión (quiz, learning path, topic messages).",
)
async def reset_session(session_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Borra toda la información de la sesión de la base de datos."""
    try:
        # Eliminar todos los mensajes de topic chat
        await db.execute(delete(TopicMessage).where(TopicMessage.session_id == session_id))
        
        # Eliminar la ruta de aprendizaje
        await db.execute(delete(LearningPath).where(LearningPath.session_id == session_id))
        
        # Eliminar el resultado del quiz
        await db.execute(delete(QuizResult).where(QuizResult.session_id == session_id))
        
        await db.commit()
        
        logger.info(f"Sesión {session_id} reseteada completamente")
        return {"status": "ok", "message": "Sesión reseteada correctamente"}
    except Exception as e:
        logger.error(f"Error reseteando sesión {session_id}: {e}")
        await db.rollback()
        return {"status": "error", "message": str(e)}
