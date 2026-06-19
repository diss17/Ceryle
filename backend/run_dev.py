"""
Ceryle - Servidor de desarrollo con auto-reload.

Ejecuta uvicorn con reload scoping a app/ y scripts/ para evitar
reloads espurios por cambios en ceryle.db, venv/ o __pycache__.
El bare `uvicorn --reload` watches todo el CWD y recarga al escribir
la BD, lo que rompe el dev loop.

Uso:
    python run_dev.py
    python run_dev.py --port 8001
    python run_dev.py --host 0.0.0.0 --port 8000
"""

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ceryle dev server con auto-reload scoping a app/ y scripts/"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000)")
    args = parser.parse_args()

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=True,
        reload_dirs=["app", "scripts"],
        reload_includes=["*.py"],
        reload_excludes=["*.db", "*.db-*", "*.pyc", "__pycache__", "venv", ".venv"],
        reload_delay=0.5,
        log_level="info",
    )


if __name__ == "__main__":
    main()
