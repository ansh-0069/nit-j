"""NIT-JOINT — Streamlit app for coordinating college seshes."""

from __future__ import annotations

from datetime import timedelta

import streamlit as st

from nit_joint.admin import get_admin_password, is_admin, verify_admin_password
from nit_joint.constants import HOSTEL_BLOCKS, STATUS_LABELS, VIBE_TAGS
from nit_joint.db import (
    add_checklist_item,
    add_expense,
    admin_get_room_chats,
    admin_join_room,
    claim_checklist,
    create_room,
    delete_expense,
    delete_seller,
    end_room,
    get_room,
    init_db,
    join_room,
    list_all_rooms_admin,
    list_rooms,
    list_sellers,
    post_message,
    register_seller,
    transfer_host,
    update_playlist,
    update_seller,
    update_status,
)
from nit_joint.helpers import names_match

init_db()

st.set_page_config(
    page_title="NIT-JOINT",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "page" not in st.session_state:
    st.session_state.page = "home"
if "room_code" not in st.session_state:
    st.session_state.room_code = ""
if "vibe_filter" not in st.session_state:
    st.session_state.vibe_filter = "All"
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


def go_room(code: str) -> None:
    st.session_state.room_code = code.upper()
    st.session_state.page = "room"


def go(page: str) -> None:
    st.session_state.page = page


def user() -> str:
    return st.session_state.user_name.strip()


def is_member(room: dict, name: str) -> bool:
    return any(names_match(m["name"], name) for m in room["members"])


def is_host(room: dict, name: str) -> bool:
    return names_match(room["host_name"], name)


def can_use_room(room: dict) -> bool:
    """Admin or joined member can interact with room content."""
    if is_admin():
        return True
    return bool(user()) and is_member(room, user())


def can_post_in_room(room: dict) -> bool:
    if room.get("is_archived"):
        return False
    if is_admin() and user() and is_member(room, user()):
        return True
    return bool(user()) and is_member(room, user()) and not room.get("is_archived")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌿 NIT-JOINT")
    st.caption("Where the boys link up")
    st.session_state.user_name = st.text_input(
        "Your name",
        value=st.session_state.user_name,
        placeholder="What do the boys call you?",
    )
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        go("home")
    if st.button("🔌 The Plugs", use_container_width=True):
        go("sellers")
    if st.session_state.room_code:
        if st.button(f"💨 Room {st.session_state.room_code}", use_container_width=True):
            go("room")

    st.divider()
    with st.expander("🔐 Admin", expanded=is_admin()):
        if is_admin():
            st.success("Logged in as admin")
            if st.button("Log out", use_container_width=True):
                st.session_state.is_admin = False
                st.rerun()
        elif get_admin_password():
            pwd = st.text_input("Password", type="password", key="admin_pwd")
            if st.button("Log in", use_container_width=True):
                if verify_admin_password(pwd):
                    st.session_state.is_admin = True
                    if not st.session_state.user_name.strip():
                        st.session_state.user_name = "Admin"
                    st.rerun()
                else:
                    st.error("Wrong password")
        else:
            st.caption("Set `admin.password` in Streamlit secrets")

    if is_admin():
        if st.button("🛡️ Admin panel", use_container_width=True):
            go("admin")

# ── HOME ──────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.header("NIT-JOINT 🌿")
    st.markdown("Pick a dorm, roll a sesh, figure out who's bringing what and who owes who.")

    tab_create, tab_join = st.tabs(["Start a sesh", "Pull up"])

    with tab_create:
        if not user():
            st.warning("Set your name in the sidebar first")
        with st.form("create"):
            title = st.text_input("Session name", placeholder="Friday night rip")
            vibes = st.multiselect("Vibe", VIBE_TAGS)
            block = st.selectbox("Block / location", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick a block")
            location = st.text_input("Or type location", placeholder="MBH A · 204")
            notes = st.text_area("Notes", placeholder="No randos, bring your own...")
            pin = st.text_input("Join PIN (optional, 4 digits)", max_chars=4)
            submit = st.form_submit_button("Let's go 🔥", type="primary")
            if submit:
                if not user():
                    st.error("Enter your name in the sidebar")
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
                        )
                        go_room(room["code"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with tab_join:
        with st.form("join"):
            code = st.text_input("Room code", max_chars=6).upper()
            submit_join = st.form_submit_button("Pull up", type="primary")
            if submit_join:
                if len(code) != 6:
                    st.error("Code must be 6 characters")
                else:
                    room = get_room(code)
                    if not room:
                        st.error("Room not found")
                    else:
                        go_room(code)
                        st.rerun()

    st.subheader("Active seshes 🔥")
    cols = st.columns(len(VIBE_TAGS) + 1)
    filters = ["All"] + list(VIBE_TAGS)
    for i, f in enumerate(filters):
        with cols[i % len(cols)]:
            if st.button(f, key=f"filter_{f}", use_container_width=True):
                st.session_state.vibe_filter = f

    vibe = None if st.session_state.vibe_filter == "All" else st.session_state.vibe_filter
    rooms = list_rooms(vibe)

    if not rooms:
        st.info("Nothing cooking yet — start a sesh!")
    for room in rooms:
        pin_badge = " 🔒" if room.get("has_pin") else ""
        tags = " · ".join(room.get("vibe_tags") or [])
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"**{room['title']}** `{room['code']}`{pin_badge}")
                if room.get("location"):
                    st.caption(f"📍 {room['location']}")
                if tags:
                    st.caption(f"🏷️ {tags}")
                if room.get("last_activity_at"):
                    st.caption(f"Active · {room['last_activity_at']}")
            with c2:
                st.caption(f"👥 {room['member_count']} in")
                st.caption(f"by {room['host_name']}")
                if st.button("Enter", key=f"enter_{room['code']}"):
                    go_room(room["code"])
                    st.rerun()

# ── ROOM ──────────────────────────────────────────────────────────────────────
elif st.session_state.page == "room":
    code = st.session_state.room_code
    if not code:
        st.warning("No room selected — go home and join one")
        if st.button("← Home"):
            go("home")
            st.rerun()
    else:

        @st.fragment(run_every=timedelta(seconds=4))
        def room_view() -> None:
            room = get_room(code)
            if not room:
                st.error("Room not found")
                if st.button("← Home"):
                    go("home")
                    st.rerun()
                return

            archived = room.get("is_archived")
            if archived:
                st.warning("This sesh is wrapped up — read-only for 24h")

            # Header
            st.markdown(f"## {room['title']}")
            st.code(room["code"], language=None)
            meta = f"Host: **{room['host_name']}** · 👥 {len(room['members'])}/{room['max_capacity']}"
            if room.get("location"):
                meta += f" · 📍 {room['location']}"
            if room.get("has_pin"):
                meta += " · 🔒 PIN"
            st.markdown(meta)
            if room.get("description"):
                st.caption(room["description"])

            if is_admin():
                st.info("🛡️ Admin view — you can read everything and join any room")
                admin_name = user() or "Admin"
                if not is_member(room, admin_name):
                    if st.button("Join this room as admin", type="primary"):
                        try:
                            st.session_state.user_name = admin_name
                            admin_join_room(code, admin_name)
                            st.success("Joined")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                elif not user():
                    st.session_state.user_name = "Admin"
                    st.rerun()

            # Join gate (regular users only)
            elif user() and not is_member(room, user()):
                st.divider()
                st.subheader("Pull up to the sesh")
                pin_val = None
                if room.get("has_pin"):
                    pin_val = st.text_input("Room PIN", max_chars=4, type="password")
                if st.button("I'm in 👊", type="primary"):
                    try:
                        join_room(code, user(), pin=pin_val)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                return

            if not can_use_room(room):
                if not user():
                    st.info("Set your name in the sidebar to join")
                return

            if not is_member(room, user()) and is_admin():
                # Admin spectating — read-only tabs below
                pass
            elif not is_member(room, user()):
                return

            read_only = archived or (is_admin() and not is_member(room, user() or "Admin"))
            # Status
            if not read_only and is_member(room, user()):
                st.caption("Your status")
                sc1, sc2, sc3 = st.columns(3)
                for col, (key, label) in zip([sc1, sc2, sc3], STATUS_LABELS.items()):
                    with col:
                        if st.button(label, key=f"status_{key}", use_container_width=True):
                            try:
                                update_status(code, user(), key)
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

            # Host actions
            if is_host(room, user()) and not read_only:
                with st.expander("Host controls"):
                    hc1, hc2 = st.columns(2)
                    with hc1:
                        others = [m["name"] for m in room["members"] if not names_match(m["name"], room["host_name"])]
                        if others:
                            new_host = st.selectbox("Pass host to", others)
                            if st.button("Pass host 👑"):
                                try:
                                    transfer_host(code, user(), new_host)
                                    st.success(f"Host passed to {new_host}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                    with hc2:
                        if st.button("Wrap up sesh (24h archive)"):
                            try:
                                end_room(code, user(), permanent=False)
                                st.success("Sesh wrapped up")
                                go("home")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                        if st.button("Delete forever", type="primary"):
                            try:
                                end_room(code, user(), permanent=True)
                                st.success("Sesh deleted")
                                go("home")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

            # Playlist
            if not read_only:
                with st.expander("🎵 Playlist"):
                    url = st.text_input("Spotify link", value=room.get("playlist_url") or "")
                    if st.button("Save playlist"):
                        try:
                            update_playlist(code, url.strip() or None)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            elif room.get("playlist_url"):
                st.link_button("🎵 Open playlist", room["playlist_url"])

            tab_chat, tab_list, tab_tab, tab_boys = st.tabs(["Yap 💬", "Grab list 🛒", "The tab 💸", "Boys 👊"])

            with tab_chat:
                if not room["messages"]:
                    st.info("Nobody's yapping yet — drop the first yap 💨")
                for msg in room["messages"]:
                    if msg.get("type") == "system" or msg["author"] == "System":
                        st.caption(f"● {msg['content']}")
                    else:
                        who = "You" if names_match(msg["author"], user()) else msg["author"]
                        st.markdown(f"**{who}:** {msg['content']}")
                if not read_only:
                    text = st.chat_input("Say something...")
                    if text:
                        try:
                            post_message(code, user(), text)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

            with tab_list:
                if not room["checklist"]:
                    st.info("Grab list is empty — add items below 🛒")
                for item in room["checklist"]:
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        claimed = item.get("claimed_by")
                        label = f"{'✅' if claimed else '⬜'} {item['item']}"
                        if claimed:
                            label += f" — _{claimed}_"
                        st.markdown(label)
                    with c2:
                        if not read_only:
                            if claimed and names_match(claimed, user()):
                                if st.button("Unclaim", key=f"unclaim_{item['id']}"):
                                    claim_checklist(code, item["id"], None)
                                    st.rerun()
                            elif not claimed:
                                if st.button("Claim", key=f"claim_{item['id']}"):
                                    claim_checklist(code, item["id"], user())
                                    st.rerun()
                if not read_only:
                    new_item = st.text_input("Add to grab list")
                    if st.button("Add item") and new_item.strip():
                        try:
                            add_checklist_item(code, new_item)
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

            with tab_tab:
                split = room["split"]
                m1, m2 = st.columns(2)
                m1.metric("Total spent", f"₹{split['total']:,.0f}")
                m2.metric("Per head", f"₹{split['perPerson']:,.0f}")

                if not room["expenses"]:
                    st.info("The tab is empty — log what was bought")

                if split["settleUp"]:
                    st.markdown("**Settle up (min transfers)**")
                    for t in split["settleUp"]:
                        st.markdown(f"- **{t['from']}** → **{t['to']}**: ₹{t['amount']:,.0f}")
                else:
                    st.success("Everyone's square ✓")

                for exp in room["expenses"]:
                    ec1, ec2, ec3 = st.columns([3, 1, 1])
                    ec1.markdown(f"**{exp['description']}** — paid by {exp['paid_by']}")
                    ec2.markdown(f"₹{exp['amount']:,.0f}")
                    if not read_only and st.button("🗑️", key=f"del_exp_{exp['id']}"):
                        delete_expense(code, exp["id"])
                        st.rerun()

                if not read_only:
                    with st.form("expense"):
                        desc = st.text_input("What was bought?")
                        amt = st.number_input("Amount (₹)", min_value=1.0, step=50.0)
                        if st.form_submit_button("Log it"):
                            try:
                                add_expense(code, desc, amt, user())
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

            with tab_boys:
                for m in room["members"]:
                    host_badge = " 👑" if names_match(m["name"], room["host_name"]) else ""
                    status = STATUS_LABELS.get(m.get("status", "here"), "")
                    block = f" · {m['block']}" if m.get("block") else ""
                    st.markdown(f"**{m['name']}**{host_badge}{block}  \n{status}")

        room_view()

# ── ADMIN ─────────────────────────────────────────────────────────────────────
elif st.session_state.page == "admin":
    if not is_admin():
        st.error("Admin access required — log in from the sidebar")
    else:
        st.header("🛡️ Admin panel")
        st.caption("All rooms and chats — join any sesh without PIN or capacity limits")

        rooms = admin_get_room_chats()
        total_msgs = sum(len(r.get("messages") or []) for r in rooms)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rooms", len(rooms))
        c2.metric("Total messages", total_msgs)
        c3.metric("Active", sum(1 for r in rooms if not r.get("is_archived")))

        if st.button("Join ALL rooms as Admin", type="primary"):
            admin_name = user() or "Admin"
            st.session_state.user_name = admin_name
            joined = 0
            for r in rooms:
                try:
                    admin_join_room(r["code"], admin_name)
                    joined += 1
                except Exception:
                    pass
            st.success(f"Joined {joined} room(s) as {admin_name}")
            st.rerun()

        st.divider()

        if not rooms:
            st.info("No rooms yet")
        for room in rooms:
            archived_tag = " · 📦 archived" if room.get("is_archived") else ""
            pin_tag = " · 🔒 PIN" if room.get("has_pin") else ""
            header = f"**{room['title']}** `{room['code']}`{archived_tag}{pin_tag}"
            with st.expander(f"{room['code']} — {room['title']} ({len(room.get('messages') or [])} msgs)"):
                st.markdown(header)
                st.caption(
                    f"Host: {room['host_name']} · 👥 {room['member_count']} · "
                    f"{room.get('user_message_count', 0)} user messages"
                )
                ac1, ac2 = st.columns(2)
                if ac1.button("Enter room", key=f"admin_enter_{room['code']}"):
                    go_room(room["code"])
                    st.rerun()
                if ac2.button("Join & enter", key=f"admin_join_{room['code']}"):
                    try:
                        name = user() or "Admin"
                        st.session_state.user_name = name
                        admin_join_room(room["code"], name)
                        go_room(room["code"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

                msgs = room.get("messages") or []
                if not msgs:
                    st.caption("No messages yet")
                else:
                    st.markdown("**Chat log**")
                    for msg in msgs:
                        if msg.get("type") == "system" or msg["author"] == "System":
                            st.caption(f"● [{msg['created_at']}] {msg['content']}")
                        else:
                            st.markdown(f"**{msg['author']}** ({msg['created_at']}): {msg['content']}")

# ── SELLERS ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "sellers":
    st.header("The Plugs 🔌")
    st.caption("Who's stocked, who's dry — sellers flip their own status")

    sellers = list_sellers()
    in_stock = sum(1 for s in sellers if s["available"])
    st.markdown(f"**{in_stock}** of **{len(sellers)}** plugs stocked rn")

    own = next((s for s in sellers if user() and names_match(s["name"], user())), None)

    if not own:
        st.subheader("You a plug?")
        st.caption("Get on the board — no account needed, just fill this in")
        with st.form("register_seller"):
            s_name = st.text_input(
                "Your name",
                value=st.session_state.user_name,
                placeholder="How people know you",
            )
            s_block = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick")
            s_contact = st.text_input("Contact (WhatsApp / Telegram)")
            s_note = st.text_area("What's available?")
            s_avail = st.checkbox("In stock", value=True)
            if st.form_submit_button("Go live on board 🌿", type="primary"):
                if not s_name.strip():
                    st.error("Enter your name in the form above")
                else:
                    try:
                        st.session_state.user_name = s_name.strip()
                        register_seller(
                            s_name.strip(),
                            s_block or None,
                            s_contact or None,
                            s_avail,
                            s_note or None,
                        )
                        st.success("You're on the board")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        st.divider()

    if not sellers:
        st.info("No sellers listed yet")
    for s in sellers:
        is_own = user() and names_match(s["name"], user())
        status = "Stocked 💨" if s["available"] else "Dry 😮‍💨"
        with st.container(border=True):
            st.markdown(f"### {s['name']} — {status}")
            if s.get("block"):
                st.caption(f"📍 {s['block']}")
            if s.get("note"):
                st.write(s["note"])
            if s.get("contact"):
                st.caption(f"💬 {s['contact']}")
            if s["available"] and s.get("stocked_at"):
                st.caption(f"Stocked since {s['stocked_at']}")
            if is_own:
                c1, c2 = st.columns(2)
                if c1.button("Mark in stock", key=f"stock_{s['id']}"):
                    try:
                        update_seller(s["id"], user(), available=True)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                if c2.button("Mark dry", key=f"dry_{s['id']}"):
                    try:
                        update_seller(s["id"], user(), available=False)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                if st.button("Remove listing", key=f"rm_{s['id']}"):
                    try:
                        delete_seller(s["id"], user())
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

# Deep link via query param ?room=CODE
qp = st.query_params.get("room")
if qp and isinstance(qp, str):
    go_room(qp.upper())
