import { Car, Check, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { MemberStatus } from '@/types'

const STATUSES: { value: MemberStatus; label: string; icon: typeof Car }[] = [
  { value: 'on_my_way', label: 'On my way', icon: Car },
  { value: 'here', label: 'Here', icon: Check },
  { value: 'running_late', label: 'Running late', icon: Clock },
]

export function PullUpStatus({
  currentStatus,
  loading,
  onUpdate,
}: {
  currentStatus?: MemberStatus
  loading?: boolean
  onUpdate: (status: MemberStatus) => void
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {STATUSES.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          variant={currentStatus === value ? 'default' : 'secondary'}
          size="sm"
          disabled={loading}
          onClick={() => onUpdate(value)}
        >
          <Icon size={14} />
          {label}
        </Button>
      ))}
    </div>
  )
}
