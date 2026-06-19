"""
Ceryle - Currículo curado de módulos de Microsoft Learn.

Mapping level -> [module UIDs] seleccionados manualmente de los learning
paths de IA Generativa de MS Learn. Cada UID corresponde a un módulo
completo que se pre-ingesta en la tabla LearnModule vía
scripts/ingest_learn_modules.py.

Criterios de curaduría:
  - Solo IA Generativa (alineado con el scope del Agente Aula).
  - Progresión pedagógica coherente dentro de cada nivel.
  - Conteo por nivel alineado con LEVEL_TOPIC_COUNTS (5/7/9).

Las UIDs son case-sensitive y estables en el tiempo (MS Learn las
mantiene aunque el contenido se actualice).
"""

CURATED_MODULES: dict[str, list[str]] = {
    # ─── Beginner: fundamentos de GenAI, LLMs, prompts, agentes, evaluación ──
    "beginner": [
        "learn.wwl.get-started-ai-fundamentals",
        "learn.wwl.fundamentals-generative-ai",
        "learn.wwl.introduction-language",
        "learn.wwl.get-started-with-generative-ai-and-agents",
        "learn.evaluate-generative-ai-apps",
    ],
    # ─── Intermediate: desarrollo con Foundry, tools, agentes, MCP ───────────
    "intermediate": [
        "learn.wwl.prepare-azure-ai-development",
        "learn.wwl.foundry-sdk",
        "learn.wwl.generative-ai-tools",
        "learn.github.foundations-agentic-ai",
        "learn.wwl.develop-ai-agents-azure-vs-code",
        "learn.wwl.build-agent-with-custom-tools",
        "learn.wwl.connect-agent-to-mcp-tools",
    ],
    # ─── Advanced: arquitectura multi-agente, GenAIOps, observabilidad ───────
    "advanced": [
        "learn.wwl.design-agentic-loops-microsoft-foundry-agent-service",
        "learn.wwl.implement-multi-agent-orchestration-azure-ai-foundry",
        "learn.wwl.apply-task-decomposition-multi-agent-azure",
        "learn.wwl.implement-cicd-multi-agent-systems-github-actions",
        "learn.wwl.secure-multi-agent-systems-azure-zero-trust",
        "learn.wwl.plan-prepare-genaiops",
        "learn.wwl.evaluate-optimize-agents",
        "learn.wwl.monitor-generative-ai-app",
        "learn.wwl.implement-distributed-observability-multi-agent-opentelemetry",
    ],
}


def get_curated_uids(level: str) -> list[str]:
    """Retorna los UIDs curados para un nivel, o lista vacía si el nivel
    no está definido."""
    return list(CURATED_MODULES.get(level, []))


def all_curated_uids() -> list[str]:
    """Retorna todos los UIDs curados (deduplicados), útil para el
    script de ingesta que descarga todo de una vez."""
    seen: set[str] = set()
    result: list[str] = []
    for uids in CURATED_MODULES.values():
        for uid in uids:
            if uid not in seen:
                seen.add(uid)
                result.append(uid)
    return result
