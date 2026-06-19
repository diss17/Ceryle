"""
Ceryle - Configuración de Base de Datos (SQLAlchemy Async).

Usa SQLite con aiosqlite para operaciones asíncronas.
El archivo ceryle.db se crea automáticamente en backend/.

Para migrar a PostgreSQL en producción, solo cambia DATABASE_URL:
  postgresql+asyncpg://user:pass@host/ceryle
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ─── Engine ─────────────────────────────────────────────────────────────────
# connect_args={"check_same_thread": False} es necesario solo para SQLite
engine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=(settings.app_env == "development"),
)

# ─── Session Factory ────────────────────────────────────────────────────────
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ─── Base declarativa ───────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""
    pass


# ─── Dependency para FastAPI ────────────────────────────────────────────────
async def get_db():
    """
    Generador de sesión para inyección de dependencias en FastAPI.

    Uso en un endpoint:
        @router.post("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        yield session


# ─── Crear tablas ───────────────────────────────────────────────────────────
async def init_db():
    """Crea todas las tablas definidas en los modelos si no existen."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
