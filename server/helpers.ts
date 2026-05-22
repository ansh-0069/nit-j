import { SQL_NOW_IST } from './time.js'

const MESSAGE_LIMIT = 10
const MESSAGE_WINDOW_MS = 60_000

const messageBuckets = new Map<string, number[]>()

export function checkMessageRateLimit(roomId: string, author: string): boolean {
  const key = `${roomId}:${author.trim().toLowerCase()}`
  const now = Date.now()
  const times = (messageBuckets.get(key) ?? []).filter((t) => now - t < MESSAGE_WINDOW_MS)
  if (times.length >= MESSAGE_LIMIT) return false
  times.push(now)
  messageBuckets.set(key, times)
  return true
}

export function computeSettleUp(
  balances: Array<{ name: string; owes: number }>,
): Array<{ from: string; to: string; amount: number }> {
  const debtors = balances
    .filter((b) => b.owes > 0.01)
    .map((b) => ({ name: b.name, amount: b.owes }))
    .sort((a, b) => b.amount - a.amount)
  const creditors = balances
    .filter((b) => b.owes < -0.01)
    .map((b) => ({ name: b.name, amount: -b.owes }))
    .sort((a, b) => b.amount - a.amount)

  const result: Array<{ from: string; to: string; amount: number }> = []
  let i = 0
  let j = 0
  while (i < debtors.length && j < creditors.length) {
    const pay = Math.min(debtors[i].amount, creditors[j].amount)
    if (pay >= 0.01) {
      result.push({
        from: debtors[i].name,
        to: creditors[j].name,
        amount: Math.round(pay * 100) / 100,
      })
    }
    debtors[i].amount -= pay
    creditors[j].amount -= pay
    if (debtors[i].amount < 0.01) i++
    if (creditors[j].amount < 0.01) j++
  }
  return result
}

export const VIBE_CHECKLIST_PRESETS: Record<string, string[]> = {
  Chill: ['Papers / rolls', 'Grinder', 'Lighter', 'Snacks & drinks', 'Music / speaker'],
  Movie: ['Snacks & drinks', 'HDMI / adapter', 'Blankets', 'Drinks', 'Music / speaker'],
  Birthday: ['Cake / snacks', 'Drinks', 'Candles', 'Music / speaker', 'Decor'],
  'Pre-game': ['Papers / rolls', 'Grinder', 'Lighter', 'Snacks & drinks', 'Ice', 'Mixers'],
  'Late night': ['Papers / rolls', 'Grinder', 'Lighter', 'Snacks & drinks', 'Water bottles'],
  'Exam break': ['Snacks & drinks', 'Coffee / energy', 'Music / speaker', 'Comfort food'],
}

export const DEFAULT_CHECKLIST = VIBE_CHECKLIST_PRESETS.Chill

export function checklistForVibes(vibeTags: string[]): string[] {
  if (vibeTags.length === 0) return [...DEFAULT_CHECKLIST]
  const items = new Set<string>()
  for (const tag of vibeTags) {
    const preset = VIBE_CHECKLIST_PRESETS[tag]
    if (preset) preset.forEach((item) => items.add(item))
  }
  return items.size > 0 ? [...items] : [...DEFAULT_CHECKLIST]
}

export function touchRoomActivity(db: import('better-sqlite3').Database, roomId: string) {
  db.prepare(`UPDATE rooms SET last_activity_at = ${SQL_NOW_IST} WHERE id = ?`).run(roomId)
}

export function purgeExpiredArchives(db: import('better-sqlite3').Database) {
  db.prepare(
    `DELETE FROM rooms WHERE archived_at IS NOT NULL
     AND datetime(archived_at, '+1 day') < ${SQL_NOW_IST}`,
  ).run()
}
