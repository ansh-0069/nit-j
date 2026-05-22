"""Shared navigation + session helpers for Streamlit pages."""

from __future__ import annotations

import streamlit as st

from nit_joint.admin import is_admin
from nit_joint.helpers import names_match


def init_session() -> None:
    defaults = {
        "user_name": "",
        "page": "home",
        "room_code": "",
        "vibe_filter": "All",
        "is_admin": False,
        "live_mode": True,
        "last_msg_counts": {},
        "plug_alerts_shown": set(),
        "trusted_crew": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def go_room(code: str) -> None:
    st.session_state.room_code = code.upper()
    st.session_state.page = "room"


def go(page: str) -> None:
    st.session_state.page = page


def user() -> str:
    return st.session_state.user_name.strip()


def app_base_url() -> str:
    try:
        url = st.secrets.get("APP_URL")
        if url:
            return str(url).rstrip("/")
    except Exception:
        pass
    return "https://nitjoint.streamlit.app"


def is_member(room: dict, name: str) -> bool:
    return any(names_match(m["name"], name) for m in room["members"])


def is_host(room: dict, name: str) -> bool:
    return names_match(room["host_name"], name)


def can_use_room(room: dict) -> bool:
    if is_admin():
        return True
    return bool(user()) and is_member(room, user())
