"""
Ceryle - Lógica de Scoring del Quiz.

Calcula el nivel de madurez de IA basado en las respuestas del usuario.

Umbrales:
  - 0-33%  del max score → "beginner"
  - 34-66% del max score → "intermediate"
  - 67-100% del max score → "advanced"
"""

from app.quiz.questions import QUESTIONS, MAX_SCORE


# ─── Descripciones por nivel ────────────────────────────────────────────────

LEVEL_DESCRIPTIONS = {
    "beginner": (
        "You're just starting your AI journey. You have basic awareness of AI tools "
        "but haven't explored them in depth yet. Ceryle will guide you from the fundamentals."
    ),
    "intermediate": (
        "You have practical experience with AI tools and understand core concepts. "
        "Ceryle will help you deepen your knowledge in prompt engineering, RAG, and agents."
    ),
    "advanced": (
        "You have strong technical knowledge of Generative AI. "
        "Ceryle will focus on advanced topics like agent orchestration, "
        "system design, and cutting-edge techniques."
    ),
}


def calculate_score(answers: dict[str, int]) -> tuple[int, int]:
    """
    Calcula la puntuación total basada en las respuestas.

    Args:
        answers: Dict {question_id: selected_option_index}

    Returns:
        Tupla (score_obtenido, score_maximo)
    """
    score = 0
    questions_map = {q.id: q for q in QUESTIONS}

    for question_id, option_index in answers.items():
        question = questions_map.get(question_id)
        if question and 0 <= option_index < len(question.weights):
            score += question.weights[option_index]

    return score, MAX_SCORE


def determine_level(score: int, total: int) -> str:
    """
    Determina el nivel de madurez según el porcentaje del score.

    Args:
        score: Puntuación obtenida
        total: Puntuación máxima posible

    Returns:
        "beginner", "intermediate", o "advanced"
    """
    if total == 0:
        return "beginner"

    percentage = (score / total) * 100

    if percentage <= 33:
        return "beginner"
    elif percentage <= 66:
        return "intermediate"
    else:
        return "advanced"
