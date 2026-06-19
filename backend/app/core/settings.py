"""
Ceryle - Configuración centralizada con pydantic-settings.

Este módulo define la clase Settings que:
1. Lee las variables de entorno desde el archivo .env
2. Las valida y tipifica automáticamente con Pydantic
3. Expone valores por defecto seguros para desarrollo

Uso:
    from app.core.settings import Settings
    settings = Settings()  # Carga .env automáticamente
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # --- Inferencia LLM ---
    gemini_api_key: str = ""  # Obligatoria si use_local_model=False
    use_local_model: bool = False  # True → Ollama, False → Gemini

    # --- Ollama (modelo local) ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # --- Base de Datos ---
    database_url: str = "sqlite+aiosqlite:///./ceryle.db"

    # --- Aplicación ---
    app_env: str = "development"
    log_level: str = "info"

    # pydantic-settings busca un archivo .env en el directorio de trabajo
    model_config = SettingsConfigDict(
        env_file=".env",        # Archivo de variables de entorno
        env_file_encoding="utf-8",
        case_sensitive=False,   # GEMINI_API_KEY == gemini_api_key
    )
