import { useLocation, useNavigate } from 'react-router-dom';
import type { QuizResult } from '../lib/session';

const levelConfig = {
  beginner: {
    emoji: '🌱',
    label: 'Beginner',
    color: 'from-green-400 to-emerald-500',
    bgColor: 'bg-green-500/10 border-green-500/30',
  },
  intermediate: {
    emoji: '⚡',
    label: 'Intermediate',
    color: 'from-yellow-400 to-orange-500',
    bgColor: 'bg-yellow-500/10 border-yellow-500/30',
  },
  advanced: {
    emoji: '🚀',
    label: 'Advanced',
    color: 'from-purple-400 to-pink-500',
    bgColor: 'bg-purple-500/10 border-purple-500/30',
  },
} as const;

export function QuizResultView() {
  const navigate = useNavigate();
  const location = useLocation();
  const result = location.state as QuizResult | null;

  if (!result) {
    navigate('/quiz');
    return null;
  }

  const config = levelConfig[result.level as keyof typeof levelConfig] ?? levelConfig.beginner;
  const percentage = Math.round((result.score / result.total) * 100);

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center">
        {/* Level badge */}
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border ${config.bgColor} mb-6`}>
          <span className="text-2xl">{config.emoji}</span>
          <span className={`text-sm font-semibold bg-gradient-to-r ${config.color} bg-clip-text text-transparent`}>
            {config.label}
          </span>
        </div>

        {/* Score */}
        <h1 className="text-4xl font-bold text-white mb-2">
          {percentage}%
        </h1>
        <p className="text-sm text-gray-500 mb-6">
          {result.score} / {result.total} points
        </p>

        {/* Description */}
        <p className="text-gray-300 text-sm leading-relaxed mb-8 px-4">
          {result.description}
        </p>

        {/* CTA */}
        <button
          onClick={() => navigate('/chat')}
          className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium rounded-xl hover:from-purple-500 hover:to-indigo-500 transition-all shadow-lg shadow-purple-900/30"
        >
          Start Learning →
        </button>

        <p className="mt-4 text-xs text-gray-600">
          Ceryle will adapt content to your level
        </p>
      </div>
    </div>
  );
}
