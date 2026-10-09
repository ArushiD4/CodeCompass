"""
tests/test_frontend.py — Streamlit AppTest regression tests.

Run:  pytest tests/test_frontend.py -v  (from d:\\CodeCompass)

Requires: streamlit >= 1.18 (AppTest introduced), pytest.
"""
import os
import sys
import pytest

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
sys.path.insert(0, FRONTEND_DIR)

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(FRONTEND_DIR, "app.py")

# ── HTML tag leak detection ───────────────────────────────────────────────────
# Bug A: HTML leaking as literal text means st.markdown() was called WITHOUT
# unsafe_allow_html=True, or HTML ended up in st.write()/st.text() which do
# not parse HTML at all. We check specifically for tag pairs in those paths.
# Markdown elements with allow_html=True are intentional and must NOT be flagged.
_SUSPICIOUS_TAG_PAIRS = [
    ("<h3>", "</h3>"),
    ("<h2>", "</h2>"),
    ("<ul>", "</ul>"),
    ("<li>", "</li>"),
]


def _no_exception(at: AppTest, context: str = "") -> None:
    """
    Assert no exceptions in the AppTest tree.
    at.exception is an ElementList (never None in Streamlit 1.62),
    so we check its length instead of is-None.
    """
    exc_list = at.exception
    assert len(exc_list) == 0, (
        f"App raised {len(exc_list)} exception(s){' (' + context + ')' if context else ''}:\n"
        + "\n".join(str(e) for e in exc_list)
    )


def _ss(at: AppTest, key: str, default=None):
    """
    Safe session-state accessor — AppTest's session_state does not support .get().
    Use direct key access with a try/except instead.
    """
    try:
        return at.session_state[key]
    except (KeyError, AttributeError):
        return default


