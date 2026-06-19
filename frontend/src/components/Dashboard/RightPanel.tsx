import type { AgentMode } from '../../lib/mode-theme';
import type { LearningPathData, LearningTopic } from '../../lib/session';
import { KnowledgeGraph } from './KnowledgeGraph';
import { BlueprintPanel } from './BlueprintPanel';

interface RightPanelProps {
  mode: AgentMode;
  learningPath: LearningPathData | null;
  onTopicClick?: (topic: LearningTopic) => void;
}

export function RightPanel({ mode, learningPath, onTopicClick }: RightPanelProps) {
  return (
    <aside className="flex flex-col h-full w-full bg-surface-secondary border-l border-border-default">
      <div className="flex-1 overflow-y-auto p-4">
        {mode === 'aula' ? (
          <KnowledgeGraph learningPath={learningPath} onTopicClick={onTopicClick} />
        ) : (
          <BlueprintPanel />
        )}
      </div>
    </aside>
  );
}
