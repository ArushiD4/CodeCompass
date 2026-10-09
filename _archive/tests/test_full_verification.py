"""test_full_verification.py — Comprehensive AppTest verification across all views and tabs."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.testing.v1 import AppTest
from config import SAMPLE_PATH

APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app.py"))


def _no_exception(at: AppTest, ctx: str = ""):
    exc_list = at.exception
    assert len(exc_list) == 0, f"Exception in {ctx}: " + "\n".join(str(e) for e in exc_list)


def test_landing_and_navbar_no_forbidden_strings():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing")

    # Verify no "Skip intro", "Backend online", "Backend URL", or "Playbook"
    raw_text = " ".join(str(m) for m in at.markdown) + " ".join(b.label for b in at.button)
    assert "Skip intro" not in raw_text
    assert "Backend online" not in raw_text
    assert "Backend URL" not in raw_text
    assert "Playbook" not in raw_text


def test_sample_audit_scans_fixture():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "landing")

    sample_btns = [b for b in at.button if "Run sample audit" in b.label]
    assert sample_btns, "Run sample audit button not found"
    sample_btns[0].click().run()
    _no_exception(at, "after sample audit click")

    assert at.session_state["_page"] == "dashboard"
    assert at.session_state["guest_mode"] is True
    assert at.session_state["scan_path"] == SAMPLE_PATH
    assert "sample_moderate" in at.session_state["scan_name"]


def test_all_workspace_areas_and_tabs():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "dashboard"
    at.session_state["authenticated"] = True
    at.session_state["offline_mode"] = True
    at.session_state["last_audit_data"] = {
        "status": "success",
        "project_id": 1,
        "project_name": "Test Project",
        "crs_score": 75,
        "total_files": 2,
        "total_functions": 4,
        "issues": [
            {"rule_name": "Hardcoded Credential", "severity": "CRITICAL", "file_path": "a.py", "line_number": 5, "viva_tip": "Secret"},
        ]
    }
    at.session_state["last_audit_path"] = SAMPLE_PATH
    at.run()
    _no_exception(at, "dashboard default")

    # Top-level areas
    for area in ("Audit", "About CodeCompass", "Roadmap", "Compare audits"):
        at.session_state["area"] = area
        at.run()
        _no_exception(at, f"Area: {area}")

    # Tabs inside Audit
    at.session_state["area"] = "Audit"
    for sec in ("Findings", "Call graph", "Project structure", "Explain files"):
        at.session_state["section"] = sec
        at.run()
        _no_exception(at, f"Section tab: {sec}")
