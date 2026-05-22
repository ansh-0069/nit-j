import { cn } from '@/lib/cn'
import type { Member } from '@/types'

export function MemberStack({ members, hostName }: { members: Member[]; hostName: string }) {
  const visible = members.slice(0, 5)
  const extra = members.length - visible.length

  return (
    <div className="flex flex-col items-start gap-2 md:items-end">
      <div className="flex -space-x-2">
        {visible.map((m) => (
          <div
            key={m.name}
            title={m.name}
            className={cn(
              'flex h-10 w-10 items-center justify-center rounded-full border-2 border-surface font-bold text-sm',
              m.name === hostName
                ? 'bg-joint-green/20 text-joint-green'
                : 'bg-surface-3 text-white',
            )}
          >
            {m.name.charAt(0).toUpperCase()}
          </div>
        ))}
        {extra > 0 && (
          <div className="flex h-10 w-10 items-center justify-center rounded-full border-2 border-surface bg-surface-2 text-xs font-bold text-smoke">
            +{extra}
          </div>
        )}
      </div>
      <p className="text-xs text-smoke">{members.length} in the joint</p>
    </div>
  )
}
