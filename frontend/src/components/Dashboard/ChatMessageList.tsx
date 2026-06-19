import { useEffect, useRef } from 'react';
import { BookOpen, Terminal } from 'lucide-react';
import type { AgentMode } from '../../lib/mode-theme';
import { modeTheme } from '../../lib/mode-theme';
import { ChatMessageBubble } from './ChatMessageBubble';
import type { ChatMessage } from './ChatMessageBubble';

interface ChatMessageListProps {
  messages: ChatMessage[];
  mode: AgentMode;
  isLoading?: boolean;
}

export function ChatMessageList({ messages, mode, isLoading = false }: ChatMessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length, isLoading]);

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
      <div className="max-w-3xl mx-auto space-y-5">
        {messages.map((message) => (
          <ChatMessageBubble key={message.id} message={message} mode={mode} />
        ))}
        {isLoading && <TypingIndicator mode={mode} />}
        <div ref={bottomRef} aria-hidden="true" />
      </div>
    </div>
  );
}

function EmptyState({ mode }: { mode: AgentMode }) {
  const theme = modeTheme[mode];
  const Icon = mode === 'aula' ? BookOpen : Terminal;

  return (
    <div className="flex-1 flex items-center justify-center px-4" role="status">
      <div className="text-center max-w-sm">
        <div
          className={`
            w-14 h-14 mx-auto mb-4 rounded-2xl flex items-center justify-center
            bg-gradient-to-br ${theme.gradient} shadow-lg ${theme.shadowStrong}
          `}
        >
          <Icon className="w-6 h-6 text-white" />
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

function TypingIndicator({ mode }: { mode: AgentMode }) {
  return (
    <div className="flex justify-start gap-3" aria-label="El agente está escribiendo" role="status">
      <div
        className={`
          w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border
          ${mode === 'aula'
            ? 'bg-blue-600/10 border-blue-600/20 text-blue-400'
            : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
          }
        `}
      >
        {mode === 'aula' ? <BookOpen className="w-4 h-4" /> : <Terminal className="w-4 h-4" />}
      </div>
      <div className="bg-surface-tertiary px-4 py-3 rounded-2xl rounded-bl-md border border-border-default">
        <div className="flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 rounded-full bg-text-muted animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
}
