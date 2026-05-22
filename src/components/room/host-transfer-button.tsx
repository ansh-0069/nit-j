import { useState } from 'react'
import { Crown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { Member } from '@/types'

export function HostTransferButton({
  members,
  hostName,
  loading,
  onTransfer,
}: {
  members: Member[]
  hostName: string
  currentUser?: string
  loading?: boolean
  onTransfer: (newHostName: string) => void
}) {
  const [open, setOpen] = useState(false)
  const candidates = members.filter((m) => m.name !== hostName)

  if (candidates.length === 0) return null

  if (!open) {
    return (
      <Button variant="secondary" size="sm" onClick={() => setOpen(true)}>
        <Crown size={14} />
        Pass host
      </Button>
    )
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-border bg-surface-2 p-3">
      <p className="text-sm text-smoke">Pass host to:</p>
      {candidates.map((m) => (
        <Button
          key={m.name}
          variant="outline"
          size="sm"
          disabled={loading}
          onClick={() => {
            onTransfer(m.name)
            setOpen(false)
          }}
        >
          {m.name}
        </Button>
      ))}
      <Button variant="ghost" size="sm" onClick={() => setOpen(false)} disabled={loading}>
        Cancel
      </Button>
    </div>
  )
}
