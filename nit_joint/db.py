from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from nit_joint.postgres import init_postgres, using_postgres
from pathlib import Path
from typing import Any, Iterator

from nit_joint.helpers import (
    compute_settle_up,
    generate_code,
    parse_vibe_tags,
)
from nit_joint.time import SQL_NOW_IST, now_ist

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "nit-joint.db"

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS rooms (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  host_name TEXT NOT NULL,
  location TEXT,
  description TEXT,
  max_capacity INTEGER DEFAULT 10,
  scheduled_at TEXT,
  playlist_url TEXT,
  vibe_tags TEXT,
  join_pin TEXT,
  archived_at TEXT,
  last_activity_at TEXT,
  created_at TEXT DEFAULT ({SQL_NOW_IST})
);

CREATE TABLE IF NOT EXISTS members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'here',
  block TEXT,
  joined_at TEXT DEFAULT ({SQL_NOW_IST}),
  UNIQUE(room_id, name),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  author TEXT NOT NULL,
  content TEXT NOT NULL,
  type TEXT DEFAULT 'user',
  created_at TEXT DEFAULT ({SQL_NOW_IST}),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checklist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  item TEXT NOT NULL,
  claimed_by TEXT,
  created_at TEXT DEFAULT ({SQL_NOW_IST}),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expenses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  description TEXT NOT NULL,
  amount REAL NOT NULL,
  paid_by TEXT NOT NULL,
  created_at TEXT DEFAULT ({SQL_NOW_IST}),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  block TEXT,
  contact TEXT,
  available INTEGER DEFAULT 0,
  note TEXT,
  stocked_at TEXT,
  updated_at TEXT DEFAULT ({SQL_NOW_IST})
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT NOT NULL,
  actor TEXT,
  target TEXT,
  detail TEXT,
  created_at TEXT DEFAULT ({SQL_NOW_IST})
);

CREATE TABLE IF NOT EXISTS banned_names (
  name TEXT PRIMARY KEY,
  reason TEXT,
  banned_at TEXT DEFAULT ({SQL_NOW_IST})
);

CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  room_code TEXT,
  created_at TEXT DEFAULT ({SQL_NOW_IST})
);

CREATE TABLE IF NOT EXISTS trusted_crew (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  block TEXT
);

CREATE TABLE IF NOT EXISTS plug_watch (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  watcher_name TEXT NOT NULL,
  block TEXT NOT NULL,
  created_at TEXT DEFAULT ({SQL_NOW_IST}),
  UNIQUE(watcher_name, block)
);

