import Database from 'better-sqlite3'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { SQL_NOW_IST } from './time.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const dbPath = path.join(__dirname, '..', 'data', 'nit-joint.db')

const db = new Database(dbPath)
db.pragma('journal_mode = WAL')
db.pragma('foreign_keys = ON')

db.exec(`
  CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    host_name TEXT NOT NULL,
    location TEXT,
    description TEXT,
    max_capacity INTEGER DEFAULT 10,
    scheduled_at TEXT,
    created_at TEXT DEFAULT (${SQL_NOW_IST})
  );

  CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    name TEXT NOT NULL,
    joined_at TEXT DEFAULT (${SQL_NOW_IST}),
    UNIQUE(room_id, name),
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (${SQL_NOW_IST}),
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS checklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    item TEXT NOT NULL,
    claimed_by TEXT,
    created_at TEXT DEFAULT (${SQL_NOW_IST}),
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    paid_by TEXT NOT NULL,
    created_at TEXT DEFAULT (${SQL_NOW_IST}),
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
  );

  CREATE TABLE IF NOT EXISTS sellers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    block TEXT,
    contact TEXT,
    available INTEGER DEFAULT 0,
    note TEXT,
    updated_at TEXT DEFAULT (${SQL_NOW_IST})
  );
`)

function migrate() {
  const roomCols = db.prepare('PRAGMA table_info(rooms)').all() as Array<{ name: string }>
  const roomColNames = new Set(roomCols.map((c) => c.name))
  if (!roomColNames.has('playlist_url')) {
    db.exec('ALTER TABLE rooms ADD COLUMN playlist_url TEXT')
  }
  if (!roomColNames.has('vibe_tags')) {
    db.exec('ALTER TABLE rooms ADD COLUMN vibe_tags TEXT')
  }
  if (!roomColNames.has('join_pin')) {
    db.exec('ALTER TABLE rooms ADD COLUMN join_pin TEXT')
  }
  if (!roomColNames.has('archived_at')) {
    db.exec('ALTER TABLE rooms ADD COLUMN archived_at TEXT')
  }
  if (!roomColNames.has('last_activity_at')) {
    db.exec('ALTER TABLE rooms ADD COLUMN last_activity_at TEXT')
    db.exec(`UPDATE rooms SET last_activity_at = COALESCE(created_at, ${SQL_NOW_IST})`)
  }

  const memberCols = db.prepare('PRAGMA table_info(members)').all() as Array<{ name: string }>
  const memberColNames = new Set(memberCols.map((c) => c.name))
  if (!memberColNames.has('status')) {
    db.exec("ALTER TABLE members ADD COLUMN status TEXT DEFAULT 'here'")
  }
  if (!memberColNames.has('block')) {
    db.exec('ALTER TABLE members ADD COLUMN block TEXT')
  }

  const sellerCols = db.prepare('PRAGMA table_info(sellers)').all() as Array<{ name: string }>
  const sellerColNames = new Set(sellerCols.map((c) => c.name))
  if (!sellerColNames.has('stocked_at')) {
    db.exec('ALTER TABLE sellers ADD COLUMN stocked_at TEXT')
  }

  const msgCols = db.prepare('PRAGMA table_info(messages)').all() as Array<{ name: string }>
  const msgColNames = new Set(msgCols.map((c) => c.name))
  if (!msgColNames.has('type')) {
    db.exec("ALTER TABLE messages ADD COLUMN type TEXT DEFAULT 'user'")
  }
}

migrate()

export default db
