"""
Ceryle - Servicio de LLM con LangChain (Patrón Strategy).

Este módulo encapsula la lógica de selección e invocación del modelo de lenguaje.
Según la variable USE_LOCAL_MODEL:
  - False → usa Google Gemini (remoto, requiere API key)
  - True  → usa Ollama (local, requiere servidor Ollama corriendo)

Funciones principales:
  - get_llm()        → Retorna la instancia del modelo configurado
  - invoke_llm(msg)  → Envía un mensaje al LLM y retorna la respuesta como string
"""

from langchain_core.language_models import BaseChatModel

from app.config import settings


def get_llm() -> BaseChatModel:
    """
    Factory que retorna el modelo de chat correcto según configuración.

    Returns:
        BaseChatModel: Instancia de ChatGoogleGenerativeAI o ChatOllama.

    Raises:
        ValueError: Si USE_LOCAL_MODEL=false y no hay GEMINI_API_KEY configurada.
    """
    if settings.use_local_model:
        # ─── Modelo Local: Ollama ───────────────────────────────────
        # Requiere que Ollama esté corriendo en OLLAMA_BASE_URL
        from langchain_ollama import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )
    else:
        # ─── Modelo Remoto: Google Gemini ───────────────────────────
        # Requiere una API key válida de Google AI Studio
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY no está configurada. "
                "Añádela al archivo .env o usa USE_LOCAL_MODEL=true para Ollama."
            )

        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
        )


async def invoke_llm(message: str) -> tuple[str, str]:
    """
    Envía un mensaje al LLM configurado y retorna la respuesta.

    Args:
        message: El texto del usuario a enviar al modelo.

    Returns:
        Tupla (respuesta_texto, nombre_modelo_usado).
    """
    llm = get_llm()

    # ainvoke es la versión async de invoke en LangChain
    response = await llm.ainvoke(message)

    # Determinar qué modelo se usó para informar al cliente
    model_name = (
        f"ollama/{settings.ollama_model}"
        if settings.use_local_model
        else "gemini-2.0-flash"
    )

    return response.content, model_name
