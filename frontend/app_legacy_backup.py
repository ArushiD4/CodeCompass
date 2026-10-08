""
app.py ΓÇö CodeCompass Streamlit frontend.

Navigation is state-driven via `st.session_state["_page"]`:
  "landing"   ΓÇö public landing page (default, unauthenticated)
  "auth"      ΓÇö login / sign-up / forgot-password card
  "dashboard" ΓÇö main application (requires authenticated=True OR offline_mode=True)

Session-state keys (all preserved):
  authenticated    bool
  user_token       str | None
  user_email       str | None
  last_audit_data  dict   ΓåÉ /api/audit response
  last_audit_path  str    ΓåÉ pre-fills call-graph path input
  report_data      dict   ΓåÉ /api/projects/{id} response
  graph_data       dict   ΓåÉ /api/graph response .graph object
  _page            str    ΓåÉ routing state (NEW)
  offline_mode     bool   ΓåÉ developer bypass flag (NEW)
"""

import os
import streamlit as st
import requests

# Auth functions ΓÇö unchanged signatures
from auth_service import (
    login_with_third_party,
    signup_with_third_party,
    reset_password_with_third_party,
)

# Shared design system
import importlib
import styles
try:
    importlib.reload(styles)
except Exception:
    pass

inject_styles = styles.inject_styles
COLORS = styles.COLORS
BUILTIN_EXCLUDE_LIST = getattr(styles, "BUILTIN_EXCLUDE_LIST", frozenset({
    "print", "len", "str", "int", "float", "dict", "list", "set", "tuple",
    "range", "enumerate", "zip", "open", "isinstance", "issubclass", "type",
    "super", "format", "hasattr", "getattr", "setattr", "delattr", "min", "max",
    "sum", "any", "all", "abs", "round", "repr", "id", "bool", "map", "filter",
    "sorted", "reversed", "iter", "next", "callable", "hash", "input",
}))
MODULE_PALETTE = getattr(styles, "MODULE_PALETTE", [
    "#2DD4BF", "#60A5FA", "#FBBF24", "#F87171", "#A78BFA", "#34D399", "#FB923C", "#38BDF8"
])

# Optional agraph for call graph visualisation
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_AVAILABLE = True
except ImportError:
    AGRAPH_AVAILABLE = False


def _patch_agraph_dark_theme() -> None:
    """Ensure streamlit-agraph's embedded iframe uses Deep Slate dark theme and large height."""
    try:
        import streamlit_agraph
        p = os.path.dirname(streamlit_agraph.__file__)
        html_path = os.path.join(p, "frontend", "build", "index.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
            dark_style = (
                "<style>html, body, #root, .vis-network { width: 100% !important; height: 100% !important; "
                "min-height: 850px !important; background-color: #0F172A !important; color: #E2E8F0 !important; } "
                ".vis-navigation { filter: invert(1) hue-rotate(180deg); opacity: 0.75; }</style>"
            )
            if "min-height: 850px" not in content:
                content = content.replace("</head>", f"{dark_style}</head>")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(content)
    except Exception:
        pass


if AGRAPH_AVAILABLE:
    _patch_agraph_dark_theme()

# ΓöÇΓöÇ Page config (must be the very first Streamlit call) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
st.set_page_config(
    page_title="CodeCompass",
    page_icon="≡ƒº¡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ΓöÇΓöÇ Initialise session state ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_DEFAULTS = {
    "authenticated": False,
    "user_token":    None,
    "user_email":    None,
    "_page":         "landing",
    "offline_mode":  False,
    "guest_mode":    False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ΓöÇΓöÇ Backend URL constant (can be overridden in the dashboard settings) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_DEFAULT_BACKEND = "http://localhost:8000"

# ΓöÇΓöÇ Path to the bundled sample snippet for the demo audit ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# Points to the directory containing sample_snippet.py so the backend's
# os.walk picks it up as a normal scan target.
_SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# Helper utilities
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _is_logged_in() -> bool:
    """Single canonical check for auth status ΓÇö used everywhere."""
    return bool(
        st.session_state.get("offline_mode")
        or st.session_state.get("authenticated")
    )


def _go(page: str) -> None:
    """Navigate to a page and rerun."""
    st.session_state["_page"] = page
    st.rerun()


def _logout() -> None:
    """Clear all auth state and return to landing."""
    st.session_state["authenticated"] = False
    st.session_state["guest_mode"]    = False
    st.session_state["user_token"]    = None
    st.session_state["user_email"]    = None
    st.session_state["offline_mode"]  = False
    st.session_state["_page"]         = "landing"
    # Clear stale data so the fresh session starts clean
    for key in ("last_audit_data", "last_audit_path", "report_data", "graph_data"):
        st.session_state.pop(key, None)
    st.rerun()


def _severity_chip(severity: str) -> str:
    """Return an HTML severity chip string."""
    s = severity.upper()
    cls = {
        "CRITICAL": "cc-chip-critical",
        "WARNING":  "cc-chip-warning",
        "INFO":     "cc-chip-info",
    }.get(s, "cc-chip-info")
    return f'<span class="cc-chip {cls}">{s}</span>'


def _crs_label(score: int) -> str:
    if score >= 80:
        return "≡ƒƒó Highly Ready"
    elif score >= 50:
        return "≡ƒƒí Needs Work"
    else:
        return "≡ƒö┤ Critical Issues Detected"


def _run_sample_audit(backend_url: str) -> bool:
    """
    Run the real backend audit against the bundled sample_snippet.py directory.
    Returns True on success, False on failure.
    Stores result in session_state["last_audit_data"], marks guest_mode=True, and navigates to dashboard.

    IMPORTANT: explicitly clears ALL prior audit result keys before the API call so
    stale data from a previous manual audit never bleeds into the sample-audit display.
    """
    # ΓöÇΓöÇ Purge all prior audit result state ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    for _stale_key in ("last_audit_data", "last_audit_path", "graph_data", "report_data"):
        st.session_state.pop(_stale_key, None)

    try:
        resp = requests.post(
            f"{backend_url}/api/audit",
            params={
                "project_name":  "Demo ΓÇö Sample Snippet",
                "directory_path": _SAMPLE_DIR,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["last_audit_data"] = data
            st.session_state["last_audit_path"] = _SAMPLE_DIR
            st.session_state["guest_mode"] = True
            st.session_state["authenticated"] = False
            st.session_state["_page"] = "dashboard"
            return True
        return False
    except Exception:
        return False


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# Persistent global navbar (landing + auth + dashboard)
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _render_global_navbar() -> None:
    """
    Unified global navbar rendered at the top of landing, auth, and dashboard views.
    - Brand / Wordmark: returns to 'landing' without clearing session.
    - Overview: returns to 'landing'.
    - Live Audit: routes to 'dashboard' (or 'auth' if not authenticated/guest).
    - Documentation: routes to 'dashboard' ('Γä╣∩╕Å  About' tab).
    - Auth section (right):
        * Authenticated: user pill + Logout button.
        * Guest mode: Guest badge + Sign In button.
        * Anonymous: Sign In button (or 'Back to Home' if currently on auth page).
    """
    user_email = st.session_state.get("user_email") or ""
    offline = st.session_state.get("offline_mode", False)
    logged_in = _is_logged_in()
    is_guest = st.session_state.get("guest_mode", False)
    current_page = st.session_state.get("_page", "landing")

    col_brand, col_links, col_auth = st.columns([2.6, 4.4, 3.0], gap="small")

    with col_brand:
        if st.button("≡ƒº¡ CodeCompass", key="nav_brand_btn", help="Return to Overview / Home"):
            _go("landing")

    with col_links:
        l1, l2, l3 = st.columns([1.1, 1.2, 1.6], gap="small")
        with l1:
            if st.button("Overview", key="nav_link_overview"):
                _go("landing")
        with l2:
            if st.button("Live Audit", key="nav_link_audit"):
                if logged_in or is_guest:
                    st.session_state["dashboard_nav"] = "≡ƒöì  Audit"
                    _go("dashboard")
                else:
                    _go("auth")
        with l3:
            if st.button("Documentation", key="nav_link_docs"):
                st.session_state["dashboard_nav"] = "Γä╣∩╕Å  About"
                if not (logged_in or is_guest):
                    st.session_state["guest_mode"] = True
                _go("dashboard")

    with col_auth:
        if logged_in:
            u_col, b_col = st.columns([1.8, 1.2], gap="small")
            with u_col:
                display = user_email or ("ΓÜí offline" if offline else "developer")
                st.markdown(
                    f'<div style="padding-top:6px;"><span class="cc-user-pill"><div class="cc-user-dot"></div>{display}</span></div>',
                    unsafe_allow_html=True,
                )
            with b_col:
                if st.button("Logout", key="logout_btn"):
                    _logout()
        elif is_guest:
            u_col, b_col = st.columns([1.6, 1.4], gap="small")
            with u_col:
                st.markdown(
                    '<div style="padding-top:6px;"><span class="cc-user-pill"><div class="cc-user-dot" style="background:#FBBF24;"></div>Guest</span></div>',
                    unsafe_allow_html=True,
                )
            with b_col:
                if st.button("Sign In ΓåÆ", key="nav_guest_signin_btn"):
                    _go("auth")
        else:
            if current_page == "auth":
                if st.button("ΓåÉ Back to Home", key="nav_anon_home_btn"):
                    _go("landing")
            else:
                if st.button("Sign In ΓåÆ", key="landing_nav_signin_btn"):
                    _go("auth")

    st.markdown("<hr class='cc-global-nav-divider'>", unsafe_allow_html=True)


def _render_navbar(show_dashboard_nav: bool = False, backend_url: str = _DEFAULT_BACKEND) -> str:
    """Backward compatibility wrapper around _render_global_navbar."""
    _render_global_navbar()
    return st.session_state.get("dashboard_nav", "≡ƒöì  Audit")


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# LANDING PAGE
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def landing_page() -> None:
    inject_styles()
    _render_global_navbar()

    # ΓöÇΓöÇ Hero ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    st.markdown("""
<div class="cc-hero">
  <div class="cc-hero-eyebrow">Static AST Analysis ┬╖ Viva Defense Companion</div>
  <h1 class="cc-hero-title">Know your code<br>before they ask about it.</h1>
  <p class="cc-hero-sub">
    CodeCompass scans your Python codebase with AST-level precision, surfaces
    hardcoded secrets, resource leaks, and silent exceptions, then arms you
    with the exact defense language to use in your project viva.
  </p>
</div>
""", unsafe_allow_html=True)

    # ΓöÇΓöÇ CTA row ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    _, cta_l, cta_r, _ = st.columns([1, 1.2, 1.2, 1])

    with cta_l:
        run_sample = st.button(
            "Γû╢ Run Sample Audit",
            key="landing_sample_btn",
            help="Audits a bundled snippet with all 4 anti-patterns ΓÇö no login or backend configuration needed.",
            use_container_width=True,
            type="primary",
        )

    with cta_r:
        if _is_logged_in() or st.session_state.get("guest_mode"):
            go_launch = st.button(
                "Launch App ΓåÆ",
                key="landing_launch_btn",
                use_container_width=True,
                type="primary",
            )
            if go_launch:
                _go("dashboard")
        else:
            go_signin = st.button(
                "Sign In ΓåÆ",
                key="landing_signin_btn",
                use_container_width=True,
                type="primary",
            )
            if go_signin:
                _go("auth")

    if run_sample:
        with st.spinner("Running sample audit against bundled snippetΓÇª"):
            ok = _run_sample_audit(_DEFAULT_BACKEND)
        if ok:
            st.success("Sample audit complete! Loading dashboardΓÇª")
            st.rerun()
        else:
            st.error(
                "Could not reach the backend at `http://localhost:8000`. "
                "Start the FastAPI server first, or use **Sign In ΓåÆ Developer Offline Mode** "
                "to explore the UI without a backend."
            )

    # ΓöÇΓöÇ Feature grid ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    st.markdown('<p class="cc-eyebrow" style="margin-top:40px;">Platform Features</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3, gap="medium")

    with f1:
        st.markdown("""
<div class="cc-feature-card">
  <div class="cc-feature-icon">≡ƒöì</div>
  <div class="cc-feature-title">AST Anti-Pattern Detection</div>
  <div class="cc-feature-body">
    Five rules powered by Python's standard-library <code>ast</code> module:
    hardcoded credentials, unclosed file handles, eval/exec injection risks,
    silent exception swallowing, and dead/orphaned functions.
  </div>
</div>
""", unsafe_allow_html=True)

    with f2:
        st.markdown("""
<div class="cc-feature-card">
  <div class="cc-feature-icon">≡ƒôè</div>
  <div class="cc-feature-title">Code Readiness Score</div>
  <div class="cc-feature-body">
    A single 0ΓÇô100 score computed from weighted deductions:
    CRITICAL issues cost 15 pts, WARNING costs 8 pts, INFO costs 3 pts.
    Persisted per-run in SQLite so you can track improvement across commits.
  </div>
</div>
""", unsafe_allow_html=True)

    with f3:
        st.markdown("""
<div class="cc-feature-card">
  <div class="cc-feature-icon">≡ƒò╕∩╕Å</div>
  <div class="cc-feature-title">Interactive Call Graph</div>
  <div class="cc-feature-body">
    AST-traversal callerΓåÆcallee relationship mapping rendered as a
    physics-based interactive network graph. Ideal for explaining
    your codebase structure out loud during a project defense.
  </div>
</div>
""", unsafe_allow_html=True)

    # ΓöÇΓöÇ Architecture comparison ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    st.markdown('<p class="cc-eyebrow" style="margin-top:40px;">Architecture</p>', unsafe_allow_html=True)
    st.markdown("""
<div class="cc-arch-table-wrap">
  <table class="cc-arch-table">
    <thead>
      <tr>
        <th>Concern</th>
        <th>CodeCompass approach</th>
        <th>Alternative (client-side)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Code parsing</td>
        <td>Python <code>ast</code> stdlib ΓÇö no dependencies, no sandboxing risk</td>
        <td>Browser-side JS parser ΓÇö limited to JS/TS, no Python AST</td>
      </tr>
      <tr>
        <td>Analysis execution</td>
        <td>FastAPI 0.141 / Uvicorn on localhost ΓÇö full Python runtime</td>
        <td>WebAssembly Pyodide ΓÇö slow startup, no filesystem access</td>
      </tr>
      <tr>
        <td>Persistence</td>
        <td>SQLite via SQLAlchemy 2.0 ORM ΓÇö zero-config, file-based</td>
        <td>Browser <code>localStorage</code> ΓÇö lost on tab close, size-capped</td>
      </tr>
      <tr>
        <td>Auth</td>
        <td>Firebase Identity Toolkit REST API with offline dev bypass</td>
        <td>N/A ΓÇö client-side tools are typically anonymous</td>
      </tr>
      <tr>
        <td>Graph rendering</td>
        <td><code>streamlit-agraph</code> / vis.js ΓÇö physics, hover, zoom</td>
        <td>Static Mermaid diagram ΓÇö no interaction</td>
      </tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# AUTH PAGE
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def auth_page() -> None:
    inject_styles()
    _render_global_navbar()

    st.markdown("""
<style>
.main .block-container { padding-top: var(--space-md) !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

    # Back link
    _, back_col, _ = st.columns([1, 2.4, 1])
    with back_col:
        if st.button("ΓåÉ Back to Home", key="auth_back_btn"):
            _go("landing")

    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.markdown("""
<div style="text-align:center; margin-bottom:4px;">
  <div class="cc-auth-wordmark">CodeCompass</div>
  <div class="cc-auth-sub">Static AST Code Auditing Platform</div>
</div>
<div class="cc-auth-accent-bar"></div>
""", unsafe_allow_html=True)

        with st.container(border=True):
            tab_login, tab_signup, tab_forgot = st.tabs(
                ["Sign In", "Sign up", "Forgot password"]
            )

            # ΓöÇΓöÇ Login ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
            with tab_login:
                st.caption("Welcome back. Enter your credentials to continue.")

                # ΓöÇΓöÇ Developer Offline Mode toggle ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
                offline_toggle = st.toggle(
                    "ΓÜí Developer offline mode",
                    value=st.session_state.get("offline_mode", False),
                    key="offline_toggle",
                    help="Bypasses Firebase auth. Grants a fake session that passes all downstream auth checks.",
                )
                if offline_toggle != st.session_state.get("offline_mode", False):
                    st.session_state["offline_mode"] = offline_toggle

                if st.session_state.get("offline_mode"):
                    st.info(
                        "**Offline mode active.** Click Launch App to enter without a real account. "
                        "All audit features require the FastAPI backend to be running."
                    )
                    _, btn_col, _ = st.columns([1, 2, 1])
                    with btn_col:
                        if st.button("Launch App ΓåÆ", key="offline_launch_btn", use_container_width=True, type="primary"):
                            st.session_state["authenticated"] = True
                            st.session_state["guest_mode"]    = False
                            st.session_state["user_email"]    = "developer@offline"
                            st.session_state["user_token"]    = "offline-token"
                            st.session_state["_page"]         = "dashboard"
                            st.rerun()
                else:
                    with st.form("login_form"):
                        email    = st.text_input("Email",    placeholder="you@example.com", key="login_email")
                        password = st.text_input("Password", type="password", placeholder="ΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇóΓÇó", key="login_password")
                        _, sbtn, _ = st.columns([1, 2, 1])
                        with sbtn:
                            submit = st.form_submit_button("Sign In ΓåÆ", use_container_width=True)

                    if submit:
                        if not email or not password:
                            st.error("Email and password are required.")
                        else:
                            result = login_with_third_party(email, password)
                            if result["success"]:
                                st.session_state["authenticated"] = True
                                st.session_state["guest_mode"]    = False
                                st.session_state["user_token"]    = result["token"]
                                st.session_state["user_email"]    = email
                                st.session_state["_page"]         = "dashboard"
                                st.success("Authenticated. Loading dashboardΓÇª")
                                st.rerun()
                            else:
                                st.error(f"Login failed: {result['error']}")

            # ΓöÇΓöÇ Sign up ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
            with tab_signup:
                st.caption("Create an account to start auditing.")
                with st.form("signup_form"):
                    new_email    = st.text_input("Email",    placeholder="you@example.com", key="signup_email")
                    new_password = st.text_input("Password", type="password", placeholder="Min. 6 characters", key="signup_password")
                    _, sbtn2, _ = st.columns([1, 2, 1])
                    with sbtn2:
                        submit_su = st.form_submit_button("Create account ΓåÆ", use_container_width=True)

                if submit_su:
                    if len(new_password) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        result = signup_with_third_party(new_email, new_password)
                        if result["success"]:
                            st.success("Account created! You can now log in.")
                        else:
                            st.error(f"Sign up failed: {result['error']}")

            # ΓöÇΓöÇ Forgot password ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
            with tab_forgot:
                st.caption("We'll send a reset link to your registered email.")
                with st.form("reset_form"):
                    reset_email = st.text_input("Registered email", placeholder="you@example.com", key="reset_email")
                    _, sbtn3, _ = st.columns([1, 2, 1])
                    with sbtn3:
                        submit_rp = st.form_submit_button("Send reset link ΓåÆ", use_container_width=True)

                if submit_rp:
                    if not reset_email:
                        st.error("Please enter an email address.")
                    else:
                        result = reset_password_with_third_party(reset_email)
                        if result["success"]:
                            st.success(f"Reset link sent to {reset_email}.")
                        else:
                            st.error(f"Error: {result['error']}")

        st.markdown("""
<p style="text-align:center;font-family:'JetBrains Mono',monospace;
          font-size:11px;color:#334155;margin-top:20px;">
  Static AST Auditor &mdash; Viva Prep Companion
</p>
""", unsafe_allow_html=True)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# DASHBOARD PAGE
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def dashboard_page() -> None:
    inject_styles()

    # Backend URL ΓÇö persisted in session so it survives tab switches
    if "backend_url" not in st.session_state:
        st.session_state["backend_url"] = _DEFAULT_BACKEND

    _render_global_navbar()

    if "dashboard_nav" not in st.session_state:
        st.session_state["dashboard_nav"] = "≡ƒöì  Audit"

    page = st.radio(
        "nav",
        ["≡ƒöì  Audit", "≡ƒôè  Reports", "Γä╣∩╕Å  About"],
        horizontal=True,
        label_visibility="collapsed",
        key="dashboard_nav",
    )
    st.markdown("<hr style='margin:4px 0 16px;border-color:#334155;'>", unsafe_allow_html=True)

    # Backend URL override (collapsed by default, does not clutter audit page)
    with st.expander("ΓÜÖ∩╕Å  Backend settings", expanded=False):
        new_url = st.text_input(
            "FastAPI base URL",
            value=st.session_state["backend_url"],
            key="backend_url_input",
        )
        if new_url != st.session_state["backend_url"]:
            st.session_state["backend_url"] = new_url

    backend_url = st.session_state["backend_url"]

    if page == "≡ƒöì  Audit":
        _page_audit(backend_url)
    elif page == "≡ƒôè  Reports":
        _page_reports(backend_url)
    elif page == "Γä╣∩╕Å  About":
        _page_about()


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# PAGE: AUDIT
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _page_audit(backend_url: str) -> None:
    st.markdown('<p class="cc-eyebrow">Static Analysis</p>', unsafe_allow_html=True)
    st.markdown("## Codebase AST Audit")
    st.caption("Scan a local Python codebase for anti-patterns, resource leaks, dynamic code injection, and orphaned functions.")

    # ΓöÇΓöÇ Audit form ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    with st.container():
        with st.form("audit_form"):
            col_a, col_b = st.columns([1, 2])
            with col_a:
                project_name = st.text_input(
                    "Project name",
                    value="CodeCompass AST",
                    placeholder="My Project",
                )
            with col_b:
                directory_path = st.text_input(
                    "Local directory path",
                    value=st.session_state.get("last_audit_path", r"d:\CodeCompass"),
                    placeholder=r"C:\path\to\your\project",
                )
            submit = st.form_submit_button("Γû╢ Run Audit Scan", type="primary")

    if submit:
        _run_audit(backend_url, project_name, directory_path)

    # ΓöÇΓöÇ Results ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    if "last_audit_data" not in st.session_state:
        st.markdown("""
<div class="cc-empty">
  <div class="cc-empty-icon">≡ƒöÄ</div>
  <div class="cc-empty-title">No audit results yet</div>
  <div class="cc-empty-sub">Run an audit above to see findings, score, and the call graph.</div>
</div>
""", unsafe_allow_html=True)
        return

    _render_audit_results()
    st.markdown("---")
    _render_call_graph_panel(backend_url)


def _run_audit(backend_url: str, project_name: str, directory_path: str) -> None:
    """POST to /api/audit, store result, show success or error."""
    if not project_name or not directory_path:
        st.error("Please provide both a project name and a codebase path.")
        return

    # Validate path exists before hitting backend
    if not os.path.isdir(directory_path):
        st.error(
            f"Directory not found: `{directory_path}`\n\n"
            "Please provide a path to an existing local directory."
        )
        return

    with st.spinner("Traversing AST and analysing code structuresΓÇª"):
        try:
            resp = requests.post(
                f"{backend_url}/api/audit",
                params={"project_name": project_name, "directory_path": directory_path},
                timeout=60,
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["last_audit_data"] = data
                st.session_state["last_audit_path"] = directory_path
                st.success(f"Audit complete ΓÇö saved as Project ID **{data.get('project_id')}**")
            else:
                st.error(
                    f"Backend returned error {resp.status_code}.\n\n"
                    f"```\n{resp.text[:500]}\n```"
                )
        except requests.exceptions.ConnectionError:
            st.error(
                f"**Backend unreachable** at `{backend_url}`.\n\n"
                "Is the FastAPI server running? Start it with:\n"
                "```\nuvicorn app.main:app --reload\n```"
            )
        except requests.exceptions.Timeout:
            st.error(
                "The audit request timed out after 60 s. "
                "The codebase may be very large ΓÇö try a more specific path."
            )
        except Exception as exc:
            st.error(f"Unexpected error: `{exc}`")


def _render_audit_results() -> None:
    """Render CRS band, metric cards, and two-column findings grid."""
    data   = st.session_state["last_audit_data"]
    issues = data.get("issues", [])
    crs    = data.get("crs_score", 100)

    # CRS hero band
    st.markdown(f"""
<div class="cc-crs-band">
  <p class="cc-crs-meta" style="margin-bottom:6px;">Code Readiness Score</p>
  <div class="cc-crs-score">{crs}<span class="cc-crs-denom">/100</span></div>
  <div class="cc-crs-label">{_crs_label(crs)}</div>
  <div class="cc-crs-meta">
    Project: {data.get('project_name', 'ΓÇö')} &nbsp;┬╖&nbsp; ID #{data.get('project_id', 'ΓÇö')}
  </div>
</div>
""", unsafe_allow_html=True)

    # Four metric cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CRS Score",       f"{crs}/100")
    c2.metric("Files Scanned",   data.get("total_files", 0))
    c3.metric("Issues Detected", data.get("issues_found", len(issues)))
    c4.metric("Functions Found", data.get("total_functions", 0))

    st.markdown("---")

    if not issues:
        st.markdown("""
<div class="cc-empty">
  <div class="cc-empty-icon">Γ£à</div>
  <div class="cc-empty-title">Clean codebase</div>
  <div class="cc-empty-sub">No anti-patterns or issues detected.</div>
</div>
""", unsafe_allow_html=True)
        return

    st.markdown('<p class="cc-eyebrow">Detected Anti-Patterns &amp; Defences</p>', unsafe_allow_html=True)

    critical_warn = [i for i in issues if i.get("severity") in ("CRITICAL", "WARNING")]
    info_items    = [i for i in issues if i.get("severity") == "INFO"]

    left_col, right_col = st.columns(2, gap="large")

    def _render_issues(issue_list: list, col_ctx) -> None:
        with col_ctx:
            if not issue_list:
                st.markdown("""
<div class="cc-empty" style="padding:20px;">
  <div class="cc-empty-icon" style="font-size:24px;">Γ£à</div>
  <div class="cc-empty-sub">No issues in this category.</div>
</div>
""", unsafe_allow_html=True)
                return
            for issue in issue_list:
                sev    = issue.get("severity", "INFO")
                rule   = issue.get("rule_name", "Anti-pattern")
                fpath  = issue.get("file_path", "unknown")
                lineno = issue.get("line_number", 0)
                tip    = issue.get("viva_tip", "No tip available.")
                chip   = _severity_chip(sev)

                with st.expander(f"{rule}  ┬╖  L{lineno}", expanded=False):
                    detail_col, tip_col = st.columns([1, 1], gap="medium")
                    with detail_col:
                        st.markdown(f"{chip}&nbsp; <strong>{rule}</strong>", unsafe_allow_html=True)
                        st.markdown(
                            f'**Location:** <span class="cc-file-mono">{fpath}</span> line {lineno}',
                            unsafe_allow_html=True,
                        )
                    with tip_col:
                        st.markdown('<p class="cc-eyebrow" style="margin-top:0;">≡ƒÄô Viva Defence</p>', unsafe_allow_html=True)
                        st.info(tip)

    with left_col:
        st.markdown('<p class="cc-eyebrow">Critical &amp; Warnings</p>', unsafe_allow_html=True)
        _render_issues(critical_warn, left_col)

    with right_col:
        st.markdown('<p class="cc-eyebrow">Info &amp; Dead Code</p>', unsafe_allow_html=True)
        _render_issues(info_items, right_col)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# CALL GRAPH SUB-PANEL
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _render_call_graph_panel(backend_url: str) -> None:
    st.markdown('<p class="cc-eyebrow">AST Traversal ΓÇö Call Graph</p>', unsafe_allow_html=True)

    default_path = st.session_state.get("last_audit_path", r"d:\CodeCompass")

    with st.container():
        col_path, col_btn = st.columns([4, 1])
        with col_path:
            directory_path = st.text_input(
                "Source directory path",
                value=default_path,
                key="graph_dir_input",
            )
        with col_btn:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            generate = st.button("Generate Graph", key="gen_graph_btn", type="primary")

    if generate:
        if not os.path.isdir(directory_path):
            st.error(f"Directory not found: `{directory_path}`")
        else:
            with st.spinner("Parsing function definitions and call treesΓÇª"):
                try:
                    resp = requests.get(
                        f"{backend_url}/api/graph",
                        params={"directory_path": directory_path},
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.session_state["graph_data"] = resp.json().get("graph", {})
                        st.success("Call graph loaded.")
                    else:
                        st.error(f"Error fetching call graph: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Backend unreachable at `{backend_url}`.")
                except Exception as exc:
                    st.error(f"Failed to connect to backend: `{exc}`")

    if "graph_data" not in st.session_state:
        return

    graph      = st.session_state["graph_data"]
    nodes_data = graph.get("nodes", [])
    edges_data = graph.get("edges", [])

    st.markdown(f"""
<div class="cc-graph-header">
  <span class="cc-graph-title">≡ƒò╕∩╕Å Interactive Call Graph</span>
  <span class="cc-graph-meta">
    {len(nodes_data)} total functions &nbsp;┬╖&nbsp; {len(edges_data)} calls detected
  </span>
</div>
""", unsafe_allow_html=True)

    if not nodes_data:
        st.markdown("""
<div class="cc-empty">
  <div class="cc-empty-icon">≡ƒô¡</div>
  <div class="cc-empty-title">No functions found</div>
  <div class="cc-empty-sub">No Python function definitions were found in the selected directory.</div>
</div>
""", unsafe_allow_html=True)
        return

    # ΓöÇΓöÇ Helper for module extraction ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    def _extract_module(file_str: str) -> str:
        clean = file_str.replace("\\", "/").strip("/")
        parts = clean.split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
        return parts[-1]

    # ΓöÇΓöÇ Part 4: Filtering Controls ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    with st.container():
        f_col1, f_col2, f_col3, f_col4 = st.columns([1.3, 1.2, 1.3, 2.2], gap="large")
        with f_col1:
            view_mode = st.radio(
                "View Mode",
                options=["All Functions", "Hubs Only"],
                index=0,
                horizontal=True,
                key="cg_view_mode",
                help="Show all functions in call graph or isolate top-K connected hub functions",
            )
        with f_col2:
            if view_mode == "Hubs Only":
                hub_k = st.slider(
                    "Top Hubs (K)",
                    min_value=3,
                    max_value=max(3, min(40, len(nodes_data))),
                    value=min(10, max(3, len(nodes_data))),
                    key="cg_hub_k",
                    help="Show top K functions with highest incoming + outgoing call volume",
                )
            else:
                hub_k = len(nodes_data)
                st.caption("Viewing complete call graph")
        with f_col3:
            min_deg = st.number_input(
                "Min Degree",
                min_value=1,
                max_value=50,
                value=1,
                step=1,
                key="cg_min_deg",
                help="Only show nodes with (incoming + outgoing calls) ΓëÑ this value",
            )
        with f_col4:
            layout_mode = st.selectbox(
                "Layout Mode",
                options=["Force-Directed (Barnes-Hut)", "Hierarchical (Caller ΓåÆ Callee)"],
                index=0,
                key="cg_layout_mode",
                help="Force-directed for cluster discovery or Hierarchical for caller-to-callee pipeline",
            )

    exclude_builtins = st.checkbox(
        "Exclude Python built-in calls (`print`, `len`, `open`, `range`, `dict`, etc.)",
        value=True,
        key="cg_exclude_builtins",
        help="Filters out low-signal standard library calls so application logic is visible",
    )

    # ΓöÇΓöÇ Filter Edges by Builtin List ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    if exclude_builtins:
        active_edges = [e for e in edges_data if e["callee"] not in BUILTIN_EXCLUDE_LIST]
    else:
        active_edges = list(edges_data)

    # ΓöÇΓöÇ Degree Calculation & Orphan Identification ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    # Map function label and ID
    label_to_id = {n["label"]: n["id"] for n in nodes_data}
    node_by_id  = {n["id"]: n for n in nodes_data}

    in_degree: dict = {}
    out_degree: dict = {}

    for e in active_edges:
        caller_id = e["caller"]
        callee_label = e["callee"]
        target_id = label_to_id.get(callee_label, f"ext::{callee_label}")

        out_degree[caller_id] = out_degree.get(caller_id, 0) + 1
        in_degree[target_id] = in_degree.get(target_id, 0) + 1

    def _get_node_degree(nid: str, label: str) -> int:
        return out_degree.get(nid, 0) + in_degree.get(nid, 0) + in_degree.get(label, 0)

    # Detect orphaned application functions (zero calls made or received)
    orphans = [n for n in nodes_data if _get_node_degree(n["id"], n["label"]) == 0]
    connected_user_nodes = [n for n in nodes_data if _get_node_degree(n["id"], n["label"]) > 0]

    # Apply Degree Threshold
    degree_filtered = [
        n for n in connected_user_nodes
        if _get_node_degree(n["id"], n["label"]) >= min_deg
    ]

    # Apply Hubs Filter
    if view_mode == "Hubs Only":
        # Sort by total degree descending
        degree_filtered.sort(key=lambda n: _get_node_degree(n["id"], n["label"]), reverse=True)
        visible_user_nodes = degree_filtered[:hub_k]
    else:
        visible_user_nodes = degree_filtered

    visible_ids = {n["id"] for n in visible_user_nodes}
    visible_labels = {n["label"] for n in visible_user_nodes}

    # Prune edges to those between visible nodes
    render_edges = []
    seen_edge_keys = set()
    referenced_externals = set()

    for e in active_edges:
        caller_id = e["caller"]
        callee_label = e["callee"]

        if caller_id in visible_ids:
            if callee_label in visible_labels:
                target_id = label_to_id[callee_label]
            elif not exclude_builtins or callee_label not in BUILTIN_EXCLUDE_LIST:
                target_id = f"ext::{callee_label}"
                referenced_externals.add(callee_label)
            else:
                continue

            edge_key = (caller_id, target_id)
            if edge_key not in seen_edge_keys:
                seen_edge_keys.add(edge_key)
                render_edges.append((caller_id, target_id, e["line"]))

    # ΓöÇΓöÇ Status Line ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    filter_desc = []
    if view_mode == "Hubs Only":
        filter_desc.append(f"top {len(visible_user_nodes)} hubs")
    if min_deg > 1:
        filter_desc.append(f"degree ΓëÑ {min_deg}")
    if exclude_builtins:
        filter_desc.append("builtins excluded")
    desc_str = f" ({', '.join(filter_desc)})" if filter_desc else " (full connected view)"

    st.markdown(f"""
<div class="cc-graph-status">
  <span>Displaying <span class="cc-graph-status-count">{len(visible_user_nodes)}</span> of {len(nodes_data)} functions{desc_str}</span>
  <span style="font-family:var(--font-mono); font-size:12px; opacity:0.8;">{len(render_edges)} active call paths</span>
</div>
""", unsafe_allow_html=True)

    # ΓöÇΓöÇ Part 3: Module Color Mapping & Sizing ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    unique_modules = sorted(list({_extract_module(n["file"]) for n in visible_user_nodes}))
    module_color_map = {
        mod: MODULE_PALETTE[i % len(MODULE_PALETTE)]
        for i, mod in enumerate(unique_modules)
    }

    # Render module color legend
    if unique_modules:
        legend_html = '<div class="cc-module-legend">'
        for mod, col in module_color_map.items():
            legend_html += f'<span class="cc-module-badge"><span class="cc-module-dot" style="background:{col};"></span>{mod}</span>'
        if referenced_externals:
            legend_html += f'<span class="cc-module-badge"><span class="cc-module-dot" style="background:#475569;"></span>external/library</span>'
        legend_html += '</div>'
        st.markdown(legend_html, unsafe_allow_html=True)

    # ΓöÇΓöÇ Render Graph or Tabular Fallback ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    if AGRAPH_AVAILABLE:
        nodes: list = []
        edges: list = []

        # Build application function nodes
        for nv in visible_user_nodes:
            nid   = nv["id"]
            label = nv["label"]
            deg   = _get_node_degree(nid, label)
            # Size scaled dynamically with degree
            node_size = min(36, max(15, 13 + int(deg * 2.2)))
            mod   = _extract_module(nv["file"])
            color = module_color_map.get(mod, COLORS["accent"])

            nodes.append(Node(
                id=nid,
                label=label,
                size=node_size,
                color=color,
                font={
                    "size": 12,
                    "color": "#F8FAFC",
                    "face": "Inter",
                    "strokeWidth": 2,
                    "strokeColor": "#0F172A",
                },
                title=f"Function: {label}\nFile: {nv['file']}:{nv['line']}\nModule: {mod}\nTotal Calls (Degree): {deg}",
            ))

        # Build external library nodes (if any referenced)
        for ext in sorted(referenced_externals):
            ext_id = f"ext::{ext}"
            nodes.append(Node(
                id=ext_id,
                label=ext,
                size=12,
                color="#334155",
                font={
                    "size": 10,
                    "color": COLORS["text_secondary"],
                    "face": "Inter",
                },
                title=f"External / Library Call: {ext}",
            ))

        # Build edges
        for caller_id, target_id, line in render_edges:
            edges.append(Edge(
                source=caller_id,
                target=target_id,
                type="CURVED",
                color={"color": "#64748B", "highlight": COLORS["accent"], "opacity": 0.45},
            ))

        # ΓöÇΓöÇ Part 1 & Part 2: Container Theme & Physics Config ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        is_hierarchical = (layout_mode == "Hierarchical (Caller ΓåÆ Callee)")

        physics_cfg = {
            "enabled": not is_hierarchical,
            "barnesHut": {
                "gravitationalConstant": -14000,
                "centralGravity": 0.35,
                "springLength": 190,
                "springConstant": 0.04,
                "damping": 0.09,
            },
            "stabilization": {
                "enabled": True,
                "iterations": 300,
                "fit": True,
                "updateInterval": 25,
            },
        }

        hierarchical_cfg = {
            "enabled": is_hierarchical,
            "direction": "UD",
            "sortMethod": "directed",
            "levelSeparation": 150,
            "nodeSpacing": 140,
            "treeSpacing": 200,
            "blockShifting": True,
            "edgeMinimization": True,
            "parentCentralization": True,
        }

        graph_config = Config(
            width="100%",
            height=850,
            directed=True,
            # NOTE: do NOT pass physics= as a top-level bool ΓÇö it overrides the
            # kwargs "physics" dict and silently disables stabilization.fit centering.
            # The full kwargs dict below is the sole physics configuration.
            hierarchical=is_hierarchical,
            backgroundColor=COLORS["bg"],
            kwargs={
                "physics": physics_cfg if not is_hierarchical else {"enabled": False},
                "layout": {"hierarchical": hierarchical_cfg},
                "nodes": {
                    "borderWidth": 2,
                    "borderWidthSelected": 4,
                    "shadow": {"enabled": True, "color": "rgba(0,0,0,0.5)", "size": 6},
                },
                "edges": {
                    "smooth": {"type": "continuous" if not is_hierarchical else "cubicBezier"},
                    "arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
                },
                "interaction": {
                    "navigationButtons": True,
                    "tooltipDelay": 150,
                    "hover": True,
                    "zoomView": True,
                },
            },
        )

        st.caption("≡ƒöì Drag nodes to inspect ┬╖ Scroll to zoom ┬╖ Hover for module and line number")
        st.markdown('<div class="cc-agraph-wrap">', unsafe_allow_html=True)
        try:
            agraph(nodes=nodes, edges=edges, config=graph_config)
        except Exception as e:
            st.warning(f"Interactive graph rendered tabular fallback: {e}")
            st.table([{"Function": n["label"], "File": n["file"], "Line": n["line"]} for n in visible_user_nodes])
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("≡ƒÆí `streamlit-agraph` is unavailable. Showing tabular representation.")
        st.markdown('<p class="cc-eyebrow">Defined Functions (Nodes)</p>', unsafe_allow_html=True)
        st.table([
            {"Function": n["label"], "File": n["file"], "Line": n["line"]}
            for n in visible_user_nodes
        ])
        if render_edges:
            st.markdown('<p class="cc-eyebrow">Function Invocations (Edges)</p>', unsafe_allow_html=True)
            st.table([{
                "Caller": src.split("::")[-1],
                "Target": tgt.replace("ext::", "").split("::")[-1],
                "Line":   line,
            } for src, tgt, line in render_edges])

    # ΓöÇΓöÇ Orphaned Functions Section (Outside Canvas) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
    if orphans:
        st.markdown(f"""
<div class="cc-orphan-box">
  <div class="cc-orphan-title">ΓÜá∩╕Å {len(orphans)} Orphaned Functions (No Invocations Detected)</div>
  <div class="cc-orphan-chips">
    {''.join(f'<span class="cc-orphan-chip">ΓÜÖ∩╕Å {o["label"]} <span style="opacity:0.6;">({_extract_module(o["file"])})</span></span>' for o in orphans)}
  </div>
</div>
""", unsafe_allow_html=True)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# PAGE: REPORTS
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _page_reports(backend_url: str) -> None:
    st.markdown('<p class="cc-eyebrow">Historical Analysis</p>', unsafe_allow_html=True)
    st.markdown("## Project Audit Reports")
    st.caption("Retrieve saved audit reports by Project ID from the SQLite database.")

    with st.container():
        col_id, col_btn = st.columns([1, 3])
        with col_id:
            project_id = st.number_input("Project ID", min_value=1, value=1, step=1)
        with col_btn:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            fetch = st.button("Fetch Report", key="fetch_report_btn", type="primary")

    if fetch:
        with st.spinner("Fetching from databaseΓÇª"):
            try:
                resp = requests.get(
                    f"{backend_url}/api/projects/{project_id}",
                    timeout=10,
                )
                if resp.status_code == 200:
                    st.session_state["report_data"] = resp.json()
                    st.success("Report retrieved.")
                elif resp.status_code == 404:
                    st.warning(f"Project ID `{project_id}` not found. Try IDs 1ΓÇô7.")
                else:
                    st.error(f"Backend error {resp.status_code}: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error(f"Backend unreachable at `{backend_url}`.")
            except Exception as exc:
                st.error(f"Failed to connect to backend: `{exc}`")

    if "report_data" not in st.session_state:
        st.markdown("""
<div class="cc-empty">
  <div class="cc-empty-icon">≡ƒôé</div>
  <div class="cc-empty-title">No report loaded</div>
  <div class="cc-empty-sub">Enter a Project ID and click "Fetch Report".</div>
</div>
""", unsafe_allow_html=True)
        return

    data    = st.session_state["report_data"]
    project = data.get("project", {})
    issues  = data.get("issues", [])
    crs     = project.get("crs_score", 0)

    st.markdown(f"""
<div class="cc-crs-band">
  <p class="cc-crs-meta" style="margin-bottom:6px;">Report ΓÇö {project.get('project_name', 'Unknown')}</p>
  <div class="cc-crs-score">{crs}<span class="cc-crs-denom">/100</span></div>
  <div class="cc-crs-label">{_crs_label(crs)}</div>
  <div class="cc-crs-meta">Audited: {project.get('created_at', 'N/A')}</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.metric("Total Files",     project.get("total_files", 0))
    col2.metric("Total Functions", project.get("total_functions", 0))

    st.markdown("---")
    st.markdown('<p class="cc-eyebrow">Issue Log</p>', unsafe_allow_html=True)

    if not issues:
        st.markdown("""
<div class="cc-empty">
  <div class="cc-empty-icon">Γ£à</div>
  <div class="cc-empty-title">No issues in this project.</div>
  <div class="cc-empty-sub">The scanned codebase was clean.</div>
</div>
""", unsafe_allow_html=True)
        return

    for issue in issues:
        sev    = issue.get("severity", "INFO")
        rule   = issue.get("rule_name", "Anti-pattern")
        fpath  = issue.get("file_path", "unknown")
        lineno = issue.get("line_number", 0)
        tip    = issue.get("viva_tip", "No tip available.")
        chip   = _severity_chip(sev)
        emoji  = {"CRITICAL": "≡ƒö┤", "WARNING": "≡ƒƒí"}.get(sev.upper(), "≡ƒö╡")

        with st.expander(f"{emoji} {rule}  ┬╖  {fpath}  (L{lineno})"):
            col_l, _ = st.columns([3, 1])
            with col_l:
                st.markdown(f"{chip}&nbsp; **{rule}**", unsafe_allow_html=True)
                st.markdown(
                    f'**Location:** <span class="cc-file-mono">{fpath}</span> line {lineno}',
                    unsafe_allow_html=True,
                )
            st.markdown("<hr style='margin:10px 0;border-color:#334155;'>", unsafe_allow_html=True)
            st.info(f"≡ƒÄô **Viva Defence Tip:**\n\n{tip}")


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# PAGE: ABOUT
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

def _page_about() -> None:
    st.markdown('<p class="cc-eyebrow">Platform Information</p>', unsafe_allow_html=True)
    st.markdown("## About CodeCompass")
    st.caption("System architecture, benchmarks, and target audience.")

    with st.expander("≡ƒÅù∩╕Å  System Architecture", expanded=True):
        st.markdown("""
<div class="cc-about-section">
<h3>Stack Overview</h3>
<p>
CodeCompass is a two-process, single-machine developer tool.
A <strong>Streamlit 1.62</strong> frontend handles all user interaction and
a <strong>FastAPI 0.141 / Uvicorn 0.52</strong> backend owns AST analysis,
persistence, and API serving. The two processes communicate over HTTP on
<code>localhost:8000</code> (backend) and <code>localhost:8501</code> (frontend).
</p>

<h3>Static Analysis Engine</h3>
<p>
The backend traverses the target directory with <code>os.walk</code>, parsing
each <code>.py</code> file into a Python AST via the standard-library
<code>ast</code> module. A custom <code>ast.NodeVisitor</code> subclass
(<code>StaticAntiPatternAuditor</code>) then visits every node, applying
five detection rules:
</p>
<ul>
<li><strong>Hardcoded Credential</strong> ΓÇö <code>visit_Assign</code>: flags string literals
    assigned to variables whose names contain KEY, SECRET, PASSWORD, TOKEN, AUTH, PASS, or CREDENTIAL.</li>
<li><strong>Unclosed Resource Handle</strong> ΓÇö <code>visit_Call</code>: flags bare
    <code>open()</code> calls not wrapped in a <code>with</code> context manager.</li>
<li><strong>Dynamic Code Injection Risk</strong> ΓÇö <code>visit_Call</code>: flags
    any use of <code>eval()</code> or <code>exec()</code>.</li>
<li><strong>Silent Exception Swallowing</strong> ΓÇö <code>visit_ExceptHandler</code>: flags
    <code>except: pass</code> blocks that suppress all errors silently.</li>
<li><strong>Orphaned Function</strong> ΓÇö post-traversal: functions defined but never called
    within the scanned path (excluding known entrypoints such as
    <code>main</code>, <code>get_db</code>, <code>run_audit</code>).</li>
</ul>

<h3>Code Readiness Score (CRS)</h3>
<p>Scored out of 100, floored at 0. Deductions per finding:</p>
<ul>
<li>CRITICAL &nbsp;ΓåÆ&nbsp; <strong>ΓêÆ15 pts</strong></li>
<li>WARNING &nbsp;ΓåÆ&nbsp; <strong>ΓêÆ8 pts</strong></li>
<li>INFO &nbsp;ΓåÆ&nbsp; <strong>ΓêÆ3 pts</strong></li>
</ul>

<h3>Call Graph Engine</h3>
<p>
A second AST visitor (<code>CallGraphVisitor</code>) tracks the currently-scoped
function and records every <code>ast.Call</code> node it encounters inside that
scope, building a directed graph of caller ΓåÆ callee relationships.
The graph is rendered interactively using <strong>streamlit-agraph 0.0.45</strong>
(vis.js under the hood), with an automatic tabular fallback when the library is
unavailable.
</p>

<h3>Persistence</h3>
<p><strong>SQLite</strong> via <strong>SQLAlchemy 2.0</strong> ORM. Two tables:</p>
<ul>
<li><code>projects</code> ΓÇö one row per audit run (name, CRS score, file/function counts, timestamp)</li>
<li><code>audit_issues</code> ΓÇö one row per detected issue, foreign-keyed to
    <code>projects.id</code> with <code>CASCADE</code> delete</li>
</ul>

<h3>Authentication</h3>
<p>
Firebase Identity Toolkit REST API (<code>identitytoolkit.googleapis.com</code>)
for login, sign-up, and password reset. A developer offline mode bypasses all
network calls and grants a fake session that passes every downstream auth check.
</p>
</div>

<div class="cc-arch-row">
  <span class="cc-arch-badge">Python 3.x</span>
  <span class="cc-arch-badge">Streamlit 1.62</span>
  <span class="cc-arch-badge">FastAPI 0.141</span>
  <span class="cc-arch-badge">Uvicorn 0.52</span>
  <span class="cc-arch-badge">SQLAlchemy 2.0</span>
  <span class="cc-arch-badge">SQLite</span>
  <span class="cc-arch-badge">ast (stdlib)</span>
  <span class="cc-arch-badge">streamlit-agraph 0.0.45</span>
  <span class="cc-arch-badge">Firebase Auth (REST)</span>
</div>
""", unsafe_allow_html=True)

    with st.expander("≡ƒôè  Benchmarks", expanded=False):
        st.markdown("""
<div class="cc-about-section">
<h3>Observed Scan Results</h3>
<p>Figures drawn from actual audit runs stored in the project database.
Placeholder values are marked <code>[TBD]</code>.</p>
<ul>
<li><strong>CodeCompass backend (7 Python files, 12 functions)</strong>
    ΓÇö CRS score: <strong>66/100</strong>, 8 issues detected, &lt;1 s scan time.</li>
<li><strong>Blockchain PoS sample repo (9 files, 7 functions)</strong>
    ΓÇö CRS score: <strong>100/100</strong>, 0 issues, &lt;1 s scan time.</li>
<li><strong>Medium project (10 files, 17 functions)</strong>
    ΓÇö CRS score: <strong>51/100</strong>, scan time &lt;1 s.</li>
<li><strong>Demo fixture (1 file, 3 functions, 4 anti-patterns)</strong>
    ΓÇö CRS score: <strong>38/100</strong>, 7 issues (4 direct + 3 orphaned), &lt;0.1 s.</li>
<li><strong>Large repo (~4,800 files)</strong> ΓÇö scan time <code>[TBD]</code>.</li>
</ul>
<h3>Known Limitation</h3>
<p>
Always pass a well-scoped <code>directory_path</code>. The backend excludes
<code>venv</code> / <code>.venv</code> / <code>ccenv</code> folder names by default,
but scanning a directory that contains a large virtual environment may still
produce inflated counts and fill the database (see Projects #3 and #4).
</p>
</div>
""", unsafe_allow_html=True)

    with st.expander("≡ƒÄô  Target Audience", expanded=False):
        st.markdown("""
<div class="cc-about-section">
<h3>Who CodeCompass Is Built For</h3>
<p>
CodeCompass is positioned as a <em>Viva Prep Companion</em> for computer science
and software engineering students who must defend their submitted code in an oral
examination. Examiners probe for understanding of design decisions, security
awareness, and code quality ΓÇö and students who cannot explain <em>why</em> they
wrote their code a certain way lose marks, even if the code works correctly.
</p>

<h3>Primary Users</h3>
<ul>
<li><strong>CS / Software Engineering students</strong> preparing for end-of-module
    or final-year project vivas. The "Viva Defence Tip" attached to every finding
    gives them the vocabulary to justify each issue to an examiner.</li>
<li><strong>Instructors and lab demonstrators</strong> who wish to review student
    submissions at scale and produce a reproducible quality score (CRS).</li>
</ul>

<h3>What CodeCompass Is Not</h3>
<ul>
<li>Not a production-grade linter ΓÇö targets student-common anti-patterns only.</li>
<li>Does not perform runtime analysis, type inference, or inter-procedural data-flow.</li>
<li>Currently supports <strong>Python only</strong>.</li>
</ul>

<h3>Ideal Use Case</h3>
<p>
Run CodeCompass the evening before your viva. Review every CRITICAL and WARNING
finding; read the Viva Defence Tip out loud; understand whether the issue is a
genuine flaw you should fix or an accepted trade-off you can defend. Use the CRS
score as a conversation-starter with your supervisor.
</p>
</div>
""", unsafe_allow_html=True)


# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
# ROUTING ΓÇö state-driven, no raw reloads
# ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

_page = st.session_state.get("_page", "landing")

# Guard: if authenticated and on auth page, push to dashboard (allow landing page visit!)
if _is_logged_in() and _page == "auth":
    st.session_state["_page"] = "dashboard"
    _page = "dashboard"

# Guard: if on dashboard without auth or guest mode, redirect to auth
if _page == "dashboard" and not (_is_logged_in() or st.session_state.get("guest_mode")):
    st.session_state["_page"] = "auth"
    _page = "auth"

if _page == "landing":
    landing_page()
elif _page == "auth":
    auth_page()
elif _page == "dashboard":
    dashboard_page()
else:
    st.session_state["_page"] = "landing"
    st.rerun()
