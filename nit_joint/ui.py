"""NIT-JOINT — Premium UI: CSS + HTML helpers."""

import html
import re

_VIDEO_ID_RE = re.compile(r"^[\w-]{11}$")

# ---------------------------------------------------------------------------
# Google Font import + CSS Custom Properties
# ---------------------------------------------------------------------------

_FONT_IMPORT = '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap");'

# ---------------------------------------------------------------------------
# The mega CSS block — Apple / Samsung flagship aesthetic
# ---------------------------------------------------------------------------

CUSTOM_CSS = (
    "<style>"
    + _FONT_IMPORT
    + r"""

/* ===== 0. CSS VARIABLES ===== */
:root {
    --bg-primary: #0a0a0a;
    --bg-card: rgba(255,255,255,0.04);
    --bg-card-hover: rgba(255,255,255,0.07);
    --border-card: rgba(255,255,255,0.08);
    --border-card-hover: rgba(124,255,107,0.25);
    --text-primary: #f5f5f7;
    --text-secondary: #86868b;
    --text-tertiary: #6e6e73;
    --accent: #7CFF6B;
    --accent-dim: rgba(124,255,107,0.12);
    --accent-mid: rgba(124,255,107,0.25);
    --glow-purple: rgba(120,80,220,0.15);
    --glow-blue: rgba(40,100,255,0.10);
    --radius-sm: 12px;
    --radius-md: 20px;
    --radius-lg: 28px;
    --radius-pill: 999px;
    --glass-bg: rgba(18,16,30,0.65);
    --glass-border: rgba(255,255,255,0.08);
    --glass-blur: blur(24px);
    --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --transition: 0.3s cubic-bezier(.25,.8,.25,1);
}

/* ===== 1. ANTI-STREAMLIT FOUNDATION ===== */
/* Hide ALL Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer,
div[data-testid="stDecoration"], div[data-testid="stToolbar"],
.viewerBadge_container__r5tak, #stStatusWidget,
button[title="View app in Streamlit Community Cloud"],
div[data-testid="manage-app-button"],
div[data-testid="stAppDeployButton"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    position: absolute !important;
    pointer-events: none !important;
}

/* Edge-to-edge canvas */
.stApp {
    background: var(--bg-primary) !important;
    font-family: var(--font) !important;
}

section[data-testid="stMain"] > div.block-container {
    max-width: 100% !important;
    padding: 1rem 2.5rem 3rem 2.5rem !important;
}

@media (max-width: 768px) {
    section[data-testid="stMain"] > div.block-container {
        padding: 0.5rem 1rem 2rem 1rem !important;
    }
}

/* Background cosmic glow */
.stApp::before {
    content: '';
    position: fixed;
    top: -40%; left: -20%;
    width: 140%; height: 140%;
    background:
        radial-gradient(ellipse 600px 600px at 15% 20%, var(--glow-purple), transparent),
        radial-gradient(ellipse 500px 500px at 80% 60%, var(--glow-blue), transparent),
        radial-gradient(ellipse 400px 400px at 50% 80%, rgba(124,255,107,0.04), transparent);
    pointer-events: none;
    z-index: 0;
    animation: cosmicDrift 20s ease-in-out infinite alternate;
}
@keyframes cosmicDrift {
    0%   { transform: translate(0, 0) scale(1); }
    100% { transform: translate(30px, -20px) scale(1.05); }
}

/* ===== 2. TYPOGRAPHY ===== */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] {
    font-family: var(--font) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
}
h1, [data-testid="stHeading"] h1 { font-size: clamp(2.2rem, 5vw, 3.8rem) !important; }
h2, [data-testid="stHeading"] h2 { font-size: clamp(1.6rem, 3.5vw, 2.4rem) !important; }
h3, [data-testid="stHeading"] h3 { font-size: clamp(1.2rem, 2.5vw, 1.6rem) !important; }

p, span, label, div, li, td, th, input, textarea, select, button {
    font-family: var(--font) !important;
}

/* ===== 3. SIDEBAR — frosted glass panel ===== */
[data-testid="stSidebar"] {
    background: rgba(10,10,10,0.85) !important;
    backdrop-filter: var(--glass-blur) !important;
    -webkit-backdrop-filter: var(--glass-blur) !important;
    border-right: 1px solid var(--glass-border) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: transparent !important;
}

/* ===== 4. GLASSMORPHISM CARDS ===== */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    -webkit-backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.25rem !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: var(--border-card-hover) !important;
    box-shadow: 0 0 40px rgba(124,255,107,0.06), 0 8px 32px rgba(0,0,0,0.4) !important;
}

/* ===== 5. BUTTONS — pill-shaped, premium ===== */
.stButton > button,
button[data-testid="baseButton-secondary"],
button[data-testid="baseButton-primary"] {
    font-family: var(--font) !important;
    font-weight: 600 !important;
    border-radius: var(--radius-pill) !important;
    padding: 0.6rem 1.8rem !important;
    transition: all var(--transition) !important;
    letter-spacing: -0.01em !important;
    border: 1px solid var(--glass-border) !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
.stButton > button:hover,
button[data-testid="baseButton-secondary"]:hover {
    transform: scale(1.04) !important;
    background: var(--bg-card-hover) !important;
    border-color: var(--accent-mid) !important;
    box-shadow: 0 0 24px rgba(124,255,107,0.08) !important;
}

/* Primary CTA — glowing accent */
button[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    color: #0a0a0a !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(124,255,107,0.2) !important;
}
button[data-testid="baseButton-primary"]:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 36px rgba(124,255,107,0.35), 0 4px 20px rgba(0,0,0,0.3) !important;
}
button[data-testid="baseButton-primary"]:active {
    transform: scale(0.98) !important;
}

/* ===== 6. INPUTS — minimalist dark ===== */
input[data-testid="stTextInputRootElement"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
.stTextInput input, .stTextArea textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font) !important;
    transition: border-color var(--transition) !important;
    caret-color: var(--accent) !important;
}
div[data-baseweb="input"] input:focus,
div[data-baseweb="textarea"] textarea:focus,
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-mid) !important;
    box-shadow: 0 0 0 2px rgba(124,255,107,0.1) !important;
    outline: none !important;
}

/* Select / multiselect */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-sm) !important;
}

/* ===== 7. TABS — underline style ===== */
button[data-baseweb="tab"] {
    font-family: var(--font) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    color: var(--text-secondary) !important;
    border-radius: 0 !important;
    transition: color var(--transition) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: var(--accent) !important;
}

/* ===== 8. METRICS ===== */
[data-testid="stMetric"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.2rem !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font) !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    font-size: 2rem !important;
    color: var(--text-primary) !important;
}

/* ===== 9. EXPANDERS ===== */
details[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
}
details[data-testid="stExpander"] summary {
    font-weight: 600 !important;
}

/* ===== 10. TOAST / ALERTS ===== */
div[data-testid="stToast"] {
    background: var(--glass-bg) !important;
    backdrop-filter: var(--glass-blur) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
}

/* ===== 11. LINK BUTTONS (WhatsApp etc) ===== */
div[data-testid="column"] a[data-testid="stLinkButton"] {
    border-radius: var(--radius-pill) !important;
    border: 1px solid rgba(37,211,102,0.3) !important;
    background: rgba(37,211,102,0.08) !important;
    color: #eafff0 !important;
    font-weight: 600 !important;
    text-align: center !important;
    justify-content: center !important;
    transition: all var(--transition) !important;
}
div[data-testid="column"] a[data-testid="stLinkButton"]:hover {
    border-color: #25D366 !important;
    background: rgba(37,211,102,0.18) !important;
    transform: scale(1.04) !important;
}

/* ===== 12. RADIO PILLS (vibe filters) ===== */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    gap: 0.5rem !important;
    flex-wrap: wrap !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-pill) !important;
    padding: 0.35rem 1rem !important;
    margin: 0 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: all var(--transition) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.07) !important;
    border-color: var(--accent-mid) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: var(--accent-dim) !important;
    border-color: var(--accent-mid) !important;
    color: var(--accent) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

/* ===== 13. TOGGLE ===== */
div[data-testid="stToggle"] label span[data-testid="stToggleSwitch"] {
    transition: all var(--transition) !important;
}

/* ===== 14. SCROLLBAR ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* ===== 15. CUSTOM COMPONENT CLASSES ===== */

/* -- Hero section -- */
.nj-hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.nj-hero h1 {
    font-size: clamp(2.8rem, 7vw, 5rem) !important;
    font-weight: 900 !important;
    letter-spacing: -0.04em !important;
    background: linear-gradient(135deg, #f5f5f7 0%, #86868b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
    line-height: 1.05;
}
.nj-hero-sub {
    font-size: clamp(1rem, 2.5vw, 1.5rem);
    color: var(--text-secondary);
    font-weight: 400;
    letter-spacing: -0.01em;
    margin-bottom: 1.5rem;
}
.nj-hero-accent {
    color: var(--accent) !important;
    -webkit-text-fill-color: var(--accent) !important;
}

/* -- Video container (cinematic floating panel) -- */
.nj-video-wrap {
    max-width: 960px;
    margin: 0 auto 3rem;
    position: relative;
}
.nj-video-wrap::before {
    content: '';
    position: absolute;
    inset: -20px;
    background: radial-gradient(ellipse at center, rgba(124,255,107,0.08), transparent 70%);
    border-radius: 40px;
    z-index: 0;
    filter: blur(30px);
    animation: videoGlow 4s ease-in-out infinite alternate;
}
@keyframes videoGlow {
    0%   { opacity: 0.6; transform: scale(0.98); }
    100% { opacity: 1;   transform: scale(1.02); }
}
.nj-video-inner {
    position: relative;
    z-index: 1;
    padding-bottom: 56.25%; /* 16:9 */
    border-radius: 24px;
    overflow: hidden;
    background: #111;
    box-shadow:
        0 0 60px rgba(124,255,107,0.07),
        0 25px 80px rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.06);
}
.nj-video-inner iframe {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    border: none;
}

/* -- Feature cards (glassmorphism grid) -- */
.nj-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}
.nj-feature-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 2rem 1.5rem;
    transition: all var(--transition);
    position: relative;
    overflow: hidden;
}
.nj-feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-mid), transparent);
    opacity: 0;
    transition: opacity var(--transition);
}
.nj-feature-card:hover {
    border-color: var(--border-card-hover);
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 40px rgba(124,255,107,0.05);
}
.nj-feature-card:hover::before { opacity: 1; }
.nj-feature-icon {
    font-size: 2rem;
    margin-bottom: 0.75rem;
    display: block;
}
.nj-feature-card h3 {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem;
}
.nj-feature-card p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
}

/* -- Status card -- */
.nj-status-card {
    background: rgba(255,255,255,0.03);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    border: 1px solid var(--glass-border);
    margin-bottom: 6px;
    transition: all var(--transition);
}
.nj-status-card:hover {
    background: rgba(255,255,255,0.06);
    border-color: var(--accent-mid);
}

/* -- Code pill -- */
.nj-code-pill {
    display: inline-block;
    font-family: ui-monospace, 'Cascadia Code', 'SF Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--accent);
    background: var(--accent-dim);
    border: 1px solid var(--accent-mid);
    border-radius: var(--radius-pill);
    padding: 0.15rem 0.65rem;
    vertical-align: middle;
}
.nj-code-lg { font-size: 1rem; padding: 0.25rem 0.85rem; }
.nj-lock { opacity: 0.85; margin-left: 0.25rem; }

/* -- Sesh title -- */
.nj-sesh-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.35rem;
    line-height: 1.4;
    letter-spacing: -0.02em;
}

/* -- Music search results -- */
.nj-music-result {
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    transition: all var(--transition);
}
.nj-music-result:hover {
    border-color: var(--accent-mid);
    background: rgba(255,255,255,0.05);
}
.nj-music-title {
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.2rem;
}
.nj-music-meta {
    color: var(--text-secondary);
    font-size: 0.85rem;
}
.nj-now-playing {
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
}
.nj-now-playing strong {
    color: var(--accent);
}

/* -- Share strip -- */
.nj-share-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
    margin-top: 0.25rem;
}

/* -- Dividers -- */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
}

/* ===== 16. ANIMATIONS ===== */
.nj-fade-in {
    animation: njFadeIn 0.8s ease-out both;
}
@keyframes njFadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Staggered animation delays for feature cards */
.nj-feature-card:nth-child(1) { animation: njFadeIn 0.6s 0.1s ease-out both; }
.nj-feature-card:nth-child(2) { animation: njFadeIn 0.6s 0.2s ease-out both; }
.nj-feature-card:nth-child(3) { animation: njFadeIn 0.6s 0.3s ease-out both; }
.nj-feature-card:nth-child(4) { animation: njFadeIn 0.6s 0.4s ease-out both; }
.nj-feature-card:nth-child(5) { animation: njFadeIn 0.6s 0.5s ease-out both; }
.nj-feature-card:nth-child(6) { animation: njFadeIn 0.6s 0.6s ease-out both; }

/* ===== 17. CHAT INPUT ===== */
div[data-testid="stChatInput"] {
    background: transparent !important;
}
div[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: var(--radius-pill) !important;
    color: var(--text-primary) !important;
}

/* ===== 18. FORM SUBMIT ===== */
div[data-testid="stFormSubmitButton"] button {
    border-radius: var(--radius-pill) !important;
    font-weight: 700 !important;
}

/* ===== 19. MATERIAL ICONS FIX ===== */
/*
 * Streamlit renders Material icon names as visible text when the
 * Material Symbols font fails to load.  The actual DOM structure is:
 *   summary > span.eqw31fm2 > span.epifhcv2 > span[data-testid="stIconMaterial"]
 * We hide the icon span and use CSS arrows on the wrapper instead.
 */

/* ---- 19a. Nuke ALL Material-icon text spans globally ---- */
span[data-testid="stIconMaterial"] {
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    display: inline-block !important;
    line-height: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
}

/* ---- 19b. Expander chevrons ---- */
/* The wrapper span (class ~epifhcv2) that contains the hidden icon */
details[data-testid="stExpander"] summary span[data-testid="stIconMaterial"] {
    /* Already hidden above */
}
/* Use the grandparent wrapper of the icon to show a CSS chevron */
details[data-testid="stExpander"] summary > span:first-child > span:first-child {
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    width: 1.2rem !important;
    height: 1.2rem !important;
    flex-shrink: 0;
    position: relative !important;
    visibility: visible !important;
    overflow: visible !important;
}
details[data-testid="stExpander"] summary > span:first-child > span:first-child::after {
    content: '▸';
    font-size: 0.95rem;
    font-family: var(--font) !important;
    color: var(--text-secondary);
    visibility: visible !important;
    position: static !important;
    transition: transform var(--transition);
}
details[data-testid="stExpander"][open] summary > span:first-child > span:first-child::after {
    content: '▾';
}

/* ---- 19c. Sidebar collapse button (inside sidebar header) ---- */
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button {
    overflow: hidden !important;
}
/* The wrapper span in the sidebar close button */
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button > span:first-child {
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    width: 1.5rem !important;
    height: 1.5rem !important;
    position: relative !important;
    visibility: visible !important;
    overflow: visible !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button > span:first-child > span[data-testid="stIconMaterial"] {
    /* Already hidden by global rule */
}
/* We only want arrows on the sidebar header close button, not all buttons */
[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button > span:first-child::after {
    content: '◀';
    font-size: 0.9rem;
    font-family: var(--font) !important;
    color: var(--text-secondary);
    visibility: visible !important;
    position: static !important;
}
/* Collapsed sidebar open button */
[data-testid="stSidebarCollapsedControl"] button {
    overflow: hidden !important;
}
[data-testid="stSidebarCollapsedControl"] button > span:first-child {
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    width: 1.5rem !important;
    height: 1.5rem !important;
    position: relative !important;
    visibility: visible !important;
}
[data-testid="stSidebarCollapsedControl"] button > span:first-child::after {
    content: '▶';
    font-size: 0.9rem;
    font-family: var(--font) !important;
    color: var(--text-secondary);
    visibility: visible !important;
    position: static !important;
}

</style>"""
)

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def inject_css() -> str:
    """Return the full CSS block for injection."""
    return CUSTOM_CSS


