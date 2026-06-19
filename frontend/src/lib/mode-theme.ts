export type AgentMode = 'aula' | 'cocreador';

/**
 * Modos de la aplicación:
 * - Aula: tutor educativo de IA Generativa.
 * - Construir (cocreador): diseño asistido de prompts.
 */
export const modeLabels: Record<AgentMode, { short: string; full: string }> = {
  aula: { short: 'Aula', full: 'Modo Aula' },
  cocreador: { short: 'Construir', full: 'Modo Construir' },
};

/**
 * Clases de acento por modo para el tema oscuro minimalista.
 * Aula: azul eléctrico (blue-600)
 * Construir: cian eléctrico (cyan-500)
 */
export const modeTheme = {
  aula: {
    gradient: 'from-blue-600 to-blue-700',
    gradientText: 'from-blue-400 to-blue-300',
    gradientHover: 'from-blue-500 to-blue-600',
    shadow: 'shadow-blue-900/20',
    shadowStrong: 'shadow-blue-900/30',
    activeButton: 'bg-blue-600',
    icon: 'graduation-cap',
    label: modeLabels.aula.full,
    welcomeTitle: 'Bienvenido al Modo Aula',
    welcomeDescription: 'Pregúntame sobre embeddings, transformers, RAG, agentes y más.',
    inputPlaceholder: 'Pregúntame sobre embeddings, transformers...',
  },
  cocreador: {
    gradient: 'from-cyan-500 to-blue-600',
    gradientText: 'from-cyan-300 to-blue-300',
    gradientHover: 'from-cyan-400 to-blue-500',
    shadow: 'shadow-cyan-900/20',
    shadowStrong: 'shadow-cyan-900/30',
    activeButton: 'bg-cyan-600',
    icon: 'terminal',
    label: modeLabels.cocreador.full,
    welcomeTitle: 'Bienvenido al Modo Construir',
    welcomeDescription: 'Describe el problema para diseñar tu prompt del sistema.',
    inputPlaceholder: 'Describe el problema para diseñar tu prompt del sistema...',
  },
} as const;

export function isAgentMode(value: string): value is AgentMode {
  return value === 'aula' || value === 'cocreador';
}
