from __future__ import annotations

import json
import random
import string
from typing import Any

from nit_joint.constants import VIBE_CHECKLIST_PRESETS

CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code(existing_codes: set[str]) -> str:
    while True:
        code = "".join(random.choice(CODE_CHARS) for _ in range(6))
        if code not in existing_codes:
            return code


def parse_vibe_tags(raw: Any) -> list[str]:
    if not raw or not isinstance(raw, str):
        return []
    try:
        parsed = json.loads(raw)
        return [t for t in parsed if isinstance(t, str)] if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def checklist_for_vibes(vibe_tags: list[str]) -> list[str]:
    if not vibe_tags:
        return list(VIBE_CHECKLIST_PRESETS["Chill"])
    items: set[str] = set()
    for tag in vibe_tags:
        preset = VIBE_CHECKLIST_PRESETS.get(tag)
        if preset:
            items.update(preset)
    return list(items) if items else list(VIBE_CHECKLIST_PRESETS["Chill"])


def compute_settle_up(balances: list[dict[str, float | str]]) -> list[dict[str, Any]]:
    debtors = sorted(
        [{"name": b["name"], "amount": float(b["owes"])} for b in balances if float(b["owes"]) > 0.01],
        key=lambda x: x["amount"],
        reverse=True,
    )
    creditors = sorted(
        [{"name": b["name"], "amount": -float(b["owes"])} for b in balances if float(b["owes"]) < -0.01],
        key=lambda x: x["amount"],
        reverse=True,
    )
    result: list[dict[str, Any]] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        pay = min(debtors[i]["amount"], creditors[j]["amount"])
        if pay >= 0.01:
            result.append(
                {
                    "from": debtors[i]["name"],
                    "to": creditors[j]["name"],
                    "amount": round(pay, 2),
                }
            )
        debtors[i]["amount"] -= pay
        creditors[j]["amount"] -= pay
        if debtors[i]["amount"] < 0.01:
            i += 1
        if creditors[j]["amount"] < 0.01:
            j += 1
    return result


def names_match(a: str, b: str) -> bool:
    return a.strip().lower() == b.strip().lower()


from nit_joint.time import now_ist_dt, parse_stored_time


def get_countdown(scheduled_at: str | None) -> str | None:
    if not scheduled_at:
        return None

    try:
        target = parse_stored_time(scheduled_at)
    except ValueError:
        return None
    now = now_ist_dt()
    diff = (target - now).total_seconds()
    if diff <= 0:
        return "Live now"
    mins = int(diff // 60)
    hours = mins // 60
    if hours > 24:
        return f"In {hours // 24}d {hours % 24}h"
    if hours > 0:
        return f"In {hours}h {mins % 60}m"
    return f"In {mins}m"


def is_starting_soon(scheduled_at: str | None, within_minutes: int = 30) -> bool:
    if not scheduled_at:
        return False

    try:
        target = parse_stored_time(scheduled_at)
    except ValueError:
        return False
    diff = (target - now_ist_dt()).total_seconds()
    return 0 < diff <= within_minutes * 60
