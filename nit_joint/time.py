from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

SQL_NOW_IST = "datetime('now', '+5 hours', '+30 minutes')"


def now_ist() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")


def parse_stored_time(value: str) -> datetime:
    if "T" in value:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=IST)
        return dt
    return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)


def now_ist_dt() -> datetime:
    return datetime.now(IST)


def format_time_ist(value: str | None) -> str:
    if not value:
        return ""
    dt = parse_stored_time(value)
    return dt.astimezone(IST).strftime("%d %b, %I:%M %p IST")
