import type { AgentMode } from '../../lib/mode-theme';
import { modeTheme } from '../../lib/mode-theme';
import { getSessionId } from '../../lib/session';

interface HeaderProps {
  currentMode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
  onToggleSidebar: () => void;
}

export function Header({ currentMode, onModeChange, onToggleSidebar }: HeaderProps) {
  const theme = modeTheme[currentMode];

  const handleResetSession = async () => {
    const sessionId = getSessionId();
    try {
      await fetch(`/api/session/${sessionId}`, { method: 'DELETE' });
      localStorage.removeItem('ceryle_session_id');
      window.location.href = '/';
    } catch (error) {
      console.error('Error resetting session:', error);
      // Fallback: al menos borra localStorage
      localStorage.removeItem('ceryle_session_id');
      window.location.href = '/';
    }
  };

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-border-default bg-surface-secondary transition-colors duration-300">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
          className="p-2 rounded-md hover:bg-surface-tertiary transition-colors lg:hidden"
        >
          <MenuIcon />
        </button>
        <h1 className={`text-lg font-bold bg-gradient-to-r ${theme.gradientText} bg-clip-text text-transparent transition-all`}>Ceryle</h1>
      </div>

      <nav aria-label="Modo del agente">
        <div className="flex items-center gap-1 p-1 rounded-lg bg-surface-primary">
          <ModeButton
            active={currentMode === 'aula'}
            onClick={() => onModeChange('aula')}
            activeClass="bg-purple-600"
          >
            Aula
          </ModeButton>
          <ModeButton
            active={currentMode === 'cocreador'}
            onClick={() => onModeChange('cocreador')}
            activeClass="bg-cyan-600"
          >
            Co-creador
          </ModeButton>
        </div>
      </nav>

      <button
        onClick={handleResetSession}
        className="p-2 rounded-md hover:bg-red-500/20 text-text-secondary hover:text-red-400 transition-colors"
        title="Reset session (testing)"
        aria-label="Reset session"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2" />
        </svg>
      </button>
    </header>
  );
}

function ModeButton({
  active,
  onClick,
  activeClass,
  children,
}: {
  active: boolean;
  onClick: () => void;
  activeClass: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
        active
          ? `${activeClass} text-white`
          : 'text-text-secondary hover:text-text-primary'
      }`}
    >
      {children}
    </button>
  );
}

function MenuIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path
        d="M3 5h14M3 10h14M3 15h14"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
