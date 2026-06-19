import { FileCode2, Server, CheckCircle2, Plus } from 'lucide-react';

export interface Blueprint {
  id: string;
  title: string;
  preview: string;
  createdAt: string;
}

interface BlueprintPanelProps {
  blueprints?: Blueprint[];
  mcpConnected?: boolean;
  onNewBlueprint?: () => void;
}

const sampleBlueprints: Blueprint[] = [
  {
    id: '1',
    title: 'System Prompt: Asistente Técnico',
    preview: 'Eres un ingeniero de soporte técnico senior. Responde en español...',
    createdAt: 'Hace 2 min',
  },
  {
    id: '2',
    title: 'Prompt: Análisis de Código',
    preview: 'Analiza el siguiente código Python y sugiere mejoras de rendimiento...',
    createdAt: 'Hace 1 hora',
  },
];

export function BlueprintPanel({
  blueprints,
  mcpConnected = true,
  onNewBlueprint,
}: BlueprintPanelProps) {
  const items = blueprints ?? sampleBlueprints;

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-4">
        <FileCode2 className="w-4 h-4 text-cyan-400" />
        <h2 className="text-sm font-semibold text-text-primary">Planos Generados</h2>
      </div>

      <div
        className={`
          flex items-center gap-2 p-3 rounded-xl border mb-4
          ${mcpConnected
            ? 'bg-emerald-500/5 border-emerald-500/15'
            : 'bg-surface-tertiary border-border-default'
          }
        `}
      >
        <div className={`
          w-8 h-8 rounded-lg flex items-center justify-center shrink-0
          ${mcpConnected ? 'bg-emerald-500/10' : 'bg-surface-quaternary'}
        `}>
          <Server className={`w-4 h-4 ${mcpConnected ? 'text-emerald-500' : 'text-text-muted'}`} />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-medium text-text-primary truncate">MCP de Microsoft</p>
          <p className="text-[10px] text-text-muted truncate">
            {mcpConnected ? 'Conectado en línea' : 'Desconectado'}
          </p>
        </div>
        {mcpConnected && (
          <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 ml-auto" />
        )}
      </div>

      {items.length === 0 ? (
        <EmptyState onNew={onNewBlueprint} />
      ) : (
        <div className="flex-1 overflow-y-auto -mx-1 px-1 space-y-2">
          {items.map((blueprint) => (
            <BlueprintCard key={blueprint.id} blueprint={blueprint} />
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={onNewBlueprint}
        className="mt-4 w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium rounded-lg border border-dashed border-border-hover text-text-secondary hover:text-text-primary hover:bg-surface-tertiary transition-colors"
      >
        <Plus className="w-3.5 h-3.5" />
        Nuevo plano
      </button>
    </div>
  );
}

function BlueprintCard({ blueprint }: { blueprint: Blueprint }) {
  return (
    <button
      type="button"
      className="w-full text-left p-3 rounded-xl bg-surface-secondary border border-border-default hover:border-border-hover hover:bg-surface-tertiary transition-colors group"
    >
      <p className="text-xs font-medium text-text-primary truncate group-hover:text-blue-400 transition-colors">
        {blueprint.title}
      </p>
      <p className="text-[10px] text-text-muted line-clamp-2 mt-1">
        {blueprint.preview}
      </p>
      <p className="text-[10px] text-text-tertiary mt-2">{blueprint.createdAt}</p>
    </button>
  );
}

function EmptyState({ onNew }: { onNew?: () => void }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center p-4 rounded-xl bg-surface-secondary border border-dashed border-border-default">
      <FileCode2 className="w-8 h-8 text-text-tertiary mb-2" />
      <p className="text-xs text-text-secondary mb-3">No hay planos generados aún.</p>
      <button
        type="button"
        onClick={onNew}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
      >
        <Plus className="w-3.5 h-3.5" />
        Crear primero
      </button>
    </div>
  );
}
