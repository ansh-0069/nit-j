from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator


def get_database_url() -> str | None:
    try:
        import streamlit as st

        url = st.secrets.get("DATABASE_URL") or st.secrets.get("database", {}).get("url")
        if url:
            return str(url)
    except Exception:
        pass
    return os.environ.get("DATABASE_URL")


def using_postgres() -> bool:
    return bool(get_database_url())


@contextmanager
def pg_conn() -> Iterator[Any]:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = psycopg2.connect(get_database_url())
    conn.autocommit = False
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def pg_fetchall(conn: Any, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    from psycopg2.extras import RealDictCursor

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def pg_fetchone(conn: Any, sql: str, params: tuple = ()) -> dict[str, Any] | None:
    from psycopg2.extras import RealDictCursor

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None


def pg_execute(conn: Any, sql: str, params: tuple = ()) -> int:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.rowcount


def init_postgres() -> None:
    if not using_postgres():
        return
    ddl = """
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
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS members (
      id SERIAL PRIMARY KEY,
      room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
      name TEXT NOT NULL,
      status TEXT DEFAULT 'here',
      block TEXT,
      joined_at TIMESTAMP DEFAULT NOW(),
      UNIQUE(room_id, name)
    );
    CREATE TABLE IF NOT EXISTS messages (
      id SERIAL PRIMARY KEY,
      room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
      author TEXT NOT NULL,
      content TEXT NOT NULL,
      type TEXT DEFAULT 'user',
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS checklist (
      id SERIAL PRIMARY KEY,
      room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
      item TEXT NOT NULL,
      claimed_by TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS expenses (
      id SERIAL PRIMARY KEY,
      room_id TEXT NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
      description TEXT NOT NULL,
      amount REAL NOT NULL,
      paid_by TEXT NOT NULL,
      receipt_data TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS sellers (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      block TEXT,
      contact TEXT,
      available INTEGER DEFAULT 0,
      note TEXT,
      stocked_at TEXT,
      updated_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS audit_log (
      id SERIAL PRIMARY KEY,
      action TEXT NOT NULL,
      actor TEXT,
      target TEXT,
      detail TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS banned_names (
      name TEXT PRIMARY KEY,
      reason TEXT,
      banned_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS feedback (
      id SERIAL PRIMARY KEY,
      content TEXT NOT NULL,
      room_code TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS trusted_crew (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL UNIQUE,
      block TEXT
    );
    CREATE TABLE IF NOT EXISTS plug_watch (
      id SERIAL PRIMARY KEY,
      watcher_name TEXT NOT NULL,
      block TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT NOW(),
      UNIQUE(watcher_name, block)
    );
    """
    with pg_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
