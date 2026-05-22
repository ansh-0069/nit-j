"""Room page rendering — tabs, chat, entertainment, expenses."""

from __future__ import annotations

import base64
import html

import streamlit as st

from nit_joint.app_state import app_base_url, go, go_room, is_host, is_member, user
from nit_joint.admin import is_admin
from nit_joint.constants import STATUS_LABELS
from nit_joint.crew import crew_block
from nit_joint.db import (
    add_checklist_item,
    add_expense,
    add_music_queue,
    admin_delete_message,
    admin_join_room,
    admin_kick_member,
    claim_checklist,
    close_session,
    delete_checklist_item,
    get_room,
    has_user_pin,
    join_room,
    mark_settlement_paid,
    play_next_track,
    post_message,
    refresh_checklist_suggestions,
    remove_music_queue_item,
    set_now_playing,
    transfer_host,
    update_playlist,
    update_status,
)
from nit_joint.helpers import grab_list_summary, names_match
from nit_joint.recap import recap_for_share
from nit_joint.share import build_invite_text, contact_whatsapp_url, export_split_text, upi_reminder, whatsapp_url
from nit_joint.ui import chat_bubble, code_pill, music_player_embed
from nit_joint.youtube import extract_video_id, normalize_api_key, search_music, watch_url


def _youtube_api_key() -> str | None:
    try:
        return normalize_api_key(st.secrets.get("YOUTUBE_API_KEY"))
    except Exception:
        return None


def render_join_panel(code: str, room: dict) -> bool:
    """Render join UI. Returns True if user still blocked from room."""
    if is_admin():
        st.info("🛡️ Admin view")
        if not is_member(room, user() or "Admin") and st.button("Join as admin"):
            admin_join_room(code, user() or "Admin")
            st.session_state.user_name = user() or "Admin"
            st.rerun()
        return False

    if user() and not is_member(room, user()):
        mode = room.get("join_mode") or "open"
        if mode == "crew_only":
            st.caption("🔒 Trusted crew only")
        if mode == "invite":
            st.caption("🔗 Invite link required")
        needs_pin = bool(room.get("has_pin")) or mode == "pin"
        pin_val = st.text_input("Room PIN", max_chars=4, type="password") if needs_pin else None
        member_pin = None
        if user() and has_user_pin(user()):
            member_pin = st.text_input("Your member PIN", type="password", max_chars=8)
        block = crew_block(st.session_state, user())
        if block:
            st.caption(f"Crew block: {block}")
        invite = st.session_state.get("pending_invite_token")
        if st.button("I'm in 👊", type="primary"):
            try:
                from nit_joint.crew import add_crew

                join_room(
                    code,
                    user(),
                    pin=pin_val,
                    block=block,
                    invite_token=invite,
                    member_pin=member_pin,
                )
                add_crew(st.session_state, user(), block)
                st.session_state.pending_invite_token = None
                st.rerun()
            except Exception as e:
                st.error(str(e))
        return True
    return False


