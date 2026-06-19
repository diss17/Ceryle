import { useRef } from 'react';
import { Send } from 'lucide-react';
import type { AgentMode } from '../../lib/mode-theme';
import { modeTheme } from '../../lib/mode-theme';

interface ChatInputBoxProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  mode?: AgentMode;
}

export function ChatInputBox({
  value,
  onChange,
  onSend,
  disabled = false,
  mode = 'aula',
}: ChatInputBoxProps) {
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
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="border-t border-border-default bg-surface-secondary p-4">
      <div className="flex items-end gap-3 max-w-3xl mx-auto">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={theme.inputPlaceholder}
          rows={1}
          aria-label="Mensaje para el agente"
          className="
            flex-1 resize-none bg-surface-primary border border-border-default rounded-xl
            px-4 py-3 text-sm text-text-primary placeholder:text-text-muted
            focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary
            transition-colors duration-200 disabled:opacity-50
          "
        />
        <button
          type="button"
          onClick={onSend}
          disabled={disabled || !value.trim()}
          aria-label="Enviar mensaje"
          className={`
            p-3 rounded-xl bg-gradient-to-br ${theme.gradient} text-white
            hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200 shadow-lg ${theme.shadow}
          `}
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
      <p className="max-w-3xl mx-auto mt-2 text-[10px] text-center text-text-muted">
        Presiona Enter para enviar. Shift + Enter para nueva línea.
      </p>
    </div>
  );
}
