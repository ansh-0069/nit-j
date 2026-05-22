import { MapPin, Clock, Users, Lock } from 'lucide-react'
import { RoomCodePill } from '@/components/brand/room-code-pill'
import { DeleteSeshButton } from '@/components/room/delete-sesh-button'
import { HostTransferButton } from '@/components/room/host-transfer-button'
import { ShareButtons } from '@/components/room/share-buttons'
import { Badge } from '@/components/ui/badge'
import { MemberStack } from '@/components/room/member-stack'
import { formatTime, getCountdown } from '@/lib/storage'
import type { Room } from '@/types'

export function RoomHeader({
  room,
  isHost,
  onEnd,
  onTransferHost,
  ending,
  transferring,
}: {
  room: Room
  isHost?: boolean
  onEnd?: (permanent: boolean) => void
  onTransferHost?: (newHostName: string) => void
  ending?: boolean
  transferring?: boolean
}) {
  const countdown = getCountdown(room.scheduled_at)
  const isLive = countdown === 'Live now'

  return (
    <div className="glass-fun glow-green rounded-3xl p-6 sticker">
      {room.is_archived && (
        <div className="mb-4 rounded-xl border border-ember/40 bg-ember/10 px-4 py-2 text-sm text-ember">
          This sesh is wrapped up — read-only for 24h
        </div>
      )}
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-3">
          <RoomCodePill code={room.code} />
          <h1 className="heading-xl">{room.title}</h1>
          {room.description && <p className="max-w-lg text-smoke">{room.description}</p>}
          <div className="flex flex-wrap items-center gap-2">
            {room.has_pin && (
              <Badge className="gap-1 normal-case">
                <Lock size={12} />
                PIN protected
              </Badge>
            )}
            {room.vibe_tags?.map((tag) => (
              <Badge key={tag} variant="host" className="normal-case">
                {tag}
              </Badge>
            ))}
            {room.location && (
              <Badge className="gap-1 normal-case">
                <MapPin size={12} />
                {room.location}
              </Badge>
            )}
            {room.scheduled_at && (
              <Badge variant={isLive ? 'live' : 'default'} className="gap-1 normal-case">
                <Clock size={12} />
                {countdown ?? formatTime(room.scheduled_at)}
              </Badge>
            )}
            <Badge className="gap-1 normal-case">
              <Users size={12} />
              {room.members.length}/{room.max_capacity}
            </Badge>
            <Badge variant="host" className="normal-case">
              Host: {room.host_name}
            </Badge>
          </div>
          <ShareButtons room={room} />
          {isHost && !room.is_archived && onEnd && (
            <div className="flex flex-col gap-2">
              <DeleteSeshButton onEnd={onEnd} loading={ending} />
              {onTransferHost && (
                <HostTransferButton
                  members={room.members}
                  hostName={room.host_name}
                  currentUser={room.host_name}
                  loading={transferring}
                  onTransfer={onTransferHost}
                />
              )}
            </div>
          )}
        </div>
        <MemberStack members={room.members} hostName={room.host_name} />
      </div>
    </div>
  )
}
