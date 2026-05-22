from __future__ import annotations

SESH_TEMPLATES: dict[str, dict] = {
    "Chill sesh": {
        "title": "Chill sesh",
        "vibe_tags": ["Chill"],
        "description": "Low-key hang — bring vibes",
        "location_hint": "MBH A common room",
        "playlist_url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
        "extra_checklist": ["Speaker charged", "Comfort spot cleared"],
    },
    "Pre-game": {
        "title": "Pre-game",
        "vibe_tags": ["Pre-game"],
        "description": "Before we head out",
        "location_hint": "MBH B",
        "playlist_url": "https://www.youtube.com/watch?v=5yx6BWlEVcY",
        "extra_checklist": ["Ice", "Mixers", "Pre-drink snacks"],
    },
    "Birthday rip": {
        "title": "Birthday rip",
        "vibe_tags": ["Birthday"],
        "description": "Cake + chaos",
        "location_hint": "BH 6",
        "playlist_url": "https://www.youtube.com/watch?v=QH2-TGUlwu4",
        "extra_checklist": ["Cake", "Candles", "Decor / banner"],
    },
    "Movie night": {
        "title": "Movie night",
        "vibe_tags": ["Movie"],
        "description": "Projector / HDMI ready",
        "location_hint": "7E TV room",
        "playlist_url": "https://www.youtube.com/watch?v=1zyNq7Q4w2U",
        "extra_checklist": ["HDMI cable", "Blankets", "Popcorn"],
    },
    "Late night": {
        "title": "Late night",
        "vibe_tags": ["Late night"],
        "description": "After curfew energy",
        "location_hint": "MBH F",
        "playlist_url": "https://www.youtube.com/watch?v=lTRiuFIWV54",
        "extra_checklist": ["Quiet snacks", "Phone on silent reminder"],
        "join_mode": "crew_only",
    },
    "Exam break": {
        "title": "Exam break",
        "vibe_tags": ["Exam break"],
        "description": "Brains off, snacks on",
        "location_hint": "MBH A",
        "playlist_url": "https://www.youtube.com/watch?v=DWcJFNfaw9c",
        "extra_checklist": ["Coffee / energy", "Comfort food"],
    },
}


def template_keys() -> list[str]:
    return list(SESH_TEMPLATES.keys())
