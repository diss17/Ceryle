import { BookOpen, Terminal } from 'lucide-react';
import type { AgentMode } from '../../lib/mode-theme';

interface ModeSelectorProps {
  mode: AgentMode;
  onChange: (mode: AgentMode) => void;
}

export function ModeSelector({ mode, onChange }: ModeSelectorProps) {
  return (
    <nav aria-label="Modo del agente" className="w-full">
      <div className="grid grid-cols-2 gap-1 p-1 rounded-xl bg-surface-tertiary border border-border-default">
        <ModeButton
          active={mode === 'aula'}
          onClick={() => onChange('aula')}
          icon={<BookOpen className="w-4 h-4" />}
          label="Aula"
        />
        <ModeButton
          active={mode === 'cocreador'}
          onClick={() => onChange('cocreador')}
          icon={<Terminal className="w-4 h-4" />}
          label="Construir"
        />
      </div>
    </nav>
  );
}

interface ModeButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

function ModeButton({ active, onClick, icon, label }: ModeButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`
        flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium rounded-lg
        transition-all duration-200
        ${active
          ? 'bg-blue-600 text-white shadow-md shadow-blue-900/20'
          : 'text-text-secondary hover:text-text-primary hover:bg-surface-quaternary'
        }
      `}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}
