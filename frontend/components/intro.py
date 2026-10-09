"""intro.py — Full-bleed looping cinematic intro rendered via components.v1.html."""
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


def render():
    if not INTRO_ENABLED or not _INTRO_HTML:
        return
    with st.container(key="intro"):
        components.html(_INTRO_HTML, height=800, scrolling=False)
