"""
Ceryle - Instancia singleton de configuración.

Importa `settings` desde aquí en cualquier módulo del backend:

    from app.config import settings
    print(settings.gemini_api_key)

Se instancia una sola vez (patrón módulo-singleton de Python).
"""

from app.core.settings import Settings

# Instancia única — se crea al importar este módulo por primera vez.
# Pydantic-settings lee .env automáticamente al construir el objeto.
settings = Settings()
