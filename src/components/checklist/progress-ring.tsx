export function ProgressRing({ claimed, total }: { claimed: number; total: number }) {
  const pct = total > 0 ? (claimed / total) * 100 : 0
  const radius = 28
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (pct / 100) * circumference

  return (
    <div className="relative flex h-16 w-16 items-center justify-center">
      <svg className="-rotate-90" width="64" height="64">
        <circle cx="32" cy="32" r={radius} fill="none" stroke="currentColor" strokeWidth="5" className="text-surface-3" />
        <circle
          cx="32"
          cy="32"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="5"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="text-joint-green transition-all duration-500"
        />
      </svg>
      <span className="absolute text-xs font-bold">
        {claimed}/{total}
      </span>
    </div>
  )
}
