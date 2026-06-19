import type { AgentMode } from '../../lib/mode-theme';
import { modeTheme } from '../../lib/mode-theme';
import type { Conversation } from '../../lib/useConversations';
import type { LearningTopic } from '../../lib/session';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  mode?: AgentMode;
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  learningTopics?: LearningTopic[] | null;
  onTopicClick?: (topic: LearningTopic) => void;
}

export function Sidebar({ open, onClose, mode = 'aula', conversations, activeId, onSelect, onNew, learningTopics, onTopicClick }: SidebarProps) {
  const theme = modeTheme[mode];

  const sectionTitle = mode === 'aula' ? 'Conversaciones' : 'Mis Prompts';
  const newButtonLabel = mode === 'aula' ? '+ Nueva conversación' : '+ Nuevo prompt';

  return (
    <>
      {/* Backdrop for mobile */}
      {open && (
        <div
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed inset-y-0 left-0 z-30 w-64 bg-surface-secondary border-r border-border-default
          transform transition-all duration-300 ease-in-out
          lg:relative lg:translate-x-0 lg:z-0
          ${open ? 'translate-x-0' : '-translate-x-full'}
        `}
        aria-label="Navegación lateral"
      >
        <div className="flex flex-col h-full pt-4">
          <div className="px-4 pb-3 flex items-center justify-between">
            <h2 className={`text-xs font-semibold uppercase tracking-wider bg-gradient-to-r ${theme.gradientText} bg-clip-text text-transparent`}>
              {sectionTitle}
            </h2>
            {/* Close button for mobile */}
            <button
              onClick={onClose}
              className="p-1 rounded hover:bg-surface-tertiary lg:hidden"
              aria-label="Cerrar sidebar"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-text-secondary">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto px-2">
            {/* Learning Path (solo en modo aula) */}
            {mode === 'aula' && learningTopics && learningTopics.length > 0 && (
              <div className="mb-4">
                <h3 className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
                  Learning Path
                </h3>
                <ul role="list" className="space-y-0.5">
                  {learningTopics.map((topic) => (
                    <li key={topic.id}>
                      <button
                        onClick={() => onTopicClick?.(topic)}
                        className="w-full flex items-start gap-2 px-3 py-1.5 rounded-md hover:bg-surface-tertiary transition-colors text-left"
                      >
                        <span className={`mt-0.5 w-4 h-4 shrink-0 rounded-full border flex items-center justify-center text-[8px] ${
                          topic.status === 'completed'
                            ? 'bg-green-500/20 border-green-500 text-green-400'
                            : 'border-gray-600 text-gray-600'
                        }`}>
                          {topic.status === 'completed' ? '✓' : topic.id}
                        </span>
                        <span className={`text-xs leading-tight ${
                          topic.status === 'completed' ? 'text-text-secondary line-through' : 'text-text-secondary'
                        }`}>
                          {topic.title}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
                <div className="mt-2 border-b border-border-default" />
              </div>
            )}

            {/* Conversations */}
            <h3 className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
              {sectionTitle}
            </h3>
            {conversations.length === 0 ? (
              <p className="px-3 py-4 text-xs text-text-tertiary text-center">
                No hay conversaciones aún. ¡Inicia una nueva!
              </p>
            ) : (
              <ul role="list" className="space-y-1">
                {conversations.map((conv) => (
                  <ConversationItem
                    key={conv.id}
                    title={conv.title}
                    active={conv.id === activeId}
                    messageCount={conv.messages.length}
                    onClick={() => {
                      onSelect(conv.id);
                      onClose();
                    }}
                  />
                ))}
              </ul>
            )}
          </nav>

          <div className="p-4 border-t border-border-default">
            <button
              onClick={() => {
                onNew();
                onClose();
              }}
              className={`w-full px-3 py-2 text-sm font-medium rounded-md transition-colors bg-gradient-to-r ${theme.gradient} text-white hover:opacity-90`}
            >
              {newButtonLabel}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

function ConversationItem({
  title,
  active = false,
  messageCount,
  onClick,
}: {
  title: string;
  active?: boolean;
  messageCount: number;
  onClick: () => void;
}) {
  return (
    <li>
      <button
        onClick={onClick}
        className={`w-full px-3 py-2 text-sm rounded-md text-left transition-colors flex items-center justify-between gap-2 ${
          active
            ? 'bg-accent-subtle text-accent-primary font-medium'
            : 'text-text-secondary hover:text-text-primary hover:bg-surface-tertiary'
        }`}
        aria-current={active ? 'page' : undefined}
      >
        <span className="truncate">{title}</span>
        {messageCount > 0 && (
          <span className="text-[10px] text-text-tertiary shrink-0">{messageCount}</span>
        )}
      </button>
    </li>
  );
}
