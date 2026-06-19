# Ceryle

Plataforma web híbrida para la adopción de IA Generativa con Memoria de Largo Plazo.

## Modos

- **Modo Aula** — Educativo, adapta complejidad según el Grafo de Conocimiento del Usuario.
- **Modo Co-creador** — Diseño de prompts asistido por servidores MCP de Microsoft.

## Stack

| Capa | Tecnología |
|------|-----------|
| Frontend | React + TypeScript + Tailwind CSS |
| Backend | Python (FastAPI) + LangChain + LangGraph |
| Contexto | Microsoft MCP Server |
| Datos | PostgreSQL / SQLite |
| Inferencia | Google Gemini API / Ollama |

## Inicio Rápido (Backend)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # Edita con tus claves
python run_dev.py              # Auto-reload (scope: app/, scripts/)
```

## Estructura

```
Ceryle/
├── backend/         # FastAPI + LangChain + LangGraph
├── frontend/        # React + TypeScript + Tailwind (Fase 2)
└── docs/            # Documentación de arquitectura
```
