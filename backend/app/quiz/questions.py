"""
Ceryle - Banco de Preguntas del Quiz de Madurez de IA.

Cada pregunta tiene:
  - id: Identificador único
  - text: El enunciado de la pregunta
  - options: Lista de opciones (el índice se usa como respuesta)
  - weights: Puntos asignados a cada opción (misma longitud que options)
             Más puntos = mayor nivel de madurez

Las preguntas están diseñadas para evaluar tres dimensiones:
  1. Conocimiento conceptual de IA Generativa
  2. Experiencia práctica con herramientas de IA
  3. Profundidad técnica (prompting, RAG, agentes)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class QuizQuestion:
    id: str
    text: str
    options: list[str]
    weights: list[int]  # Puntos por cada opción (0 = menos maduro, 3 = más maduro)


# ─── Banco de Preguntas ─────────────────────────────────────────────────────

QUESTIONS: list[QuizQuestion] = [
    QuizQuestion(
        id="q1",
        text="How would you describe your experience with AI tools like ChatGPT, Gemini, or Copilot?",
        options=[
            "I've heard of them but never used one",
            "I've tried them a few times out of curiosity",
            "I use them regularly for work or study",
            "I use them daily and have optimized my workflows around them",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q2",
        text="What is a 'prompt' in the context of Generative AI?",
        options=[
            "I'm not sure what that means",
            "It's the text you type to ask the AI something",
            "It's the instruction that guides the model's behavior and output format",
            "It's a structured input that can include role, context, constraints, and output specification",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q3",
        text="Which of these techniques have you used or understand?",
        options=[
            "None of these are familiar to me",
            "Zero-shot prompting (just asking directly)",
            "Few-shot prompting (giving examples in the prompt)",
            "Chain of Thought, System prompts, or Temperature tuning",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q4",
        text="What do you know about LLM 'hallucinations'?",
        options=[
            "I don't know what that refers to",
            "I know AI can sometimes make things up",
            "I understand why it happens and can identify when output is unreliable",
            "I use grounding techniques (RAG, citations, verification) to mitigate them",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q5",
        text="What is RAG (Retrieval Augmented Generation)?",
        options=[
            "I have no idea",
            "Something related to connecting AI with external data",
            "A pattern where you retrieve relevant documents and feed them to the LLM as context",
            "I've implemented or designed RAG pipelines with embeddings and vector stores",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q6",
        text="How do you handle a task that requires multiple steps when using AI?",
        options=[
            "I ask one big question and hope for the best",
            "I break it into separate prompts manually",
            "I use structured prompting (step-by-step instructions within one prompt)",
            "I design agent workflows or use frameworks like LangChain/LangGraph",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q7",
        text="What does 'fine-tuning' a model mean?",
        options=[
            "I'm not familiar with the concept",
            "It's about adjusting settings like temperature or max tokens",
            "It's training an existing model on your own dataset to specialize it",
            "I understand the difference between fine-tuning, LoRA, RLHF, and prompt engineering",
        ],
        weights=[0, 1, 2, 3],
    ),
    QuizQuestion(
        id="q8",
        text="Which best describes your understanding of AI ethics and limitations?",
        options=[
            "I haven't thought much about it",
            "I know AI can be biased and shouldn't be trusted blindly",
            "I understand data privacy concerns, bias sources, and responsible use principles",
            "I can design AI systems with guardrails, content filtering, and bias mitigation",
        ],
        weights=[0, 1, 2, 3],
    ),
]

# Puntuación máxima posible
MAX_SCORE = sum(max(q.weights) for q in QUESTIONS)
