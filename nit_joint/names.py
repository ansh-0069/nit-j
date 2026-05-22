"""Lightweight name helpers — no heavy imports."""

from __future__ import annotations


def names_match(a: str, b: str) -> bool:
    return a.strip().lower() == b.strip().lower()
