"""intro.py — Full-bleed looping cinematic intro rendered via components.v1.html."""
import logging
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from config import INTRO_ENABLED

_logger = logging.getLogger(__name__)
_INTRO_PATH = Path(__file__).resolve().parent.parent / "assets" / "intro.html"
_INTRO_HTML = ""
if _INTRO_PATH.exists():
    try:
        _INTRO_HTML = _INTRO_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        _logger.warning("Failed to read intro animation asset: %s", exc)


def render():
    if not INTRO_ENABLED or not _INTRO_HTML:
        return
    with st.container(key="intro"):
        components.html(_INTRO_HTML, height=800, scrolling=False)
