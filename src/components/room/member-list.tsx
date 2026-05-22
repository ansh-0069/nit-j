import { Crown, Shield, MapPin } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { formatTime } from '@/lib/storage'
import { isTrustedCrew } from '@/lib/trusted-crew'
import type { Member, MemberStatus } from '@/types'

const STATUS_LABELS: Record<MemberStatus, string> = {
  on_my_way: 'On the way 🚶',
  here: 'Here ✅',
  running_late: 'Late ⏰',
}

export function MemberList({ members, hostName }: { members: Member[]; hostName: string }) {
  return (
    <ul className="space-y-3">
      {members.map((m) => {
        const trusted = isTrustedCrew(m.name)
        const status = (m.status ?? 'here') as MemberStatus
        return (
          <li
            key={m.name}
            className="flex items-center gap-4 rounded-xl border border-border bg-surface-2 p-4"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-joint-green/15 font-display text-lg font-semibold text-joint-green">
              {m.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <strong className="heading-md">{m.name}</strong>
                {m.name === hostName && (
                  <Badge variant="host" className="gap-1 normal-case">
                    <Crown size={10} />
                    Host
                  </Badge>
                )}
                {trusted && (
                  <Badge variant="dank" className="gap-1 normal-case">
                    <Shield size={10} />
                    Crew
                  </Badge>
                )}
                {status !== 'here' && (
                  <Badge variant="default" className="normal-case">
                    {STATUS_LABELS[status]}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-smoke">Joined {formatTime(m.joined_at)}</p>
              {m.block && (
                <p className="mt-0.5 flex items-center gap-1 text-xs text-joint-green">
                  <MapPin size={10} />
                  {m.block}
                </p>
              )}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
