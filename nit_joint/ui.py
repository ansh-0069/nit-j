CUSTOM_CSS = """
<style>
    .stApp { background: linear-gradient(160deg, #07050f 0%, #12101f 45%, #0a0818 100%); }
    [data-testid="stSidebar"] { background: #0d0b18; border-right: 1px solid #7CFF6B22; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    .nj-badge { background: #7CFF6B18; border: 1px solid #7CFF6B55; border-radius: 999px;
                padding: 2px 10px; font-size: 0.75rem; color: #7CFF6B; }
    .nj-pulse { animation: nj-pulse 1.5s ease-in-out infinite; }
    @keyframes nj-pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
    .nj-status-card { background: #1a1830; border-radius: 12px; padding: 8px 12px;
                      border: 1px solid #ffffff11; margin-bottom: 6px; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #12101f !important;
        border: 1px solid #ffffff14 !important;
        border-radius: 16px !important;
        padding: 0.75rem 1rem !important;
    }
    .nj-sesh-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f4f2ff;
        margin-bottom: 0.35rem;
        line-height: 1.4;
    }
    .nj-code-pill {
        display: inline-block;
        font-family: ui-monospace, 'Cascadia Code', monospace;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #7CFF6B;
        background: #7CFF6B14;
        border: 1px solid #7CFF6B44;
        border-radius: 999px;
        padding: 0.15rem 0.65rem;
        vertical-align: middle;
    }
    .nj-code-lg { font-size: 1rem; padding: 0.25rem 0.85rem; }
    .nj-lock { opacity: 0.85; margin-left: 0.25rem; }
    .nj-meta { color: #9b97b8; font-size: 0.82rem; margin: 0.1rem 0 0.65rem; }
    .nj-share-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        margin-top: 0.25rem;
    }
    div[data-testid="column"] .stButton > button[kind="primary"],
    div[data-testid="column"] .stButton > button[data-testid="baseButton-primary"] {
        border-radius: 10px;
        font-weight: 600;
    }
    div[data-testid="column"] a[data-testid="stLinkButton"] {
        border-radius: 10px !important;
        border: 1px solid #25D36655 !important;
        background: #25D36618 !important;
        color: #eafff0 !important;
        font-weight: 600;
        text-align: center;
        justify-content: center;
    }
    div[data-testid="column"] a[data-testid="stLinkButton"]:hover {
        border-color: #25D366 !important;
        background: #25D36633 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 0.45rem;
        flex-wrap: wrap;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background: #16142a !important;
        border: 1px solid #ffffff18 !important;
        border-radius: 999px !important;
        padding: 0.3rem 0.85rem !important;
        margin: 0 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background: #7CFF6B22 !important;
        border-color: #7CFF6B55 !important;
        color: #7CFF6B !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
</style>
"""

import html


def inject_css() -> str:
    return CUSTOM_CSS


def code_pill(code: str, *, large: bool = False) -> str:
    cls = "nj-code-pill nj-code-lg" if large else "nj-code-pill"
    return f'<span class="{cls}">{html.escape(code)}</span>'


def sesh_title(title: str, code: str, *, has_pin: bool = False) -> str:
    lock = ' <span class="nj-lock">🔒</span>' if has_pin else ""
    return f'<div class="nj-sesh-title">{html.escape(title)} {code_pill(code)}{lock}</div>'


PWA_TIP = """
**Add to Home Screen (mobile)**
1. Open this app in Chrome/Safari
2. Tap **Share** → **Add to Home Screen**
3. Open NIT-JOINT like a native app
"""
