import { GraduationCap, Terminal, User } from 'lucide-react';
import type { AgentMode } from '../../lib/mode-theme';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  modelUsed?: string;
}

interface ChatMessageBubbleProps {
  message: ChatMessage;
  mode: AgentMode;
}

export function ChatMessageBubble({ message, mode }: ChatMessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} gap-3`}
      role="article"
      aria-label={isUser ? 'Tu mensaje' : 'Respuesta del agente'}
    >
      {!isUser && <AgentAvatar mode={mode} />}

      <div className={`max-w-[85%] sm:max-w-[75%] ${isUser ? 'order-1' : 'order-2'}`}>
        <div
          className={`
            px-4 py-3 rounded-2xl
            ${isUser
              ? 'bg-blue-600 text-white rounded-br-md'
              : 'bg-surface-tertiary text-text-primary border border-border-default rounded-bl-md'
            }
          `}
        >
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>
        {!isUser && message.modelUsed && (
          <span className="block mt-1.5 text-[10px] text-text-muted pl-1">
            {message.modelUsed}
          </span>
        )}
      </div>

      {isUser && <UserAvatar />}
    </div>
  );
}

function AgentAvatar({ mode }: { mode: AgentMode }) {
  const isAula = mode === 'aula';
  return (
    <div
      className={`
        order-1 w-8 h-8 rounded-xl flex items-center justify-center shrink-0
        border
        ${isAula
          ? 'bg-blue-600/10 border-blue-600/20 text-blue-400'
          : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400'
        }
      `}
      aria-hidden="true"
    >
      {isAula ? <GraduationCap className="w-4 h-4" /> : <Terminal className="w-4 h-4" />}
    </div>
  );
}

function UserAvatar() {
  return (
    <div
      className="order-2 w-8 h-8 rounded-xl flex items-center justify-center shrink-0 bg-surface-quaternary text-text-secondary border border-border-default"
      aria-hidden="true"
    >
      <User className="w-4 h-4" />
    </div>
  );
}
