"""
Ceryle - Agente Modo Aula (LangGraph).

Este agente actúa como tutor de IA Generativa. Su responsabilidad es:
1. Recibir la pregunta del usuario
2. Generar una respuesta educativa adaptada al nivel del alumno
3. Retornar la respuesta con metadatos (modelo usado)

Arquitectura del grafo:
  [START] → generate → [END]

  - generate: Nodo que invoca el LLM con un system prompt pedagógico.
    En fases futuras se añadirán nodos para:
    - Consultar el Grafo de Conocimiento (Memoria de Largo Plazo)
    - Clasificar el nivel del alumno
    - Decidir si usar ejemplos, analogías, etc.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from app.services.llm_service import get_llm

# ─── System Prompt del Agente Aula ─────────────────────────────────────────
# Define la personalidad y comportamiento del tutor.

AULA_SYSTEM_PROMPT = """Eres "Ceryle Aula", un tutor experto en Inteligencia Artificial Generativa.

Tu misión es enseñar conceptos de IA Generativa de forma clara, progresiva y adaptada al nivel del alumno.

REGLAS DE COMPORTAMIENTO:
1. Responde siempre en español.
2. Usa un tono amigable pero profesional, como un profesor universitario accesible.
3. Estructura tus respuestas con claridad: usa listas, ejemplos y analogías cuando sea apropiado.
4. Si el alumno hace una pregunta básica, no asumas que sabe conceptos avanzados.
5. Si la pregunta es avanzada, responde con profundidad técnica.
6. Al final de cada respuesta, sugiere una pregunta de seguimiento para profundizar.
7. Si no sabes algo, dilo honestamente. No inventes información.
8. Usa ejemplos prácticos y del mundo real para ilustrar conceptos.

ÁREAS DE EXPERTISE:
- Modelos de lenguaje (LLMs): arquitectura, entrenamiento, inferencia
- Prompt Engineering: técnicas, patrones, mejores prácticas
- RAG (Retrieval Augmented Generation)
- Agentes de IA y herramientas
- Ética y limitaciones de la IA Generativa
- Aplicaciones prácticas en industria y educación
"""


# ─── Estado del Grafo ───────────────────────────────────────────────────────
# TypedDict que define qué datos fluyen entre los nodos del grafo.

class AulaState(TypedDict):
    """Estado que se pasa entre nodos del grafo Aula."""
    user_message: str       # Mensaje original del usuario
    response: str           # Respuesta generada por el LLM
    model_used: str         # Identificador del modelo usado


# ─── Nodos del Grafo ────────────────────────────────────────────────────────

async def generate(state: AulaState) -> AulaState:
    """
    Nodo principal: invoca el LLM con el system prompt pedagógico.

    Recibe el mensaje del usuario en state["user_message"],
    construye la lista de mensajes (system + human),
    invoca el LLM y guarda la respuesta en state["response"].
    """
    llm = get_llm()

    # Construir la secuencia de mensajes para el LLM
    messages = [
        SystemMessage(content=AULA_SYSTEM_PROMPT),
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

def build_aula_graph() -> StateGraph:
    """
    Construye y compila el grafo LangGraph del Agente Aula.

    Flujo actual (Fase 1):
        START → generate → END

    Flujo futuro (con Memoria de Largo Plazo):
        START → retrieve_context → classify_level → generate → update_memory → END

    Returns:
        CompiledGraph listo para ser invocado con .ainvoke()
    """
    # Crear el grafo con el schema de estado
    graph = StateGraph(AulaState)

    # Registrar nodos
    graph.add_node("generate", generate)

    # Definir flujo: START → generate → END
    graph.add_edge(START, "generate")
    graph.add_edge("generate", END)

    # Compilar y retornar
    return graph.compile()


# ─── Instancia compilada (singleton) ───────────────────────────────────────
# Se compila una vez al importar el módulo. Es thread-safe.

aula_graph = build_aula_graph()


# ─── Función de invocación pública ─────────────────────────────────────────

async def invoke_aula_agent(message: str) -> tuple[str, str]:
    """
    Punto de entrada para invocar el Agente Aula.

    Args:
        message: Pregunta o mensaje del usuario.

    Returns:
        Tupla (respuesta_texto, modelo_usado).
    """
    result = await aula_graph.ainvoke({"user_message": message})
    return result["response"], result["model_used"]
