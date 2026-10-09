"""intro.py — Cinematic 6-second intro rendered via components.v1.html."""
import os
import streamlit as st
import streamlit.components.v1 as components
from config import INTRO_ENABLED

_INTRO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "intro.html")
_INTRO_HTML = ""
if os.path.exists(_INTRO_PATH):
    try:
        with open(_INTRO_PATH, "r", encoding="utf-8") as f:
            _INTRO_HTML = f.read()
    except Exception:
        pass


def _skip():
    st.session_state["intro_seen"] = True


def render():
    if not INTRO_ENABLED or st.session_state.get("intro_seen", False):
        return False

    c_skip, _ = st.columns([1.5, 8.5])
    c_skip.button("Skip intro →", key="btn_skip_intro", on_click=_skip)
    if _INTRO_HTML:
        components.html(_INTRO_HTML, height=520, scrolling=False)
    return True
