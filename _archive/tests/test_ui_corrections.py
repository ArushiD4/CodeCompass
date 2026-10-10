"""test_ui_corrections.py — Verification for UI Corrections, Access Control & Bug Fixes."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.testing.v1 import AppTest
from config import APP_NAME, TAGLINE, SAMPLE_PATH, AREAS
from views.landing import _headline

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def _no_exception(at: AppTest, context: str = ""):
    assert not at.exception, f"Exception in {context}: {[e.value for e in at.exception]}"


def test_landing_brand_hierarchy():
    """Verify exact brand hierarchy: CodeCompass > Tagline, and examiner sentence is removed."""
    hero_block = _headline()
    assert "cc-hero-lockup" in hero_block, "Hero lockup element not found"

    idx_brand = hero_block.find(APP_NAME)
    idx_tagline = hero_block.find(TAGLINE)

    assert idx_brand != -1, "Brand name CodeCompass not found in hero lockup"
    assert idx_tagline != -1, "Tagline not found in hero lockup"
    assert idx_brand < idx_tagline, "CodeCompass must be above Tagline"
    assert "Audit your code the way your examiner will read it." not in hero_block


def test_findings_answer_hidden_initially():
    """Verify findings show question first and hide answers/strategies in reveal details."""
    from components import findings
    issue = {
        "rule_name": "Hardcoded Credential",
        "severity": "CRITICAL",
        "file_path": "auth.py",
        "line_number": 10,
        "viva_tip": "Sensitive credentials must be loaded from environment variables.",
    }
    card_html = findings._card(issue)
    assert "Question:" in card_html
    assert "Show simple explanation" in card_html
    res = findings._lookup("Hardcoded Credential")
    assert res is not None
    assert len(res) == 4




def test_sample_audit_single_use_restriction():
    """Verify visitor gets exactly 1 sample audit before auth redirect."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    _no_exception(at, "fresh landing")

    # 1. First sample audit: allowed
    sample_btns = [b for b in at.button if "Run sample audit" in b.label]
    assert sample_btns
    sample_btns[0].click().run()
    _no_exception(at, "first sample click")
    assert at.session_state["_page"] == "dashboard"
    assert at.session_state["sample_audit_used"] is True

    # 2. Return to landing and attempt second sample audit
    at.session_state["_page"] = "landing"
    at.run()
    sample_btns2 = [b for b in at.button if "Run sample audit" in b.label]
    assert sample_btns2
    sample_btns2[0].click().run()
    _no_exception(at, "second sample click")

    # Must be redirected to auth with notice
    assert at.session_state["_page"] == "auth"
    assert "1 free sample audit" in at.session_state["auth_notice"]


def test_authenticated_user_unrestricted():
    """Verify authenticated users are not restricted by sample audit limits."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "dashboard"
    at.session_state["authenticated"] = True
    at.session_state["user_email"] = "student@university.edu"
    at.session_state["sample_audit_used"] = True  # Even if marked true
    at.run()
    _no_exception(at, "auth user dashboard")
    assert at.session_state["_page"] == "dashboard"


def test_platform_vs_project_navigation_separation():
    """Verify About CodeCompass & Future Enhancements are platform routes, not project areas."""
    assert "About CodeCompass" not in AREAS
    assert "Roadmap" not in AREAS
    assert "Future Enhancements" not in AREAS
    assert AREAS == ("Audit", "Compare audits")


def test_unauthenticated_navbar_actions():
    """Verify unauthenticated visitor sees Sign in (never Sign out) on About and Future Enhancements."""
    for pg in ("landing", "about", "future_enhancements"):
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.session_state["_page"] = pg
        at.run()
        _no_exception(at, f"unauth {pg}")
        btn_labels = [b.label for b in at.button]
        assert any("Sign in" in l for l in btn_labels), f"Expected 'Sign in' on {pg}"
        assert not any("Sign out" in l for l in btn_labels), f"Unexpected 'Sign out' on {pg}"


def test_authenticated_user_navigation_and_home_link():
    """Verify authenticated user sees Sign out and can click brand logo to go home without losing session."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["_page"] = "dashboard"
    at.session_state["authenticated"] = True
    at.session_state["user_email"] = "analyst@codecompass.dev"
    at.run()
    _no_exception(at, "auth dashboard")

    # Brand button exists and clicks to landing
    brand_btn = [b for b in at.button if APP_NAME in b.label]
    assert brand_btn, "Brand logo button not found in navbar"
    brand_btn[0].click().run()
    _no_exception(at, "brand click")

    assert at.session_state["_page"] == "landing"
    assert at.session_state["authenticated"] is True
    assert at.session_state["user_email"] == "analyst@codecompass.dev"
    btn_labels = [b.label for b in at.button]
    assert any("Sign out" in l for l in btn_labels), "Authenticated user should see Sign out on landing"
    assert any("Dashboard" in l for l in btn_labels), "Authenticated user should see Dashboard nav on landing"
