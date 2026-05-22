# NIT-JOINT

Private friends-group app for coordinating college seshes — rooms, chat, grab lists, expense splits, and campus seller board.

**Stack:** Python 3.10+ · [Streamlit](https://streamlit.io) · SQLite (optional Postgres via `DATABASE_URL`)

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

## Features

| Area | What's included |
|------|-----------------|
| **Rooms** | Create/join, PIN, vibe templates, scheduled countdown, QR + WhatsApp share |
| **Chat** | Live refresh toggle, new-message toast, rate limits |
| **Grab list** | Vibe-based presets, claim items |
| **The tab** | Split + settle-up, UPI reminder copy, receipt photo upload |
| **Pull-up board** | On my way / here / running late status per member |
| **Plugs** | Seller board, stocked timestamps, block watch alerts |
| **Crew** | Trusted names + blocks in sidebar |
| **Admin** | All chats, join any room, kick/ban/delete, audit log, force-end |
| **Feedback** | Anonymous reports to admin |
| **Bot** | Optional Telegram bot (`python -m nit_joint.bot`) |

## Secrets

```toml
[admin]
password = "your-strong-password"
# passwords = "admin1-pass, admin2-pass"  # multi-admin

APP_URL = "https://nitjoint.streamlit.app"

# Optional persistent DB (Postgres — Supabase/Neon)
# DATABASE_URL = "postgresql://..."

# TELEGRAM_BOT_TOKEN = "..."
```

## Deep links

```
https://your-app.streamlit.app/?room=ABC123
```

## Data persistence

- **Local / default:** SQLite in `data/nit-joint.db`
- **Streamlit Cloud:** filesystem may reset — set `DATABASE_URL` to hosted Postgres for production
- Postgres schema auto-creates when `DATABASE_URL` is set (migration path; SQLite remains default for reads/writes unless fully migrated)

## Optional Telegram bot

```bash
export TELEGRAM_BOT_TOKEN=...
python -m nit_joint.bot
```

Commands: `/stocked`, `/sesh CODE`, `/help`

## Legacy React app

The original React + Express stack in `src/` and `server/` is optional — not needed for Streamlit deployment.

```bash
npm run dev
```

## Project layout

```
streamlit_app.py       # Main UI
nit_joint/
  db.py                # Database + business logic
  admin.py             # Multi-admin auth
  share.py             # WhatsApp / invite / UPI
  crew.py              # Trusted crew (session)
  templates.py         # Quick sesh templates
  ui.py                # Theme CSS
  bot.py               # Telegram bot (optional)
  postgres.py          # Optional Postgres init
```
