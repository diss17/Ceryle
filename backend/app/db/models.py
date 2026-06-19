"""
Ceryle - Modelos de Base de Datos.

Define las tablas de la aplicación usando SQLAlchemy ORM.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class QuizResult(Base):
    """
    Almacena el resultado del quiz de madurez de IA de cada sesión.

    Campos:
      - id: Primary key autoincremental
      - session_id: UUID anónimo del usuario (almacenado en localStorage)
      - level: Nivel calculado ("beginner", "intermediate", "advanced")
      - score: Puntuación obtenida
      - total: Puntuación máxima posible
      - answers: JSON con las respuestas del usuario {question_id: selected_option_index}
      - created_at: Timestamp de cuándo se completó el quiz
    """

    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True, unique=True)
    level: Mapped[str] = mapped_column(String(20))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    answers: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearnModule(Base):
    """
    Biblioteca de módulos de Microsoft Learn pre-ingestados.

    Cada fila es un módulo completo (con todas sus unidades) descargado
    por scripts/ingest_learn_modules.py. Es independiente de las
    sesiones de usuario: el learning path builder consulta esta tabla
    por UID para hidratar los tópicos.

    Campos:
      - uid: UID estable de MS Learn (ej. learn.wwl.fundamentals-generative-ai)
      - title, summary, url: metadata del catálogo
      - level: nivel declarado del módulo ("beginner" | "intermediate" | "advanced")
      - duration_minutes: duración total del módulo
      - learning_path_uid: UID del learning path de MS Learn al que pertenece (opcional)
      - content: markdown concatenado de todas las unidades (para RAG del agente)
      - code_samples: [{language, code, description, url}, ...]
      - units: [{uid, title, url, duration_minutes, content}, ...] navegables
      - icon_url: URL del SVG badge de logro del módulo (100x100, transparente)
      - social_image_url: URL de la imagen social PNG del módulo (opcional)
      - last_ingested_at: timestamp de la última ingesta (para refresh)
    """

    __tablename__ = "learn_modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uid: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(500), default="")
    level: Mapped[str] = mapped_column(String(20), index=True, default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    learning_path_uid: Mapped[str] = mapped_column(String(120), nullable=True, default=None)
    content: Mapped[str] = mapped_column(Text, default="")
    code_samples: Mapped[list] = mapped_column(JSON, default=list)
    units: Mapped[list] = mapped_column(JSON, default=list)
    icon_url: Mapped[str] = mapped_column(String(500), default="")
    social_image_url: Mapped[str] = mapped_column(String(500), default="")
    last_ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class LearningPath(Base):
    """
    Almacena la ruta de aprendizaje generada para cada sesión.

    Desde la ingesta de módulos completos, `topics` es una lista de
    referencias ligeras: [{id, module_uid, status}]. El contenido real
    (markdown, unidades, code samples) se hidrata desde LearnModule en
    el momento del GET, evitando duplicar ~KBs de markdown por sesión.

    Compatibilidad legacy: filas creadas antes de la ingesta pueden
    tener topics con shape inline {id, title, description, url, content,
    code_samples, status} (sin module_uid). El router detecta la
    presencia de module_uid para distinguir el formato.
    """

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True, unique=True)
    level: Mapped[str] = mapped_column(String(20))
    topics: Mapped[list] = mapped_column(JSON)  # [{id, module_uid, status}] (nuevo) o inline (legacy)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


class TopicMessage(Base):
    """
    Almacena mensajes de chat persistentes por tópico de la ruta de aprendizaje.
    Cada combinación session_id + topic_id representa un chat independiente.
    """

    __tablename__ = "topic_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True)
    topic_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(10))  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
