# NIT-JOINT

Private friends-group app for coordinating college seshes — rooms, chat, grab lists, expense splits, and campus seller board.

**Stack:** Python 3.10+ · [Streamlit](https://streamlit.io) · SQLite

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open the URL shown (usually `http://localhost:8501`).

## Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect the repo
3. Set **Main file path** to `streamlit_app.py`
4. Deploy

No Node.js or build step required.

### Deep links

Share a room directly:

```
https://your-app.streamlit.app/?room=ABC123
```

## Data

SQLite database: `data/nit-joint.db` (created automatically on first run).

> **Note:** On Streamlit Cloud, the filesystem may reset when the app reboots. For persistent production data, swap SQLite for a hosted DB (e.g. Supabase, PlanetScale) later.

## Project layout

```
streamlit_app.py    # Main UI (Streamlit Cloud entry point)
requirements.txt    # Python dependencies
nit_joint/
  db.py             # Database + business logic
  constants.py      # Blocks, vibes, presets
  helpers.py        # Utilities
data/               # SQLite file (gitignored)
```

## Legacy React app

The original React + Express frontend lives in `src/` and `server/`. It is no longer required for deployment — use the Streamlit app above.

```bash
npm run dev   # old stack (optional)
```