CREATE TABLE IF NOT EXISTS music_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  video_id TEXT NOT NULL,
  title TEXT NOT NULL,
  channel TEXT,
  added_by TEXT,
  position INTEGER NOT NULL DEFAULT 0,
  created_at TEXT DEFAULT ({SQL_NOW_IST}),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settlement_paid (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  room_id TEXT NOT NULL,
  from_name TEXT NOT NULL,
  to_name TEXT NOT NULL,
  amount REAL NOT NULL,
  paid INTEGER DEFAULT 0,
  UNIQUE(room_id, from_name, to_name, amount),
  FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_pins (
  name TEXT PRIMARY KEY,
  pin TEXT NOT NULL
);
"""


def _now_iso() -> str:
    return now_ist()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    try:
        init_postgres()
    except Exception:
        pass
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        _migrate(conn)
        _expire_stale_plugs(conn)
        conn.execute(
            f"""DELETE FROM rooms WHERE archived_at IS NOT NULL
               AND datetime(archived_at, '+1 day') < {SQL_NOW_IST}""",
        )


def _migrate(conn: sqlite3.Connection) -> None:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(expenses)").fetchall()}
    if "receipt_data" not in cols:
        try:
            conn.execute("ALTER TABLE expenses ADD COLUMN receipt_data TEXT")
        except sqlite3.OperationalError:
            pass
    room_cols = {r[1] for r in conn.execute("PRAGMA table_info(rooms)").fetchall()}
    for col, ddl in [
        ("join_mode", "ALTER TABLE rooms ADD COLUMN join_mode TEXT DEFAULT 'open'"),
        ("invite_token", "ALTER TABLE rooms ADD COLUMN invite_token TEXT"),
        ("recap_text", "ALTER TABLE rooms ADD COLUMN recap_text TEXT"),
        ("current_track_id", "ALTER TABLE rooms ADD COLUMN current_track_id TEXT"),
        ("current_track_title", "ALTER TABLE rooms ADD COLUMN current_track_title TEXT"),
    ]:
        if col not in room_cols:
            try:
                conn.execute(ddl)
            except sqlite3.OperationalError:
                pass
    member_cols = {r[1] for r in conn.execute("PRAGMA table_info(members)").fetchall()}
    for col, ddl in [
        ("eta_minutes", "ALTER TABLE members ADD COLUMN eta_minutes INTEGER"),
        ("needs_pickup", "ALTER TABLE members ADD COLUMN needs_pickup INTEGER DEFAULT 0"),
    ]:
        if col not in member_cols:
            try:
                conn.execute(ddl)
            except sqlite3.OperationalError:
                pass


PLUG_STALE_HOURS = 6


def _expire_stale_plugs(conn: sqlite3.Connection) -> None:
    conn.execute(
        f"""UPDATE sellers SET available = 0, stocked_at = NULL
           WHERE available = 1 AND stocked_at IS NOT NULL
           AND datetime(stocked_at, '+{PLUG_STALE_HOURS} hours') < {SQL_NOW_IST}"""
    )


def _audit(conn: sqlite3.Connection, action: str, actor: str | None, target: str | None, detail: str | None) -> None:
    conn.execute(
        "INSERT INTO audit_log (action, actor, target, detail) VALUES (?, ?, ?, ?)",
        (action, actor, target, detail),
    )


def is_banned(name: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM banned_names WHERE lower(name) = lower(?)",
            (name.strip(),),
        ).fetchone()
        return row is not None


def _check_banned(name: str) -> None:
    if is_banned(name):
        raise ValueError("You are not allowed to join or post")


def log_audit(action: str, actor: str | None, target: str | None = None, detail: str | None = None) -> None:
    with get_conn() as conn:
        _audit(conn, action, actor, target, detail)


def list_audit(limit: int = 100) -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()]


def ban_name(name: str, reason: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO banned_names (name, reason) VALUES (?, ?)",
            (name.strip(), reason),
        )
        _audit(conn, "ban", "admin", name.strip(), reason)


def unban_name(name: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM banned_names WHERE lower(name) = lower(?)", (name.strip(),))
        _audit(conn, "unban", "admin", name.strip(), None)


def list_banned() -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM banned_names ORDER BY banned_at DESC").fetchall()]


def submit_feedback(content: str, room_code: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feedback (content, room_code) VALUES (?, ?)",
            (content.strip(), room_code),
        )


def list_feedback(limit: int = 50) -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()]


def add_plug_watch(watcher_name: str, block: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO plug_watch (watcher_name, block) VALUES (?, ?)",
            (watcher_name.strip(), block.strip()),
        )


def remove_plug_watch(watcher_name: str, block: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM plug_watch WHERE lower(watcher_name) = lower(?) AND block = ?",
            (watcher_name.strip(), block.strip()),
        )


def list_plug_watch(watcher_name: str) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT block FROM plug_watch WHERE lower(watcher_name) = lower(?)",
            (watcher_name.strip(),),
        ).fetchall()
        return [r[0] for r in rows]


def stocked_blocks() -> set[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT block FROM sellers WHERE available = 1 AND block IS NOT NULL"
        ).fetchall()
        return {r[0] for r in rows if r[0]}


def save_trusted_crew_db(name: str, block: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO trusted_crew (name, block) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET block = excluded.block",
            (name.strip(), block),
        )


def list_trusted_crew_db() -> list[dict[str, Any]]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT name, block FROM trusted_crew ORDER BY name").fetchall()]


def admin_delete_message(message_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        _audit(conn, "delete_message", "admin", str(message_id), None)


def admin_kick_member(code: str, member_name: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        conn.execute(
            "DELETE FROM members WHERE room_id = ? AND name = ?",
            (room["id"], member_name.strip()),
        )
        _audit(conn, "kick", "admin", member_name.strip(), code)


def admin_force_end(code: str, permanent: bool = True) -> None:
    close_session(code, "Admin", delete=permanent, as_admin=True)


def create_room_from_template(template_key: str, host_name: str, location: str | None = None, join_pin: str | None = None, scheduled_at: str | None = None) -> dict[str, Any]:
    from nit_joint.templates import SESH_TEMPLATES

    tpl = SESH_TEMPLATES.get(template_key)
    if not tpl:
        raise ValueError("Unknown template")
    return create_room(
        title=tpl["title"],
        host_name=host_name,
        location=location or tpl.get("location_hint"),
        description=tpl.get("description"),
        vibe_tags=tpl.get("vibe_tags"),
        join_pin=join_pin,
        scheduled_at=scheduled_at,
        playlist_url=tpl.get("playlist_url"),
        join_mode=tpl.get("join_mode", "open"),
        extra_checklist=tpl.get("extra_checklist"),
    )


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def _touch_room(conn: sqlite3.Connection, room_id: str) -> None:
    conn.execute(
        f"UPDATE rooms SET last_activity_at = {SQL_NOW_IST} WHERE id = ?",
        (room_id,),
    )


def _system_message(conn: sqlite3.Connection, room_id: str, content: str) -> None:
    conn.execute(
        "INSERT INTO messages (room_id, author, content, type) VALUES (?, ?, ?, ?)",
        (room_id, "System", content, "system"),
    )
    _touch_room(conn, room_id)


def get_room_by_code(conn: sqlite3.Connection, code: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM rooms WHERE code = ? COLLATE NOCASE",
        (code.upper(),),
    ).fetchone()
    return _row_dict(row)


def _compute_split(expenses: list[dict], member_names: list[str]) -> dict[str, Any]:
    total = sum(e["amount"] for e in expenses)
    per_person = total / len(member_names) if member_names else 0
    paid_map: dict[str, float] = {}
    for e in expenses:
        paid_map[e["paid_by"]] = paid_map.get(e["paid_by"], 0) + e["amount"]
    balances = []
    for name in member_names:
        paid = paid_map.get(name, 0)
        balances.append({"name": name, "paid": round(paid, 2), "owes": round(per_person - paid, 2)})
    return {
        "total": round(total, 2),
        "perPerson": round(per_person, 2),
        "memberCount": len(member_names),
        "balances": balances,
        "settleUp": compute_settle_up(balances),
    }


def build_room_payload(conn: sqlite3.Connection, room: dict[str, Any]) -> dict[str, Any]:
    room_id = room["id"]
    members = [dict(r) for r in conn.execute(
        """SELECT name, joined_at, COALESCE(status, 'here') as status, block,
                  eta_minutes, COALESCE(needs_pickup, 0) as needs_pickup
           FROM members WHERE room_id = ? ORDER BY joined_at""",
        (room_id,),
    ).fetchall()]
    messages = [dict(r) for r in conn.execute(
        "SELECT * FROM messages WHERE room_id = ? ORDER BY created_at ASC",
        (room_id,),
    ).fetchall()]
    checklist = [dict(r) for r in conn.execute(
        "SELECT * FROM checklist WHERE room_id = ? ORDER BY created_at ASC",
        (room_id,),
    ).fetchall()]
    expenses = [dict(r) for r in conn.execute(
        "SELECT * FROM expenses WHERE room_id = ? ORDER BY created_at ASC",
        (room_id,),
    ).fetchall()]

    total = sum(e["amount"] for e in expenses)
    per_person = total / len(members) if members else 0
    paid_map: dict[str, float] = {}
    for e in expenses:
        paid_map[e["paid_by"]] = paid_map.get(e["paid_by"], 0) + e["amount"]

    balances = []
    for m in members:
        paid = paid_map.get(m["name"], 0)
        balances.append(
            {
                "name": m["name"],
                "paid": round(paid, 2),
                "owes": round(per_person - paid, 2),
            }
        )

    attendee_names = [m["name"] for m in members if m.get("status") == "here"]
    all_names = [m["name"] for m in members]
    split_attendees = _compute_split(expenses, attendee_names)
    settle_rows = conn.execute(
        "SELECT from_name, to_name, amount, paid FROM settlement_paid WHERE room_id = ?",
        (room_id,),
    ).fetchall()
    paid_set = {(r["from_name"], r["to_name"], round(r["amount"], 2)) for r in settle_rows if r["paid"]}
    settle_up = []
    for t in compute_settle_up(balances):
        key = (t["from"], t["to"], round(t["amount"], 2))
        settle_up.append({**t, "paid": key in paid_set})

    music_queue = [dict(r) for r in conn.execute(
        "SELECT * FROM music_queue WHERE room_id = ? ORDER BY position ASC, id ASC",
        (room_id,),
    ).fetchall()]

    last_msg = conn.execute(
        "SELECT created_at FROM messages WHERE room_id = ? ORDER BY created_at DESC LIMIT 1",
        (room_id,),
    ).fetchone()

    return {
        **room,
        "code": room["code"].upper(),
        "vibe_tags": parse_vibe_tags(room.get("vibe_tags")),
        "has_pin": bool(room.get("join_pin")),
        "join_mode": room.get("join_mode") or "open",
        "invite_token": room.get("invite_token"),
        "is_archived": bool(room.get("archived_at")),
        "recap_text": room.get("recap_text"),
        "current_track_id": room.get("current_track_id"),
        "current_track_title": room.get("current_track_title"),
        "members": members,
        "messages": messages,
        "checklist": checklist,
        "expenses": expenses,
        "music_queue": music_queue,
        "last_message_at": last_msg["created_at"] if last_msg else None,
        "split": {
            "total": round(total, 2),
            "perPerson": round(per_person, 2),
            "memberCount": len(members),
            "balances": balances,
            "settleUp": settle_up,
        },
        "split_attendees": split_attendees,
    }


def list_rooms(vibe: str | None = None) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.*, COUNT(m.id) as member_count,
                      (SELECT COUNT(*) FROM messages msg WHERE msg.room_id = r.id AND msg.type = 'user') as message_count,
                      (SELECT MAX(created_at) FROM messages msg WHERE msg.room_id = r.id) as last_message_at
               FROM rooms r
               LEFT JOIN members m ON m.room_id = r.id
               WHERE r.archived_at IS NULL
               GROUP BY r.id
               ORDER BY COALESCE(r.last_activity_at, r.created_at) DESC
               LIMIT 50"""
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["code"] = d["code"].upper()
            d["vibe_tags"] = parse_vibe_tags(d.get("vibe_tags"))
            d["has_pin"] = bool(d.get("join_pin"))
            if vibe and vibe not in d["vibe_tags"]:
                continue
            result.append(d)
        return result


def list_all_rooms_admin() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.*, COUNT(m.id) as member_count,
                      (SELECT COUNT(*) FROM messages msg WHERE msg.room_id = r.id) as message_count,
                      (SELECT COUNT(*) FROM messages msg WHERE msg.room_id = r.id AND msg.type = 'user') as user_message_count
               FROM rooms r
               LEFT JOIN members m ON m.room_id = r.id
               GROUP BY r.id
               ORDER BY COALESCE(r.last_activity_at, r.created_at) DESC"""
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["code"] = d["code"].upper()
            d["vibe_tags"] = parse_vibe_tags(d.get("vibe_tags"))
            d["has_pin"] = bool(d.get("join_pin"))
            d["is_archived"] = bool(d.get("archived_at"))
            result.append(d)
        return result


def admin_get_room_chats() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rooms = list_all_rooms_admin()
        for room in rooms:
            msgs = conn.execute(
                """SELECT id, author, content, type, created_at FROM messages
                   WHERE room_id = ? ORDER BY created_at ASC""",
                (room["id"],),
            ).fetchall()
            room["messages"] = [dict(m) for m in msgs]
        return rooms


def admin_join_room(code: str, name: str) -> dict[str, Any]:
    """Join any room — bypasses PIN, capacity, and archived gate."""
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")

        room_id = room["id"]
        trimmed = name.strip()
        existing = conn.execute(
            "SELECT id FROM members WHERE room_id = ? AND name = ?",
            (room_id, trimmed),
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO members (room_id, name, status) VALUES (?, ?, ?)",
                (room_id, trimmed, "here"),
            )

        _touch_room(conn, room_id)
        room = get_room_by_code(conn, code)
        assert room
        return build_room_payload(conn, room)


def create_room(
    title: str,
    host_name: str,
    location: str | None = None,
    description: str | None = None,
    vibe_tags: list[str] | None = None,
    join_pin: str | None = None,
    scheduled_at: str | None = None,
    playlist_url: str | None = None,
    join_mode: str = "open",
    extra_checklist: list[str] | None = None,
) -> dict[str, Any]:
    tags = vibe_tags or []
    from nit_joint.helpers import checklist_for_vibes_and_size

    if join_mode == "pin" and not join_pin:
        raise ValueError("PIN required for PIN-only rooms")
    invite_token = str(uuid.uuid4())[:12] if join_mode == "invite" else None
    with get_conn() as conn:
        codes = {r[0] for r in conn.execute("SELECT code FROM rooms").fetchall()}
        room_id = str(uuid.uuid4())[:12]
        code = generate_code(codes)
        conn.execute(
            f"""INSERT INTO rooms (id, code, title, host_name, location, description, vibe_tags,
               join_pin, scheduled_at, playlist_url, join_mode, invite_token, last_activity_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {SQL_NOW_IST})""",
            (
                room_id,
                code,
                title.strip(),
                host_name.strip(),
                location,
                description,
                json.dumps(tags) if tags else None,
                join_pin,
                scheduled_at,
                playlist_url,
                join_mode,
                invite_token,
            ),
        )
        conn.execute(
            "INSERT INTO members (room_id, name, status) VALUES (?, ?, ?)",
            (room_id, host_name.strip(), "here"),
        )
        _system_message(conn, room_id, f"{host_name.strip()} opened the joint")
        items = checklist_for_vibes_and_size(tags, 1)
        if extra_checklist:
            items.extend(extra_checklist)
        seen_items: set[str] = set()
        for item in items:
            if item in seen_items:
                continue
            seen_items.add(item)
            conn.execute("INSERT INTO checklist (room_id, item) VALUES (?, ?)", (room_id, item))
        room = get_room_by_code(conn, code)
        assert room
        return build_room_payload(conn, room)


def get_room(code: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            return None
        return build_room_payload(conn, room)


def join_room(
    code: str,
    name: str,
    pin: str | None = None,
    block: str | None = None,
    invite_token: str | None = None,
    member_pin: str | None = None,
) -> dict[str, Any]:
    _check_banned(name)
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        if room.get("archived_at"):
            raise ValueError("This sesh is wrapped up")

        join_mode = room.get("join_mode") or "open"
        if join_mode == "pin" or room.get("join_pin"):
            if room.get("join_pin") and room["join_pin"] != (pin or "").strip():
                raise ValueError("Wrong PIN")
        if join_mode == "crew_only":
            crew_row = conn.execute(
                "SELECT 1 FROM trusted_crew WHERE lower(name) = lower(?)",
                (name.strip(),),
            ).fetchone()
            if not crew_row:
                raise ValueError("Trusted crew only — ask the host to add you")
        if join_mode == "invite":
            token = (invite_token or "").strip()
            if not token or token != (room.get("invite_token") or ""):
                raise ValueError("Valid invite link required")

        pin_row = conn.execute(
            "SELECT pin FROM user_pins WHERE lower(name) = lower(?)",
            (name.strip(),),
        ).fetchone()
        if pin_row and pin_row["pin"] != (member_pin or "").strip():
            raise ValueError("Wrong member PIN for this name")

        room_id = room["id"]
        trimmed = name.strip()
        existing = conn.execute(
            "SELECT id FROM members WHERE room_id = ? AND name = ?",
            (room_id, trimmed),
        ).fetchone()

        if not existing:
            count = conn.execute(
                "SELECT COUNT(*) FROM members WHERE room_id = ?",
                (room_id,),
            ).fetchone()[0]
            if count >= room["max_capacity"]:
                raise ValueError("Room is full")
            conn.execute(
                "INSERT INTO members (room_id, name, status, block) VALUES (?, ?, ?, ?)",
                (room_id, trimmed, "here", block),
            )
            _system_message(conn, room_id, f"{trimmed} slid into the joint")

        _touch_room(conn, room_id)
        room = get_room_by_code(conn, code)
        assert room
        return build_room_payload(conn, room)


def post_message(code: str, author: str, content: str) -> None:
    _check_banned(author)
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        if room.get("archived_at"):
            raise ValueError("This sesh is wrapped up — read only")
        conn.execute(
            "INSERT INTO messages (room_id, author, content, type) VALUES (?, ?, ?, ?)",
            (room["id"], author.strip(), content.strip(), "user"),
        )
        _touch_room(conn, room["id"])


def update_status(code: str, name: str, status: str, eta_minutes: int | None = None, needs_pickup: bool | None = None) -> None:
    labels = {
        "on_my_way": "is on the way 🚶",
        "here": "pulled up ✅",
        "running_late": "is running late ⏰",
    }
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot update status")
        pickup_val = None
        if needs_pickup is not None:
            pickup_val = 1 if needs_pickup else 0
        conn.execute(
            """UPDATE members SET status = ?,
               eta_minutes = COALESCE(?, eta_minutes),
               needs_pickup = COALESCE(?, needs_pickup)
               WHERE room_id = ? AND name = ?""",
            (status, eta_minutes, pickup_val, room["id"], name.strip()),
        )
        msg = f"{name.strip()} {labels[status]}"
        if eta_minutes is not None and status == "on_my_way":
            msg += f" · ETA {eta_minutes}m"
        if needs_pickup:
            msg += " · needs pickup 🚪"
        _system_message(conn, room["id"], msg)


def claim_checklist(code: str, item_id: int, claimed_by: str | None) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot update checklist")
        existing = conn.execute("SELECT * FROM checklist WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise ValueError("Item not found")
        item = dict(existing)
        prev = item.get("claimed_by")
        conn.execute(
            "UPDATE checklist SET claimed_by = ? WHERE id = ? AND room_id = ?",
            (claimed_by, item_id, room["id"]),
        )
        if claimed_by and prev and claimed_by != prev:
            _system_message(conn, room["id"], f"{item['item']} reassigned from {prev} to {claimed_by}")
        elif claimed_by and not prev:
            _system_message(conn, room["id"], f"{claimed_by} claimed {item['item']} on the run sheet")
        elif not claimed_by and prev:
            _system_message(conn, room["id"], f"{prev} unclaimed {item['item']}")


def delete_checklist_item(code: str, item_id: int, actor: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot delete item")
        existing = conn.execute(
            "SELECT * FROM checklist WHERE id = ? AND room_id = ?",
            (item_id, room["id"]),
        ).fetchone()
        if not existing:
            raise ValueError("Item not found")
        item = dict(existing)
        conn.execute("DELETE FROM checklist WHERE id = ? AND room_id = ?", (item_id, room["id"]))
        who = item.get("claimed_by")
        suffix = f" (was {who})" if who else ""
        _system_message(conn, room["id"], f"{actor.strip()} removed {item['item']}{suffix} from the run sheet")


def add_checklist_item(code: str, item: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot add item")
        conn.execute("INSERT INTO checklist (room_id, item) VALUES (?, ?)", (room["id"], item.strip()))
        _system_message(conn, room["id"], f"Added to run sheet: {item.strip()}")


def add_expense(
    code: str,
    description: str,
    amount: float,
    paid_by: str,
    receipt_data: str | None = None,
) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot add expense")
        conn.execute(
            "INSERT INTO expenses (room_id, description, amount, paid_by, receipt_data) VALUES (?, ?, ?, ?, ?)",
            (room["id"], description.strip(), amount, paid_by.strip(), receipt_data),
        )
        _system_message(
            conn,
            room["id"],
            f"{paid_by.strip()} logged ₹{round(amount)} for {description.strip()}",
        )


def delete_expense(code: str, expense_id: int) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot delete expense")
        conn.execute("DELETE FROM expenses WHERE id = ? AND room_id = ?", (expense_id, room["id"]))


def update_playlist(code: str, url: str | None) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot update playlist")
        conn.execute("UPDATE rooms SET playlist_url = ? WHERE id = ?", (url, room["id"]))
        if url:
            _system_message(conn, room["id"], "Playlist link updated 🎵")


def close_session(
    code: str,
    actor_name: str,
    *,
    delete: bool = False,
    as_admin: bool = False,
) -> str | None:
    """Archive (wrap up) or permanently delete a sesh. Host or admin only."""
    from nit_joint.recap import build_recap

    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")

        is_host_actor = room["host_name"].strip().lower() == actor_name.strip().lower()
        if not is_host_actor and not as_admin:
            raise ValueError("Only the host or admin can end this sesh")

        payload = build_room_payload(conn, room)
        recap = build_recap(payload)
        actor = actor_name.strip() or "Admin"

        if delete:
            conn.execute("DELETE FROM rooms WHERE id = ?", (room["id"],))
            _audit(conn, "delete_sesh", actor, code, "admin" if as_admin else "host")
            return recap

        if room.get("archived_at"):
            raise ValueError("Sesh is already wrapped up")

        conn.execute(
            f"UPDATE rooms SET archived_at = {SQL_NOW_IST}, recap_text = ? WHERE id = ?",
            (recap, room["id"]),
        )
        who = "Admin" if as_admin and not is_host_actor else actor
        _system_message(conn, room["id"], f"{who} wrapped up the sesh — read-only for 24h")
        _audit(conn, "archive_sesh", actor, code, "admin" if as_admin else "host")
        return recap


def end_room(code: str, actor_name: str, permanent: bool = False) -> str | None:
    return close_session(code, actor_name, delete=permanent, as_admin=False)


def transfer_host(code: str, actor_name: str, new_host: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot transfer host")
        if room["host_name"].strip().lower() != actor_name.strip().lower():
            raise ValueError("Only the host can transfer")
        member = conn.execute(
            "SELECT id FROM members WHERE room_id = ? AND name = ?",
            (room["id"], new_host.strip()),
        ).fetchone()
        if not member:
            raise ValueError("New host must be in the room")
        conn.execute("UPDATE rooms SET host_name = ? WHERE id = ?", (new_host.strip(), room["id"]))
        _system_message(conn, room["id"], f"{actor_name.strip()} passed host to {new_host.strip()} 👑")


def list_sellers() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM sellers ORDER BY available DESC, updated_at DESC"
        ).fetchall()
        return [
            {
                **dict(r),
                "available": bool(r["available"]),
            }
            for r in rows
        ]


def register_seller(name: str, block: str | None, contact: str | None, available: bool, note: str | None) -> None:
    with get_conn() as conn:
        existing = conn.execute("SELECT id FROM sellers WHERE name = ?", (name.strip(),)).fetchone()
        if existing:
            raise ValueError("Seller already listed")
        stocked = _now_iso() if available else None
        conn.execute(
            f"""INSERT INTO sellers (name, block, contact, available, note, stocked_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, {SQL_NOW_IST})""",
            (name.strip(), block, contact, int(available), note, stocked),
        )


def update_seller(
    seller_id: int,
    actor_name: str,
    available: bool | None = None,
    note: str | None = None,
    block: str | None = None,
) -> None:
    with get_conn() as conn:
        seller = conn.execute("SELECT * FROM sellers WHERE id = ?", (seller_id,)).fetchone()
        if not seller:
            raise ValueError("Seller not found")
        if seller["name"].lower() != actor_name.strip().lower():
            raise ValueError("You can only update your own listing")
        stocked = _now_iso() if available is True else (None if available is False else seller["stocked_at"])
        avail = int(available) if available is not None else seller["available"]
        conn.execute(
            f"""UPDATE sellers SET block = COALESCE(?, block), available = ?, note = COALESCE(?, note),
               stocked_at = ?, updated_at = {SQL_NOW_IST} WHERE id = ?""",
            (block, avail, note, stocked, seller_id),
        )


def delete_seller(seller_id: int, actor_name: str) -> None:
    with get_conn() as conn:
        seller = conn.execute("SELECT * FROM sellers WHERE id = ?", (seller_id,)).fetchone()
        if not seller:
            raise ValueError("Seller not found")
        if seller["name"].lower() != actor_name.strip().lower():
            raise ValueError("You can only remove your own listing")
        conn.execute("DELETE FROM sellers WHERE id = ?", (seller_id,))


def set_user_pin(name: str, pin: str) -> None:
    if not pin or len(pin) < 4:
        raise ValueError("PIN must be at least 4 characters")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_pins (name, pin) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET pin = excluded.pin",
            (name.strip(), pin.strip()),
        )


def has_user_pin(name: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM user_pins WHERE lower(name) = lower(?)",
            (name.strip(),),
        ).fetchone()
        return row is not None


def add_music_queue(code: str, video_id: str, title: str, channel: str, added_by: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot update queue")
        pos = conn.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 FROM music_queue WHERE room_id = ?",
            (room["id"],),
        ).fetchone()[0]
        conn.execute(
            """INSERT INTO music_queue (room_id, video_id, title, channel, added_by, position)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (room["id"], video_id, title, channel, added_by.strip(), pos),
        )
        if not room.get("current_track_id"):
            conn.execute(
                "UPDATE rooms SET current_track_id = ?, current_track_title = ? WHERE id = ?",
                (video_id, title, room["id"]),
            )
        _system_message(conn, room["id"], f"{added_by.strip()} queued {title} 🎵")


