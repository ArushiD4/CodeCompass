"""Top bar shared by every page: brand lockup, links, user chip, action button."""
import streamlit as st
import state
from config import APP_NAME
from components.primitives import pill

NAV_CSS = """
<style>
.st-key-navbar {
  width: 100% !important;
  margin-bottom: 0.75rem !important;
  position: relative !important;
  z-index: 10 !important;
}
.st-key-navbar [data-testid="stHorizontalBlock"] {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
}
.st-key-navbar [data-testid="column"] {
  display: flex !important;
  align-items: center !important;
  min-width: 0 !important;
}
.st-key-navbar [data-testid="stHorizontalBlock"] .stButton button,
.st-key-navbar [data-testid="stHorizontalBlock"] .stButton button p {
  white-space: nowrap !important;
  word-break: keep-all !important;
  overflow-wrap: normal !important;
}
.st-key-navbar .stButton {
  width: 100% !important;
}
.st-key-navbar .stButton button {
  min-width: max-content !important;
  padding: 0 1.1rem !important;
  height: 2.5rem !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.st-key-navbar div[class*="st-key-nav_brand"] button {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  min-width: auto !important;
  justify-content: flex-start !important;
  font-size: 1.15rem !important;
  font-weight: 700 !important;
}
.st-key-navbar div[class*="st-key-nav_brand"] button:hover {
  color: var(--brand) !important;
  transform: none !important;
  box-shadow: none !important;
}
.st-key-navbar .cc-chips {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
  width: 100% !important;
}
.st-key-navbar .cc-chips .cc-pill,
.st-key-navbar .cc-pill {
  white-space: nowrap !important;
  max-width: 220px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  display: inline-block !important;
  vertical-align: middle !important;
  line-height: 1.5 !important;
}
</style>
"""


def _brand(col, page):
    col.button(f"{APP_NAME}", key=f"nav_brand_{page}", on_click=state.go, args=("landing",),
               help="Go to CodeCompass Home")


def _l1(col, page):
    if page == "about":
        col.button("Home", key="nav_home_ab", width="stretch", on_click=state.go, args=("landing",))
    else:
        col.button("About", key=f"nav_ab_{page}", width="stretch", on_click=state.go, args=("about",))


def _l2(col, page):
    if page in ("roadmap", "future_enhancements"):
        col.button("Home", key="nav_home_fe", width="stretch", on_click=state.go, args=("landing",))
    else:
        col.button("Future Enhancements", key=f"nav_fe_{page}", width="stretch",
                   on_click=state.go, args=("future_enhancements",))


def _chip_markup():
    ss = st.session_state
    if state.is_authenticated():
        return pill(ss.get("user_email") or "User", "good")
    if state.is_offline():
        return pill("Developer (Offline)", "warn")
    if state.is_guest():
        return pill("Guest", "info")
    return ""


def render(page):
    with st.container(key="navbar"):
        st.html(NAV_CSS)
        if page == "auth":
            c_brand, _, c_act = st.columns([3, 7.8, 1.2], vertical_alignment="center")
            _brand(c_brand, page)
            c_act.button("Back", key="nav_back", width="stretch", on_click=state.go, args=("landing",))
            return

        if not state.is_authenticated():
            c_brand, c_ab, c_fe, _, c_act = st.columns([2.2, 1, 1.9, 4, 1], vertical_alignment="center")
            _brand(c_brand, page)
            _l1(c_ab, page)
            _l2(c_fe, page)
            c_act.button("Sign in", key=f"nav_in_{page}", type="primary", width="stretch",
                         on_click=state.go, args=("auth",))
            return

        has_dash = state.is_allowed() and page != "dashboard"
        if has_dash:
            c_b, c_ab, c_fe, c_d, _, c_cp, c_act = st.columns(
                [2.0, 0.9, 1.9, 1.1, 0.4, 2.2, 1.2], vertical_alignment="center")
            _brand(c_b, page)
            _l1(c_ab, page)
            _l2(c_fe, page)
            c_d.button("Dashboard", key=f"nav_dash_{page}", width="stretch",
                       on_click=state.go, args=("dashboard",))
            c_cp.html(f'<div class="cc-chips">{_chip_markup()}</div>')
            c_act.button("Sign out", key=f"nav_out_{page}", width="stretch", on_click=state.sign_out)
        else:
            c_b, c_ab, c_fe, _, c_cp, c_act = st.columns(
                [2, 1, 2, 0.4, 2.2, 1.2], vertical_alignment="center")
            _brand(c_b, page)
            _l1(c_ab, page)
            _l2(c_fe, page)
            c_cp.html(f'<div class="cc-chips">{_chip_markup()}</div>')
            c_act.button("Sign out", key=f"nav_out_{page}", width="stretch", on_click=state.sign_out)
