import type { ChecklistItem, Expense, Message, Room, RoomListItem, Seller } from './types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new Error('Cannot reach server — is npm run dev running?')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.error || `Request failed (${res.status})`)
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

export function healthCheck() {
  return request<{ ok: boolean; ts: string }>('/health')
}

export function listRooms(vibe?: string) {
  const qs = vibe ? `?vibe=${encodeURIComponent(vibe)}` : ''
  return request<RoomListItem[]>(`/rooms${qs}`)
}

export function createRoom(data: {
  title: string
  hostName: string
  location?: string
  description?: string
  maxCapacity?: number
  scheduledAt?: string
  vibeTags?: string[]
  playlistUrl?: string
  joinPin?: string
}) {
  return request<Room>('/rooms', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateRoomPlaylist(code: string, playlistUrl: string | null) {
  return request<Room>(`/rooms/${code}`, {
    method: 'PATCH',
    body: JSON.stringify({ playlistUrl }),
  })
}

export function endRoom(code: string, actorName: string, permanent = false) {
  const trimmed = actorName.trim()
  if (!code?.trim()) throw new Error('Invalid room code')
  if (!trimmed) throw new Error('Your name is required')
  return request<void>(`/rooms/${encodeURIComponent(code)}/end`, {
    method: 'POST',
    body: JSON.stringify({ actorName: trimmed, permanent }),
  })
}

export function transferHost(code: string, actorName: string, newHostName: string) {
  return request<Room>(`/rooms/${code}/transfer-host`, {
    method: 'POST',
    body: JSON.stringify({ actorName, newHostName }),
  })
}

export function getRoom(code: string) {
  return request<Room>(`/rooms/${code}`)
}

export function joinRoom(code: string, name: string, pin?: string, block?: string) {
  return request<Room>(`/rooms/${code}/join`, {
    method: 'POST',
    body: JSON.stringify({ name, pin, block }),
  })
}

export function updateMemberStatus(code: string, name: string, status: string) {
  return request<Room>(`/rooms/${code}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ name, status }),
  })
}

export function postMessage(code: string, author: string, content: string) {
  return request<Message>(`/rooms/${code}/messages`, {
    method: 'POST',
    body: JSON.stringify({ author, content }),
  })
}

export function addChecklistItem(code: string, item: string) {
  return request<ChecklistItem>(`/rooms/${code}/checklist`, {
    method: 'POST',
    body: JSON.stringify({ item }),
  })
}

export function claimChecklistItem(code: string, id: number, claimedBy: string | null) {
  return request<ChecklistItem>(`/rooms/${code}/checklist/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ claimedBy }),
  })
}

export function deleteChecklistItem(code: string, id: number) {
  return request<void>(`/rooms/${code}/checklist/${id}`, { method: 'DELETE' })
}

export function addExpense(code: string, data: { description: string; amount: number; paidBy: string }) {
  return request<Expense>(`/rooms/${code}/expenses`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function deleteExpense(code: string, id: number) {
  return request<void>(`/rooms/${code}/expenses/${id}`, { method: 'DELETE' })
}

export function listSellers() {
  return request<Seller[]>('/sellers')
}

export function registerSeller(data: {
  name: string
  block?: string
  contact?: string
  available?: boolean
  note?: string
}) {
  return request<Seller>('/sellers', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateSeller(
  id: number,
  data: {
    actorName: string
    block?: string
    contact?: string
    available?: boolean
    note?: string
  },
) {
  return request<Seller>(`/sellers/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export function removeSeller(id: number, actorName: string) {
  return request<void>(`/sellers/${id}`, {
    method: 'DELETE',
    body: JSON.stringify({ actorName }),
  })
}

export function subscribeGlobalEvents(onUpdate: () => void): () => void {
  const es = new EventSource(`${BASE}/events`)
  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'rooms-updated' || data.type === 'room-updated') onUpdate()
    } catch {
      /* ignore */
    }
  }
  return () => es.close()
}

export function subscribeRoomEvents(code: string, onUpdate: () => void): () => void {
  const es = new EventSource(`${BASE}/rooms/${encodeURIComponent(code)}/events`)
  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'room-updated') onUpdate()
    } catch {
      /* ignore */
    }
  }
  return () => es.close()
}
