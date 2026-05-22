from __future__ import annotations

import os


def get_admin_passwords() -> list[str]:
    passwords: list[str] = []
    try:
        import streamlit as st

        if "admin" in st.secrets:
            admin = st.secrets["admin"]
            if "password" in admin:
                passwords.append(str(admin["password"]))
            if "passwords" in admin:
                raw = admin["passwords"]
                if isinstance(raw, str):
                    passwords.extend(p.strip() for p in raw.split(",") if p.strip())
                elif isinstance(raw, list):
                    passwords.extend(str(p) for p in raw)
    except Exception:
        pass
    env = os.environ.get("NIT_JOINT_ADMIN_PASSWORD", "")
    if env:
        passwords.extend(p.strip() for p in env.split(",") if p.strip())
    return list(dict.fromkeys(passwords))


def get_admin_password() -> str:
    pwds = get_admin_passwords()
    return pwds[0] if pwds else ""


def verify_admin_password(password: str) -> bool:
    expected = get_admin_passwords()
    if not expected:
        return False
    return password in expected


def is_admin() -> bool:
    try:
        import streamlit as st

        return bool(st.session_state.get("is_admin"))
    except Exception:
        return False
