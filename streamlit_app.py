"""NIT-JOINT — Streamlit app."""

from __future__ import annotations

import base64
import io
from datetime import timedelta

import streamlit as st

from nit_joint.admin import get_admin_passwords, is_admin, verify_admin_password
from nit_joint.app_state import (
    app_base_url,
    can_use_room,
    go,
    go_room,
    init_session,
    is_host,
    is_member,
    user,
)
from nit_joint.constants import HOSTEL_BLOCKS, STATUS_LABELS, VIBE_TAGS
from nit_joint.crew import add_crew, crew_block, get_crew_from_session, remove_crew
from nit_joint.db import (
    add_checklist_item,
    add_expense,
    add_plug_watch,
    admin_delete_message,
    admin_force_end,
    admin_get_room_chats,
    admin_join_room,
    admin_kick_member,
    ban_name,
    claim_checklist,
    create_room,
    create_room_from_template,
    delete_expense,
    delete_seller,
    end_room,
    get_room,
    init_db,
    join_room,
    list_audit,
    list_banned,
    list_feedback,
    list_plug_watch,
    list_rooms,
    list_sellers,
    log_audit,
    post_message,
    register_seller,
    remove_plug_watch,
    save_trusted_crew_db,
    stocked_blocks,
    submit_feedback,
    transfer_host,
    unban_name,
    update_playlist,
    update_seller,
    update_status,
)
from nit_joint.helpers import get_countdown, is_starting_soon, names_match
from nit_joint.share import build_invite_text, upi_reminder, whatsapp_url
from nit_joint.templates import template_keys
from nit_joint.time import format_time_ist
from nit_joint.ui import PWA_TIP, inject_css

init_db()
init_session()

st.set_page_config(page_title="NIT-JOINT", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
st.markdown(inject_css(), unsafe_allow_html=True)


def render_qr(code: str) -> None:
    try:
        import qrcode

        img = qrcode.make(f"{app_base_url()}/?room={code.upper()}")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption=f"Scan to join {code}", width=160)
    except Exception:
        st.caption(f"Link: {app_base_url()}/?room={code.upper()}")


def check_new_messages(room_code: str, count: int) -> bool:
    prev = st.session_state.last_msg_counts.get(room_code, 0)
    st.session_state.last_msg_counts[room_code] = count
    return st.session_state.live_mode and count > prev and prev > 0


def render_sidebar() -> None:
    with st.sidebar:
        st.title("🌿 NIT-JOINT")
        st.caption("Where the boys link up")
        st.session_state.user_name = st.text_input(
            "Your name",
            value=st.session_state.user_name,
            placeholder="Optional — needed to join/chat",
        )
        st.session_state.live_mode = st.toggle("Live updates", value=st.session_state.live_mode)

        with st.expander("📱 Add to home screen"):
            st.markdown(PWA_TIP)

        with st.expander("👊 Trusted crew"):
            crew = get_crew_from_session(st.session_state)
            cn = st.text_input("Add name", key="crew_name")
            cb = st.selectbox("Block", [""] + HOSTEL_BLOCKS, key="crew_block", format_func=lambda x: x or "—")
            if st.button("Add to crew", use_container_width=True) and cn.strip():
                add_crew(st.session_state, cn, cb or None)
                save_trusted_crew_db(cn, cb or None)
                st.rerun()
            for c in crew:
                col1, col2 = st.columns([3, 1])
                col1.caption(f"{c['name']}" + (f" · {c['block']}" if c.get("block") else ""))
                if col2.button("✕", key=f"rm_crew_{c['name']}"):
                    remove_crew(st.session_state, c["name"])
                    st.rerun()
                if st.button(f"Use {c['name']}", key=f"use_{c['name']}"):
                    st.session_state.user_name = c["name"]
                    st.rerun()

        # Plug watch alerts
        if user():
            watched = list_plug_watch(user())
            stocked = stocked_blocks()
            for block in watched:
                if block in stocked and block not in st.session_state.plug_alerts_shown:
                    st.success(f"🔔 {block} has a plug stocked!")
                    st.session_state.plug_alerts_shown.add(block)

        st.divider()
        for label, page in [("🏠 Home", "home"), ("🔌 The Plugs", "sellers"), ("📣 Feedback", "feedback")]:
            if st.button(label, use_container_width=True):
                go(page)
        if st.session_state.room_code and st.button(f"💨 Room {st.session_state.room_code}", use_container_width=True):
            go("room")

        st.divider()
        with st.expander("🔐 Admin", expanded=is_admin()):
            if is_admin():
                st.success("Admin logged in")
                if st.button("Log out", use_container_width=True):
                    st.session_state.is_admin = False
                    st.rerun()
            elif get_admin_passwords():
                pwd = st.text_input("Password", type="password")
                if st.button("Log in", use_container_width=True) and verify_admin_password(pwd):
                    st.session_state.is_admin = True
                    if not user():
                        st.session_state.user_name = "Admin"
                    st.rerun()
            else:
                st.caption("Set admin.password in secrets")
        if is_admin() and st.button("🛡️ Admin panel", use_container_width=True):
            go("admin")


