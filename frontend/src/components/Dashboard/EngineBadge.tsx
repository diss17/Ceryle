import { Cloud, Cpu } from 'lucide-react';

export type InferenceEngine = 'gemini' | 'ollama';

interface EngineBadgeProps {
  engine: InferenceEngine;
  modelName?: string;
}

export function EngineBadge({ engine, modelName }: EngineBadgeProps) {
  const isCloud = engine === 'gemini';
  const label = isCloud ? 'Gemini Cloud' : modelName ? `Llama 3 Local` : 'Local';

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium
        border transition-colors
        ${isCloud
          ? 'bg-blue-600/10 border-blue-600/20 text-blue-400'
          : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
        }
      `}
      title={label}
    >
      {isCloud ? (
        <Cloud className="w-3.5 h-3.5" />
      ) : (
        <Cpu className="w-3.5 h-3.5" />
      )}
      <span>{label}</span>
      <span
        className={`w-1.5 h-1.5 rounded-full ${isCloud ? 'bg-blue-500' : 'bg-emerald-500'}`}
        aria-hidden="true"
      />
    </div>
  );
}
