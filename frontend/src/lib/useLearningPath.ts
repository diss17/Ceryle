import { useState, useEffect, useCallback } from 'react';
import {
  fetchLearningPath,
  type LearningPathData,
  type LearningPathError,
} from './session';

interface UseLearningPathResult {
  learningPath: LearningPathData | null;
  pathError: LearningPathError | null;
  isLoading: boolean;
  retry: () => void;
}

/**
 * Hook que gestiona la carga de la ruta de aprendizaje.
 *
 * Encapsula el unwrap del FetchLearningPathResult discriminado y expone:
 *   - learningPath: datos cuando status === 'ok'
 *   - pathError:    'no-quiz' | 'service-unavailable' | 'error' | null
 *   - isLoading:    true durante la primera carga
 *   - retry:        callback para reintentar (útil tras un 503)
 */
export function useLearningPath(): UseLearningPathResult {
  const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
  const [pathError, setPathError] = useState<LearningPathError | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const applyResult = useCallback((result: Awaited<ReturnType<typeof fetchLearningPath>>) => {
    if (result.status === 'ok') {
      setLearningPath(result.data);
      setPathError(null);
    } else {
      setLearningPath(null);
      setPathError(result.status);
    }
  }, []);

  // Carga inicial: el setState ocurre tras el await (no síncrono en el effect).
  useEffect(() => {
    let cancelled = false;
    fetchLearningPath().then((result) => {
      if (!cancelled) {
        applyResult(result);
        setIsLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, [applyResult]);

  // Retry explícito (user action): puede setear isLoading síncronamente.
  const retry = useCallback(() => {
    setIsLoading(true);
    fetchLearningPath().then(applyResult).finally(() => setIsLoading(false));
  }, [applyResult]);

  return { learningPath, pathError, isLoading, retry };
}