def _check_no_raw_html(at: AppTest, context: str = "") -> None:
    """
    Assert that no literal unrendered HTML tag PAIRS appear in render paths
    that do NOT support HTML rendering.

    Bug A = HTML tag pairs leaking into:
      - st.markdown() called WITHOUT unsafe_allow_html=True  (allow_html=False)
      - st.text() / st.caption() — these never parse HTML

    HTML inside st.markdown(html, unsafe_allow_html=True) is intentional and
    is correctly rendered by the browser — we MUST NOT flag those.
    """
    non_html_pieces = []

    # Only collect markdown elements where allow_html is explicitly False
    for md in at.markdown:
        # AppTest Markdown elements have an allow_html attribute
        allow_html = getattr(md, "allow_html", True)  # default True = don't flag
        if not allow_html:
            v = md.value if hasattr(md, "value") else str(md)
            non_html_pieces.append(v)

    # caption and text never parse HTML — always flag
    for cap in at.caption:
        v = cap.value if hasattr(cap, "value") else str(cap)
        non_html_pieces.append(v)
    for txt in at.text:
        v = txt.value if hasattr(txt, "value") else str(txt)
        non_html_pieces.append(v)

    combined = "\n".join(non_html_pieces)
    for open_tag, close_tag in _SUSPICIOUS_TAG_PAIRS:
        if open_tag in combined and close_tag in combined:
            assert False, (
                f"Raw HTML pair '{open_tag}...{close_tag}' found in non-HTML render path"
                f"{' (' + context + ')' if context else ''}.\n"
                f"This means HTML was passed to st.markdown() without unsafe_allow_html=True "
                f"or was placed in st.text()/st.caption().\n"
                f"Snippet: {combined[:400]}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# T1: App boots without exceptions
# ─────────────────────────────────────────────────────────────────────────────

def test_app_boots_without_exception():
    """App must boot and render the landing page without raising any exception."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "boot")


# ─────────────────────────────────────────────────────────────────────────────
# T2: Landing page renders correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_landing_page_renders():
    """Landing page must render without exceptions and contain key UI elements."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing page")

    button_labels = [btn.label for btn in at.button]
    assert any("Sample Audit" in lbl or "Run" in lbl for lbl in button_labels), (
        f"'Run Sample Audit' button not found. Buttons: {button_labels}"
    )
    assert any("Sign In" in lbl for lbl in button_labels), (
        f"'Sign In' button not found. Buttons: {button_labels}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# T3: No raw HTML tags in landing page output
# ─────────────────────────────────────────────────────────────────────────────

def test_no_raw_html_on_landing():
    """Regression for Bug A — no literal HTML tag pairs in rendered markdown/text."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing")
    _check_no_raw_html(at, "landing page")


# ─────────────────────────────────────────────────────────────────────────────
# T4: Landing → Auth navigation
# ─────────────────────────────────────────────────────────────────────────────

def test_landing_to_auth_navigation():
    """Clicking 'Sign In' on the landing page must set _page to 'auth'."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing pre-click")

    signin_btns = [btn for btn in at.button if "Sign In" in btn.label]
    assert signin_btns, "Sign In button not found on landing page"

    signin_btns[0].click().run()
    _no_exception(at, "after Sign In click")
    assert _ss(at, "_page") == "auth", (
        f"Expected _page='auth' after clicking Sign In, got: {_ss(at, '_page')}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# T5: No raw HTML on auth page
# ─────────────────────────────────────────────────────────────────────────────

def test_no_raw_html_on_auth():
    """Regression for Bug A on the auth page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "auth"
    at.run()
    _no_exception(at, "auth page")
    _check_no_raw_html(at, "auth page")


# ─────────────────────────────────────────────────────────────────────────────
# T6: Offline developer mode reaches dashboard
# ─────────────────────────────────────────────────────────────────────────────

def test_offline_mode_reaches_dashboard():
    """
    Setting offline_mode=True and authenticated=True in session state before
    run() should directly reach the dashboard (the routing guard redirects
    landing/auth → dashboard when _is_logged_in() is True).
    """
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]         = "dashboard"
    at.session_state["offline_mode"]  = True
    at.session_state["authenticated"] = True
    at.session_state["user_email"]    = "developer@offline"
    at.session_state["user_token"]    = "offline-token"
    at.run()
    _no_exception(at, "offline mode dashboard")
    # If we're on the dashboard, the logout button should be visible
    logout_btns = [btn for btn in at.button if "Logout" in btn.label]
    assert logout_btns, "Dashboard did not render — Logout button not found"
    assert _ss(at, "_page") == "dashboard"


# ─────────────────────────────────────────────────────────────────────────────
# T7: Dashboard renders without exception in offline mode
# ─────────────────────────────────────────────────────────────────────────────

def test_dashboard_renders_in_offline_mode():
    """Dashboard must render without exceptions in offline mode."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]         = "dashboard"
    at.session_state["authenticated"]  = True
    at.session_state["offline_mode"]   = True
    at.session_state["user_email"]     = "developer@offline"
    at.run()
    _no_exception(at, "dashboard offline mode")


# ─────────────────────────────────────────────────────────────────────────────
# T8: No raw HTML on dashboard
# ─────────────────────────────────────────────────────────────────────────────

def test_no_raw_html_on_dashboard():
    """Regression for Bug A on the dashboard page."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]          = "dashboard"
    at.session_state["authenticated"]   = True
    at.session_state["offline_mode"]    = True
    at.session_state["user_email"]      = "test@example.com"
    at.run()
    _no_exception(at, "dashboard")
    _check_no_raw_html(at, "dashboard page")


# ─────────────────────────────────────────────────────────────────────────────
# T9: Dashboard with mock audit data renders without exception
# ─────────────────────────────────────────────────────────────────────────────

def test_dashboard_with_audit_data():
    """Pre-loading last_audit_data must render the results section without exception."""
    mock_audit_data = {
        "status": "success",
        "project_id": 999,
        "project_name": "Test Project",
        "crs_score": 55,
        "total_files": 3,
        "total_functions": 5,
        "issues_found": 2,
        "issues": [
            {
                "rule_name": "Hardcoded Credential",
                "severity": "CRITICAL",
                "file_path": "test.py",
                "line_number": 5,
                "viva_tip": "Use environment variables for secrets.",
            },
            {
                "rule_name": "Orphaned Function",
                "severity": "INFO",
                "file_path": "Global Codebase",
                "line_number": 0,
                "viva_tip": "Dead code explanation.",
            },
        ],
    }

    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]           = "dashboard"
    at.session_state["authenticated"]    = True
    at.session_state["offline_mode"]     = True
    at.session_state["user_email"]       = "test@example.com"
    at.session_state["last_audit_data"]  = mock_audit_data
    at.session_state["last_audit_path"]  = r"C:\fake"
    at.run()
    _no_exception(at, "dashboard with audit data")
    _check_no_raw_html(at, "dashboard with audit data")


# ─────────────────────────────────────────────────────────────────────────────
# T10: Logout clears auth state and returns to landing
# ─────────────────────────────────────────────────────────────────────────────

def test_logout_returns_to_landing():
    """Clicking Logout must clear auth state and set _page back to 'landing'."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]          = "dashboard"
    at.session_state["authenticated"]   = True
    at.session_state["offline_mode"]    = True
    at.session_state["user_email"]      = "test@example.com"
    at.run()
    _no_exception(at, "dashboard pre-logout")

    logout_btns = [btn for btn in at.button if "Logout" in btn.label]
    assert logout_btns, f"Logout button not found. Buttons: {[b.label for b in at.button]}"

    logout_btns[0].click().run()
    _no_exception(at, "after Logout click")
    assert _ss(at, "authenticated") is False
    assert _ss(at, "_page") == "landing"


# ─────────────────────────────────────────────────────────────────────────────
# T11: Guest mode in dashboard does NOT show logout button (Bug 3 regression)
# ─────────────────────────────────────────────────────────────────────────────

def test_guest_mode_no_logout():
    """In guest mode (Sample Audit session), dashboard must NOT show a Logout button."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]         = "dashboard"
    at.session_state["guest_mode"]    = True
    at.session_state["authenticated"] = False
    at.session_state["offline_mode"]  = False
    at.run()
    _no_exception(at, "guest mode dashboard")
    logout_btns = [btn for btn in at.button if "Logout" in btn.label]
    assert len(logout_btns) == 0, (
        f"Logout button unexpectedly shown in guest mode! Found: {[b.label for b in logout_btns]}"
    )
    assert _ss(at, "authenticated") is False


# ─────────────────────────────────────────────────────────────────────────────
# T12: Authenticated user can visit landing page and return via Launch App (Bug 4 regression)
# ─────────────────────────────────────────────────────────────────────────────

def test_authenticated_can_visit_landing_and_return():
    """Authenticated user can visit 'landing' without being logged out and re-enter dashboard."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"]         = "landing"
    at.session_state["authenticated"] = True
    at.session_state["offline_mode"]  = True
    at.session_state["user_email"]    = "developer@offline"
    at.run()
    _no_exception(at, "authenticated user on landing")

    assert _ss(at, "_page") == "landing", f"Expected _page='landing', got {_ss(at, '_page')}"
    assert _ss(at, "authenticated") is True

    # "Launch App →" button should be present
    launch_btns = [btn for btn in at.button if "Launch App" in btn.label]
    assert launch_btns, f"'Launch App' button not found on landing for authenticated user: {[b.label for b in at.button]}"

    launch_btns[0].click().run()
    _no_exception(at, "after Launch App click")
    assert _ss(at, "_page") == "dashboard"
    assert _ss(at, "authenticated") is True


