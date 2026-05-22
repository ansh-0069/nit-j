from __future__ import annotations

import urllib.parse


def room_url(code: str, base: str | None = None, invite_token: str | None = None) -> str:
    path = f"/?room={code.upper()}"
    if invite_token:
        path += f"&invite={invite_token}"
    if base:
        return f"{base.rstrip('/')}{path}"
    return path


def build_invite_text(
    title: str,
    code: str,
    location: str | None = None,
    base: str | None = None,
    invite_token: str | None = None,
) -> str:
    loc = f" · {location}" if location else ""
    link = room_url(code, base, invite_token)
    if base and link.startswith("/"):
        link = base.rstrip("/") + link
    return f"🌿 NIT-JOINT: {title}{loc}\nCode: {code}\n{link}\nSlide in boys 👊"


def whatsapp_url(text: str) -> str:
    return f"https://wa.me/?text={urllib.parse.quote(text)}"


def contact_whatsapp_url(contact: str, message: str) -> str:
    digits = "".join(c for c in contact if c.isdigit())
    if digits.startswith("91") or len(digits) == 10:
        if len(digits) == 10:
            digits = "91" + digits
        return f"https://wa.me/{digits}?text={urllib.parse.quote(message)}"
    return whatsapp_url(message)


def upi_reminder(name: str, amount: float, room_title: str) -> str:
    return f"Bro {name}, you owe ₹{round(amount)} for {room_title} 🌿 — settle on UPI pls"


def build_recap_share_text(recap: str) -> str:
    return recap


def export_split_text(room_title: str, split: dict, *, attendees_only: bool = False) -> str:
    label = "attendees" if attendees_only else "everyone"
    lines = [
        f"💸 {room_title} — split ({label})",
        f"Total: ₹{split.get('total', 0):,.0f}",
        f"Per head: ₹{split.get('perPerson', 0):,.0f}",
        "",
    ]
    for t in split.get("settleUp") or []:
        paid = " ✅ paid" if t.get("paid") else ""
        lines.append(f"{t['from']} → {t['to']}: ₹{t['amount']:,.0f}{paid}")
    return "\n".join(lines)
