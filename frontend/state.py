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
    "sample_audit_used": False, "auth_notice": "",
}
RESULT_KEYS = ("last_audit_data", "last_audit_path", "report_data",
               "graph_data", "graph_error", "file_facts")


def init():
    """Bootstraps session state with all required default keys."""
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def is_allowed():
    return st.session_state.get("authenticated") or st.session_state.get("guest_mode")


def is_authenticated() -> bool:
    """True only if the user has an active authenticated account session."""
    ss = st.session_state
    return bool(ss.get("authenticated") and not ss.get("offline_mode") and not ss.get("guest_mode"))


def is_offline() -> bool:
    """True if in Developer Offline Mode."""
    return bool(st.session_state.get("offline_mode"))


def is_guest() -> bool:
    """True if in guest sample audit mode."""
    return bool(st.session_state.get("guest_mode"))


def go(page):
    st.session_state["_page"] = page


def clear_results():
    """Purges all cached audit and report data."""
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)
    st.session_state["findings_limit"] = DEFAULTS["findings_limit"]


from entrypoints import entrypoint


@entrypoint()
def open_sample():
    """Guest entry callback for 'Run sample audit'."""
    ss = st.session_state
    if not ss.get("authenticated") and ss.get("sample_audit_used"):
        ss["auth_notice"] = (
            "You have already used your 1 free sample audit for this session. "
            "Please sign in or create an account to audit additional projects."
        )
        ss["_page"] = "auth"
        return

    if not os.path.exists(SAMPLE_PATH):
        st.error(f"Sample directory not found. Check SAMPLE_PATH in config.py ({SAMPLE_PATH})")
        return
    clear_results()
    folder_name = os.path.basename(SAMPLE_PATH)
    ss["_sample_in_flight"] = True
    ss.update(guest_mode=True, scan_name=f"Sample: {folder_name}",
              scan_path=SAMPLE_PATH, autorun=True, _page="dashboard", area="Audit")


@entrypoint()
def sign_out():
    """Terminates active session."""
    clear_results()
    st.session_state.update(authenticated=False, guest_mode=False, user_token=None,
                            user_email=None, offline_mode=False, _page="landing", area="Audit")

