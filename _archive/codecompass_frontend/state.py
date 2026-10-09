"""Session-state schema (ARCHITECTURE.md section 5.1) and navigation callbacks."""
import streamlit as st
from config import BACKEND_URL, SAMPLE_PATH

DEFAULTS = {
    "_page": "landing", "authenticated": False, "guest_mode": False,
    "user_token": None, "user_email": None, "offline_mode": False,
    "backend_url": BACKEND_URL, "scan_name": "", "scan_path": "",
    "findings_limit": 8,
}
RESULT_KEYS = ("last_audit_data", "last_audit_path", "report_data",
               "graph_data", "graph_error")


def init():
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_allowed():
    return st.session_state["authenticated"] or st.session_state["guest_mode"]


def go(page):
    """on_click callback: switch the visible page."""
    st.session_state["_page"] = page


def clear_results():
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state["findings_limit"] = DEFAULTS["findings_limit"]


def open_sample():
    """Guest entry from the landing page: prefill the form and auto-run once."""
    clear_results()
    ss = st.session_state
    ss.update(guest_mode=True, scan_name="CodeCompass sample",
              scan_path=SAMPLE_PATH, autorun=True, _page="dashboard")


def sign_out():
    clear_results()
    st.session_state.update(authenticated=False, guest_mode=False, user_token=None,
                            user_email=None, offline_mode=False, _page="landing")
