"""
Ceryle - Agente Experto en Tópico (LangGraph).

Este agente actúa como tutor especializado en UN tema específico
de la ruta de aprendizaje. Mantiene conversación contextual con
historial, rechaza preguntas fuera de su scope, y cuando el tópico
tiene contenido real de Microsoft Learn lo usa como referencia
primaria (RAG nativo).

Arquitectura del grafo:
  [START] → generate → [END]
"""

from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.agents.prompts import TOPIC_EXPERT_PROMPT
from app.services.llm_service import get_llm


# Cuántos caracteres del módulo de MS Learn inyectar al system prompt.
# Un módulo completo puede tener 10-50KB; truncamos para dejar margen
# al historial y la pregunta del usuario dentro del context window.
MAX_REFERENCE_CHARS = 20000

# Cuántos code samples formatear en el system prompt
MAX_CODE_SAMPLES_INJECTED = 3


class TopicState(TypedDict):
    """Estado del grafo del agente de tópico."""

    user_message: str
    topic_title: str
    topic_description: str
    reference_content: str  # markdown de MS Learn (puede ser vacío)
    code_samples: list  # [{language, code, description, url}, ...]
    units: list  # [{uid, title, url, duration_minutes, content}, ...]
    history: list  # Lista de dicts {role, content}
    response: str
    model_used: str


def _format_code_samples(code_samples: list[dict]) -> str:
    """Formatea los code samples para inyectarlos en el prompt."""
    if not code_samples:
        return "(no code samples available)"
    parts = []
    for s in code_samples[:MAX_CODE_SAMPLES_INJECTED]:
        lang = s.get("language", "")
        code = s.get("code", "")
        desc = s.get("description", "")
        parts.append(f"```{lang}\n# {desc}\n{code}\n```")
    return "\n\n".join(parts)


def _format_unit_outline(units: list[dict]) -> str:
    """Formatea la lista de unidades del módulo como un outline para
    que el agente pueda referenciar unidades concretas por título."""
    if not units:
        return "(no unit outline available)"
    lines = []
    for i, u in enumerate(units, 1):
        title = u.get("title", f"Unit {i}")
        dur = u.get("duration_minutes", 0)
        dur_str = f" ({dur} min)" if dur else ""
        lines.append(f"{i}. {title}{dur_str}")
    return "\n".join(lines)


def _truncate_reference(text: str, limit: int = MAX_REFERENCE_CHARS) -> str:
    """Trunca el reference content al límite y añade marcador."""
    if not text:
        return "(no reference content available for this topic yet)"
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[... truncated for length ...]"


async def generate(state: TopicState) -> TopicState:
    """
    Nodo principal: invoca el LLM con system prompt dinámico
    basado en el tópico asignado, incluyendo historial, reference
    content y code samples.
    """
    llm = get_llm()

    system_prompt = TOPIC_EXPERT_PROMPT.format(
        topic_title=state["topic_title"],
        topic_description=state["topic_description"],
        reference_content=_truncate_reference(state.get("reference_content", "")),
        code_samples=_format_code_samples(state.get("code_samples", [])),
        unit_outline=_format_unit_outline(state.get("units", [])),
    )

    # Construir secuencia de mensajes: system + historial + mensaje actual
    messages: list = [SystemMessage(content=system_prompt)]

    # Agregar historial (últimos 20 mensajes para no exceder context window)
    for msg in state["history"][-20:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Mensaje actual del usuario
    messages.append(HumanMessage(content=state["user_message"]))

    # Invocar LLM
    response = await llm.ainvoke(messages)

    # Determinar modelo usado
    from app.config import settings

    model_name = (
        f"ollama/{settings.ollama_model}"
        if settings.use_local_model
        else "gemini-2.5-flash"
    )

    return {
        "user_message": state["user_message"],
        "topic_title": state["topic_title"],
        "topic_description": state["topic_description"],
        "reference_content": state.get("reference_content", ""),
        "code_samples": state.get("code_samples", []),
        "units": state.get("units", []),
        "history": state["history"],
        "response": response.content,
        "model_used": model_name,
    }


def build_topic_graph() -> StateGraph:
    """Construye y compila el grafo del agente de tópico."""
    graph = StateGraph(TopicState)
    graph.add_node("generate", generate)
    graph.add_edge(START, "generate")
    graph.add_edge("generate", END)
    return graph.compile()


topic_graph = build_topic_graph()


async def invoke_topic_agent(
    message: str,
    topic_title: str,
    topic_description: str,
    history: list,
    reference_content: str = "",
    code_samples: list | None = None,
    units: list | None = None,
) -> tuple[str, str]:
    """
    Punto de entrada para invocar el Agente de Tópico.

    Args:
        message: Pregunta del usuario.
        topic_title: Título del tópico asignado.
        topic_description: Descripción del tópico.
        history: Historial de mensajes previos [{role, content}].
        reference_content: Markdown de MS Learn (opcional).
        code_samples: Lista de snippets [{language, code, description, url}].
        units: Lista de unidades del módulo [{uid, title, url, ...}].

    Returns:
        Tupla (respuesta_texto, modelo_usado).
    """
    result = await topic_graph.ainvoke(
        {
            "user_message": message,
            "topic_title": topic_title,
            "topic_description": topic_description,
            "reference_content": reference_content,
            "code_samples": code_samples or [],
            "units": units or [],
            "history": history,
            "response": "",
            "model_used": "",
        }
    )
    return result["response"], result["model_used"]
