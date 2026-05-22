"""YouTube helpers — search + video ID parsing."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

_SEARCH_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_VIDEO_ID_RE = re.compile(r"^[\w-]{11}$")


def extract_video_id(value: str) -> str | None:
    """Return a YouTube video ID from a URL, ID, or search-like string."""
    value = value.strip()
    if not value:
        return None
    if _VIDEO_ID_RE.fullmatch(value):
        return value

    if value.startswith("http"):
        parsed = urlparse(value)
        host = parsed.netloc.lower().removeprefix("www.")
        if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
            if parsed.path == "/watch":
                vid = parse_qs(parsed.query).get("v", [None])[0]
                return vid if vid and _VIDEO_ID_RE.fullmatch(vid) else None
            if parsed.path.startswith("/embed/"):
                vid = parsed.path.split("/embed/", 1)[1].split("/")[0]
                return vid if _VIDEO_ID_RE.fullmatch(vid) else None
            if parsed.path.startswith("/shorts/"):
                vid = parsed.path.split("/shorts/", 1)[1].split("/")[0]
                return vid if _VIDEO_ID_RE.fullmatch(vid) else None
        if host == "youtu.be":
            vid = parsed.path.lstrip("/").split("/")[0]
            return vid if _VIDEO_ID_RE.fullmatch(vid) else None
    return None


def watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def normalize_api_key(api_key: str | None) -> str | None:
    """Reject missing/placeholder keys (e.g. str(None) -> 'None')."""
    if api_key is None:
        return None
    key = str(api_key).strip()
    if not key or key.lower() in {"none", "null", "undefined"}:
        return None
    return key


def search_music(query: str, *, max_results: int = 8, api_key: str | None = None) -> list[dict[str, Any]]:
    """Search YouTube for music videos."""
    query = query.strip()
    if not query:
        return []

    direct_id = extract_video_id(query)
    if direct_id:
        return [_video_stub(direct_id, title=query, channel="YouTube link")]

    api_key = normalize_api_key(api_key)
    if api_key:
        try:
            api_results = _search_via_api(query, max_results=max_results, api_key=api_key)
            if api_results:
                return api_results
        except requests.RequestException:
            pass

    return _search_via_html(query, max_results=max_results)


def _video_stub(video_id: str, *, title: str, channel: str = "", duration: str = "") -> dict[str, Any]:
    return {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "duration": duration,
    }


def _search_via_api(query: str, *, max_results: int, api_key: str) -> list[dict[str, Any]]:
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "part": "snippet",
            "type": "video",
            "videoCategoryId": "10",
            "q": query,
            "maxResults": max_results,
            "key": api_key,
        },
        timeout=12,
    )
    resp.raise_for_status()
    payload = resp.json()
    results: list[dict[str, Any]] = []
    for item in payload.get("items", []):
        vid = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if not vid:
            continue
        results.append(
            _video_stub(
                vid,
                title=snippet.get("title") or "Untitled",
                channel=snippet.get("channelTitle") or "",
            )
        )
    return results


def _search_via_html(query: str, *, max_results: int) -> list[dict[str, Any]]:
    url = "https://www.youtube.com/results?search_query=" + requests.utils.quote(query)
    resp = requests.get(url, headers=_SEARCH_HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text

    match = re.search(r"var ytInitialData = ({.*?});</script>", html)
    if not match:
        return _search_via_regex(html, max_results=max_results)

    data = json.loads(match.group(1))
    contents = (
        data.get("contents", {})
        .get("twoColumnSearchResultsRenderer", {})
        .get("primaryContents", {})
        .get("sectionListRenderer", {})
        .get("contents", [])
    )

    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for section in contents:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            renderer = item.get("videoRenderer")
            if not renderer:
                continue
            vid = renderer.get("videoId")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            title_runs = renderer.get("title", {}).get("runs", [])
            channel_runs = renderer.get("ownerText", {}).get("runs", [])
            results.append(
                _video_stub(
                    vid,
                    title=title_runs[0]["text"] if title_runs else "Untitled",
                    channel=channel_runs[0]["text"] if channel_runs else "",
                    duration=renderer.get("lengthText", {}).get("simpleText", ""),
                )
            )
            if len(results) >= max_results:
                return results
    return results


def _search_via_regex(html: str, *, max_results: int) -> list[dict[str, Any]]:
    ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for vid in ids:
        if vid in seen:
            continue
        seen.add(vid)
        results.append(_video_stub(vid, title="YouTube result"))
        if len(results) >= max_results:
            break
    return results
