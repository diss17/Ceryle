import { useState, useEffect, useRef } from 'react';
import { fetchTopicHistory, sendTopicMessage, markTopicCompleted, type TopicMessageData } from '../../lib/topicChat';
import type { LearningTopic } from '../../lib/session';
import { MessageBubble } from '../Chat/MessageBubble';
import { ChatInput } from '../Chat/ChatInput';
import { TopicMaterialPanel } from './TopicMaterialPanel';

interface TopicChatViewProps {
  topic: LearningTopic;
  onBack: () => void;
  onTopicCompleted?: (topicId: number) => void;
}

export function TopicChatView({ topic, onBack, onTopicCompleted }: TopicChatViewProps) {
  const [messages, setMessages] = useState<TopicMessageData[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Cargar historial al montar o cambiar de tópico
  useEffect(() => {
    fetchTopicHistory(topic.id).then(setMessages);
  }, [topic.id]);

  // Auto-scroll al último mensaje
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages.length]);

  async function handleSend() {
    const text = input.trim();
    if (!text || isLoading) return;

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
    <main className="flex-1 flex flex-col min-w-0">
      {/* Topic header bar */}
      <div className="flex items-center gap-3 px-4 py-2.5 border-b border-border-default bg-surface-secondary">
        <button
          onClick={onBack}
          className="p-1.5 rounded-lg hover:bg-surface-tertiary text-text-secondary transition-colors"
          aria-label="Back to general chat"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-semibold text-text-primary truncate">
            {topic.title}
          </h2>
          <p className="text-xs text-text-tertiary truncate">{topic.description}</p>
        </div>
        {topic.status !== 'completed' && (
          <button
            onClick={handleMarkCompleted}
            className="text-xs px-2.5 py-1 rounded-md bg-green-600/20 text-green-400 hover:bg-green-600/30 transition-colors whitespace-nowrap"
          >
            ✓ Complete
          </button>
        )}
        {topic.status === 'completed' && (
          <span className="text-xs px-2.5 py-1 rounded-md bg-green-600/10 text-green-500">
            ✓ Completed
          </span>
        )}
      </div>

      {/* Material del tópico (markdown de MS Learn + link a fuente) */}
      <TopicMaterialPanel topic={topic} />

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6" role="log" aria-label="Topic conversation">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="text-4xl mb-3">📚</div>
            <p className="text-sm text-text-secondary">
              Ask anything about <strong>{topic.title}</strong>
            </p>
            <p className="text-xs text-text-tertiary mt-1">
              This chat is specialized in this topic only. Questions outside scope will be redirected to resources.
            </p>
          </div>
        )}

        <div className="max-w-3xl mx-auto space-y-4">
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
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        disabled={isLoading}
        mode="aula"
        placeholder={`Ask about ${topic.title}...`}
      />
    </main>
  );
}
