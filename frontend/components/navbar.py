"""Top bar shared by every page: brand, backend status, settings, main action."""
import streamlit as st
import api_client
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
    brand, chips, settings, action = st.columns([4, 5, 1.7, 1.7], vertical_alignment="center")
    brand.html(f'<div class="cc-brand"><span class="cc-logo"></span>{esc(APP_NAME)}</div>')
    online = api_client.health()
    markup = pill("Backend online" if online else "Backend offline",
                  "good" if online else "bad", dot=True)
    if page == "dashboard":
        markup += pill("Guest" if ss.get("guest_mode") else (ss.get("user_email") or "Developer"), "info")
    chips.html(f'<div class="cc-chips">{markup}</div>')
    with settings.popover("Settings", icon=":material/settings:", width="stretch"):
        st.text_input("Backend URL", key="backend_url", help="FastAPI base URL, default port 8000")
    _action(action, page)
