import type { CrewMember } from '@/types'

const CREW_KEY = 'nit-joint-crew'
const MAX_CREW = 10
const JOINED_KEY = 'nit-joint-joined'
const SEEN_ROOMS_KEY = 'nit-joint-seen-rooms'

export function getTrustedCrew(): CrewMember[] {
  try {
    const raw = localStorage.getItem(CREW_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
      .map((entry) => {
        if (typeof entry === 'string') return { name: entry }
        if (entry && typeof entry.name === 'string') {
          return { name: entry.name, block: entry.block }
        }
        return null
      })
      .filter((e): e is CrewMember => Boolean(e))
      .slice(0, MAX_CREW)
  } catch {
    return []
  }
}

export function saveTrustedCrew(crew: CrewMember[]) {
  localStorage.setItem(CREW_KEY, JSON.stringify(crew.slice(0, MAX_CREW)))
}

export function addToCrew(name: string, block?: string): CrewMember[] {
  const trimmed = name.trim()
  if (!trimmed) return getTrustedCrew()
  const crew = getTrustedCrew().filter((n) => n.name.toLowerCase() !== trimmed.toLowerCase())
  crew.unshift({ name: trimmed, block: block?.trim() || undefined })
  saveTrustedCrew(crew)
  return crew.slice(0, MAX_CREW)
}

export function removeFromCrew(name: string): CrewMember[] {
  const crew = getTrustedCrew().filter((n) => n.name !== name)
  saveTrustedCrew(crew)
  return crew
}

export function getCrewBlock(name: string): string | undefined {
  const match = getTrustedCrew().find((c) => c.name.toLowerCase() === name.trim().toLowerCase())
  return match?.block
}

export function isTrustedCrew(name: string): boolean {
  return getTrustedCrew().some((c) => c.name.toLowerCase() === name.trim().toLowerCase())
}

export function markFirstJoin() {
  localStorage.setItem(JOINED_KEY, '1')
}

export function hasJoinedBefore(): boolean {
  return localStorage.getItem(JOINED_KEY) === '1'
}

export function getRoomLastSeen(code: string): string | null {
  try {
    const raw = localStorage.getItem(SEEN_ROOMS_KEY)
    if (!raw) return null
    const map = JSON.parse(raw) as Record<string, string>
    return map[code.toUpperCase()] ?? null
  } catch {
    return null
  }
}

export function markRoomSeen(code: string, lastMessageAt?: string | null) {
  try {
    const raw = localStorage.getItem(SEEN_ROOMS_KEY)
    const map = raw ? (JSON.parse(raw) as Record<string, string>) : {}
    map[code.toUpperCase()] = lastMessageAt ?? new Date().toISOString()
    localStorage.setItem(SEEN_ROOMS_KEY, JSON.stringify(map))
  } catch {
    /* ignore */
  }
}

export function countNewMessages(
  lastMessageAt: string | null | undefined,
  code: string,
): number {
  if (!lastMessageAt) return 0
  const seen = getRoomLastSeen(code)
  if (!seen) return 0
  return new Date(lastMessageAt) > new Date(seen) ? 1 : 0
}
