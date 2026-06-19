import { type AgentMode, modeTheme } from '../../lib/mode-theme';

interface MessageBubbleProps {
  content: string;
  role: 'user' | 'assistant';
  modelUsed?: string;
  mode?: AgentMode;
}

export function MessageBubble({ content, role, modelUsed, mode = 'aula' }: MessageBubbleProps) {
  const isUser = role === 'user';
  const theme = modeTheme[mode];

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      role="article"
      aria-label={isUser ? 'Tu mensaje' : 'Respuesta del tutor'}
    >
      <div
        className={`max-w-[80%] sm:max-w-[70%] px-4 py-3 rounded-2xl ${
          isUser
            ? `bg-gradient-to-br ${theme.gradient} text-white shadow-lg ${theme.shadow}`
            : 'bg-surface-tertiary text-text-primary border border-border-subtle'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap leading-relaxed">{content}</p>
        {!isUser && modelUsed && (
          <span className="block mt-2 text-xs text-text-muted">{modelUsed}</span>
        )}
      </div>
    </div>
  );
}
