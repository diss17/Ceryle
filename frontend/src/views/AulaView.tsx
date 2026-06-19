import { useState } from 'react';
import { Header } from '../components/Layout/Header';
import { Sidebar } from '../components/Layout/Sidebar';
import { AppLayout } from '../components/Layout/AppLayout';
import { MessageList, type Message } from '../components/Chat/MessageList';
import { ChatInput } from '../components/Chat/ChatInput';
import { TopicChatView } from '../components/TopicChat/TopicChatView';
import { useConversations } from '../lib/useConversations';
import { useLearningPath } from '../lib/useLearningPath';
import type { LearningTopic } from '../lib/session';

export function AulaView() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { learningPath, pathError, retry: retryLearningPath } = useLearningPath();
  const [activeTopic, setActiveTopic] = useState<LearningTopic | null>(null);

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

  // Mensajes de la conversación activa (o vacío si no hay ninguna)
  const messages = active?.messages ?? [];

  async function handleSend() {
    if (!input.trim() || isLoading) return;

    // Si no hay conversación activa, crear una nueva
    let targetId = activeId;
    if (!targetId) {
      targetId = createConversation();
    }

    const userMessage: Message = {
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

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: data.response,
        role: 'assistant',
        modelUsed: data.model_used,
      };

      addMessage(assistantMessage, targetId);
    } catch {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        content: 'Hubo un error al conectar con el servidor. Intenta de nuevo.',
        role: 'assistant',
      };
      addMessage(errorMessage, targetId);
    } finally {
      setIsLoading(false);
    }
  }

  function handleNewConversation() {
    createConversation();
  }

  return (
    <AppLayout mode={currentMode}>
      <Header
        currentMode={currentMode}
        onModeChange={(mode) => { setActiveTopic(null); changeMode(mode); }}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          mode={currentMode}
          conversations={conversations}
          activeId={activeId}
          onSelect={selectConversation}
          onNew={handleNewConversation}
          learningTopics={learningPath?.topics}
          onTopicClick={(topic) => setActiveTopic(topic)}
        />

        {activeTopic ? (
          <TopicChatView
            topic={activeTopic}
            onBack={() => setActiveTopic(null)}
            onTopicCompleted={() => {
              retryLearningPath();
              setActiveTopic(null);
            }}
          />
        ) : (
          <main className="flex-1 flex flex-col min-w-0">
            {pathError === 'service-unavailable' && (
              <div className="mx-4 mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-sm text-amber-200 flex items-center justify-between gap-3">
                <span>Microsoft Learn no está disponible. Tu ruta no pudo generarse.</span>
                <button
                  onClick={retryLearningPath}
                  className="shrink-0 px-3 py-1 rounded-md bg-amber-500/20 hover:bg-amber-500/30 text-amber-100 text-xs font-medium transition-colors"
                >
                  Reintentar
                </button>
              </div>
            )}
            <MessageList messages={messages} isLoading={isLoading} mode={currentMode} />
            <ChatInput
              value={input}
              onChange={setInput}
              onSend={handleSend}
              disabled={isLoading}
              mode={currentMode}
              placeholder={
                currentMode === 'aula'
                  ? 'Pregunta sobre IA Generativa...'
                  : 'Describe el prompt que quieres crear...'
              }
            />
          </main>
        )}
      </div>
    </AppLayout>
  );
}
