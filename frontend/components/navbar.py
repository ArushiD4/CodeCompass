"""Top bar shared by every page: brand lockup, platform links, user chip, action button."""
import streamlit as st
import state
from config import APP_NAME
from components.primitives import esc, pill


def _action(col, page):
    if page == "auth":
        col.button("Back", key="nav_back", width="stretch", on_click=state.go, args=("landing",))
    elif state.is_authenticated():
        col.button("Sign out", key=f"nav_out_{page}", width="stretch", on_click=state.sign_out)
    else:
        col.button("Sign in", key=f"nav_in_{page}", type="primary", width="stretch",
                   on_click=state.go, args=("auth",))


def render(page):
    ss = st.session_state
    brand, links, chips, action = st.columns([3, 4.5, 2.5, 2], vertical_alignment="center")
    brand.button(f"{APP_NAME}", key=f"nav_brand_{page}", on_click=state.go, args=("landing",),
                 help="Go to CodeCompass Home")

    has_dash = state.is_allowed() and page != "dashboard"
    cols = links.columns(3 if has_dash else 2)
    c_ab, c_fe = cols[0], cols[1]

    if page == "about":
        c_ab.button("Home", key="nav_home_ab", width="stretch", on_click=state.go, args=("landing",))
    else:
        c_ab.button("About", key=f"nav_ab_{page}", width="stretch", on_click=state.go, args=("about",))

    if page in ("roadmap", "future_enhancements"):
        c_fe.button("Home", key="nav_home_fe", width="stretch", on_click=state.go, args=("landing",))
    else:
        c_fe.button("Future Enhancements", key=f"nav_fe_{page}", width="stretch",
                    on_click=state.go, args=("future_enhancements",))

    if has_dash:
        cols[2].button("Dashboard", key=f"nav_dash_{page}", width="stretch",
                       on_click=state.go, args=("dashboard",))

    user_markup = ""
    if state.is_authenticated():
        user_markup = pill(ss.get("user_email") or "User", "good")
    elif state.is_offline():
        user_markup = pill("Developer (Offline)", "warn")
    elif state.is_guest():
        user_markup = pill("Guest", "info")
    chips.html(f'<div class="cc-chips">{user_markup}</div>')

    _action(action, page)
