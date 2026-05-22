import express from 'express'
import cors from 'cors'
import { nanoid } from 'nanoid'
import db from './db.js'
import { broadcastRoomUpdate, broadcastRoomsListUpdate, subscribeGlobalEvents, subscribeRoomEvents } from './events.js'
import {
  checkMessageRateLimit,
  checklistForVibes,
  computeSettleUp,
  purgeExpiredArchives,
  touchRoomActivity,
} from './helpers.js'
import { nowIst, SQL_NOW_IST } from './time.js'

export function createApp() {
  const app = express()

  app.use(cors())
  app.use(express.json())

  purgeExpiredArchives(db)

  function generateCode(): string {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    let code = ''
    for (let i = 0; i < 6; i++) {
      code += chars[Math.floor(Math.random() * chars.length)]
    }
    const existing = db.prepare('SELECT id FROM rooms WHERE code = ?').get(code)
    return existing ? generateCode() : code
  }

  function getRoomByCode(code: string) {
    return db
      .prepare('SELECT * FROM rooms WHERE code = ? COLLATE NOCASE')
      .get(code.toUpperCase()) as Record<string, unknown> | undefined
  }

  function parseVibeTags(raw: unknown): string[] {
    if (!raw || typeof raw !== 'string') return []
    try {
      const parsed = JSON.parse(raw)
      return Array.isArray(parsed) ? parsed.filter((t) => typeof t === 'string') : []
    } catch {
      return []
    }
  }

  function insertSystemMessage(roomId: string, content: string) {
    db.prepare('INSERT INTO messages (room_id, author, content, type) VALUES (?, ?, ?, ?)').run(
      roomId,
      'System',
      content,
      'system',
    )
    touchRoomActivity(db, roomId)
  }

  function getMembers(roomId: string) {
    return db
      .prepare(
        'SELECT name, joined_at, COALESCE(status, \'here\') as status, block FROM members WHERE room_id = ? ORDER BY joined_at',
      )
      .all(roomId)
  }

  function getMessages(roomId: string) {
    return db
      .prepare('SELECT * FROM messages WHERE room_id = ? ORDER BY created_at ASC')
      .all(roomId)
  }

  function getChecklist(roomId: string) {
    return db
      .prepare('SELECT * FROM checklist WHERE room_id = ? ORDER BY created_at ASC')
      .all(roomId)
  }

  function getExpenses(roomId: string) {
    return db
      .prepare('SELECT * FROM expenses WHERE room_id = ? ORDER BY created_at ASC')
      .all(roomId)
  }

  function isArchived(room: Record<string, unknown>) {
    return Boolean(room.archived_at)
  }

  function notifyRoom(code: string) {
    broadcastRoomUpdate(code)
    broadcastRoomsListUpdate()
  }

  function buildRoomPayload(room: Record<string, unknown>) {
    const roomId = room.id as string
    const members = getMembers(roomId)
    const expenses = getExpenses(roomId) as Array<{ amount: number; paid_by: string }>
    const total = expenses.reduce((sum, e) => sum + e.amount, 0)
    const perPerson = members.length > 0 ? total / members.length : 0

    const paidMap = new Map<string, number>()
    for (const e of expenses) {
      paidMap.set(e.paid_by, (paidMap.get(e.paid_by) ?? 0) + e.amount)
    }

    const balances = members.map((m) => {
      const member = m as { name: string }
      const paid = paidMap.get(member.name) ?? 0
      return {
        name: member.name,
        paid: Math.round(paid * 100) / 100,
        owes: Math.round((perPerson - paid) * 100) / 100,
      }
    })

    const lastMsg = db
      .prepare(
        'SELECT created_at FROM messages WHERE room_id = ? ORDER BY created_at DESC LIMIT 1',
      )
      .get(roomId) as { created_at: string } | undefined

    return {
      ...room,
      code: (room.code as string).toUpperCase(),
      playlist_url: (room.playlist_url as string | null) ?? null,
      vibe_tags: parseVibeTags(room.vibe_tags),
      has_pin: Boolean(room.join_pin),
      is_archived: isArchived(room),
      archived_at: (room.archived_at as string | null) ?? null,
      last_activity_at: (room.last_activity_at as string | null) ?? null,
      last_message_at: lastMsg?.created_at ?? null,
      members,
      messages: getMessages(roomId),
      checklist: getChecklist(roomId),
      expenses,
      split: {
        total: Math.round(total * 100) / 100,
        perPerson: Math.round(perPerson * 100) / 100,
        memberCount: members.length,
        balances,
        settleUp: computeSettleUp(balances),
      },
    }
  }

  app.get('/api/health', (_req, res) => {
    res.json({ ok: true, ts: nowIst(), timezone: 'Asia/Kolkata' })
  })

  app.get('/api/events', (_req, res) => {
    res.setHeader('Content-Type', 'text/event-stream')
    res.setHeader('Cache-Control', 'no-cache')
    res.setHeader('Connection', 'keep-alive')
    res.flushHeaders()
    res.write(`data: ${JSON.stringify({ type: 'connected' })}\n\n`)
    subscribeGlobalEvents(res)
  })

  app.get('/api/rooms/:code/events', (req, res) => {
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }

    res.setHeader('Content-Type', 'text/event-stream')
    res.setHeader('Cache-Control', 'no-cache')
    res.setHeader('Connection', 'keep-alive')
    res.flushHeaders()
    res.write(`data: ${JSON.stringify({ type: 'connected', code: req.params.code.toUpperCase() })}\n\n`)
    subscribeRoomEvents(req.params.code, res)
  })

  app.get('/api/rooms', (req, res) => {
    const vibe = req.query.vibe as string | undefined
    let rooms = db
      .prepare(
        `SELECT r.*, COUNT(m.id) as member_count,
          (SELECT COUNT(*) FROM messages msg WHERE msg.room_id = r.id AND msg.type = 'user') as message_count,
          (SELECT MAX(created_at) FROM messages msg WHERE msg.room_id = r.id) as last_message_at
         FROM rooms r
         LEFT JOIN members m ON m.room_id = r.id
         WHERE r.archived_at IS NULL
         GROUP BY r.id
         ORDER BY COALESCE(r.last_activity_at, r.created_at) DESC
         LIMIT 50`,
      )
      .all() as Array<Record<string, unknown>>

    if (vibe) {
      rooms = rooms.filter((r) => parseVibeTags(r.vibe_tags).includes(vibe))
    }

    res.json(
      rooms.map((r) => ({
        ...r,
        code: (r.code as string).toUpperCase(),
        vibe_tags: parseVibeTags(r.vibe_tags),
        playlist_url: (r.playlist_url as string | null) ?? null,
        has_pin: Boolean(r.join_pin),
        last_activity_at: (r.last_activity_at as string | null) ?? null,
        last_message_at: (r.last_message_at as string | null) ?? null,
        message_count: Number(r.message_count ?? 0),
      })),
    )
  })

  app.post('/api/rooms', (req, res) => {
    const {
      title,
      hostName,
      location,
      description,
      maxCapacity,
      scheduledAt,
      vibeTags,
      playlistUrl,
      joinPin,
    } = req.body

    if (!title?.trim() || !hostName?.trim()) {
      res.status(400).json({ error: 'Title and your name are required' })
      return
    }

    const pin = joinPin?.trim()
    if (pin && (!/^\d{4}$/.test(pin))) {
      res.status(400).json({ error: 'PIN must be 4 digits' })
      return
    }

    const id = nanoid()
    const code = generateCode()
    const tags = Array.isArray(vibeTags) ? vibeTags.filter((t: unknown) => typeof t === 'string') : []

    db.prepare(
      `INSERT INTO rooms (id, code, title, host_name, location, description, max_capacity, scheduled_at, vibe_tags, playlist_url, join_pin, last_activity_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ${SQL_NOW_IST})`,
    ).run(
      id,
      code,
      title.trim(),
      hostName.trim(),
      location?.trim() || null,
      description?.trim() || null,
      maxCapacity || 10,
      scheduledAt || null,
      tags.length > 0 ? JSON.stringify(tags) : null,
      playlistUrl?.trim() || null,
      pin || null,
    )

    db.prepare('INSERT INTO members (room_id, name, status) VALUES (?, ?, ?)').run(
      id,
      hostName.trim(),
      'here',
    )
    insertSystemMessage(id, `${hostName.trim()} opened the joint`)

    const insertChecklist = db.prepare('INSERT INTO checklist (room_id, item) VALUES (?, ?)')
    for (const item of checklistForVibes(tags)) {
      insertChecklist.run(id, item)
    }

    const room = getRoomByCode(code)!
    notifyRoom(code)
    res.status(201).json(buildRoomPayload(room))
  })

  app.patch('/api/rooms/:code', (req, res) => {
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const { playlistUrl } = req.body

    db.prepare('UPDATE rooms SET playlist_url = ? WHERE id = ?').run(
      playlistUrl?.trim() || null,
      room.id,
    )

    if (playlistUrl?.trim()) {
      insertSystemMessage(room.id as string, 'Playlist link updated 🎵')
    }

    touchRoomActivity(db, room.id as string)
    notifyRoom(req.params.code)
    res.json(buildRoomPayload(getRoomByCode(req.params.code)!))
  })

  app.post('/api/rooms/:code/end', (req, res) => {
    const actorName = (req.body?.actorName ?? req.query.actorName) as string | undefined
    const permanent = Boolean(req.body?.permanent)

    if (!actorName?.trim()) {
      res.status(400).json({ error: 'Your name is required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }

    if ((room.host_name as string).trim().toLowerCase() !== actorName.trim().toLowerCase()) {
      res.status(403).json({ error: 'Only the host can end this sesh' })
      return
    }

    const roomId = room.id as string
    const code = room.code as string

    if (permanent) {
      db.prepare('DELETE FROM rooms WHERE id = ?').run(roomId)
    } else {
      db.prepare(`UPDATE rooms SET archived_at = ${SQL_NOW_IST} WHERE id = ?`).run(roomId)
      insertSystemMessage(roomId, `${actorName.trim()} wrapped up the sesh — read-only for 24h`)
    }

    notifyRoom(code)
    res.status(204).end()
  })

  app.post('/api/rooms/:code/transfer-host', (req, res) => {
    const { actorName, newHostName } = req.body
    if (!actorName?.trim() || !newHostName?.trim()) {
      res.status(400).json({ error: 'Actor and new host name required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    if ((room.host_name as string).trim().toLowerCase() !== actorName.trim().toLowerCase()) {
      res.status(403).json({ error: 'Only the host can transfer host' })
      return
    }

    const member = db
      .prepare('SELECT id FROM members WHERE room_id = ? AND name = ?')
      .get(room.id, newHostName.trim())
    if (!member) {
      res.status(400).json({ error: 'New host must already be in the room' })
      return
    }

    db.prepare('UPDATE rooms SET host_name = ? WHERE id = ?').run(newHostName.trim(), room.id)
    insertSystemMessage(
      room.id as string,
      `${actorName.trim()} passed host to ${newHostName.trim()} 👑`,
    )
    notifyRoom(req.params.code)
    res.json(buildRoomPayload(getRoomByCode(req.params.code)!))
  })

  app.get('/api/rooms/:code', (req, res) => {
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    res.json(buildRoomPayload(room))
  })

  app.post('/api/rooms/:code/join', (req, res) => {
    const { name, pin, block } = req.body
    if (!name?.trim()) {
      res.status(400).json({ error: 'Name is required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up' })
      return
    }

    const roomPin = room.join_pin as string | null
    if (roomPin && roomPin !== String(pin ?? '').trim()) {
      res.status(403).json({ error: 'Wrong PIN' })
      return
    }

    const roomId = room.id as string
    const trimmed = name.trim()
    const existing = db
      .prepare('SELECT id FROM members WHERE room_id = ? AND name = ?')
      .get(roomId, trimmed)

    if (!existing) {
      const members = getMembers(roomId)
      if (members.length >= (room.max_capacity as number)) {
        res.status(400).json({ error: 'Room is full' })
        return
      }
      db.prepare('INSERT INTO members (room_id, name, status, block) VALUES (?, ?, ?, ?)').run(
        roomId,
        trimmed,
        'here',
        block?.trim() || null,
      )
      insertSystemMessage(roomId, `${trimmed} slid into the joint`)
    }

    touchRoomActivity(db, roomId)
    notifyRoom(req.params.code)
    res.json(buildRoomPayload(getRoomByCode(req.params.code)!))
  })

  app.patch('/api/rooms/:code/status', (req, res) => {
    const { name, status } = req.body
    const valid = ['on_my_way', 'here', 'running_late']
    if (!name?.trim() || !valid.includes(status)) {
      res.status(400).json({ error: 'Valid name and status required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const result = db
      .prepare('UPDATE members SET status = ? WHERE room_id = ? AND name = ?')
      .run(status, room.id, name.trim())
    if (result.changes === 0) {
      res.status(404).json({ error: 'Member not found' })
      return
    }

    const labels: Record<string, string> = {
      on_my_way: 'is on the way 🚶',
      here: 'pulled up ✅',
      running_late: 'is running late ⏰',
    }
    insertSystemMessage(room.id as string, `${name.trim()} ${labels[status]}`)
    notifyRoom(req.params.code)
    res.json(buildRoomPayload(getRoomByCode(req.params.code)!))
  })

  app.post('/api/rooms/:code/messages', (req, res) => {
    const { author, content } = req.body
    if (!author?.trim() || !content?.trim()) {
      res.status(400).json({ error: 'Author and content required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    if (!checkMessageRateLimit(room.id as string, author.trim())) {
      res.status(429).json({ error: 'Slow down — max 10 messages per minute' })
      return
    }

    const result = db
      .prepare('INSERT INTO messages (room_id, author, content, type) VALUES (?, ?, ?, ?)')
      .run(room.id, author.trim(), content.trim(), 'user')

    touchRoomActivity(db, room.id as string)
    notifyRoom(req.params.code)

    const message = db.prepare('SELECT * FROM messages WHERE id = ?').get(result.lastInsertRowid)
    res.status(201).json(message)
  })

  app.post('/api/rooms/:code/checklist', (req, res) => {
    const { item } = req.body
    if (!item?.trim()) {
      res.status(400).json({ error: 'Item required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const trimmed = item.trim()
    const result = db
      .prepare('INSERT INTO checklist (room_id, item) VALUES (?, ?)')
      .run(room.id, trimmed)

    insertSystemMessage(room.id as string, `Added to run sheet: ${trimmed}`)
    notifyRoom(req.params.code)

    const checklistItem = db.prepare('SELECT * FROM checklist WHERE id = ?').get(result.lastInsertRowid)
    res.status(201).json(checklistItem)
  })

  app.patch('/api/rooms/:code/checklist/:id', (req, res) => {
    const { claimedBy } = req.body
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const existing = db.prepare('SELECT * FROM checklist WHERE id = ?').get(req.params.id) as
      | { item: string; claimed_by: string | null }
      | undefined

    db.prepare('UPDATE checklist SET claimed_by = ? WHERE id = ? AND room_id = ?').run(
      claimedBy || null,
      req.params.id,
      room.id,
    )

    if (existing) {
      if (claimedBy) {
        insertSystemMessage(
          room.id as string,
          `${claimedBy} claimed ${existing.item} on the run sheet`,
        )
      } else if (existing.claimed_by) {
        insertSystemMessage(
          room.id as string,
          `${existing.claimed_by} unclaimed ${existing.item}`,
        )
      }
    }

    notifyRoom(req.params.code)
    const item = db.prepare('SELECT * FROM checklist WHERE id = ?').get(req.params.id)
    res.json(item)
  })

  app.delete('/api/rooms/:code/checklist/:id', (req, res) => {
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const existing = db.prepare('SELECT * FROM checklist WHERE id = ?').get(req.params.id) as
      | { item: string }
      | undefined

    db.prepare('DELETE FROM checklist WHERE id = ? AND room_id = ?').run(req.params.id, room.id)

    if (existing) {
      insertSystemMessage(room.id as string, `Removed from run sheet: ${existing.item}`)
    }

    notifyRoom(req.params.code)
    res.status(204).end()
  })

  app.post('/api/rooms/:code/expenses', (req, res) => {
    const { description, amount, paidBy } = req.body
    if (!description?.trim() || !paidBy?.trim() || typeof amount !== 'number' || amount <= 0) {
      res.status(400).json({ error: 'Valid description, amount, and payer required' })
      return
    }

    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const result = db
      .prepare('INSERT INTO expenses (room_id, description, amount, paid_by) VALUES (?, ?, ?, ?)')
      .run(room.id, description.trim(), amount, paidBy.trim())

    insertSystemMessage(
      room.id as string,
      `${paidBy.trim()} logged ₹${Math.round(amount)} for ${description.trim()}`,
    )
    notifyRoom(req.params.code)

    const expense = db.prepare('SELECT * FROM expenses WHERE id = ?').get(result.lastInsertRowid)
    res.status(201).json(expense)
  })

  app.delete('/api/rooms/:code/expenses/:id', (req, res) => {
    const room = getRoomByCode(req.params.code)
    if (!room) {
      res.status(404).json({ error: 'Room not found' })
      return
    }
    if (isArchived(room)) {
      res.status(403).json({ error: 'This sesh is wrapped up — read only' })
      return
    }

    const existing = db.prepare('SELECT * FROM expenses WHERE id = ?').get(req.params.id) as
      | { description: string; amount: number }
      | undefined

    db.prepare('DELETE FROM expenses WHERE id = ? AND room_id = ?').run(req.params.id, room.id)

    if (existing) {
      insertSystemMessage(
        room.id as string,
        `Removed expense: ${existing.description} (₹${Math.round(existing.amount)})`,
      )
    }

    notifyRoom(req.params.code)
    res.status(204).end()
  })

  function formatSeller(row: Record<string, unknown>) {
    return {
      id: row.id as number,
      name: row.name as string,
      block: (row.block as string | null) ?? null,
      contact: (row.contact as string | null) ?? null,
      available: Boolean(row.available),
      note: (row.note as string | null) ?? null,
      updated_at: row.updated_at as string,
      stocked_at: (row.stocked_at as string | null) ?? null,
    }
  }

  app.get('/api/sellers', (_req, res) => {
    const sellers = db
      .prepare('SELECT * FROM sellers ORDER BY available DESC, updated_at DESC')
      .all()
      .map((row) => formatSeller(row as Record<string, unknown>))
    res.json(sellers)
  })

  app.post('/api/sellers', (req, res) => {
    const { name, block, contact, available, note } = req.body
    if (!name?.trim()) {
      res.status(400).json({ error: 'Name is required' })
      return
    }

    const trimmed = name.trim()
    const existing = db.prepare('SELECT id FROM sellers WHERE name = ?').get(trimmed)

    if (existing) {
      res.status(409).json({ error: 'Seller already listed — update your existing entry' })
      return
    }

    const isAvailable = available ? 1 : 0
    const result = db
      .prepare(
        `INSERT INTO sellers (name, block, contact, available, note, updated_at, stocked_at)
         VALUES (?, ?, ?, ?, ?, ${SQL_NOW_IST}, ?)`,
      )
      .run(
        trimmed,
        block?.trim() || null,
        contact?.trim() || null,
        isAvailable,
        note?.trim() || null,
        isAvailable ? nowIst() : null,
      )

    const seller = db.prepare('SELECT * FROM sellers WHERE id = ?').get(result.lastInsertRowid)
    res.status(201).json(formatSeller(seller as Record<string, unknown>))
  })

  app.patch('/api/sellers/:id', (req, res) => {
    const { actorName, block, contact, available, note } = req.body
    if (!actorName?.trim()) {
      res.status(400).json({ error: 'Your name is required to update' })
      return
    }

    const seller = db.prepare('SELECT * FROM sellers WHERE id = ?').get(req.params.id) as
      | Record<string, unknown>
      | undefined

    if (!seller) {
      res.status(404).json({ error: 'Seller not found' })
      return
    }

    if ((seller.name as string).toLowerCase() !== actorName.trim().toLowerCase()) {
      res.status(403).json({ error: 'You can only update your own listing' })
      return
    }

    const current = formatSeller(seller)
    const nextAvailable = available !== undefined ? available : current.available
    const stockedAt =
      available === true
        ? nowIst()
        : available === false
          ? null
          : current.stocked_at

    db.prepare(
      `UPDATE sellers SET block = ?, contact = ?, available = ?, note = ?, updated_at = ${SQL_NOW_IST}, stocked_at = ? WHERE id = ?`,
    ).run(
      block !== undefined ? block?.trim() || null : current.block,
      contact !== undefined ? contact?.trim() || null : current.contact,
      nextAvailable ? 1 : 0,
      note !== undefined ? note?.trim() || null : current.note,
      stockedAt,
      req.params.id,
    )

    const updated = db.prepare('SELECT * FROM sellers WHERE id = ?').get(req.params.id)
    res.json(formatSeller(updated as Record<string, unknown>))
  })

  app.delete('/api/sellers/:id', (req, res) => {
    const { actorName } = req.body
    if (!actorName?.trim()) {
      res.status(400).json({ error: 'Your name is required' })
      return
    }

    const seller = db.prepare('SELECT * FROM sellers WHERE id = ?').get(req.params.id) as
      | Record<string, unknown>
      | undefined

    if (!seller) {
      res.status(404).json({ error: 'Seller not found' })
      return
    }

    if ((seller.name as string).toLowerCase() !== actorName.trim().toLowerCase()) {
      res.status(403).json({ error: 'You can only remove your own listing' })
      return
    }

    db.prepare('DELETE FROM sellers WHERE id = ?').run(req.params.id)
    res.status(204).end()
  })

  return app
}
