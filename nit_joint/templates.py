from __future__ import annotations

import urllib.parse

from nit_joint.constants import VIBE_TAGS

SESH_TEMPLATES: dict[str, dict] = {
    "Chill sesh": {
        "title": "Chill sesh",
        "vibe_tags": ["Chill"],
        "description": "Low-key hang — bring vibes",
    },
    "Pre-game": {
        "title": "Pre-game",
        "vibe_tags": ["Pre-game"],
        "description": "Before we head out",
    },
    "Birthday rip": {
        "title": "Birthday rip",
        "vibe_tags": ["Birthday"],
        "description": "Cake + chaos",
    },
    "Movie night": {
        "title": "Movie night",
        "vibe_tags": ["Movie"],
        "description": "Projector / HDMI ready",
    },
    "Late night": {
        "title": "Late night",
        "vibe_tags": ["Late night"],
        "description": "After curfew energy",
    },
    "Exam break": {
        "title": "Exam break",
        "vibe_tags": ["Exam break"],
        "description": "Brains off, snacks on",
    },
}


def template_keys() -> list[str]:
    return list(SESH_TEMPLATES.keys())
