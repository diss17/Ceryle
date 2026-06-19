import { useEffect } from 'react';
import type { AgentMode } from '../../lib/mode-theme';

interface AppLayoutProps {
  children: React.ReactNode;
  mode: AgentMode;
}

export function AppLayout({ children, mode }: AppLayoutProps) {
  // Sync data-mode to <html> so fixed elements and body also get themed
  useEffect(() => {
    document.documentElement.setAttribute('data-mode', mode);
  }, [mode]);

  return (
    <div className="h-screen flex flex-col overflow-hidden transition-colors duration-300" data-mode={mode}>
      {children}
    </div>
  );
}
