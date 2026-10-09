"""CodeCompass frontend entry point: routes between views by session state."""
import streamlit as st

st.set_page_config(page_title="CodeCompass", page_icon="🧭", layout="wide",
                   initial_sidebar_state="collapsed")

import state  # noqa: E402  (must come after set_page_config)
import styles  # noqa: E402
from views import auth, dashboard, landing  # noqa: E402

ROUTES = {"landing": landing.render, "auth": auth.render, "dashboard": dashboard.render}


def main():
    state.init()
    styles.inject()
    if st.session_state["_page"] == "dashboard" and not state.is_allowed():
        st.session_state["_page"] = "auth"  # route guard
    ROUTES.get(st.session_state["_page"], landing.render)()


main()
