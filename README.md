# NIT-JOINT

Private friends-group app for coordinating college seshes — rooms, chat, grab lists, expense splits, plugs, and shared music.

**Primary UI:** Python 3.10+ · [Streamlit](https://streamlit.io) · SQLite (optional Postgres via `DATABASE_URL`)

> The legacy React + Express app in `src/` and `server/` is archived — use **`streamlit_app.py`** for deployment.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and set your admin password.

## Deploy on Streamlit Cloud

1. Push to GitHub
2. [share.streamlit.io](https://share.streamlit.io) → connect repo
3. Main file: `streamlit_app.py`
4. Add secrets (see example file)
5. Set `DATABASE_URL` to hosted Postgres for persistent data

## Features

| Area | What's included |
|------|-----------------|
| **Rooms** | Create/join, PIN / crew-only / invite-link modes, vibe templates with presets, scheduling picker |
| **Chat** | Bubble UI, live refresh, toast alerts |
| **Grab list** | Vibe + headcount suggestions, claim / unclaim / reassign, refresh for crew size |
| **The tab** | Split all vs attendees-only, mark UPI paid, export & WhatsApp share |
| **Entertainment** | Shared room music queue — search, queue, play next |
| **Playlist** | Host sets Spotify/YouTube playlist link per room |
| **Pull-up board** | Status + ETA + pickup flag |
| **Plugs** | Stocked board, WhatsApp contact, block watch, auto-dry after 6h |
| **Identity** | Optional member PIN per name |
| **Recap** | Auto-generated post-sesh summary on wrap-up |
| **Onboarding** | First-run wizard (name → crew → sesh) |
| **PWA** | Add to home screen + manifest |
| **Admin** | All chats, kick/ban, audit log, force-end |
| **Bot** | Optional Telegram bot (`python -m nit_joint.bot`) |

## Deep links

```
https://your-app.streamlit.app/?room=ABC123
https://your-app.streamlit.app/?room=ABC123&invite=TOKEN   # invite-only rooms
```

## Secrets

```toml
[admin]
password = "your-strong-password"

APP_URL = "https://nitjoint.streamlit.app"

# Optional
# DATABASE_URL = "postgresql://..."
# YOUTUBE_API_KEY = "..."
```

## Project layout

```
streamlit_app.py       # Main UI entry
nit_joint/
  db.py                # Database + business logic
  room_views.py        # Room tabs (chat, grab, tab, entertainment)
  ui.py                # Premium theme + PWA hooks
  scheduling.py        # Date/time picker
  recap.py             # Post-sesh recap
  youtube.py           # Music search
  templates.py         # Sesh templates with presets
static/
  manifest.json        # PWA manifest
```
