"""
Ceryle - Cliente MCP para Microsoft Learn.

Se conecta al servidor MCP de Microsoft Learn para extraer conocimiento
real de la documentación oficial de Microsoft.

Endpoint: https://learn.microsoft.com/api/mcp
Transporte: Streamable HTTP (MCP spec)

Expone 3 herramientas, una por cada tool del MCP:
  - search_learn_content(query)       -> chunks de contenido (≤500 tokens c/u)
  - fetch_learn_page(url)             -> markdown completo de una página
  - search_learn_code_samples(query)  -> snippets de código

Y un agregador de alto nivel usado por el learning path builder:
  - collect_resources_for_level(level) -> [chunk, chunk, ...] deduplicados
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)


# ─── Excepciones ────────────────────────────────────────────────────────────


class MCPUnavailableError(RuntimeError):
    """El MCP de Microsoft Learn no responde o no pudo inicializar la sesión.

    Se propaga al caller para que decida la UX (típicamente HTTP 503 con un
    mensaje claro de reintentar), en vez de enmascarar el fallo con recursos
    placeholder que no aportan valor pedagógico.
    """


# ─── Configuración por nivel ────────────────────────────────────────────────

LEVEL_TOPIC_COUNTS: dict[str, int] = {
    "beginner": 5,
    "intermediate": 7,
    "advanced": 9,
}

LEVEL_QUERIES: dict[str, list[str]] = {
    "beginner": [
        "introduction to generative AI",
        "large language models basics",
        "prompt engineering fundamentals",
        "responsible AI principles",
        "Azure OpenAI getting started",
    ],
    "intermediate": [
        "retrieval augmented generation RAG",
        "embeddings and vector search",
        "LangChain orchestration",
        "advanced prompt engineering patterns",
        "evaluating LLM applications",
        "Azure AI Search",
        "function calling LLMs",
    ],
    "advanced": [
        "multi-agent systems design",
        "fine-tuning large language models",
        "LangGraph agent workflows",
        "LLM evaluation and monitoring",
        "production AI systems",
        "agentic AI patterns",
        "model distillation",
        "Model Context Protocol MCP",
        "LLM cost optimization",
    ],
}

LEVEL_FALLBACK_QUERIES: dict[str, list[str]] = {
    "beginner": [
        "getting started with AI",
        "what is a large language model",
        "writing effective prompts",
        "AI for beginners",
        "copilot fundamentals",
    ],
    "intermediate": [
        "Azure AI services overview",
        "vector databases",
        "prompt flow",
        "chat with your data",
        "AI app templates",
    ],
    "advanced": [
        "AI architecture patterns",
        "model evaluation framework",
        "responsible AI dashboard",
        "AI safety",
        "generative AI ops",
    ],
}


# ─── Helper compartido de conexión al MCP ──────────────────────────────────


@asynccontextmanager
async def _mcp_session():
    """
    Context manager que abre una sesión contra el MCP de Microsoft Learn.

    Uso:
        async with _mcp_session() as session:
            tools = await session.list_tools()
    """
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    async with streamablehttp_client("https://learn.microsoft.com/api/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def _parse_tool_payload(item: Any) -> Any:
    """Extrae y parsea el JSON del campo text de un content item del MCP."""
    text = getattr(item, "text", None)
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


# ─── Tool 1: microsoft_docs_search ─────────────────────────────────────────


async def search_learn_content(query: str) -> list[dict]:
    """
    Busca contenido oficial en Microsoft Learn y retorna hasta 10 chunks
    de hasta ~500 tokens cada uno (markdown).

    Retorna lista de dicts con:
      - title: str
      - url / contentUrl: str
      - content: str (markdown del chunk, ~2700 chars)
      - description: str (igual a los primeros 300 chars de content)

    Semántica de retorno:
      - Lista (posiblemente vacía) si el MCP respondió correctamente.
        Lista vacía = el MCP no tenía resultados para esta query.
      - Levanta MCPUnavailableError si el MCP no pudo inicializarse o
        respondió con error. El caller decide si reintentar o devolver 503.
    """
    try:
        async with _mcp_session() as session:
            result = await session.call_tool(
                "microsoft_docs_search",
                arguments={"query": query},
            )

            chunks: list[dict] = []
            for item in result.content or []:
                data = _parse_tool_payload(item)
                if not data:
                    continue
                results_list = (
                    data.get("results", data.get("items", []))
                    if isinstance(data, dict)
                    else (data if isinstance(data, list) else [])
                )
                for entry in results_list[:10]:
                    title = entry.get("title", "Microsoft Learn Resource")
                    content = entry.get("content", "")
                    url = entry.get("contentUrl", entry.get("url", ""))
                    chunks.append(
                        {
                            "title": title,
                            "url": url,
                            "contentUrl": url,
                            "content": content,
                            "description": (content[:300] + "...") if len(content) > 300 else content,
                        }
                    )

            return chunks

    except ImportError:
        logger.error("mcp package not installed. Run: pip install mcp")
        raise MCPUnavailableError(
            "El paquete 'mcp' no está instalado. Ejecuta: pip install mcp"
        )
    except MCPUnavailableError:
        raise
    except Exception as e:
        logger.warning(f"microsoft_docs_search failed for '{query}': {e}")
        raise MCPUnavailableError(
            f"microsoft_docs_search falló para '{query}': {e}"
        ) from e


# ─── Tool 2: microsoft_docs_fetch ──────────────────────────────────────────


FETCH_ERROR_MARKERS = (
    "could not be retrieved",
    "404",
    "not found",
    "unable to fetch",
)


async def fetch_learn_page(url: str) -> str:
    """
    Descarga el contenido completo de una página de Microsoft Learn
    y la retorna como markdown.

    Args:
        url: URL completa de una página de learn.microsoft.com.

    Returns:
        Markdown completo, o cadena vacía si la página no se pudo obtener.
    """
    if not url or "learn.microsoft.com" not in url:
        logger.warning(f"fetch_learn_page: URL no soportada: {url}")
        return ""

    try:
        async with _mcp_session() as session:
            result = await session.call_tool(
                "microsoft_docs_fetch",
                arguments={"url": url},
            )

            for item in result.content or []:
                text = getattr(item, "text", "")
                if not text:
                    continue
                lower = text.lower()
                if any(marker in lower for marker in FETCH_ERROR_MARKERS):
                    logger.info(f"fetch_learn_page: página no disponible {url}")
                    return ""
                if len(text) < 100:
                    # Respuesta sospechosamente corta, no es contenido real
                    logger.info(f"fetch_learn_page: respuesta corta para {url}: {text[:80]}")
                    return ""
                return text

            return ""

    except ImportError:
        logger.error("mcp package not installed. Run: pip install mcp")
        return ""
    except Exception as e:
        logger.warning(f"microsoft_docs_fetch failed for '{url}': {e}")
        return ""


async def fetch_learn_pages_batch(urls: list[str]) -> dict[str, str]:
    """Descarga el markdown de múltiples URLs en una sola sesión MCP.

    Abrir una sesión MCP por URL (como hace fetch_learn_page) tiene
    overhead de handshake + initialize. Para la ingesta de módulos
    completos (~168 unidades) conviene reutilizar una sesión para todas
    las llamadas microsoft_docs_fetch.

    Args:
        urls: Lista de URLs de learn.microsoft.com.

    Returns:
        Dict {url: markdown}. Las URLs que fallen o no sean contenido
        real se omiten (no aparecen en el dict). Nunca levanta
        excepción: errores por-URL se loguean y se continúa.
    """
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    results: dict[str, str] = {}
    valid_urls = [u for u in urls if u and "learn.microsoft.com" in u]
    if not valid_urls:
        return results

    try:
        async with streamablehttp_client("https://learn.microsoft.com/api/mcp") as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                for url in valid_urls:
                    try:
                        result = await session.call_tool(
                            "microsoft_docs_fetch",
                            arguments={"url": url},
                        )
                        for item in result.content or []:
                            text = getattr(item, "text", "")
                            if not text:
                                continue
                            lower = text.lower()
                            if any(marker in lower for marker in FETCH_ERROR_MARKERS):
                                logger.info(
                                    f"fetch_learn_pages_batch: no disponible {url}"
                                )
                                break
                            if len(text) < 100:
                                logger.info(
                                    f"fetch_learn_pages_batch: respuesta corta {url}"
                                )
                                break
                            results[url] = text
                            break
                    except Exception as e:
                        logger.warning(
                            f"fetch_learn_pages_batch: error en {url}: {e}"
                        )
                        continue
    except ImportError:
        logger.error("mcp package not installed. Run: pip install mcp")
    except Exception as e:
        logger.warning(f"fetch_learn_pages_batch: sesión MCP falló: {e}")

    return results


# ─── Tool 3: microsoft_code_sample_search ──────────────────────────────────


async def search_learn_code_samples(
    query: str,
    language: str | None = None,
    max_results: int = 3,
) -> list[dict]:
    """
    Busca snippets de código oficiales en Microsoft Learn.

    Args:
        query: Descripción del snippet, SDK, método, etc.
        language: Filtro opcional (python, javascript, csharp, ...).
        max_results: Máximo de snippets a retornar.

    Returns:
        Lista de dicts {language, code, description, url}.
        Vacía si no hay resultados o el MCP falla.
    """
    try:
        async with _mcp_session() as session:
            arguments: dict[str, Any] = {"query": query}
            if language:
                arguments["language"] = language

            result = await session.call_tool(
                "microsoft_code_sample_search",
                arguments=arguments,
            )

            samples: list[dict] = []
            for item in result.content or []:
                data = _parse_tool_payload(item)
                if not data:
                    continue
                results_list = (
                    data.get("results", data.get("items", []))
                    if isinstance(data, dict)
                    else (data if isinstance(data, list) else [])
                )
                for entry in results_list[:max_results]:
                    samples.append(
                        {
                            "language": entry.get("language", ""),
                            "code": entry.get("codeSnippet", ""),
                            "description": entry.get("description", ""),
                            "url": entry.get("link", ""),
                        }
                    )
                if samples:
                    break

            return samples

    except ImportError:
        logger.error("mcp package not installed. Run: pip install mcp")
        return []
    except Exception as e:
        logger.warning(f"microsoft_code_sample_search failed for '{query}': {e}")
        return []


# ─── Agregador de alto nivel ───────────────────────────────────────────────


async def collect_resources_for_level(
    level: str,
    primary_queries: list[str] | None = None,
    fallback_queries: list[str] | None = None,
    target_count: int | None = None,
) -> list[dict]:
    """
    Recolecta chunks de contenido de Microsoft Learn para un nivel dado.

    Estrategia:
      1. Ejecuta cada query primaria vía search_learn_content
      2. Deduplica por URL
      3. Si no alcanza target_count, ejecuta queries de fallback
      4. Retorna hasta target_count chunks

    Semántica de errores:
      - Si alguna query responde (aunque sea parcial), se acumula lo obtenido.
      - Si TODAS las queries (primarias + fallback) fallan con
        MCPUnavailableError → se propaga la excepción para que el caller
        decida la UX (típicamente HTTP 503).

    Returns:
        Lista de dicts {title, url, content, description, contentUrl}.

    Raises:
        MCPUnavailableError: Si ninguna query pudo completarse contra el MCP.
    """
    if target_count is None:
        target_count = LEVEL_TOPIC_COUNTS.get(level, 5)
    if primary_queries is None:
        primary_queries = LEVEL_QUERIES.get(level, [])
    if fallback_queries is None:
        fallback_queries = LEVEL_FALLBACK_QUERIES.get(level, [])

    collected: list[dict] = []
    seen_urls: set[str] = set()
    failures: list[str] = []

    def _add(chunks: list[dict]) -> None:
        for c in chunks:
            url = c.get("url") or c.get("contentUrl") or ""
            if url and url not in seen_urls:
                seen_urls.add(url)
                collected.append(c)

    async def _run_phase(queries: list[str], phase: str) -> None:
        for q in queries:
            if len(collected) >= target_count:
                break
            try:
                results = await search_learn_content(q)
                _add(results)
            except MCPUnavailableError as e:
                failures.append(f"{phase}:'{q}': {e}")
                logger.warning(f"Query failed in {phase} phase '{q}': {e}")

    await _run_phase(primary_queries, "primary")

    if len(collected) < target_count and fallback_queries:
        logger.info(
            f"Primary phase returned {len(collected)}/{target_count} chunks. "
            f"Trying fallback queries for level={level}."
        )
        await _run_phase(fallback_queries, "fallback")

    if not collected and failures:
        # Ningún recurso y todas las queries fallaron → MCP caído.
        raise MCPUnavailableError(
            f"Todas las queries MCP fallaron para level='{level}'. "
            f"Último error: {failures[-1]}"
        )

    return collected[:target_count]
