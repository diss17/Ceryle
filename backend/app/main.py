"""
Ceryle API - Entry Point.

Este es el punto de entrada de la aplicación FastAPI.
Aquí se:
  1. Crea la instancia de la app con metadatos
  2. Configura CORS para permitir requests del frontend en desarrollo
  3. Registra los routers (endpoints)
  4. Define el health check
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.models.schemas import HealthResponse
from app.routers import chat, learning_path, quiz, session, topic_chat

# ─── Configuración de Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)

# Silenciar el ruido HTTP de bajo nivel (GET/POST/DELETE request lines,
# incluyendo los 405 inofensivos del cleanup de sesiones MCP).
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ─── Crear la aplicación FastAPI ────────────────────────────────────────────
app = FastAPI(
    title="Ceryle API",
    description=(
        "Backend de Ceryle: plataforma híbrida para adopción de IA Generativa "
        "con Memoria de Largo Plazo y servidores MCP."
    ),
    version="0.1.0",
)

# ─── Middleware CORS ────────────────────────────────────────────────────────
# Permite que el frontend (Vite en localhost:5173) haga requests al backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternativa React
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Registrar Routers ─────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(quiz.router)
app.include_router(learning_path.router)
app.include_router(topic_chat.router)
app.include_router(session.router)

# ─── Health Check ───────────────────────────────────────────────────────────


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["sistema"],
    summary="Verificar que el servidor está activo",
)
async def health_check() -> HealthResponse:
    """Retorna el estado del servidor y el entorno actual."""
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
    )


# ─── Evento de Startup ─────────────────────────────────────────────────────


@app.on_event("startup")
async def on_startup():
    """Inicializa la base de datos y loguea la configuración."""
    # Crear tablas si no existen
    await init_db()

    model_info = (
        f"Ollama ({settings.ollama_model}) en {settings.ollama_base_url}"
        if settings.use_local_model
        else "Google Gemini (remoto)"
    )
    logger.info("=" * 50)
    logger.info("🐦 Ceryle API iniciada")
    logger.info(f"   Entorno: {settings.app_env}")
    logger.info(f"   Modelo:  {model_info}")
    logger.info(f"   DB:      {settings.database_url}")
    logger.info("=" * 50)
