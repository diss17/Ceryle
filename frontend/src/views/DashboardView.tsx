import { useState, useEffect } from 'react';
import { Menu, PanelRight } from 'lucide-react';
import { Sidebar } from '../components/Dashboard/Sidebar';
import { RightPanel } from '../components/Dashboard/RightPanel';
import { ChatPanel } from '../components/Dashboard/ChatPanel';
import { TopicChatView } from '../components/TopicChat/TopicChatView';
import { useConversations } from '../lib/useConversations';
import { useLearningPath } from '../lib/useLearningPath';
import type { LearningTopic } from '../lib/session';
import type { ChatMessage } from '../components/Dashboard/ChatMessageBubble';

export function DashboardView() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { learningPath, pathError, retry: retryLearningPath } = useLearningPath();
  const [activeTopic, setActiveTopic] = useState<LearningTopic | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [rightPanelOpen, setRightPanelOpen] = useState(false);

  const {
    conversations,
    active,
    activeId,
    currentMode,
    createConversation,
    selectConversation,
    addMessage,
    changeMode,
  } = useConversations('aula');

  const messages: ChatMessage[] = active?.messages ?? [];

  // Sync data-mode to <html> so theme tokens apply to fixed elements and body
  useEffect(() => {
    document.documentElement.setAttribute('data-mode', currentMode);
  }, [currentMode]);

  async function handleSend() {
    if (!input.trim() || isLoading) return;

    let targetId = activeId;
    if (!targetId) {
      targetId = createConversation();
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      content: input.trim(),
      role: 'user',
    };

    addMessage(userMessage, targetId);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          mode: currentMode,
        }),
      });

      if (!response.ok) throw new Error('Error en la respuesta');

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        content: data.response,
        role: 'assistant',
        modelUsed: data.model_used,
      };

      addMessage(assistantMessage, targetId);
    } catch {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        content: 'Hubo un error al conectar con el servidor. Intenta de nuevo.',
        role: 'assistant',
      };
      addMessage(errorMessage, targetId);
    } finally {
      setIsLoading(false);
    }
  }

  function handleModeChange(mode: 'aula' | 'cocreador') {
    setActiveTopic(null);
    changeMode(mode);
  }

  function handleTopicClick(topic: LearningTopic) {
    setActiveTopic(topic);
    setRightPanelOpen(false);
  }

  function handleTopicCompleted() {
    retryLearningPath();
    setActiveTopic(null);
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-surface-primary" data-mode={currentMode}>
      {/* Mobile header */}
      <header className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-border-default bg-surface-secondary">
        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="p-2 rounded-lg hover:bg-surface-tertiary text-text-secondary"
          aria-label="Abrir navegación"
        >
          <Menu className="w-5 h-5" />
        </button>
        <span className="text-sm font-semibold text-text-primary">Ceryle</span>
        <button
          type="button"
          onClick={() => setRightPanelOpen(true)}
          className="p-2 rounded-lg hover:bg-surface-tertiary text-text-secondary"
          aria-label="Abrir panel de contexto"
        >
          <PanelRight className="w-5 h-5" />
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Left sidebar */}
        <div
          className={`
            absolute lg:relative z-30 h-full w-64 lg:w-72 transform transition-transform duration-300 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          `}
        >
          <Sidebar mode={currentMode} onModeChange={handleModeChange} />
        </div>

        {/* Sidebar mobile backdrop */}
        {sidebarOpen && (
          <div
            className="absolute inset-0 z-20 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Central chat panel */}
        <div className="flex-1 min-w-0 relative">
          {activeTopic ? (
            <TopicChatView
              topic={activeTopic}
              onBack={() => setActiveTopic(null)}
              onTopicCompleted={handleTopicCompleted}
            />
          ) : (
            <>
              {pathError === 'service-unavailable' && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 px-4 py-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-sm text-amber-200 flex items-center gap-3 max-w-md">
                  <span className="flex-1">Microsoft Learn no está disponible. Tu ruta no pudo generarse.</span>
                  <button
                    onClick={retryLearningPath}
                    className="shrink-0 px-3 py-1 rounded-md bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 text-xs font-medium transition-colors"
                  >
                    Reintentar
                  </button>
                </div>
              )}
              <ChatPanel
                messages={messages}
                input={input}
                onInputChange={setInput}
                onSend={handleSend}
                mode={currentMode}
                isLoading={isLoading}
              />
            </>
          )}
        </div>

        {/* Right panel */}
        <div
          className={`
            absolute lg:relative right-0 z-30 h-full w-80 lg:w-80 transform transition-transform duration-300 ease-in-out
            ${rightPanelOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'}
          `}
        >
          <RightPanel
            mode={currentMode}
            learningPath={learningPath}
            onTopicClick={handleTopicClick}
          />
        </div>

        {/* Right panel mobile backdrop */}
        {rightPanelOpen && (
          <div
            className="absolute inset-0 z-20 bg-black/50 lg:hidden"
            onClick={() => setRightPanelOpen(false)}
            aria-hidden="true"
          />
        )}
      </div>

      {/* Hidden conversation selector for keyboard/accessibility */}
      <nav aria-label="Conversaciones" className="sr-only">
        <ul>
          {conversations.map((conv) => (
            <li key={conv.id}>
              <button type="button" onClick={() => selectConversation(conv.id)}>
                {conv.title}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
