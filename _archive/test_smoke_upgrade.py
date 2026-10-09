"""Smoke test for upgraded dark cinematic frontend via Streamlit AppTest."""
import os
import sys
import pytest

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
sys.path.insert(0, FRONTEND_DIR)

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(FRONTEND_DIR, "app.py")


def _no_exception(at: AppTest, context: str = ""):
    exc_list = at.exception
    assert len(exc_list) == 0, f"App raised exception(s) in {context}: " + "\n".join(str(e) for e in exc_list)


def test_landing_boots_and_navigates():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing boot")

    # Click Enter project path -> routes to auth
    enter_btns = [b for b in at.button if "Enter project path" in b.label]
    assert enter_btns, "Enter project path button not found"
    enter_btns[0].click().run()
    _no_exception(at, "after enter project path click")
    assert at.session_state["_page"] == "auth"


def test_auth_offline_reaches_dashboard():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "auth"
    at.session_state["offline_mode"] = True
    at.run()
    _no_exception(at, "auth with offline mode")

    enter_offline = [b for b in at.button if "Enter dashboard" in b.label]
    assert enter_offline, "Enter dashboard button not found"
    enter_offline[0].click().run()
    _no_exception(at, "after entering dashboard via offline mode")
    assert at.session_state["_page"] == "dashboard"


def test_dashboard_workspace_areas():
    mock_audit = {
        "status": "success",
        "project_id": 1,
        "project_name": "Demo Project",
        "crs_score": 85,
        "total_files": 4,
        "total_functions": 12,
        "issues": [
            {
                "rule_name": "Hardcoded Credential",
                "severity": "CRITICAL",
                "file_path": "auth.py",
                "line_number": 10,
                "viva_tip": "Move credentials to environment variables.",
            }
        ]
    }

    areas = ["Audit", "Playbook", "About CodeCompass", "Roadmap", "Fix and rescan"]
    for area in areas:
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.session_state["_page"] = "dashboard"
        at.session_state["authenticated"] = True
        at.session_state["offline_mode"] = True
        at.session_state["area"] = area
        at.session_state["last_audit_data"] = mock_audit
        at.run()
        _no_exception(at, f"workspace area '{area}'")

        # Confirm About CodeCompass has NO project hero
        if area == "About CodeCompass":
            text_dump = " ".join(str(m) for m in at.markdown)
            assert "Demo Project" not in text_dump, "About CodeCompass should not render the scanned project hero!"


def test_audit_project_tabs():
    mock_audit = {
        "status": "success",
        "project_id": 1,
        "project_name": "Demo Project",
        "crs_score": 85,
        "total_files": 4,
        "total_functions": 12,
        "issues": []
    }

    sections = ["Findings", "Call graph", "Project structure"]
    for sec in sections:
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.session_state["_page"] = "dashboard"
        at.session_state["authenticated"] = True
        at.session_state["offline_mode"] = True
        at.session_state["area"] = "Audit"
        at.session_state["section"] = sec
        at.session_state["last_audit_data"] = mock_audit
        at.run()
        _no_exception(at, f"audit project tab '{sec}'")
