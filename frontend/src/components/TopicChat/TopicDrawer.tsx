import { useState, useEffect, useRef } from 'react';
import { fetchTopicHistory, sendTopicMessage, markTopicCompleted, type TopicMessageData } from '../../lib/topicChat';
import type { LearningTopic } from '../../lib/session';
import { MessageBubble } from '../Chat/MessageBubble';
import { ChatInput } from '../Chat/ChatInput';
import { TopicMaterialPanel } from './TopicMaterialPanel';

interface TopicDrawerProps {
  open: boolean;
  onClose: () => void;
  topic: LearningTopic;
  onTopicCompleted?: (topicId: number) => void;
}

export function TopicDrawer({ open, onClose, topic, onTopicCompleted }: TopicDrawerProps) {
  const [messages, setMessages] = useState<TopicMessageData[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Cargar historial al abrir o cambiar de tópico
  useEffect(() => {
    if (open && topic) {
      fetchTopicHistory(topic.id).then(setMessages);
    }
  }, [open, topic]);

  // Auto-scroll al último mensaje
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  async function handleSend() {
    const text = input.trim();
    if (!text || isLoading) return;

    // Agregar mensaje del usuario inmediatamente
    const tempUserMsg: TopicMessageData = {
      id: Date.now(),
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const result = await sendTopicMessage(topic.id, text);
      const assistantMsg: TopicMessageData = {
        id: Date.now() + 1,
        role: 'assistant',
        content: result.response,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const errorMsg: TopicMessageData = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleMarkCompleted() {
    await markTopicCompleted(topic.id);
    onTopicCompleted?.(topic.id);
  }

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 bg-black/50 z-40 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 right-0 h-full w-full sm:w-[480px] bg-surface-primary border-l border-border-default z-50 flex flex-col transform transition-transform duration-300 ease-in-out ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
        role="dialog"
        aria-label={`Chat: ${topic?.title}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border-default bg-surface-secondary">
          <div className="flex-1 min-w-0">
            <h2 className="text-sm font-semibold text-text-primary truncate">
              {topic?.title}
            </h2>
            <p className="text-xs text-text-tertiary truncate">
              {topic?.description}
            </p>
          </div>
          <div className="flex items-center gap-2 ml-2">
            {topic?.status !== 'completed' && (
              <button
                onClick={handleMarkCompleted}
                className="text-xs px-2 py-1 rounded bg-green-600/20 text-green-400 hover:bg-green-600/30 transition-colors"
                title="Mark topic as completed"
              >
                ✓ Complete
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-surface-tertiary text-text-secondary transition-colors"
              aria-label="Close topic chat"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Material del tópico (markdown de MS Learn + link a fuente) */}
        <TopicMaterialPanel topic={topic} />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="text-3xl mb-3">📚</div>
              <p className="text-sm text-text-secondary">
                Ask anything about <strong>{topic?.title}</strong>
              </p>
              <p className="text-xs text-text-tertiary mt-1">
                This chat is specialized in this topic only.
              </p>
            </div>
          )}

          <div className="space-y-3">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                content={msg.content}
                role={msg.role}
                mode="aula"
              />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-surface-tertiary border border-border-subtle px-4 py-3 rounded-2xl">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce" />
                    <span className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce [animation-delay:150ms]" />
                    <span className="w-2 h-2 bg-text-tertiary rounded-full animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
          </div>
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-border-default p-3">
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={handleSend}
            disabled={isLoading}
            placeholder={`Ask about ${topic?.title}...`}
          />
        </div>
      </div>
    </>
  );
}
