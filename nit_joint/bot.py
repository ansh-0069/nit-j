#!/usr/bin/env python3
"""Optional Telegram bot — run separately: python -m nit_joint.bot

Set TELEGRAM_BOT_TOKEN in env or Streamlit secrets.
Commands: /stocked, /sesh CODE, /help
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("Set TELEGRAM_BOT_TOKEN to run the bot")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print("pip install requests")
        sys.exit(1)

    from nit_joint.db import get_room, init_db, list_sellers

    init_db()
    offset = 0
    print("NIT-JOINT bot running...")
    while True:
        resp = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=35,
        ).json()
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            text = (msg.get("text") or "").strip()
            chat = msg.get("chat", {}).get("id")
            if not text or not chat:
                continue
            reply = "Commands: /stocked · /sesh CODE · /help"
            if text.startswith("/help"):
                reply = "🌿 /stocked — who's good\n/sesh ABC123 — room info"
            elif text.startswith("/stocked"):
                sellers = [s for s in list_sellers() if s["available"]]
                if not sellers:
                    reply = "Nobody stocked rn 😮‍💨"
                else:
                    lines = [f"💨 {s['name']} ({s.get('block') or '?'})" for s in sellers]
                    reply = "Stocked:\n" + "\n".join(lines)
            elif text.startswith("/sesh"):
                parts = text.split()
                if len(parts) < 2:
                    reply = "Usage: /sesh ROOMCODE"
                else:
                    room = get_room(parts[1])
                    if not room:
                        reply = "Room not found"
                    else:
                        reply = f"🌿 {room['title']} ({room['code']})\n👥 {len(room['members'])} in · host {room['host_name']}"
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat, "text": reply},
            )


if __name__ == "__main__":
    main()
