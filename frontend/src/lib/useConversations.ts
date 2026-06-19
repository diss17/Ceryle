import { useState, useCallback } from 'react';
import type { Message } from '../components/Chat/MessageList';
import type { AgentMode } from './mode-theme';

export interface Conversation {
  id: string;
  title: string;
  mode: AgentMode;
  messages: Message[];
  createdAt: number;
}

/**
 * Hook que gestiona múltiples conversaciones.
 * Mantiene un historial por modo y permite crear/seleccionar conversaciones.
 */
export function useConversations(initialMode: AgentMode = 'aula') {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [currentMode, setCurrentMode] = useState<AgentMode>(initialMode);

  // Conversación activa actual
  const active = conversations.find((c) => c.id === activeId) ?? null;

  // Conversaciones filtradas por modo actual
  const filtered = conversations.filter((c) => c.mode === currentMode);

  // Crear nueva conversación
  const createConversation = useCallback(() => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: 'Nueva conversación',
      mode: currentMode,
      messages: [],
      createdAt: Date.now(),
    };
    setConversations((prev) => [newConv, ...prev]);
    setActiveId(newConv.id);
    return newConv.id;
  }, [currentMode]);

  // Seleccionar una conversación existente
  const selectConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  // Agregar mensaje a la conversación activa (o a un id específico)
  const addMessage = useCallback((message: Message, targetId?: string) => {
    const id = targetId ?? activeId;
    if (!id) return;
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== id) return c;
        const updated = { ...c, messages: [...c.messages, message] };
        // Actualizar título con el primer mensaje del usuario
        if (message.role === 'user' && c.messages.length === 0) {
          updated.title = message.content.slice(0, 40) + (message.content.length > 40 ? '...' : '');
        }
        return updated;
      })
    );
  }, [activeId]);

  // Cambiar de modo (puede crear nueva conversación si no hay ninguna activa en ese modo)
  const changeMode = useCallback((mode: AgentMode) => {
    setCurrentMode(mode);
    // Si hay conversaciones en el nuevo modo, seleccionar la más reciente
    const modeConvs = conversations.filter((c) => c.mode === mode);
    if (modeConvs.length > 0) {
      setActiveId(modeConvs[0].id);
    } else {
      setActiveId(null);
    }
  }, [conversations]);

  return {
    conversations: filtered,
    active,
    activeId,
    currentMode,
    createConversation,
    selectConversation,
    addMessage,
    changeMode,
  };
}