def render_home() -> None:
    st.header("NIT-JOINT 🌿")
    st.markdown("Pick a dorm, roll a sesh, figure out who's bringing what and who owes who.")

    st.subheader("Quick templates")
    tcols = st.columns(3)
    for i, key in enumerate(template_keys()):
        with tcols[i % 3]:
            if st.button(key, key=f"tpl_{key}", use_container_width=True):
                if not user():
                    st.warning("Set your name in the sidebar first")
                else:
                    try:
                        room = create_room_from_template(key, user())
                        go_room(room["code"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    tab_create, tab_join = st.tabs(["Start a sesh", "Pull up"])

    with tab_create:
        with st.form("create"):
            title = st.text_input("Session name", placeholder="Friday night rip")
            vibes = st.multiselect("Vibe", VIBE_TAGS)
            block = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick")
            location = st.text_input("Or type location", placeholder="MBH A · 204")
            when = st.text_input("When (ISO)", placeholder="2026-05-23T20:00")
            notes = st.text_area("Notes")
            pin = st.text_input("Join PIN (4 digits, optional)", max_chars=4)
            if st.form_submit_button("Let's go 🔥", type="primary"):
                if not user():
                    st.error("Set your name in the sidebar")
                elif not title.strip():
                    st.error("Give the session a name")
                elif pin and (len(pin) != 4 or not pin.isdigit()):
                    st.error("PIN must be 4 digits")
                else:
                    try:
                        room = create_room(
                            title=title,
                            host_name=user(),
                            location=location or block or None,
                            description=notes or None,
                            vibe_tags=vibes,
                            join_pin=pin or None,
                            scheduled_at=when or None,
                        )
                        go_room(room["code"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with tab_join:
        with st.form("join"):
            code = st.text_input("Room code", max_chars=6).upper()
            if st.form_submit_button("Pull up", type="primary"):
                if len(code) != 6:
                    st.error("Code must be 6 characters")
                elif not get_room(code):
                    st.error("Room not found")
                else:
                    go_room(code)
                    st.rerun()

    st.subheader("Active seshes 🔥")
    vibe = None if st.session_state.vibe_filter == "All" else st.session_state.vibe_filter
    for f in ["All"] + list(VIBE_TAGS):
        if st.button(f, key=f"f_{f}"):
            st.session_state.vibe_filter = f

    for room in list_rooms(vibe):
        cd = get_countdown(room.get("scheduled_at"))
        soon = is_starting_soon(room.get("scheduled_at"))
        with st.container(border=True):
            st.markdown(f"**{room['title']}** `{room['code']}`" + (" 🔒" if room.get("has_pin") else ""))
            if room.get("location"):
                st.caption(f"📍 {room['location']}")
            if cd:
                st.caption(f"⏰ {cd}" + (" · **Starting soon!**" if soon else ""))
            if room.get("last_activity_at"):
                st.caption(f"Active · {format_time_ist(room['last_activity_at'])}")
            c1, c2, c3, c4 = st.columns(4)
            if c1.button("Enter", key=f"e_{room['code']}"):
                go_room(room["code"])
                st.rerun()
            inv = build_invite_text(room["title"], room["code"], room.get("location"), app_base_url())
            c2.code(inv, language=None)
            c3.link_button("WhatsApp", whatsapp_url(inv), key=f"wa_{room['code']}")
            with c4:
                render_qr(room["code"])


def render_room() -> None:
    code = st.session_state.room_code
    if not code:
        st.warning("No room selected")
        return

    interval = timedelta(seconds=3) if st.session_state.live_mode else None

    @st.fragment(run_every=interval)
    def room_view() -> None:
        room = get_room(code)
        if not room:
            st.error("Room not found")
            return

        archived = room.get("is_archived")
        if archived:
            st.warning("Wrapped up — read-only for 24h")

        st.markdown(f"## {room['title']}")
        inv = build_invite_text(room["title"], code, room.get("location"), app_base_url())
        sc1, sc2, sc3 = st.columns(3)
        sc1.code(code)
        if sc2.button("Copy invite"):
            st.toast("Invite copied")
            st.code(inv)
        sc3.link_button("WhatsApp share", whatsapp_url(inv))
        render_qr(code)

        cd = get_countdown(room.get("scheduled_at"))
        if cd:
            st.info(f"⏰ {cd}")

        msg_count = len([m for m in room["messages"] if m.get("type") != "system"])
        if check_new_messages(code, msg_count):
            st.toast("💬 New message!", icon="💬")

        # Pull-up board
        st.markdown("**Who's pulling up**")
        for m in room["members"]:
            st.markdown(
                f'<div class="nj-status-card"><strong>{m["name"]}</strong> '
                f'{STATUS_LABELS.get(m.get("status", "here"), "")}</div>',
                unsafe_allow_html=True,
            )

        if is_admin():
            st.info("🛡️ Admin view")
            if not is_member(room, user() or "Admin") and st.button("Join as admin"):
                admin_join_room(code, user() or "Admin")
                st.session_state.user_name = user() or "Admin"
                st.rerun()
        elif user() and not is_member(room, user()):
            pin_val = st.text_input("PIN", max_chars=4, type="password") if room.get("has_pin") else None
            block = crew_block(st.session_state, user())
            if block:
                st.caption(f"Crew block: {block}")
            if st.button("I'm in 👊", type="primary"):
                try:
                    join_room(code, user(), pin=pin_val, block=block)
                    add_crew(st.session_state, user(), block)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
            return

        if not can_use_room(room):
            st.info("Set your name and join to participate")
            return
        if not is_admin() and not is_member(room, user()):
            return

        read_only = archived or (is_admin() and not is_member(room, user() or "Admin"))

        if not read_only and is_member(room, user()):
            st.caption("Your status")
            cols = st.columns(3)
            for col, (k, lbl) in zip(cols, STATUS_LABELS.items()):
                if col.button(lbl, key=f"st_{k}"):
                    update_status(code, user(), k)
                    st.rerun()

        if is_host(room, user()) and not read_only:
            with st.expander("Host controls"):
                others = [m["name"] for m in room["members"] if not names_match(m["name"], room["host_name"])]
                if others and st.button("Pass host"):
                    transfer_host(code, user(), others[0])
                    st.rerun()
                if st.button("Wrap up"):
                    end_room(code, user(), permanent=False)
                    go("home")
                    st.rerun()

        tabs = st.tabs(["Yap 💬", "Grab list 🛒", "The tab 💸", "Boys 👊"])
        with tabs[0]:
            for msg in room["messages"]:
                if msg.get("type") == "system":
                    st.caption(f"● {msg['content']}")
                else:
                    st.markdown(f"**{msg['author']}:** {msg['content']}")
                    if is_admin() and st.button("🗑️ del", key=f"dm_{msg['id']}"):
                        admin_delete_message(msg["id"])
                        st.rerun()
            if not read_only:
                text = st.chat_input("Say something...")
                if text:
                    post_message(code, user(), text)
                    st.rerun()

        with tabs[1]:
            for item in room["checklist"]:
                st.markdown(f"{'✅' if item.get('claimed_by') else '⬜'} {item['item']} {item.get('claimed_by') or ''}")
                if not read_only and not item.get("claimed_by") and st.button("Claim", key=f"c_{item['id']}"):
                    claim_checklist(code, item["id"], user())
                    st.rerun()
            if not read_only:
                ni = st.text_input("Add item", key="ni")
                if st.button("Add") and ni.strip():
                    add_checklist_item(code, ni)
                    st.rerun()

        with tabs[2]:
            split = room["split"]
            st.metric("Total", f"₹{split['total']:,.0f}")
            st.metric("Per head", f"₹{split['perPerson']:,.0f}")
            for t in split["settleUp"]:
                st.markdown(f"**{t['from']}** → **{t['to']}**: ₹{t['amount']:,.0f}")
                if st.button(f"Copy UPI remind {t['from']}", key=f"upi_{t['from']}_{t['to']}"):
                    st.code(upi_reminder(t["from"], t["amount"], room["title"]))
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
                        rdata = None
                        if rc:
                            rdata = base64.b64encode(rc.read()).decode("ascii")
                        add_expense(code, d, a, user(), rdata)
                        st.rerun()

        with tabs[3]:
            for m in room["members"]:
                st.markdown(f"**{m['name']}** {STATUS_LABELS.get(m.get('status', 'here'), '')}")
                if is_admin() and st.button(f"Kick {m['name']}", key=f"kick_{m['name']}"):
                    admin_kick_member(code, m["name"])
                    st.rerun()

    room_view()


def render_sellers() -> None:
    st.header("The Plugs 🔌")
    sellers = list_sellers()
    st.markdown(f"**{sum(1 for s in sellers if s['available'])}** / **{len(sellers)}** stocked")

    with st.expander("🔔 Notify when block is stocked"):
        if user():
            bw = st.selectbox("Watch block", HOSTEL_BLOCKS)
            if st.button("Watch this block"):
                add_plug_watch(user(), bw)
                st.success(f"Watching {bw}")
            for b in list_plug_watch(user()):
                st.caption(f"Watching: {b}")
                if st.button(f"Stop {b}", key=f"unwatch_{b}"):
                    remove_plug_watch(user(), b)
                    st.rerun()
        else:
            st.caption("Set a name to watch blocks")

    own = next((s for s in sellers if user() and names_match(s["name"], user())), None)
    if not own:
        with st.form("reg"):
            sn = st.text_input("Your name", value=st.session_state.user_name)
            sb = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick")
            sc = st.text_input("Contact")
            snote = st.text_area("Note")
            sav = st.checkbox("In stock", True)
            if st.form_submit_button("Go live 🌿"):
                if not sn.strip():
                    st.error("Enter your name")
                else:
                    register_seller(sn.strip(), sb or None, sc or None, sav, snote or None)
                    st.session_state.user_name = sn.strip()
                    st.rerun()

    for s in sellers:
        with st.container(border=True):
            st.markdown(f"### {s['name']} — {'Stocked 💨' if s['available'] else 'Dry'}")
            if s.get("block"):
                st.caption(s["block"])
            if s.get("note"):
                st.write(s["note"])


def render_admin() -> None:
    if not is_admin():
        st.error("Admin login required")
        return
    st.header("🛡️ Admin panel")
    rooms = admin_get_room_chats()
    if st.button("Join ALL rooms"):
        for r in rooms:
            try:
                admin_join_room(r["code"], user() or "Admin")
            except Exception:
                pass
        st.rerun()

    tab_rooms, tab_audit, tab_ban, tab_fb = st.tabs(["Rooms & chats", "Audit log", "Banned", "Feedback"])
    with tab_rooms:
        for room in rooms:
            with st.expander(f"{room['code']} — {room['title']}"):
                for msg in room.get("messages") or []:
                    st.markdown(f"**{msg['author']}:** {msg['content']}")
                c1, c2, c3 = st.columns(3)
                if c1.button("Enter", key=f"ae_{room['code']}"):
                    go_room(room["code"])
                    st.rerun()
                if c2.button("Force delete", key=f"fd_{room['code']}"):
                    admin_force_end(room["code"], permanent=True)
                    st.rerun()
                if c3.button("Archive", key=f"fa_{room['code']}"):
                    admin_force_end(room["code"], permanent=False)
                    st.rerun()

    with tab_audit:
        for row in list_audit():
            st.caption(f"[{format_time_ist(row['created_at'])}] {row['action']} · {row['actor']} → {row['target']} · {row['detail']}")

    with tab_ban:
        bn = st.text_input("Name to ban")
        br = st.text_input("Reason")
        if st.button("Ban") and bn.strip():
            ban_name(bn, br or None)
            st.rerun()
        for b in list_banned():
            st.markdown(f"**{b['name']}** — {b.get('reason') or ''}")
            if st.button(f"Unban {b['name']}", key=f"ub_{b['name']}"):
                unban_name(b["name"])
                st.rerun()

    with tab_fb:
        for f in list_feedback():
            st.markdown(f"_{format_time_ist(f['created_at'])}_ · {f.get('room_code') or 'general'}")
            st.write(f["content"])


def render_feedback() -> None:
    st.header("📣 Anonymous feedback")
    st.caption("Goes to admin only — report dry plugs, issues, etc.")
    with st.form("fb"):
        msg = st.text_area("What's up?")
        rc = st.text_input("Room code (optional)", max_chars=6).upper() or None
        if st.form_submit_button("Send"):
            if msg.strip():
                submit_feedback(msg.strip(), rc)
                st.success("Sent — admin will see it")
            else:
                st.error("Write something")


render_sidebar()

page = st.session_state.page
if page == "home":
    render_home()
elif page == "room":
    render_room()
elif page == "sellers":
    render_sellers()
elif page == "admin":
    render_admin()
elif page == "feedback":
    render_feedback()

qp = st.query_params.get("room")
if qp and isinstance(qp, str):
    go_room(qp.upper())
