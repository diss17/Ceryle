"""
Ceryle - Agente Modo Co-creador (LangGraph).

Este agente actúa como experto en Prompt Engineering. Su responsabilidad es:
1. Recibir la intención o borrador de prompt del usuario
2. Analizar, mejorar o construir un prompt optimizado
3. Retornar el prompt refinado con explicación de las mejoras

Arquitectura del grafo:
  [START] → generate → [END]

  - generate: Nodo que invoca el LLM con un system prompt de experto en prompts.
    En fases futuras se añadirán nodos para:
    - Conectar con MCP Server para obtener contexto adicional
    - Aplicar frameworks de prompting (CO-STAR, RISEN, etc.)
    - Iterar con feedback del usuario
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from app.services.llm_service import get_llm
from app.agents.prompts import COCREADOR_SYSTEM_PROMPT


# ─── Estado del Grafo ───────────────────────────────────────────────────────

class CocreadorState(TypedDict):
    """Estado que se pasa entre nodos del grafo Co-creador."""
    user_message: str       # Mensaje/intención/borrador del usuario
    response: str           # Prompt refinado + explicación
    model_used: str         # Identificador del modelo usado


# ─── Nodos del Grafo ────────────────────────────────────────────────────────

async def generate(state: CocreadorState) -> CocreadorState:
    """
    Nodo principal: invoca el LLM con el system prompt de prompt engineering.

    Recibe el mensaje del usuario en state["user_message"],
    construye la secuencia de mensajes y genera el prompt refinado.
    """
    llm = get_llm()

    # Construir la secuencia de mensajes para el LLM
    messages = [
        SystemMessage(content=COCREADOR_SYSTEM_PROMPT),
        HumanMessage(content=state["user_message"]),
    ]

    # Invocar el LLM de forma asíncrona
    response = await llm.ainvoke(messages)

    # Determinar qué modelo se usó
    from app.config import settings
    model_name = (
        f"ollama/{settings.ollama_model}"
        if settings.use_local_model
        else "gemini-2.5-flash"
    )

    return {
        "user_message": state["user_message"],
        "response": response.content,
        "model_used": model_name,
    }


# ─── Construcción del Grafo ─────────────────────────────────────────────────

def build_cocreador_graph() -> StateGraph:
    """
    Construye y compila el grafo LangGraph del Agente Co-creador.

    Flujo actual (Fase 1):
        START → generate → END

    Flujo futuro (con MCP Server):
        START → analyze_intent → fetch_mcp_context → generate → refine → END

    Returns:
        CompiledGraph listo para ser invocado con .ainvoke()
    """
    graph = StateGraph(CocreadorState)

    # Registrar nodos
    graph.add_node("generate", generate)

    # Definir flujo: START → generate → END
    graph.add_edge(START, "generate")
    graph.add_edge("generate", END)

    # Compilar y retornar
    return graph.compile()


# ─── Instancia compilada (singleton) ───────────────────────────────────────

cocreador_graph = build_cocreador_graph()


# ─── Función de invocación pública ─────────────────────────────────────────

async def invoke_cocreador_agent(message: str) -> tuple[str, str]:
    """
    Punto de entrada para invocar el Agente Co-creador.

    Args:
        message: Intención, borrador de prompt o prompt a mejorar.

    Returns:
        Tupla (respuesta_texto, modelo_usado).
    """
    result = await cocreador_graph.ainvoke({"user_message": message})
    return result["response"], result["model_used"]
