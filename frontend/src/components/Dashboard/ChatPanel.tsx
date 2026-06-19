import type { AgentMode } from '../../lib/mode-theme';
import { ChatInputBox } from './ChatInputBox';
import { ChatMessageList } from './ChatMessageList';
import type { ChatMessage } from './ChatMessageBubble';

interface ChatPanelProps {
  messages: ChatMessage[];
  input: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  mode: AgentMode;
  isLoading?: boolean;
}

export function ChatPanel({
  messages,
  input,
  onInputChange,
  onSend,
  mode,
  isLoading = false,
}: ChatPanelProps) {
  return (
    <main className="flex flex-col h-full min-w-0 bg-surface-primary">
      <ChatMessageList messages={messages} mode={mode} isLoading={isLoading} />
      <ChatInputBox
        value={input}
        onChange={onInputChange}
        onSend={onSend}
        disabled={isLoading}
        mode={mode}
      />
    </main>
  );
}