# ─────────────────────────────────────────────────────────────────────────────
# T13: Global navbar links navigate correctly (Bug 5 regression)
# ─────────────────────────────────────────────────────────────────────────────

def test_global_navbar_navigation():
    """Global navbar links (Overview, Live Audit, Documentation) navigate properly."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "landing"
    at.run()
    _no_exception(at, "landing navbar check")

    # Documentation should route to About tab
    docs_btns = [btn for btn in at.button if "Documentation" in btn.label]
    assert docs_btns, f"Documentation link not found in navbar: {[b.label for b in at.button]}"
    docs_btns[0].click().run()
    _no_exception(at, "after Documentation click")
    assert _ss(at, "_page") == "dashboard"
    assert _ss(at, "dashboard_nav") == "ℹ️  About"

    # From dashboard, clicking Overview in navbar returns to landing
    overview_btns = [btn for btn in at.button if "Overview" in btn.label]
    assert overview_btns, f"Overview link not found in navbar: {[b.label for b in at.button]}"
    overview_btns[0].click().run()
    _no_exception(at, "after Overview click")
    assert _ss(at, "_page") == "landing"


# ─────────────────────────────────────────────────────────────────────────────
# T14: Directory input pre-fill behavior (blank on load/sample, manual persists)
# ─────────────────────────────────────────────────────────────────────────────

def test_audit_input_prefill_behavior():
    """Directory inputs must be blank on first load and after sample audit,

    pre-filling only when the user has executed a real manual audit.
    """
    sample_dir = os.path.abspath(FRONTEND_DIR)

    # 1. Fresh dashboard load: directory input must be blank
    at1 = AppTest.from_file(APP_PATH, default_timeout=30)
    at1.session_state["_page"] = "dashboard"
    at1.session_state["authenticated"] = True
    at1.session_state["offline_mode"] = True
    at1.run()
    _no_exception(at1, "fresh dashboard load")
    dir_inputs = [ti for ti in at1.text_input if ti.label == "Local directory path"]
    assert dir_inputs, "Local directory path text input not found"
    assert dir_inputs[0].value == "", f"Expected blank directory input on first load, got {dir_inputs[0].value!r}"

    # 2. After sample audit (last_audit_path is sample_dir): both inputs must remain blank
    at2 = AppTest.from_file(APP_PATH, default_timeout=30)
    at2.session_state["_page"] = "dashboard"
    at2.session_state["authenticated"] = True
    at2.session_state["offline_mode"] = True
    at2.session_state["last_audit_data"] = {
        "project_id": 99,
        "project_name": "Demo — Sample Snippet",
        "crs_score": 85,
        "total_files": 1,
        "issues_found": 0,
        "total_functions": 1,
        "issues": [],
    }
    at2.session_state["last_audit_path"] = sample_dir
    at2.run()
    _no_exception(at2, "after sample audit load")
    audit_inputs = [ti for ti in at2.text_input if ti.label == "Local directory path"]
    assert audit_inputs and audit_inputs[0].value == "", (
        f"Expected blank audit path after sample audit, got {audit_inputs[0].value!r}"
    )
    graph_inputs = [ti for ti in at2.text_input if ti.label == "Source directory path"]
    assert graph_inputs and graph_inputs[0].value == "", (
        f"Expected blank graph path after sample audit, got {graph_inputs[0].value!r}"
    )

    # 3. After real manual audit: inputs must pre-fill with the manual audit path
    manual_path = r"C:\path\to\my_project"
    at3 = AppTest.from_file(APP_PATH, default_timeout=30)
    at3.session_state["_page"] = "dashboard"
    at3.session_state["authenticated"] = True
    at3.session_state["offline_mode"] = True
    at3.session_state["last_audit_data"] = {
        "project_id": 100,
        "project_name": "Manual Scan",
        "crs_score": 90,
        "total_files": 3,
        "issues_found": 1,
        "total_functions": 5,
        "issues": [],
    }
    at3.session_state["last_audit_path"] = manual_path
    at3.run()
    _no_exception(at3, "after manual audit load")
    audit_inputs_manual = [ti for ti in at3.text_input if ti.label == "Local directory path"]
    assert audit_inputs_manual and audit_inputs_manual[0].value == manual_path, (
        f"Expected {manual_path!r}, got {audit_inputs_manual[0].value!r}"
    )
    graph_inputs_manual = [ti for ti in at3.text_input if ti.label == "Source directory path"]
    assert graph_inputs_manual and graph_inputs_manual[0].value == manual_path, (
        f"Expected {manual_path!r}, got {graph_inputs_manual[0].value!r}"
    )

