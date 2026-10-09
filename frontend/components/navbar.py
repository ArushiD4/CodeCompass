"""Top bar shared by every page: brand lockup, user chip, action button."""
import streamlit as st
import state
from config import APP_NAME
from components.primitives import esc, pill


def _action(col, page):
    ss = st.session_state
    if page == "landing" or (page == "dashboard" and ss.get("guest_mode")):
        col.button("Sign in", key=f"nav_in_{page}", type="primary", width="stretch",
                   on_click=state.go, args=("auth",))
    elif page == "auth":
        col.button("Back", key="nav_back", width="stretch", on_click=state.go, args=("landing",))
    else:
        col.button("Sign out", key="nav_out", width="stretch", on_click=state.sign_out)


def render(page):
    ss = st.session_state
    brand, chips, action = st.columns([5, 5, 2], vertical_alignment="center")
    brand.html(f'<div class="cc-brand"><span class="cc-logo"></span>{esc(APP_NAME)}</div>')

    user_markup = ""
    if page == "dashboard" or ss.get("authenticated") or ss.get("guest_mode"):
        user_name = "Guest" if ss.get("guest_mode") else (ss.get("user_email") or "Developer")
        user_markup = pill(user_name, "info")
    chips.html(f'<div class="cc-chips">{user_markup}</div>')

    _action(action, page)
