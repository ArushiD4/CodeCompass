"""app.py — CodeCompass Streamlit Frontend Entry Point."""
import streamlit as st
from config import APP_NAME, TAGLINE

st.set_page_config(page_title=f"{APP_NAME} · {TAGLINE}", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")

import state  # noqa: E402  (must come after set_page_config)
import styles  # noqa: E402
from views import auth, dashboard, landing  # noqa: E402

ROUTES = {"landing": landing.render, "auth": auth.render, "dashboard": dashboard.render}


def main():
    """Main application loop executed on every Streamlit script rerun."""
    state.init()
    styles.inject()
    if st.session_state["_page"] == "dashboard" and not state.is_allowed():
        st.session_state["_page"] = "auth"
    ROUTES.get(st.session_state["_page"], landing.render)()


main()
