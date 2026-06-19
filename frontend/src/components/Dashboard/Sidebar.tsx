import { User } from 'lucide-react';
import type { AgentMode } from '../../lib/mode-theme';
import { Logo } from './Logo';
import { ModeSelector } from './ModeSelector';
import { EngineBadge, type InferenceEngine } from './EngineBadge';

interface SidebarProps {
  mode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
  engine?: InferenceEngine;
  userName?: string;
  userRole?: string;
}

export function Sidebar({
  mode,
  onModeChange,
  engine = 'gemini',
  userName = 'Daniel Soto',
  userRole = 'Aprendiz',
}: SidebarProps) {
  return (
    <aside className="flex flex-col h-full w-full bg-surface-secondary border-r border-border-default">
      <div className="p-4 border-b border-border-default">
        <Logo />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <div className="space-y-2">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-text-muted px-1">
            Modo activo
          </label>
          <ModeSelector mode={mode} onChange={onModeChange} />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-text-muted px-1">
            Motor de inferencia
          </label>
          <EngineBadge engine={engine} />
        </div>
      </div>

      <div className="p-4 border-t border-border-default">
        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-surface-tertiary border border-border-default">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white text-xs font-semibold">
            <User className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-text-primary truncate">{userName}</p>
            <p className="text-[10px] text-text-muted truncate">{userRole}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
