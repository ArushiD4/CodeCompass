"""Adapter between the UI and your existing auth_service.py.

No Firebase logic lives here. If your auth_service.py names its functions
differently, edit FUNCTION_NAMES below. Nothing else needs to change.
Expected return shape (ARCHITECTURE.md 5.2): {"success": bool, "token", "user_id", "error"}
"""
import streamlit as st
from config import OFFLINE_EMAIL, OFFLINE_TOKEN

try:
    import auth_service
    _IMPORT_ERROR = None
except Exception as exc:  # missing file, bad path or a config error at import time
    auth_service, _IMPORT_ERROR = None, str(exc)

# Exact function names from frontend/auth_service.py (verified against git HEAD).
# Return shapes:
#   login_with_third_party  -> {"success": bool, "token": str, "user_id": str}
#   signup_with_third_party -> {"success": bool}  (no token on sign-up)
#   reset_password_with_third_party -> {"success": bool}
FUNCTION_NAMES = {
    "sign_in": ("login_with_third_party",),
    "sign_up": ("signup_with_third_party",),
    "reset":   ("reset_password_with_third_party",),
}


def _call(action, *args):
    if auth_service is None:
        return {"success": False, "error": f"auth_service.py could not be imported: {_IMPORT_ERROR}"}
    for name in FUNCTION_NAMES[action]:
        func = getattr(auth_service, name, None)
        if callable(func):
            try:
                result = func(*args)
            except Exception as exc:
                return {"success": False, "error": f"auth_service.{name} failed: {exc}"}
            return result if isinstance(result, dict) else {"success": bool(result)}
    return {"success": False, "error": f"auth_service.py has none of {FUNCTION_NAMES[action]}. "
                                       "Edit FUNCTION_NAMES in auth_bridge.py."}


def _start_session(email, token):
    st.session_state.update(authenticated=True, guest_mode=False, user_email=email,
                            user_token=token, _page="dashboard")


def _finish(result, email):
    if result.get("success"):
        _start_session(email, result.get("token"))
        return True, ""
    return False, result.get("error") or "Authentication failed."


def enter_offline():
    """Developer Offline Mode: no network call at all (section 5.2)."""
    st.session_state["offline_mode"] = True
    _start_session(OFFLINE_EMAIL, OFFLINE_TOKEN)


def sign_in(email, password):
    if st.session_state["offline_mode"]:
        enter_offline()
        return True, ""
    return _finish(_call("sign_in", email, password), email)


def sign_up(email, password):
    return _finish(_call("sign_up", email, password), email)


def reset_password(email):
    result = _call("reset", email)
    return bool(result.get("success")), result.get("error") or ""
