"""
Ceryle - Router de Chat por Tópico.

Endpoints:
  - GET  /topic-chat/{session_id}/{topic_id} → Retorna historial de mensajes
  - POST /topic-chat/{session_id}/{topic_id} → Envía mensaje, invoca agente, guarda en DB

El agente de tópico recibe, además del título/descripción, el contenido
real de la página de Microsoft Learn y code samples para fundamentar
sus respuestas (RAG nativo basado en la ruta del usuario).
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.topic_agent import invoke_topic_agent
from app.db import get_db
from app.db.models import LearningPath, TopicMessage
from app.services.learning_path_builder import hydrate_topics
from app.services.mcp_learn_client import MCPUnavailableError, search_learn_content

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/topic-chat",
    tags=["topic-chat"],
)


class TopicChatRequest(BaseModel):
    message: str


class TopicChatResponse(BaseModel):
    response: str
    model_used: str
    resources: list[dict] | None = None
    url: str | None = None


@router.get(
    "/{session_id}/{topic_id}",
    summary="Get topic chat history",
    description="Returns all messages for a specific topic chat.",
)
async def get_topic_history(
    session_id: str,
    topic_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna el historial completo de un chat de tópico."""
    result = await db.execute(
        select(TopicMessage)
        .where(TopicMessage.session_id == session_id)
        .where(TopicMessage.topic_id == topic_id)
        .order_by(TopicMessage.created_at.asc())
    )
    messages = result.scalars().all()

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
        }
        for msg in messages
    ]


@router.post(
    "/{session_id}/{topic_id}",
    response_model=TopicChatResponse,
    summary="Send message to topic chat",
    description=(
        "Sends a message to the topic-specialized agent. The agent uses the "
        "Microsoft Learn content cached in the topic as primary reference. "
        "Persists both messages in DB."
    ),
)
async def send_topic_message(
    session_id: str,
    topic_id: int,
    body: TopicChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Flujo:
      1. Obtiene metadata del tópico desde LearningPath (incluye content + code_samples)
      2. Carga historial previo para contexto
      3. Invoca el agente especializado con reference content (RAG nativo)
      4. Si la respuesta es out_of_scope → busca recursos vía MCP
      5. Guarda ambos mensajes en DB
      6. Retorna respuesta + recursos opcionales
    """
    # 1. Obtener tópico metadata
    lp_result = await db.execute(
        select(LearningPath).where(LearningPath.session_id == session_id)
    )
    learning_path = lp_result.scalar_one_or_none()

    if not learning_path:
        raise HTTPException(status_code=404, detail="No learning path found.")

    # Buscar el tópico por id
    topic = None
    for t in learning_path.topics:
        if t["id"] == topic_id:
            topic = t
            break

    if not topic:
        raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found.")

    # Hidratar el tópico desde LearnModule (las refs solo tienen
    # {id, module_uid, status}; el agente necesita content/code_samples).
    # Compatibilidad legacy: si no hay module_uid, el topic ya viene inline.
    if topic.get("module_uid"):
        hydrated = await hydrate_topics([topic], db)
        topic = hydrated[0]

    # 2. Cargar historial previo
    history_result = await db.execute(
        select(TopicMessage)
        .where(TopicMessage.session_id == session_id)
        .where(TopicMessage.topic_id == topic_id)
        .order_by(TopicMessage.created_at.asc())
    )
    history_msgs = history_result.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs]

    # 3. Guardar mensaje del usuario en DB
    user_msg = TopicMessage(
        session_id=session_id,
        topic_id=topic_id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)

    # 4. Invocar agente especializado con reference content + code samples
    response_text, model_used = await invoke_topic_agent(
        message=body.message,
        topic_title=topic["title"],
        topic_description=topic["description"],
        history=history,
        reference_content=topic.get("content", ""),
        code_samples=topic.get("code_samples", []),
        units=topic.get("units", []),
    )

    # 5. Detectar out_of_scope
    resources = None
    was_out_of_scope = False
    try:
        parsed = json.loads(response_text.strip())
        if isinstance(parsed, dict) and parsed.get("out_of_scope"):
            was_out_of_scope = True
            query = parsed.get("query", topic["title"])
            try:
                resources = await search_learn_content(query)
            except MCPUnavailableError as e:
                logger.warning(
                    f"Topic chat out-of-scope search failed (MCP down): {e}"
                )
                resources = None

            if resources:
                # Rewrite response to be user-friendly
                resource_lines = "\n".join(
                    f"- [{r['title']}]({r['url']}): {r['description']}"
                    for r in resources
                )
                response_text = (
                    f"That question is outside the scope of **{topic['title']}**. "
                    f"Here are some resources that might help:\n\n{resource_lines}"
                )
            else:
                # MCP caído o sin resultados: avisar al usuario sin recursos.
                response_text = (
                    f"That question is outside the scope of **{topic['title']}**. "
                    f"I couldn't fetch external resources right now, but you can "
                    f"search Microsoft Learn directly for: \"{query}\"."
                )
    except (json.JSONDecodeError, TypeError):
        # Not JSON — it's a normal in-scope response
        pass

    # 6. Guardar respuesta del asistente en DB
    assistant_msg = TopicMessage(
        session_id=session_id,
        topic_id=topic_id,
        role="assistant",
        content=response_text,
    )
    db.add(assistant_msg)
    await db.commit()

    logger.info(
        f"Topic chat: session={session_id[:8]}... topic={topic_id} "
        f"out_of_scope={was_out_of_scope} "
        f"resources={len(resources) if resources else 0} "
        f"has_ref={'content' in topic and bool(topic.get('content'))}"
    )

    return TopicChatResponse(
        response=response_text,
        model_used=model_used,
        resources=resources,
        url=topic.get("url"),
    )
