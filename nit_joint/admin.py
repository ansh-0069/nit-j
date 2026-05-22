from __future__ import annotations

import os


def get_admin_password() -> str:
    try:
        import streamlit as st

        return str(st.secrets["admin"]["password"])
    except Exception:
        return os.environ.get("NIT_JOINT_ADMIN_PASSWORD", "")


def verify_admin_password(password: str) -> bool:
    expected = get_admin_password()
    if not expected:
        return False
    return password == expected


def is_admin() -> bool:
    try:
        import streamlit as st

        return bool(st.session_state.get("is_admin"))
    except Exception:
        return False
