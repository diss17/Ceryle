import { CheckCircle2, Circle, TrendingUp, AlertCircle, Brain } from 'lucide-react';
import type { LearningPathData, LearningTopic } from '../../lib/session';

interface KnowledgeGraphProps {
  learningPath: LearningPathData | null;
  onTopicClick?: (topic: LearningTopic) => void;
}

export function KnowledgeGraph({ learningPath, onTopicClick }: KnowledgeGraphProps) {
  const topics = learningPath?.topics ?? [];
  const completedCount = topics.filter((t) => t.status === 'completed').length;
  const total = topics.length || 1;
  const progress = Math.round((completedCount / total) * 100);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-4 h-4 text-blue-400" />
        <h2 className="text-sm font-semibold text-text-primary">Grafo de Conocimiento</h2>
      </div>

      <div className="p-3 rounded-xl bg-surface-tertiary border border-border-default mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-text-secondary">Progreso general</span>
          <span className="text-xs font-medium text-emerald-400">{progress}%</span>
        </div>
        <div className="h-1.5 w-full bg-surface-quaternary rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
            aria-hidden="true"
          />
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-xs text-text-muted">
          <TrendingUp className="w-3 h-3" />
          <span>
            {completedCount} de {topics.length || 0} tópicos dominados
          </span>
        </div>
      </div>

      {topics.length === 0 ? (
        <EmptyState message="Completa el quiz para generar tu ruta de aprendizaje." />
      ) : (
        <div className="flex-1 overflow-y-auto -mx-1 px-1 space-y-2">
          <h3 className="text-[10px] font-semibold uppercase tracking-wider text-text-muted px-1">
            Tópicos
          </h3>
          {topics.map((topic) => (
            <TopicNode
              key={topic.id}
              topic={topic}
              onClick={() => onTopicClick?.(topic)}
            />
          ))}
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-border-default">
        <div className="flex items-start gap-2 text-xs text-text-secondary">
          <AlertCircle className="w-3.5 h-3.5 text-text-muted shrink-0 mt-0.5" />
          <p>Los tópicos en gris son áreas por reforzar. Los verdes son dominados.</p>
        </div>
      </div>
    </div>
  );
}

function TopicNode({ topic, onClick }: { topic: LearningTopic; onClick?: () => void }) {
  const isCompleted = topic.status === 'completed';
  const unitCount = topic.units?.length ?? 0;
  const duration = topic.duration_minutes ?? 0;
  const hasIcon = Boolean(topic.icon_url);

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full text-left p-3 rounded-xl bg-surface-secondary border border-border-default hover:border-border-hover hover:bg-surface-tertiary transition-colors group relative"
    >
      <div className="flex items-start gap-2.5">
        {hasIcon ? (
          <div className="shrink-0 w-7 h-7 rounded-md bg-surface-quaternary flex items-center justify-center overflow-hidden">
            <img
              src={topic.icon_url}
              alt=""
              className="w-full h-full object-contain"
              loading="lazy"
            />
          </div>
        ) : (
          <Circle className="w-4 h-4 text-text-muted shrink-0 mt-0.5 group-hover:text-text-secondary" />
        )}
        <div className="min-w-0 flex-1">
          <p className={`text-xs font-medium truncate ${isCompleted ? 'text-text-secondary line-through' : 'text-text-primary'}`}>
            {topic.title}
          </p>
          <p className="text-[10px] text-text-muted line-clamp-2 mt-0.5">
            {topic.description}
          </p>
          {(unitCount > 0 || duration) && (
            <div className="flex items-center gap-2 mt-1.5">
              {unitCount > 0 && (
                <span className="text-[9px] font-medium px-1.5 py-0.5 rounded bg-surface-quaternary text-text-secondary">
                  {unitCount} {unitCount === 1 ? 'unit' : 'units'}
                </span>
              )}
              {duration > 0 && (
                <span className="text-[9px] text-text-muted">
                  {duration} min
                </span>
              )}
            </div>
          )}
        </div>
      </div>
      {hasIcon && isCompleted && (
        <span className="absolute top-1.5 right-1.5 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-surface-secondary flex items-center justify-center">
          <CheckCircle2 className="w-2.5 h-2.5 text-white" />
        </span>
      )}
    </button>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center p-4 rounded-xl bg-surface-secondary border border-dashed border-border-default">
      <Brain className="w-8 h-8 text-text-tertiary mb-2" />
      <p className="text-xs text-text-secondary">{message}</p>
    </div>
  );
}
