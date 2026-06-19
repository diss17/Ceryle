"""
Ceryle - Schemas Pydantic para request/response.

Define los contratos de datos (DTOs) que validan automáticamente
las peticiones entrantes y estructuran las respuestas de la API.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AgentMode(str, Enum):
    """Modos disponibles en la plataforma Ceryle."""
    AULA = "aula"
    COCREADOR = "cocreador"


class ChatRequest(BaseModel):
    """Cuerpo de la petición POST /chat."""

    message: str = Field(
        ...,  # Campo obligatorio
        min_length=1,
        max_length=4000,
        description="Mensaje del usuario para enviar al agente.",
        examples=["¿Qué es un prompt en IA Generativa?"],
    )
    mode: AgentMode = Field(
        default=AgentMode.AULA,
        description="Modo del agente: 'aula' (educativo) o 'cocreador' (diseño de prompts).",
        examples=["aula", "cocreador"],
    )


class ChatResponse(BaseModel):
    """Respuesta del endpoint POST /chat."""

    response: str = Field(
        ...,
        description="Respuesta generada por el modelo de lenguaje.",
    )
    model_used: str = Field(
        ...,
        description="Identificador del modelo que generó la respuesta.",
        examples=["gemini-2.5-flash", "ollama/llama3"],
    )


class HealthResponse(BaseModel):
    """Respuesta del endpoint GET /health."""

    status: str = "ok"
    environment: str = "development"


# ─── Quiz Schemas ───────────────────────────────────────────────────────────


class QuizQuestionOut(BaseModel):
    """Una pregunta del quiz (sin revelar pesos/respuestas correctas)."""

    id: str
    text: str
    options: list[str]


class QuizSubmitRequest(BaseModel):
    """Cuerpo de la petición POST /quiz/submit."""

    session_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
        description="UUID de la sesión anónima del usuario.",
    )
    answers: dict[str, int] = Field(
        ...,
        description="Respuestas del usuario: {question_id: índice_opción_seleccionada}.",
    )


class QuizResultResponse(BaseModel):
    """Respuesta con el resultado del quiz."""

    session_id: str
    level: str = Field(..., description="Nivel calculado: beginner, intermediate, advanced.")
    score: int
    total: int
    description: str = Field(..., description="Descripción del nivel para el usuario.")
