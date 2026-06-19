interface LogoProps {
  compact?: boolean;
}

export function Logo({ compact = false }: LogoProps) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 shadow-lg shadow-blue-900/20">
        <KingfisherIcon className="w-5 h-5 text-white" />
      </div>
      {!compact && (
        <span className="text-base font-semibold tracking-tight text-text-primary">
          Ceryle
        </span>
      )}
    </div>
  );
}

function KingfisherIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={className}
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {/* Stylized kingfisher / swift silhouette */}
      <path d="M4 14c4-1 7-4 9-7 1 3 4 5 7 5-3 2-6 1-8-1-1 3-4 5-8 3z" />
      <path d="M13 7c0-1.5 1-3 3-3s2.5 2 1 3" />
      <circle cx="16" cy="5.5" r="0.8" fill="currentColor" stroke="none" />
    </svg>
  );
}
