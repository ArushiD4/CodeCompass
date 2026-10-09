"""
auth_bridge.py — Authentication UI Adapter.

Provides a standardized interface between the Streamlit UI components and the 
underlying authentication service (Firebase). Isolates the frontend views from 
implementation-specific authentication logic and manages session state hydration 
upon successful login.

Expected return shape (ARCHITECTURE.md 5.2): {"success": bool, "token": str, "user_id": str, "error": str}
"""
import streamlit as st
from config import OFFLINE_EMAIL, OFFLINE_TOKEN
from entrypoints import entrypoint

try:
    import auth_service
    _IMPORT_ERROR = None
except Exception as exc:  # missing file, bad path or a config error at import time
    auth_service, _IMPORT_ERROR = None, str(exc)

# Direct calls to auth_service replacing previous getattr/FUNCTION_NAMES indirection.


def _start_session(email, token):
    st.session_state.update(authenticated=True, guest_mode=False, user_email=email,
                            user_token=token, _page="dashboard")


def _finish(result, email):
    if result.get("success"):
        _start_session(email, result.get("token"))
        return True, ""
    return False, result.get("error") or "Authentication failed."


def enter_offline():
    """
    Developer Offline Mode initializer (Architecture section 5.2).
    
    Bypasses external network calls entirely, hydrating the session state with
    a mock developer identity and routing directly to the dashboard.
    """
    st.session_state["offline_mode"] = True
    _start_session(OFFLINE_EMAIL, OFFLINE_TOKEN)


@entrypoint()
def sign_in(email, password):
    if st.session_state.get("offline_mode"):
        enter_offline()
        return True, ""
    if auth_service is None:
        return False, f"auth_service could not be imported: {_IMPORT_ERROR}"
    try:
        result = auth_service.login_with_third_party(email, password)
    except Exception as exc:
        return False, f"auth_service.login_with_third_party failed: {exc}"
    return _finish(result, email)


@entrypoint()
def sign_up(email, password):
    if auth_service is None:
        return False, f"auth_service could not be imported: {_IMPORT_ERROR}"
    try:
        result = auth_service.signup_with_third_party(email, password)
    except Exception as exc:
        return False, f"auth_service.signup_with_third_party failed: {exc}"
    return _finish(result, email)


@entrypoint()
def reset_password(email):
    if auth_service is None:
        return False, f"auth_service could not be imported: {_IMPORT_ERROR}"
    try:
        result = auth_service.reset_password_with_third_party(email)
    except Exception as exc:
        return False, f"auth_service.reset_password_with_third_party failed: {exc}"
    if result.get("success"):
        return True, ""
    return False, result.get("error") or "Password reset failed."

