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
</style>
"""


def inject_css() -> str:
    return CUSTOM_CSS


PWA_TIP = """
**Add to Home Screen (mobile)**
1. Open this app in Chrome/Safari
2. Tap **Share** → **Add to Home Screen**
3. Open NIT-JOINT like a native app
"""
