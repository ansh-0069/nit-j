import { useState } from 'react'
import { Archive, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function DeleteSeshButton({
  onEnd,
  loading,
}: {
  onEnd: (permanent: boolean) => void
  loading?: boolean
}) {
  const [confirming, setConfirming] = useState(false)

  if (!confirming) {
    return (
      <Button variant="danger" size="sm" onClick={() => setConfirming(true)}>
        <Archive size={14} />
        Wrap up sesh
      </Button>
    )
  }

  return (
    <div className="flex flex-col gap-2 rounded-2xl border-2 border-danger/40 bg-danger/10 p-3">
      <p className="text-sm text-danger">Wrap up for everyone? Read-only for 24h, then auto-cleared.</p>
      <div className="flex flex-wrap gap-2">
        <Button
          variant="danger"
          size="sm"
          disabled={loading}
          onClick={() => onEnd(false)}
        >
          {loading ? 'Wrapping...' : 'Wrap up'}
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={loading}
          onClick={() => onEnd(true)}
          className="border-danger/40 text-danger"
        >
          <Trash2 size={14} />
          Delete forever
        </Button>
        <Button variant="ghost" size="sm" onClick={() => setConfirming(false)} disabled={loading}>
          Cancel
        </Button>
      </div>
    </div>
  )
}
