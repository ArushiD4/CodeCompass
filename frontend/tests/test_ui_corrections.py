"""test_ui_corrections.py — Verification for UI Corrections, Access Control & Bug Fixes."""
import os
import pytest
from streamlit.testing.v1 import AppTest
from config import APP_NAME, TAGLINE, SAMPLE_PATH, AREAS
from views.landing import _headline

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def _no_exception(at: AppTest, context: str = ""):
    assert not at.exception, f"Exception in {context}: {[e.value for e in at.exception]}"


def test_landing_brand_hierarchy():
    """Verify exact brand hierarchy: CodeCompass > Tagline > Supporting copy."""
    hero_block = _headline()
    assert "cc-hero-lockup" in hero_block, "Hero lockup element not found"

    # Verify order of text in hero lockup
    idx_brand = hero_block.find(APP_NAME)
    idx_tagline = hero_block.find(TAGLINE)
    idx_support = hero_block.find("Audit your code the way your examiner will read it.")

    assert idx_brand != -1, "Brand name CodeCompass not found in hero lockup"
    assert idx_tagline != -1, "Tagline not found in hero lockup"
    assert idx_support != -1, "Supporting copy not found in hero lockup"

    assert idx_brand < idx_tagline < idx_support, (
        f"Brand hierarchy incorrect: Brand({idx_brand}) < Tagline({idx_tagline}) < Support({idx_support})"
    )


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
    assert "Examiner Question:" in card_html
    assert "Reveal answer / defense strategy" in card_html
    # Ensure viva tip is not directly shown in the card outside the reveal details
    assert "Viva Defense Summary:" not in card_html


def test_explain_files_terminology_explanation():
    """Verify plain English AST and call-graph explanations."""
    with open(os.path.join(os.path.dirname(__file__), "..", "components", "explain_files.py"), "r", encoding="utf-8") as f:
        content = f.read()

    assert "How CodeCompass reads your code" in content
    assert "What do 'Calls into' and 'Called by' mean?" in content
    assert "Calls into:" in content
    assert "Called by:" in content
    assert "Possible connection (?):" in content
    assert "Important limitation:" in content


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
    """Verify About CodeCompass & Roadmap are platform routes, not project areas."""
    assert "About CodeCompass" not in AREAS
    assert "Roadmap" not in AREAS
    assert AREAS == ("Audit", "Compare audits")