def render_invite_strip(code: str, room: dict) -> None:
    base = app_base_url()
    token = room.get("invite_token") if room.get("join_mode") == "invite" else None
    inv = build_invite_text(room["title"], code, room.get("location"), base, token)
    link = inv.split("\n")[-2] if "\n" in inv else inv
    st.markdown(f'<div class="nj-share-strip">{code_pill(code, large=True)}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    c1.link_button("WhatsApp", whatsapp_url(inv), use_container_width=True)
    if c2.button("Copy link", use_container_width=True):
        st.session_state.copied_invite = link
        st.toast("Invite link ready — select from box below")
    c3.link_button("Open link", link, use_container_width=True)
    if st.session_state.get("copied_invite"):
        st.code(st.session_state.copied_invite)


def render_pullup_board(code: str, room: dict, read_only: bool) -> None:
    st.markdown("**Who's pulling up**")
    for m in room["members"]:
        eta = f" · ETA {m['eta_minutes']}m" if m.get("eta_minutes") else ""
        pickup = " · 🚪 pickup" if m.get("needs_pickup") else ""
        st.markdown(
            f'<div class="nj-status-card"><strong>{html.escape(m["name"])}</strong> '
            f'{STATUS_LABELS.get(m.get("status", "here"), "")}{html.escape(eta)}{pickup}</div>',
            unsafe_allow_html=True,
        )

    if not read_only and is_member(room, user()):
        st.caption("Your status")
        cols = st.columns(3)
        for col, (k, lbl) in zip(cols, STATUS_LABELS.items()):
            if col.button(lbl, key=f"st_{k}"):
                eta = st.session_state.get("status_eta") if k == "on_my_way" else None
                pickup = st.session_state.get("status_pickup", False) if k == "on_my_way" else False
                update_status(code, user(), k, eta_minutes=eta, needs_pickup=pickup)
                st.rerun()
        if st.checkbox("Need pickup from gate", key="status_pickup"):
            pass
        eta_val = st.number_input("ETA (minutes)", min_value=1, max_value=180, value=15, key="status_eta")
        st.caption(f"Set ETA to {eta_val}m when you tap On the way")


def render_playlist_bar(code: str, room: dict, read_only: bool) -> None:
    url = room.get("playlist_url")
    if url:
        st.markdown(f"🎵 **Tonight's playlist:** [{url}]({url})")
    if not read_only and is_member(room, user()):
        with st.expander("Set playlist link"):
            new_url = st.text_input("Spotify / YouTube playlist", value=url or "")
            if st.button("Save playlist", key="save_pl"):
                update_playlist(code, new_url.strip() or None)
                st.rerun()


def render_chat_tab(code: str, room: dict, read_only: bool) -> None:
    st.markdown('<div class="nj-chat-wrap">', unsafe_allow_html=True)
    me = user()
    for msg in room["messages"]:
        if msg.get("type") == "system":
            st.markdown(f'<div class="nj-chat-system">● {html.escape(msg["content"])}</div>', unsafe_allow_html=True)
        else:
            own = names_match(msg["author"], me)
            st.markdown(chat_bubble(msg["author"], msg["content"], own=own), unsafe_allow_html=True)
            if is_admin() and st.button("🗑️", key=f"dm_{msg['id']}"):
                admin_delete_message(msg["id"])
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    if not read_only:
        text = st.chat_input("Say something...")
        if text:
            post_message(code, user(), text)
            st.rerun()


def render_session_controls(code: str, room: dict) -> None:
    """Host / admin: wrap up or permanently delete the sesh."""
    me = user() or "Admin"
    host = is_host(room, me)
    admin = is_admin()
    archived = room.get("is_archived")

    if not host and not admin:
        return

    role = "Host" if host else "Admin"
    with st.expander(f"⚙️ {role} — session controls"):
        if host and not archived:
            others = [m["name"] for m in room["members"] if not names_match(m["name"], room["host_name"])]
            if others:
                new_host = st.selectbox("Pass host to", others, key=f"pass_host_{code}")
                if st.button("Pass host 👑", key=f"pass_host_btn_{code}"):
                    transfer_host(code, me, new_host)
                    st.rerun()

        st.caption("Wrap up = read-only for 24h with recap · Delete = removed forever")

        wrap_col, del_col = st.columns(2, gap="small")
        if not archived:
            if wrap_col.button("Wrap up sesh", key=f"wrap_{code}", use_container_width=True, type="primary"):
                try:
                    recap = close_session(code, me, delete=False, as_admin=admin and not host)
                    st.session_state.last_wrap_recap = recap or ""
                    st.session_state.room_code = ""
                    go("home")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            wrap_col.caption("Already wrapped up")

        confirm_key = f"confirm_delete_{code}"
        st.checkbox("I understand — delete permanently", key=confirm_key)
        if del_col.button(
            "Delete sesh 🗑️",
            key=f"delete_{code}",
            use_container_width=True,
            disabled=not st.session_state.get(confirm_key, False),
        ):
            try:
                recap = close_session(code, me, delete=True, as_admin=admin and not host)
                st.session_state.last_wrap_recap = recap or ""
                st.session_state.room_code = ""
                go("home")
                st.rerun()
            except Exception as e:
                st.error(str(e))


def render_grab_tab(code: str, room: dict, read_only: bool) -> None:
    summary = grab_list_summary(room["checklist"])
    st.caption(f"{summary['claimed']}/{summary['total']} claimed · {summary['open']} open")
    if summary["open_items"]:
        st.info("Still need: " + ", ".join(summary["open_items"][:6]))

    if not read_only:
        if st.button("Refresh list for crew size", key="refresh_cl"):
            refresh_checklist_suggestions(code)
            st.rerun()

    member_names = [m["name"] for m in room["members"]]
    me = user()

    for item in room["checklist"]:
        claimed = item.get("claimed_by")
        item_id = item["id"]
        with st.container(border=True):
            st.markdown(
                f"**{'✅' if claimed else '⬜'} {item['item']}**"
                + (f"  ·  _{claimed}_" if claimed else "")
            )
            if read_only:
                continue

            if not claimed:
                if st.button("Claim", key=f"c_{item_id}", use_container_width=True, type="primary"):
                    claim_checklist(code, item_id, me)
                    st.rerun()
                if st.button("Remove item", key=f"d_{item_id}", use_container_width=True):
                    delete_checklist_item(code, item_id, me)
                    st.rerun()
                continue

            # Claimed — unclaim, reassign, or delete
            can_manage = (
                names_match(claimed, me)
                or is_host(room, me)
            )
            if not can_manage:
                st.caption("Only the assignee or host can change this")
                continue

            act1, act2, act3 = st.columns(3, gap="small")
            if act1.button("Unclaim", key=f"u_{item_id}", use_container_width=True):
                claim_checklist(code, item_id, None)
                st.rerun()

            others = [n for n in member_names if not names_match(n, claimed)]
            if others:
                with act2:
                    new_person = st.selectbox(
                        "Reassign to",
                        others,
                        key=f"reassign_pick_{item_id}",
                        label_visibility="collapsed",
                    )
                if act3.button("Reassign", key=f"r_{item_id}", use_container_width=True):
                    claim_checklist(code, item_id, new_person)
                    st.rerun()
            else:
                act2.caption("No one else to reassign")

            if st.button("Remove item", key=f"del_{item_id}", use_container_width=True):
                delete_checklist_item(code, item_id, me)
                st.rerun()

    if not read_only:
        ni = st.text_input("Add item", key="ni")
        if st.button("Add", key="add_cl") and ni.strip():
            add_checklist_item(code, ni)
            st.rerun()


def render_expense_tab(code: str, room: dict, read_only: bool) -> None:
    split_mode = st.radio("Split among", ["Everyone in room", "Attendees only (Here ✅)"], horizontal=True, key="split_mode")
    split = room["split_attendees"] if "Attendees" in split_mode else room["split"]
    st.metric("Total", f"₹{split['total']:,.0f}")
    st.metric("Per head", f"₹{split['perPerson']:,.0f}")
    export_txt = export_split_text(room["title"], split, attendees_only="Attendees" in split_mode)
    st.download_button("Export split", export_txt, file_name=f"{code}-split.txt", mime="text/plain")
    if st.button("Share split on WhatsApp", key="wa_split"):
        st.session_state.split_wa = export_txt
    if st.session_state.get("split_wa"):
        st.link_button("Open WhatsApp with split", whatsapp_url(st.session_state.split_wa))

    for t in split["settleUp"]:
        paid = " ✅" if t.get("paid") else ""
        st.markdown(f"**{t['from']}** → **{t['to']}**: ₹{t['amount']:,.0f}{paid}")
        c1, c2 = st.columns(2)
        if c1.button(f"UPI remind {t['from']}", key=f"upi_{t['from']}_{t['to']}"):
            st.code(upi_reminder(t["from"], t["amount"], room["title"]))
        if not read_only and c2.button(f"Mark paid", key=f"paid_{t['from']}_{t['to']}"):
            mark_settlement_paid(code, t["from"], t["to"], t["amount"], paid=not t.get("paid"))
            st.rerun()

    for exp in room["expenses"]:
        st.markdown(f"**{exp['description']}** — ₹{exp['amount']:,.0f} by {exp['paid_by']}")
        if exp.get("receipt_data"):
            st.image(base64.b64decode(exp["receipt_data"]), width=200)

    if not read_only:
        with st.form("exp"):
            d = st.text_input("What")
            a = st.number_input("₹", min_value=1.0, step=50.0)
            rc = st.file_uploader("Receipt (optional)", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Log"):
                rdata = base64.b64encode(rc.read()).decode("ascii") if rc else None
                add_expense(code, d, a, user(), rdata)
                st.rerun()


def render_entertainment_tab(code: str, room: dict, read_only: bool) -> None:
    track_id = room.get("current_track_id")
    track_title = room.get("current_track_title")
    if track_id:
        st.markdown(
            f'<p class="nj-now-playing">Now playing · <strong>{html.escape(track_title or track_id)}</strong></p>',
            unsafe_allow_html=True,
        )
        st.markdown(music_player_embed(track_id), unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if not read_only:
            if c1.button("Play next", use_container_width=True, key="play_next"):
                play_next_track(code)
                st.rerun()
        c2.link_button("YouTube", watch_url(track_id), use_container_width=True)
        if not read_only and c3.button("Clear", use_container_width=True, key="clear_track"):
            set_now_playing(code, None, None)
            st.rerun()

    st.markdown("**Queue**")
    queue = room.get("music_queue") or []
    if not queue:
        st.caption("Queue is empty — search below to add tracks")
    for q in queue:
        st.caption(f"▶ {q['title']} · {q.get('added_by') or '—'}")
        if not read_only and st.button("Remove", key=f"rmq_{q['id']}"):
            remove_music_queue_item(code, q["id"])
            st.rerun()

    if read_only:
        return

    with st.form(f"music_search_{code}"):
        query = st.text_input("Search music", placeholder="Artist, song, vibe…")
        if st.form_submit_button("Search 🎵") and query.strip():
            st.session_state[f"room_music_results_{code}"] = search_music(query.strip(), api_key=_youtube_api_key())
            st.session_state[f"room_music_query_{code}"] = query.strip()

    with st.expander("Paste YouTube link"):
        pasted = st.text_input("URL or ID", key=f"paste_{code}")
        if st.button("Add link", key=f"paste_btn_{code}") and pasted.strip():
            vid = extract_video_id(pasted.strip())
            if vid:
                add_music_queue(code, vid, pasted.strip(), "", user())
                set_now_playing(code, vid, pasted.strip())
                st.rerun()
            else:
                st.error("Invalid link")

    results = st.session_state.get(f"room_music_results_{code}", [])
    for i, track in enumerate(results):
        if st.button(f"Add · {track['title'][:50]}", key=f"q_{code}_{track['video_id']}_{i}", use_container_width=True):
            add_music_queue(code, track["video_id"], track["title"], track.get("channel") or "", user())
            if not track_id:
                set_now_playing(code, track["video_id"], track["title"])
            st.rerun()


def render_recap(room: dict) -> None:
    recap = room.get("recap_text")
    if recap:
        st.success("Sesh recap")
        st.text(recap)
        st.link_button("Share recap", whatsapp_url(recap_for_share(room)), use_container_width=True)
