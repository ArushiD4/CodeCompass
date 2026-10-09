"""
state.py — Session State Management.

Defines the core session state schema (ARCHITECTURE.md section 5.1) and provides 
utility callbacks for navigation, state resetting, and guest session initialization.
"""
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
    """
    Bootstraps the Streamlit session state dictionary with all required default keys.
    Called once during the main app script execution.
    """
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_allowed():
    return st.session_state["authenticated"] or st.session_state["guest_mode"]


def go(page):
    """
    Navigation callback attached to interactive UI elements (buttons, links).
    Transitions the application to the specified page view on the next rerun.
    
    Args:
        page (str): The destination view identifier (e.g., 'auth', 'dashboard').
    """
    st.session_state["_page"] = page


def clear_results():
    """
    Purges all cached audit and report data from the active session state.
    Used before starting a fresh audit to ensure stale data is not displayed.
    """
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state["findings_limit"] = DEFAULTS["findings_limit"]


def open_sample():
    """
    Guest entry callback triggered from the landing page 'Run Sample Audit' button.
    
    Initializes a non-authenticated 'guest_mode' session, clears any prior data,
    pre-fills the scan form with the local sample snippet directory, and triggers
    an automatic initial scan upon reaching the dashboard.
    """
    clear_results()
    ss = st.session_state
    ss.update(guest_mode=True, scan_name="CodeCompass sample",
              scan_path=SAMPLE_PATH, autorun=True, _page="dashboard")


def sign_out():
    """
    Terminates the current session.
    
    Wipes all authentication tokens, clears cached audit results, and explicitly
    routes the user back to the public landing page.
    """
    clear_results()
    st.session_state.update(authenticated=False, guest_mode=False, user_token=None,
                            user_email=None, offline_mode=False, _page="landing")
