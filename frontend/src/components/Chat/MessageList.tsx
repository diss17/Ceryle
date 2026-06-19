import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { type AgentMode, modeTheme } from '../../lib/mode-theme';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  modelUsed?: string;
}

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  mode?: AgentMode;
}

export function MessageList({ messages, isLoading, mode = 'aula' }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  if (messages.length === 0) {
    return <EmptyState mode={mode} />;
  }

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-6"
      role="log"
      aria-label="Historial de conversación"
      aria-live="polite"
    >
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            content={msg.content}
            role={msg.role}
            modelUsed={msg.modelUsed}
            mode={mode}
          />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} aria-hidden="true" />
      </div>
    </div>
  );
}

function EmptyState({ mode }: { mode: AgentMode }) {
  const theme = modeTheme[mode];

  return (
    <div className="flex-1 flex items-center justify-center px-4" role="status">
      <div className="text-center max-w-sm">
        <div className={`w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${theme.gradient} flex items-center justify-center shadow-lg ${theme.shadowStrong}`}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d={mode === 'aula'
                ? 'M12 6v6l4 2M12 2a10 10 0 100 20 10 10 0 000-20z'
                : 'M12 3l1.5 4.5H18l-3.5 2.5 1.5 4.5L12 12l-4 2.5 1.5-4.5L6 7.5h4.5z'
              }
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <h2 className={`text-base font-semibold bg-gradient-to-r ${theme.gradientText} bg-clip-text text-transparent mb-1`}>
          {theme.welcomeTitle}
        </h2>
        <p className="text-sm text-text-secondary">
          {theme.welcomeDescription}
        </p>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-label="El tutor está escribiendo" role="status">
      <div className="bg-surface-tertiary px-4 py-3 rounded-xl">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}
