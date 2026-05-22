from __future__ import annotations

import json
from typing import Any

CREW_KEY = "trusted_crew"


def get_crew_from_session(session_state: Any) -> list[dict[str, str]]:
    raw = session_state.get(CREW_KEY, [])
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raw = []
    return [c for c in raw if isinstance(c, dict) and c.get("name")]


def save_crew_to_session(session_state: Any, crew: list[dict[str, str]]) -> None:
    session_state[CREW_KEY] = crew[:10]


def add_crew(session_state: Any, name: str, block: str | None = None) -> list[dict[str, str]]:
    crew = get_crew_from_session(session_state)
    crew = [c for c in crew if c["name"].lower() != name.strip().lower()]
    crew.insert(0, {"name": name.strip(), "block": (block or "").strip()})
    save_crew_to_session(session_state, crew)
    return get_crew_from_session(session_state)


def remove_crew(session_state: Any, name: str) -> list[dict[str, str]]:
    crew = [c for c in get_crew_from_session(session_state) if c["name"] != name]
    save_crew_to_session(session_state, crew)
    return crew


def crew_block(session_state: Any, name: str) -> str | None:
    for c in get_crew_from_session(session_state):
        if c["name"].lower() == name.strip().lower():
            b = c.get("block", "")
            return b if b else None
    return None
