"""state.py — Session State Management."""
import os
import streamlit as st
from config import BACKEND_URL, SAMPLE_PATH

DEFAULTS = {
    "_page": "landing", "area": "Audit",
    "authenticated": False, "guest_mode": False,
    "user_token": None, "user_email": None, "offline_mode": False,
    "backend_url": os.environ.get("CODECOMPASS_BACKEND_URL", BACKEND_URL),
    "scan_name": "", "scan_path": "",
    "findings_limit": 8, "section": "Findings",
}
RESULT_KEYS = ("last_audit_data", "last_audit_path", "report_data",
               "graph_data", "graph_error", "file_facts")


def init():
    """Bootstraps session state with all required default keys."""
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_allowed():
    return st.session_state.get("authenticated") or st.session_state.get("guest_mode")


def go(page):
    st.session_state["_page"] = page


def clear_results():
    """Purges all cached audit and report data."""
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state["findings_limit"] = DEFAULTS["findings_limit"]


def open_sample():
    """Guest entry callback for 'Run sample audit'."""
    if not os.path.exists(SAMPLE_PATH):
        st.error(f"Sample directory not found. Check SAMPLE_PATH in config.py ({SAMPLE_PATH})")
        return
    clear_results()
    folder_name = os.path.basename(SAMPLE_PATH)
    ss = st.session_state
    ss.update(guest_mode=True, scan_name=f"Sample: {folder_name}",
              scan_path=SAMPLE_PATH, autorun=True, _page="dashboard", area="Audit")


def sign_out():
    """Terminates active session."""
    clear_results()
    st.session_state.update(authenticated=False, guest_mode=False, user_token=None,
                            user_email=None, offline_mode=False, _page="landing", area="Audit")
