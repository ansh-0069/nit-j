"""Scheduling helpers for sesh create forms."""

from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from nit_joint.time import IST


def schedule_picker(*, key_prefix: str = "sched") -> str | None:
    """Render date/time picker; return ISO scheduled_at or None."""
    choice = st.radio(
        "When",
        ["Tonight", "Tomorrow", "Pick date & time", "Not scheduled"],
        horizontal=True,
        key=f"{key_prefix}_when_choice",
    )
    now = datetime.now(IST)

    if choice == "Not scheduled":
        return None
    if choice == "Tonight":
        target = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target.isoformat()
    if choice == "Tomorrow":
        target = (now + timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        return target.isoformat()

    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("Date", value=now.date(), key=f"{key_prefix}_date")
    with col2:
        t = st.time_input("Time", value=now.replace(minute=0, second=0, microsecond=0).time(), key=f"{key_prefix}_time")
    target = datetime.combine(d, t, tzinfo=IST)
    return target.isoformat()
