/**
 * Ceryle - Gestión de sesión anónima.
 *
 * Genera o recupera un UUID almacenado en localStorage.
 * Este ID identifica al usuario de forma anónima (sin autenticación).
 * Se usa para asociar resultados del quiz y conversaciones.
 */

const SESSION_KEY = 'ceryle_session_id';

/**
 * Obtiene el session_id existente o genera uno nuevo.
 */
export function getSessionId(): string {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

/**
 * Verifica si el usuario ya completó el quiz consultando el backend.
 * Retorna el resultado si existe, o null si no.
 */
export async function checkQuizCompleted(): Promise<QuizResult | null> {
  const sessionId = getSessionId();
  try {
    const response = await fetch(`/api/quiz/result/${sessionId}`);
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch {
    return null;
  }
}

export interface QuizResult {
  session_id: string;
  level: string;
  score: number;
  total: number;
  description: string;
}

export interface CodeSample {
  language: string;
  code: string;
  description: string;
  url: string;
}

export interface LearnUnit {
  uid: string;
  title: string;
  url: string;
  duration_minutes: number;
  content?: string;
}

export interface LearningTopic {
  id: number;
  title: string;
  description: string;
  status: string;
  url?: string;
  content?: string;
  code_samples?: CodeSample[];
  module_uid?: string;
  duration_minutes?: number;
  units?: LearnUnit[];
  icon_url?: string;
  social_image_url?: string;
}

export interface LearningPathData {
  session_id: string;
  level: string;
  topics: LearningTopic[];
}

/**
 * Resultado discriminado de fetchLearningPath.
 * Permite al caller distinguir:
 *   - 'ok'                 → ruta disponible
 *   - 'no-quiz'            → 404: el usuario no completó el quiz todavía
 *   - 'service-unavailable'→ 503: Microsoft Learn caído, se puede reintentar
 *   - 'error'              → otro error inesperado
 */
export type LearningPathError = 'no-quiz' | 'service-unavailable' | 'error';

export type FetchLearningPathResult =
  | { status: 'ok'; data: LearningPathData }
  | { status: 'no-quiz' }
  | { status: 'service-unavailable' }
  | { status: 'error' };

/**
 * Obtiene la ruta de aprendizaje del usuario.
 * Si no existe, el backend la genera con el LLM.
 *
 * Retorna un resultado discriminado para que el caller pueda diferenciar
 * un 503 (Microsoft Learn caído, reintentable) de un 404 (falta quiz)
 * u otros errores.
 */
export async function fetchLearningPath(): Promise<FetchLearningPathResult> {
  const sessionId = getSessionId();
  try {
    const response = await fetch(`/api/learning-path/${sessionId}`);
    if (response.ok) {
      return { status: 'ok', data: await response.json() };
    }
    if (response.status === 404) {
      return { status: 'no-quiz' };
    }
    if (response.status === 503) {
      return { status: 'service-unavailable' };
    }
    return { status: 'error' };
  } catch {
    return { status: 'error' };
  }
}
