import { useState } from 'react';
import { ChevronDown, ExternalLink, BookOpen, Clock, FileText } from 'lucide-react';
import type { LearningTopic, LearnUnit } from '../../lib/session';
import { MarkdownRenderer } from '../Chat/MarkdownRenderer';

interface TopicMaterialPanelProps {
  topic: LearningTopic;
}

function getDomain(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return '';
  }
}

export function TopicMaterialPanel({ topic }: TopicMaterialPanelProps) {
  const [expanded, setExpanded] = useState(true);
  const [openUnit, setOpenUnit] = useState<number | null>(null);

  const units = topic.units ?? [];
  const hasUnits = units.length > 0;
  const hasModuleContent = Boolean(topic.content && topic.content.trim().length > 0);
  const domain = topic.url ? getDomain(topic.url) : '';

  // Default: open the first unit with content when units are first shown
  const firstContentIdx = hasUnits
    ? units.findIndex((u) => u.content && u.content.trim().length > 0)
    : -1;
  const effectiveOpen = openUnit ?? (firstContentIdx >= 0 ? firstContentIdx : null);

  function toggleUnit(idx: number) {
    setOpenUnit((cur) => (cur === idx ? null : idx));
  }

  return (
    <section
      className="border-b border-border-default bg-surface-secondary"
      aria-label="Material del tópico"
    >
      {/* Header (siempre visible) */}
      <div className="flex items-center gap-2 px-4 py-2.5">
        {topic.icon_url && (
          <img
            src={topic.icon_url}
            alt=""
            className="w-6 h-6 shrink-0 object-contain"
            loading="lazy"
          />
        )}
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="flex items-center gap-2 flex-1 min-w-0 text-left rounded-md hover:bg-surface-tertiary transition-colors px-1.5 py-1 -mx-1.5 -my-1"
          aria-expanded={expanded}
          aria-controls="topic-material-body"
        >
          <BookOpen className="w-4 h-4 text-accent-primary shrink-0" />
          <span className="text-xs font-semibold uppercase tracking-wider text-text-secondary truncate">
            Material del tópico
          </span>
          {domain && (
            <span className="text-[10px] text-text-muted truncate hidden sm:inline">
              · {domain}
            </span>
          )}
          {hasUnits && (
            <span className="text-[10px] text-text-muted shrink-0">
              · {units.length} {units.length === 1 ? 'unidad' : 'unidades'}
            </span>
          )}
          <ChevronDown
            className={`w-4 h-4 text-text-muted ml-auto shrink-0 transition-transform ${
              expanded ? 'rotate-180' : ''
            }`}
          />
        </button>

        {topic.url && (
          <a
            href={topic.url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 flex items-center gap-1 text-xs px-2 py-1 rounded-md bg-surface-tertiary text-text-secondary hover:text-accent-primary hover:bg-accent-subtle/30 transition-colors"
            title="Abrir fuente oficial en Microsoft Learn"
          >
            Fuente oficial
            <ExternalLink className="w-3 h-3" />
          </a>
        )}
      </div>

      {/* Cuerpo colapsable */}
      {expanded && (
        <div
          id="topic-material-body"
          className="px-4 pb-4 pt-1 max-h-[45vh] overflow-y-auto border-t border-border-subtle"
        >
          {hasUnits ? (
            <UnitAccordion
              units={units}
              openIdx={effectiveOpen}
              onToggle={toggleUnit}
            />
          ) : hasModuleContent ? (
            <MarkdownRenderer content={topic.content ?? ''} />
          ) : (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <div className="text-2xl mb-2 text-text-muted">📄</div>
              <p className="text-sm text-text-secondary">
                No hay material disponible para este tópico.
              </p>
              {topic.url && (
                <a
                  href={topic.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-flex items-center gap-1 text-xs text-accent-primary hover:text-accent-hover"
                >
                  Abrir fuente oficial
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function UnitAccordion({
  units,
  openIdx,
  onToggle,
}: {
  units: LearnUnit[];
  openIdx: number | null;
  onToggle: (idx: number) => void;
}) {
  return (
    <div className="space-y-1">
      {units.map((unit, idx) => {
        const isOpen = openIdx === idx;
        const hasContent = Boolean(unit.content && unit.content.trim().length > 0);
        return (
          <div
            key={unit.uid ?? idx}
            className="rounded-lg border border-border-subtle bg-surface-tertiary/40 overflow-hidden"
          >
            <button
              type="button"
              onClick={() => hasContent && onToggle(idx)}
              className={`w-full flex items-center gap-2 px-3 py-2 text-left transition-colors ${
                hasContent ? 'hover:bg-surface-tertiary cursor-pointer' : 'cursor-default opacity-70'
              }`}
              aria-expanded={isOpen}
              disabled={!hasContent}
            >
              <FileText className={`w-3.5 h-3.5 shrink-0 ${hasContent ? 'text-accent-primary' : 'text-text-muted'}`} />
              <span className="text-xs font-medium text-text-primary truncate flex-1">
                {unit.title}
              </span>
              {unit.duration_minutes > 0 && (
                <span className="flex items-center gap-0.5 text-[10px] text-text-muted shrink-0">
                  <Clock className="w-3 h-3" />
                  {unit.duration_minutes}m
                </span>
              )}
              {hasContent && (
                <ChevronDown
                  className={`w-3.5 h-3.5 text-text-muted shrink-0 transition-transform ${
                    isOpen ? 'rotate-180' : ''
                  }`}
                />
              )}
            </button>
            {isOpen && hasContent && (
              <div className="px-3 pb-3 pt-1 border-t border-border-subtle">
                <MarkdownRenderer content={unit.content ?? ''} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
