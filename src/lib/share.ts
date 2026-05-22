import type { Room } from '@/types'

export function getRoomUrl(code: string) {
  return `${window.location.origin}/room/${code}`
}

export function buildShareText(room: Pick<Room, 'title' | 'code' | 'location'> & { scheduled_at?: string | null }) {
  const loc = room.location ? ` · ${room.location}` : ''
  return `🌿 NIT-JOINT: ${room.title}${loc}\nCode: ${room.code}\n${getRoomUrl(room.code)}`
}

export function buildCrewInviteText(
  room: Pick<Room, 'title' | 'code' | 'location'>,
  crew: string[],
) {
  const tags = crew.length > 0 ? `\n@${crew.join(' @')}` : ''
  return `${buildShareText(room)}${tags}\nSlide in boys 👊`
}

export function copyRoomLink(code: string) {
  return navigator.clipboard.writeText(getRoomUrl(code))
}

export function copyShareText(room: Pick<Room, 'title' | 'code' | 'location'> & { scheduled_at?: string | null }) {
  return navigator.clipboard.writeText(buildShareText(room))
}

export function shareWhatsApp(
  room: Pick<Room, 'title' | 'code' | 'location'> & { scheduled_at?: string | null },
  crew?: string[],
) {
  const text = crew && crew.length > 0 ? buildCrewInviteText(room, crew) : buildShareText(room)
  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank', 'noopener,noreferrer')
}

export function isSpotifyUrl(url: string): boolean {
  return url.includes('spotify.com') || url.includes('open.spotify')
}