def remove_music_queue_item(code: str, item_id: int) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        conn.execute("DELETE FROM music_queue WHERE id = ? AND room_id = ?", (item_id, room["id"]))


def play_next_track(code: str) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        current = room.get("current_track_id")
        if current:
            conn.execute(
                "DELETE FROM music_queue WHERE room_id = ? AND video_id = ?",
                (room["id"], current),
            )
        nxt = conn.execute(
            "SELECT video_id, title FROM music_queue WHERE room_id = ? ORDER BY position ASC, id ASC LIMIT 1",
            (room["id"],),
        ).fetchone()
        if nxt:
            conn.execute(
                "UPDATE rooms SET current_track_id = ?, current_track_title = ? WHERE id = ?",
                (nxt["video_id"], nxt["title"], room["id"]),
            )
        else:
            conn.execute(
                "UPDATE rooms SET current_track_id = NULL, current_track_title = NULL WHERE id = ?",
                (room["id"],),
            )


def set_now_playing(code: str, video_id: str | None, title: str | None) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot update player")
        conn.execute(
            "UPDATE rooms SET current_track_id = ?, current_track_title = ? WHERE id = ?",
            (video_id or None, title or None, room["id"]),
        )


def mark_settlement_paid(code: str, from_name: str, to_name: str, amount: float, paid: bool = True) -> None:
    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room:
            raise ValueError("Room not found")
        conn.execute(
            """INSERT INTO settlement_paid (room_id, from_name, to_name, amount, paid)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(room_id, from_name, to_name, amount)
               DO UPDATE SET paid = excluded.paid""",
            (room["id"], from_name, to_name, amount, int(paid)),
        )


def refresh_checklist_suggestions(code: str) -> None:
    from nit_joint.helpers import checklist_for_vibes_and_size

    with get_conn() as conn:
        room = get_room_by_code(conn, code)
        if not room or room.get("archived_at"):
            raise ValueError("Cannot refresh checklist")
        count = conn.execute(
            "SELECT COUNT(*) FROM members WHERE room_id = ?",
            (room["id"],),
        ).fetchone()[0]
        tags = parse_vibe_tags(room.get("vibe_tags"))
        existing = {
            r["item"]
            for r in conn.execute("SELECT item FROM checklist WHERE room_id = ?", (room["id"],)).fetchall()
        }
        for item in checklist_for_vibes_and_size(tags, count):
            if item not in existing:
                conn.execute("INSERT INTO checklist (room_id, item) VALUES (?, ?)", (room["id"], item))
        _system_message(conn, room["id"], "Grab list refreshed for crew size 🛒")


def reassign_checklist(code: str, item_id: int, new_person: str | None) -> None:
    claim_checklist(code, item_id, new_person)
