import { getSessionId } from './session';

export interface TopicMessageData {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface TopicChatResponse {
  response: string;
  model_used: string;
  resources: { title: string; url: string; description: string }[] | null;
}

/**
 * Obtiene el historial de mensajes de un tópico específico.
 */
export async function fetchTopicHistory(topicId: number): Promise<TopicMessageData[]> {
  const sessionId = getSessionId();
  try {
    const res = await fetch(`/api/topic-chat/${sessionId}/${topicId}`);
    if (res.ok) return await res.json();
    return [];
  } catch {
    return [];
  }
}

/**
 * Envía un mensaje al chat de un tópico específico.
 */
export async function sendTopicMessage(topicId: number, message: string): Promise<TopicChatResponse> {
  const sessionId = getSessionId();
  const res = await fetch(`/api/topic-chat/${sessionId}/${topicId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error(`Topic chat failed: ${res.status}`);
  }

  return await res.json();
}

/**
 * Marca un tópico como completado.
 */
export async function markTopicCompleted(topicId: number): Promise<void> {
  const sessionId = getSessionId();
  await fetch(`/api/learning-path/${sessionId}/topic/${topicId}`, {
    method: 'PATCH',
  });
}
