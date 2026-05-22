import { Link2, MessageCircle, Share2 } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { copyRoomLink, copyShareText, shareWhatsApp } from '@/lib/share'
import { getTrustedCrew } from '@/lib/trusted-crew'
import type { Room } from '@/types'

export function ShareButtons({ room }: { room: Pick<Room, 'title' | 'code' | 'location' | 'scheduled_at'> }) {
  const crew = getTrustedCrew()

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        variant="secondary"
        size="sm"
        onClick={() =>
          copyRoomLink(room.code).then(() => toast.success('Link copied — send it on WhatsApp'))
        }
      >
        <Link2 size={14} />
        Copy link
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={() =>
          copyShareText(room).then(() => toast.success('Invite copied to clipboard'))
        }
      >
        <Share2 size={14} />
        Copy invite
      </Button>
      <Button
        variant="outline"
        size="sm"
        onClick={() => shareWhatsApp(room, crew.map((c) => c.name))}
      >
        <MessageCircle size={14} />
        {crew.length > 0 ? 'Ping the boys' : 'WhatsApp'}
      </Button>
    </div>
  )
}