def code_pill(code: str, *, large: bool = False) -> str:
    cls = "nj-code-pill nj-code-lg" if large else "nj-code-pill"
    return f'<span class="{cls}">{html.escape(code)}</span>'


def sesh_title(title: str, code: str, *, has_pin: bool = False) -> str:
    lock = ' <span class="nj-lock">🔒</span>' if has_pin else ""
    return f'<div class="nj-sesh-title">{html.escape(title)} {code_pill(code)}{lock}</div>'


def hero_section(
    title: str = "NIT-JOINT",
    subtitle: str = "Where the boys link up.",
    accent_word: str = "JOINT",
) -> str:
    """Cinematic hero header HTML — Apple keynote style."""
    # Split title to apply accent color to one word
    if accent_word and accent_word in title:
        parts = title.split(accent_word, 1)
        title_html = (
            f'{html.escape(parts[0])}'
            f'<span class="nj-hero-accent">{html.escape(accent_word)}</span>'
            f'{html.escape(parts[1])}'
        )
    else:
        title_html = html.escape(title)

    return f"""
    <div class="nj-hero nj-fade-in">
        <h1>{title_html}</h1>
        <p class="nj-hero-sub">{html.escape(subtitle)}</p>
    </div>
    """


def video_embed(
    youtube_url: str,
    *,
    autoplay: bool = False,
    controls: bool = True,
    loop: bool = False,
    muted: bool = False,
) -> str:
    """Cinematic floating-glass YouTube embed."""
    embed_url = youtube_url
    if "watch?v=" in youtube_url:
        vid_id = youtube_url.split("watch?v=")[1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{html.escape(vid_id)}"
    elif "youtu.be/" in youtube_url:
        vid_id = youtube_url.split("youtu.be/")[1].split("?")[0]
        embed_url = f"https://www.youtube.com/embed/{html.escape(vid_id)}"
    elif youtube_url.startswith("https://www.youtube.com/embed/"):
        embed_url = youtube_url
    elif _VIDEO_ID_RE.match(youtube_url.strip()):
        embed_url = f"https://www.youtube.com/embed/{html.escape(youtube_url.strip())}"

    params: list[str] = []
    if autoplay:
        params.append("autoplay=1")
    if controls:
        params.append("controls=1")
    else:
        params.append("controls=0")
    if loop:
        params.append("loop=1")
    if muted:
        params.append("mute=1")
    params.extend(["rel=0", "modestbranding=1"])

    sep = "&" if "?" in embed_url else "?"
    embed_url += sep + "&".join(params)

    return f"""
    <div class="nj-video-wrap nj-fade-in">
        <div class="nj-video-inner">
            <iframe
                src="{embed_url}"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowfullscreen
                loading="lazy"
            ></iframe>
        </div>
    </div>
    """


def music_player_embed(video_id: str, *, autoplay: bool = True) -> str:
    """YouTube player tuned for the Entertainment tab."""
    return video_embed(video_id, autoplay=autoplay, controls=True, loop=False, muted=False)


def feature_grid(features: list[dict]) -> str:
    """
    Glassmorphism feature cards grid.

    Each feature dict: {"icon": "🎯", "title": "...", "desc": "..."}
    """
    cards = ""
    for f in features:
        cards += f"""
        <div class="nj-feature-card">
            <span class="nj-feature-icon">{f.get('icon', '✦')}</span>
            <h3>{html.escape(f['title'])}</h3>
            <p>{html.escape(f['desc'])}</p>
        </div>
        """
    return f'<div class="nj-feature-grid">{cards}</div>'


PWA_TIP = """
**Add to Home Screen (mobile)**
1. Open this app in Chrome/Safari
2. Tap **Share** → **Add to Home Screen**
3. Open NIT-JOINT like a native app
"""
