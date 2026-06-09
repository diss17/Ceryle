# Arquitectura de Ceryle

## Visión General

Ceryle es una plataforma web híbrida para la adopción de IA Generativa con dos modos:

- **Modo Aula**: Educativo, adapta complejidad según el Grafo de Conocimiento del Usuario.
- **Modo Co-creador**: Diseño de prompts asistido por servidores MCP de Microsoft.

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React + TypeScript + Tailwind CSS |
| Backend | Python (FastAPI) + LangChain + LangGraph |
| Contexto | Microsoft MCP Server |
| Base de Datos | PostgreSQL / SQLite |
| Inferencia | Google Gemini API / Ollama (local) |

## Diagrama de Capas

```
┌─────────────────────────────────────────┐
│           Frontend (React/TS)           │
│      Modo Aula  │  Modo Co-creador      │
└────────────────┬────────────────────────┘
                 │ HTTP/SSE
┌────────────────▼────────────────────────┐
│         Backend (FastAPI)               │
│  Routers → Services → Core             │
├─────────────────────────────────────────┤
│  LangChain / LangGraph (Orquestación)  │
├──────────┬──────────────┬───────────────┤
│ Gemini API│  Ollama Local │  MCP Server  │
└──────────┴──────────────┴───────────────┘
                 │
┌────────────────▼────────────────────────┐
│  PostgreSQL / SQLite                    │
│  (Grafo de Conocimiento del Usuario)    │
└─────────────────────────────────────────┘
```
