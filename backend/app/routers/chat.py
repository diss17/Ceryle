"""
Ceryle - Router de Chat.

Define el endpoint POST /chat que:
1. Recibe un mensaje del usuario con el modo seleccionado
2. Hace dispatch al agente correcto (Aula o Co-creador)
3. Retorna la respuesta estructurada (ChatResponse)
"""

import logging

from fastapi import APIRouter, HTTPException

from app.agents.aula_agent import invoke_aula_agent
from app.agents.cocreador_agent import invoke_cocreador_agent
from app.models.schemas import AgentMode, ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

# Crear el router con prefijo y tag para la documentación automática
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
    summary="Enviar mensaje a un agente Ceryle",
    description="Recibe un mensaje y lo enruta al agente correspondiente según el modo (aula o cocreador).",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal de conversación.

    Flujo:
      1. Valida el body con Pydantic (ChatRequest)
      2. Según request.mode, invoca el agente Aula o Co-creador
      3. Retorna ChatResponse con la respuesta y el modelo usado
    """
    try:
        logger.info(
            f"[{request.mode.value}] Mensaje recibido ({len(request.message)} chars)"
        )

        # ─── Dispatch al agente correcto ────────────────────────────
        if request.mode == AgentMode.AULA:
            response_text, model_used = await invoke_aula_agent(request.message)
        else:
            response_text, model_used = await invoke_cocreador_agent(request.message)

        logger.info(f"[{request.mode.value}] Respuesta generada por {model_used}")

        return ChatResponse(
            response=response_text,
            model_used=model_used,
        )

    except ValueError as e:
        # Error de configuración (ej: API key faltante)
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        logger.error(f"Error al invocar agente [{request.mode.value}]: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Error al comunicarse con el modelo: {str(e)}",
        )
