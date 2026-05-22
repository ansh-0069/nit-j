"""NIT-JOINT — Streamlit app for coordinating college seshes."""

from __future__ import annotations

from datetime import timedelta

import streamlit as st

from nit_joint.constants import HOSTEL_BLOCKS, STATUS_LABELS, VIBE_TAGS
from nit_joint.db import (
    add_checklist_item,
    add_expense,
    claim_checklist,
    create_room,
    delete_expense,
    delete_seller,
    end_room,
    get_room,
    init_db,
    join_room,
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

            # Join gate
            if user() and not is_member(room, user()):
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

            if not user():
                st.info("Set your name in the sidebar to join")
                return

            if not is_member(room, user()):
                return

            # Status
            if not archived:
                my = next((m for m in room["members"] if names_match(m["name"], user())), None)
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
            if is_host(room, user()) and not archived:
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
            if not archived:
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
                if not archived:
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
                        if not archived:
                            if claimed and names_match(claimed, user()):
                                if st.button("Unclaim", key=f"unclaim_{item['id']}"):
                                    claim_checklist(code, item["id"], None)
                                    st.rerun()
                            elif not claimed:
                                if st.button("Claim", key=f"claim_{item['id']}"):
                                    claim_checklist(code, item["id"], user())
                                    st.rerun()
                if not archived:
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
                    if not archived and st.button("🗑️", key=f"del_exp_{exp['id']}"):
                        delete_expense(code, exp["id"])
                        st.rerun()

                if not archived:
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

# ── SELLERS ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "sellers":
    st.header("The Plugs 🔌")
    st.caption("Who's stocked, who's dry — sellers flip their own status")

    sellers = list_sellers()
    in_stock = sum(1 for s in sellers if s["available"])
    st.markdown(f"**{in_stock}** of **{len(sellers)}** plugs stocked rn")

    own = next((s for s in sellers if user() and names_match(s["name"], user())), None)

    if not own and user():
        with st.expander("List me up 🌿"):
            with st.form("register_seller"):
                s_block = st.selectbox("Block", [""] + HOSTEL_BLOCKS, format_func=lambda x: x or "Pick")
                s_contact = st.text_input("Contact (WhatsApp / Telegram)")
                s_note = st.text_area("What's available?")
                s_avail = st.checkbox("In stock", value=True)
                if st.form_submit_button("Go live"):
                    try:
                        register_seller(user(), s_block or None, s_contact or None, s_avail, s_note or None)
                        st.success("You're on the board")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

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
