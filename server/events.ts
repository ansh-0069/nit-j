import type { Response } from 'express'

type Client = { res: Response; roomCode: string | null }

const clients = new Set<Client>()

export function subscribeRoomEvents(roomCode: string, res: Response) {
  const client = { res, roomCode: roomCode.toUpperCase() }
  clients.add(client)

  res.on('close', () => {
    clients.delete(client)
  })
}

export function subscribeGlobalEvents(res: Response) {
  const client = { res, roomCode: null }
  clients.add(client)
  res.on('close', () => {
    clients.delete(client)
  })
}

export function broadcastRoomUpdate(roomCode: string) {
  const code = roomCode.toUpperCase()
  const payload = `data: ${JSON.stringify({ type: 'room-updated', code })}\n\n`
  for (const client of clients) {
    if (client.roomCode === code || client.roomCode === null) {
      client.res.write(payload)
    }
  }
}

export function broadcastRoomsListUpdate() {
  const payload = `data: ${JSON.stringify({ type: 'rooms-updated' })}\n\n`
  for (const client of clients) {
    client.res.write(payload)
  }
}
