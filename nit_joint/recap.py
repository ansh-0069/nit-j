"""Post-sesh recap generation."""

from __future__ import annotations

from typing import Any

from nit_joint.share import build_recap_share_text


def build_recap(room: dict[str, Any]) -> str:
    members = room.get("members") or []
    checklist = room.get("checklist") or []
    split = room.get("split") or {}
    expenses = room.get("expenses") or []

    here = [m["name"] for m in members if m.get("status") == "here"]
    claimed = [f"{i['item']} ({i['claimed_by']})" for i in checklist if i.get("claimed_by")]
    unclaimed = [i["item"] for i in checklist if not i.get("claimed_by")]

    lines = [
        f"🌿 {room['title']} — wrapped",
        f"Code: {room['code']}",
    ]
    if room.get("location"):
        lines.append(f"📍 {room['location']}")
    lines.append("")
    lines.append(f"👊 Pulled up ({len(here)}): {', '.join(here) if here else 'nobody logged here'}")
    lines.append("")
    lines.append(f"💸 Total: ₹{split.get('total', 0):,.0f} · Per head: ₹{split.get('perPerson', 0):,.0f}")
    if split.get("settleUp"):
        lines.append("Settle up:")
        for t in split["settleUp"]:
            lines.append(f"  • {t['from']} → {t['to']}: ₹{t['amount']:,.0f}")
    lines.append("")
    if expenses:
        lines.append("Logged:")
        for e in expenses:
            lines.append(f"  • {e['description']} ₹{e['amount']:,.0f} ({e['paid_by']})")
        lines.append("")
    if claimed:
        lines.append("✅ Grab list done:")
        for c in claimed:
            lines.append(f"  • {c}")
    if unclaimed:
        lines.append("⬜ Still open:")
        for u in unclaimed:
            lines.append(f"  • {u}")
    lines.append("")
    lines.append("Slide in next time 👊")
    return "\n".join(lines)


def recap_for_share(room: dict[str, Any]) -> str:
    return build_recap_share_text(build_recap(room))
