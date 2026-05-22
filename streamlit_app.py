"""NIT-JOINT — Streamlit app (primary UI)."""

from __future__ import annotations

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
from nit_joint.crew import add_crew, get_crew_from_session, remove_crew
from nit_joint.db import (
    add_plug_watch,
    admin_force_end,
    admin_get_room_chats,
    admin_join_room,
    admin_kick_member,
    ban_name,
    create_room,
    create_room_from_template,
    end_room,
    get_room,
    has_user_pin,
    init_db,
    join_room,
    list_audit,
    list_banned,
    list_feedback,
    list_plug_watch,
    list_rooms,
    list_sellers,
    register_seller,
    remove_plug_watch,
    save_trusted_crew_db,
    set_user_pin,
    stocked_blocks,
    submit_feedback,
    transfer_host,
    unban_name,
    update_seller,
)
from nit_joint.helpers import active_vibe_filters, get_countdown, is_starting_soon, names_match
from nit_joint.room_views import (
    render_chat_tab,
    render_entertainment_tab,
    render_expense_tab,
    render_grab_tab,
    render_invite_strip,
    render_join_panel,
    render_playlist_bar,
    render_pullup_board,
    render_recap,
)
from nit_joint.scheduling import schedule_picker
from nit_joint.share import build_invite_text, contact_whatsapp_url, whatsapp_url
from nit_joint.templates import template_keys
from nit_joint.time import format_time_ist
from nit_joint.ui import PWA_TIP, hero_section, inject_css, inject_pwa, sesh_title

st.set_page_config(page_title="NIT-JOINT", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

init_db()
init_session()

st.markdown(inject_css(), unsafe_allow_html=True)
st.markdown(inject_pwa(), unsafe_allow_html=True)


def check_new_messages(room_code: str, count: int) -> bool:
    prev = st.session_state.last_msg_counts.get(room_code, 0)
    st.session_state.last_msg_counts[room_code] = count
    return st.session_state.live_mode and count > prev and prev > 0


def render_onboarding() -> bool:
    """First-run wizard. Returns True if onboarding blocks main home."""
    if st.session_state.onboarding_done:
        return False
    st.markdown(
        """<div class="nj-onboard-card nj-fade-in">
        <h2>Welcome to NIT-JOINT 🌿</h2>
        <p class="nj-hero-sub">Set up in 3 taps — name, crew, first sesh.</p></div>""",
        unsafe_allow_html=True,
    )
    step = st.session_state.onboarding_step
    if step == 0:
        st.subheader("1 · Your name")
        name = st.text_input("What do the boys call you?", value=st.session_state.user_name)
        pin = st.text_input("Member PIN (optional — locks your name)", type="password", max_chars=8)
        if st.button("Next →", type="primary") and name.strip():
            st.session_state.user_name = name.strip()
            if pin.strip():
                try:
                    set_user_pin(name.strip(), pin.strip())
                except Exception as e:
                    st.error(str(e))
                    return True
            st.session_state.onboarding_step = 1
            st.rerun()
    elif step == 1:
        st.subheader("2 · Trusted crew (optional)")
        st.caption("Save regulars for one-tap join")
        cn = st.text_input("Add a name")
        cb = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "—")
        if st.button("Add to crew") and cn.strip():
            add_crew(st.session_state, cn, cb or None)
            save_trusted_crew_db(cn, cb or None)
            st.rerun()
        if st.button("Next →", type="primary"):
            st.session_state.onboarding_step = 2
            st.rerun()
    else:
        st.subheader("3 · Start or join")
        c1, c2 = st.columns(2)
        if c1.button("Start a sesh 🔥", use_container_width=True, type="primary"):
            st.session_state.onboarding_done = True
            st.rerun()
        if c2.button("Browse active seshes", use_container_width=True):
            st.session_state.onboarding_done = True
            st.rerun()
    return True


def render_sidebar() -> None:
    with st.sidebar:
        st.title("🌿 NIT-JOINT")
        st.caption("Where the boys link up")
        st.session_state.user_name = st.text_input(
            "Your name",
            value=st.session_state.user_name,
            placeholder="Needed to join / chat",
        )
        if user():
            mp = st.text_input("Member PIN (optional)", type="password", max_chars=8, key="sidebar_pin")
            if st.button("Save PIN", use_container_width=True) and mp.strip():
                try:
                    set_user_pin(user(), mp.strip())
                    st.success("PIN saved")
                except Exception as e:
                    st.error(str(e))
            if has_user_pin(user()):
                st.caption("🔒 PIN active for your name")

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


