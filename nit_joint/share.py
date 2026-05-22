from __future__ import annotations

import urllib.parse


def room_url(code: str, base: str | None = None) -> str:
    if base:
        return f"{base.rstrip('/')}/?room={code.upper()}"
    return f"/?room={code.upper()}"


def build_invite_text(title: str, code: str, location: str | None = None, base: str | None = None) -> str:
    loc = f" · {location}" if location else ""
    link = room_url(code, base)
    if base and link.startswith("/"):
        link = base.rstrip("/") + link
    return f"🌿 NIT-JOINT: {title}{loc}\nCode: {code}\n{link}\nSlide in boys 👊"


def whatsapp_url(text: str) -> str:
    return f"https://wa.me/?text={urllib.parse.quote(text)}"


def upi_reminder(name: str, amount: float, room_title: str) -> str:
    return f"Bro {name}, you owe ₹{round(amount)} for {room_title} 🌿 — settle on UPI pls"
