"""
app.py — CodeCompass Streamlit Frontend Entry Point.

This module serves as the primary router and orchestrator for the Streamlit application.
It initializes the session state, injects global CSS styling, enforces navigation guards 
(authentication checks), and dispatches rendering to the appropriate view based on the 
current state.
"""
import streamlit as st

st.set_page_config(page_title="CodeCompass", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")

import state  # noqa: E402  (must come after set_page_config)
import styles  # noqa: E402
from views import auth, dashboard, landing  # noqa: E402

ROUTES = {"landing": landing.render, "auth": auth.render, "dashboard": dashboard.render}


def main():
    """
    Main application loop executed on every Streamlit script rerun.
    
    Responsibilities:
      1. Initialize default session state variables.
      2. Inject dynamic global CSS.
      3. Enforce auth guards (redirects unauthenticated users to the auth view).
      4. Render the currently active page.
    """
    state.init()
    styles.inject()
    if st.session_state["_page"] == "dashboard" and not state.is_allowed():
        st.session_state["_page"] = "auth"  # route guard
    ROUTES.get(st.session_state["_page"], landing.render)()


main()
