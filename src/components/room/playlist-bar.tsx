import { useState } from 'react'
import { ExternalLink, Music2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { isSpotifyUrl } from '@/lib/share'
import type { Room } from '@/types'

export function PlaylistBar({
  room,
  onSave,
  saving,
  disabled,
}: {
  room: Room
  onSave: (url: string | null) => void
  saving?: boolean
  disabled?: boolean
}) {
  const [editing, setEditing] = useState(false)
  const [url, setUrl] = useState(room.playlist_url ?? '')

  if (!editing && room.playlist_url) {
    return (
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-joint-green/25 bg-joint-green/5 p-4">
        <div className="flex items-center gap-3">
          <Music2 className="text-joint-green" size={20} />
          <div>
            <p className="text-xs uppercase tracking-wider text-smoke">Tonight&apos;s playlist</p>
            <a
              href={room.playlist_url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-display font-semibold text-joint-green hover:underline"
            >
              Open on Spotify
              <ExternalLink size={12} className="ml-1 inline" />
            </a>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={() => setEditing(true)} disabled={disabled}>
          Edit
        </Button>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-surface-2 p-4">
      <p className="mb-2 text-xs uppercase tracking-wider text-smoke">Who&apos;s DJ tonight?</p>
      {disabled ? (
        <p className="text-sm text-smoke">No playlist set</p>
      ) : (
      <div className="flex gap-2">
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Spotify playlist link"
        />
        <Button
          disabled={saving}
          onClick={() => {
            const trimmed = url.trim()
            if (trimmed && !isSpotifyUrl(trimmed)) {
              toast.error('Paste a valid Spotify link')
              return
            }
            onSave(trimmed || null)
            setEditing(false)
          }}
        >
          Save
        </Button>
      </div>
      )}
    </div>
  )
}