FEATURES = [
    {"icon": "💨", "title": "Instant Sesh Rooms", "desc": "One tap to create. Share code or link — crew pulls up fast."},
    {"icon": "🛒", "title": "Smart Grab Lists", "desc": "Auto lists by vibe + headcount. Claim, unclaim, reassign."},
    {"icon": "💸", "title": "Split The Tab", "desc": "Split by attendees, mark UPI paid, export & share."},
    {"icon": "💬", "title": "Live Yap Chat", "desc": "Bubble chat with live refresh and toast alerts."},
    {"icon": "🎵", "title": "Room Entertainment", "desc": "Shared music queue in every sesh — search & play together."},
    {"icon": "🔌", "title": "The Plugs Network", "desc": "Stocked board with alerts, contact, auto-expire."},
]


def render_home() -> None:
    if not st.session_state.onboarding_done:
        if render_onboarding():
            return

    st.markdown(
        hero_section(
            title="NIT-JOINT",
            subtitle="Pick a dorm. Roll a sesh. Figure out who's bringing what and who owes who.",
            accent_word="JOINT",
        ),
        unsafe_allow_html=True,
    )

    for row_start in range(0, len(FEATURES), 3):
        row = FEATURES[row_start : row_start + 3]
        cols = st.columns(len(row))
        for col, feat in zip(cols, row):
            with col:
                st.markdown(
                    f"""<div class="nj-feature-card">
                        <span class="nj-feature-icon">{feat['icon']}</span>
                        <h3>{feat['title']}</h3>
                        <p>{feat['desc']}</p>
                    </div>""",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
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
            when = schedule_picker(key_prefix="create")
            notes = st.text_area("Notes")
            join_mode = st.selectbox(
                "Who can join",
                ["open", "pin", "crew_only", "invite"],
                format_func=lambda x: {
                    "open": "Anyone with code",
                    "pin": "PIN required",
                    "crew_only": "Trusted crew only",
                    "invite": "Invite link only",
                }[x],
            )
            pin = st.text_input("Join PIN (4 digits)", max_chars=4) if join_mode == "pin" else None
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
                            join_pin=pin if join_mode == "pin" else None,
                            scheduled_at=when,
                            join_mode=join_mode,
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
    all_rooms = list_rooms(None)
    if not all_rooms:
        st.info("No active seshes — be the first to start one above 👆")
        return

    filters = active_vibe_filters(all_rooms)
    if st.session_state.vibe_filter not in filters:
        st.session_state.vibe_filter = "All"
    if len(filters) > 1:
        st.session_state.vibe_filter = st.radio(
            "Filter seshes", filters, index=filters.index(st.session_state.vibe_filter), horizontal=True, label_visibility="collapsed"
        )

    vibe = None if st.session_state.vibe_filter == "All" else st.session_state.vibe_filter
    rooms = [r for r in all_rooms if not vibe or vibe in r.get("vibe_tags", [])]

    for room in rooms:
        cd = get_countdown(room.get("scheduled_at"))
        soon = is_starting_soon(room.get("scheduled_at"))
        inv = build_invite_text(room["title"], room["code"], room.get("location"), app_base_url())
        with st.container(border=True):
            st.markdown(sesh_title(room["title"], room["code"], has_pin=bool(room.get("has_pin"))), unsafe_allow_html=True)
            meta_parts = []
            if room.get("location"):
                meta_parts.append(f"📍 {room['location']}")
            if cd:
                meta_parts.append(f"⏰ {cd}" + (" · starting soon" if soon else ""))
            if room.get("last_activity_at"):
                meta_parts.append(f"Active · {format_time_ist(room['last_activity_at'])}")
            if meta_parts:
                st.caption(" · ".join(meta_parts))
            enter_col, share_col, link_col = st.columns([1, 1.2, 1.2], gap="small")
            with enter_col:
                if st.button("Enter 👊", key=f"e_{room['code']}", use_container_width=True, type="primary"):
                    go_room(room["code"])
                    st.rerun()
            with share_col:
                st.link_button("WhatsApp", whatsapp_url(inv), key=f"wa_{room['code']}", use_container_width=True)
            with link_col:
                if st.button("Copy link", key=f"cp_{room['code']}", use_container_width=True):
                    st.session_state.copied_invite = f"{app_base_url()}/?room={room['code']}"
                    st.toast("Link copied to box below")
    if st.session_state.get("copied_invite"):
        st.code(st.session_state.copied_invite)


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
            render_recap(room)

        st.markdown(f"## {room['title']}")
        render_invite_strip(code, room)
        render_playlist_bar(code, room, archived)

        cd = get_countdown(room.get("scheduled_at"))
        if cd:
            st.info(f"⏰ {cd}")

        msg_count = len([m for m in room["messages"] if m.get("type") != "system"])
        if check_new_messages(code, msg_count):
            st.toast("💬 New message!", icon="💬")

        if render_join_panel(code, room):
            if not user():
                st.info("Set your name in the sidebar to join")
            return

        if not can_use_room(room):
            st.info("Set your name and join to participate")
            return
        if not is_admin() and not is_member(room, user()):
            return

        read_only = archived or (is_admin() and not is_member(room, user() or "Admin"))

        render_pullup_board(code, room, read_only)

        if is_host(room, user()) and not read_only:
            with st.expander("Host controls"):
                others = [m["name"] for m in room["members"] if not names_match(m["name"], room["host_name"])]
                if others and st.button("Pass host"):
                    transfer_host(code, user(), others[0])
                    st.rerun()
                if st.button("Wrap up sesh"):
                    recap = end_room(code, user(), permanent=False)
                    st.session_state.last_wrap_recap = recap or ""
                    go("home")
                    st.rerun()

        tabs = st.tabs(["Yap 💬", "Grab list 🛒", "The tab 💸", "Entertainment 🎵", "Boys 👊"])
        with tabs[0]:
            render_chat_tab(code, room, read_only)
        with tabs[1]:
            render_grab_tab(code, room, read_only)
        with tabs[2]:
            render_expense_tab(code, room, read_only)
        with tabs[3]:
            render_entertainment_tab(code, room, read_only)
        with tabs[4]:
            for m in room["members"]:
                st.markdown(f"**{m['name']}** {STATUS_LABELS.get(m.get('status', 'here'), '')}")
                if is_admin() and st.button(f"Kick {m['name']}", key=f"kick_{m['name']}"):
                    admin_kick_member(code, m["name"])
                    st.rerun()

    room_view()


def render_sellers() -> None:
    st.header("The Plugs 🔌")
    sellers = list_sellers()
    stocked = sum(1 for s in sellers if s["available"])
    st.markdown(f"**{stocked}** / **{len(sellers)}** stocked · auto-dry after 6h")

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
    if own:
        st.subheader("Your listing")
        with st.container(border=True):
            st.markdown(f"### {own['name']} — {'Stocked 💨' if own['available'] else 'Dry'}")
            if own.get("stocked_at") and own["available"]:
                st.caption(f"Stocked since {format_time_ist(own['stocked_at'])}")
            av = st.checkbox("In stock", value=own["available"], key="own_av")
            note = st.text_area("Note", value=own.get("note") or "", key="own_note")
            if st.button("Update listing"):
                update_seller(own["id"], user(), available=av, note=note or None)
                st.rerun()
    elif user():
        with st.form("reg"):
            sn = st.text_input("Your name", value=st.session_state.user_name)
            sb = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick")
            sc = st.text_input("Contact (WhatsApp number)")
            snote = st.text_area("Note")
            sav = st.checkbox("In stock", True)
            if st.form_submit_button("Go live 🌿"):
                register_seller(sn.strip(), sb or None, sc or None, sav, snote or None)
                st.session_state.user_name = sn.strip()
                st.rerun()

    for s in sellers:
        with st.container(border=True):
            st.markdown(f"### {s['name']} — {'Stocked 💨' if s['available'] else 'Dry'}")
            meta = []
            if s.get("block"):
                meta.append(s["block"])
            if s.get("stocked_at") and s["available"]:
                meta.append(f"since {format_time_ist(s['stocked_at'])}")
            if meta:
                st.caption(" · ".join(meta))
            if s.get("note"):
                st.write(s["note"])
            if s.get("contact") and s["available"]:
                msg = f"Yo {s['name']}, still stocked?"
                st.link_button("WhatsApp", contact_whatsapp_url(s["contact"], msg), use_container_width=True)


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


def try_auto_join(code: str) -> None:
    if not user() or is_admin():
        return
    room = get_room(code)
    if not room or is_member(room, user()):
        return
    try:
        join_room(
            code,
            user(),
            invite_token=st.session_state.get("pending_invite_token"),
            block=None,
        )
    except Exception:
        pass


render_sidebar()

if st.session_state.get("last_wrap_recap"):
    with st.expander("📋 Last sesh recap", expanded=True):
        st.text(st.session_state.last_wrap_recap)
        st.link_button("Share recap", whatsapp_url(st.session_state.last_wrap_recap))
        if st.button("Dismiss recap"):
            st.session_state.last_wrap_recap = ""
            st.rerun()

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
elif page == "entertainment":
    go("home")
    st.rerun()

qp = st.query_params.get("room")
if qp and isinstance(qp, str):
    go_room(qp.upper())
    try_auto_join(qp.upper())

inv = st.query_params.get("invite")
if inv and isinstance(inv, str):
    st.session_state.pending_invite_token = inv
