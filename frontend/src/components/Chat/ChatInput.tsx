import { useRef } from 'react';
import type { AgentMode } from '../../lib/mode-theme';
import { modeTheme } from '../../lib/mode-theme';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  placeholder?: string;
  mode?: AgentMode;
}

export function ChatInput({
  value,
  onChange,
  onSend,
  disabled = false,
  placeholder = 'Escribe tu pregunta...',
  mode = 'aula',
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const theme = modeTheme[mode];

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) onSend();
    }
  }

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    onChange(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="border-t border-border-default bg-surface-secondary p-4 transition-colors duration-300">
      <div className="flex items-end gap-3 max-w-3xl mx-auto">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          rows={1}
          aria-label="Mensaje para el tutor"
          className="flex-1 resize-none bg-surface-primary border border-border-default rounded-lg px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-primary transition-colors duration-300 disabled:opacity-50"
        />
        <button
          onClick={onSend}
          disabled={disabled || !value.trim()}
          aria-label="Enviar mensaje"
          className={`p-3 rounded-lg bg-gradient-to-br ${theme.gradient} hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-300 shadow-lg ${theme.shadow}`}
        >
          <SendIcon />
        </button>
      </div>
    </div>
  );
}

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path
        d="M2.25 9h13.5M9.75 3l6 6-6 6"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
