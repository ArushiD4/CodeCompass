"""
tests/test_backend.py — FastAPI backend regression tests.

Run:  pytest tests/test_backend.py -v  (from d:\\CodeCompass)

Requires: pytest, httpx2 (both in ccenv)
"""
import sys
import os
import pytest

# Make backend importable without installing as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


# ─────────────────────────────────────────────────────────────────────────────
# T1: Health check
# ─────────────────────────────────────────────────────────────────────────────

def test_root_returns_200():
    """GET / must return 200 with the 'online' message."""
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert "message" in body
    assert "online" in body["message"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# T2-T6: Anti-pattern detection against the fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def audit_result():
    """Run one audit against fixtures/sample_bad.py and cache the response."""
    resp = client.post(
        "/api/audit",
        params={"project_name": "test-fixture", "directory_path": FIXTURES_DIR},
    )
    assert resp.status_code == 200, f"Audit failed: {resp.text}"
    return resp.json()


def test_audit_detects_hardcoded_credential(audit_result):
    """Rule 1: variable API_SECRET='...' must produce a Hardcoded Credential CRITICAL."""
    rules = [i["rule_name"] for i in audit_result["issues"]]
    assert "Hardcoded Credential" in rules, f"Missing Hardcoded Credential. Issues: {rules}"
    crit = [i for i in audit_result["issues"] if i["rule_name"] == "Hardcoded Credential"]
    assert all(i["severity"] == "CRITICAL" for i in crit)


def test_audit_detects_unclosed_open(audit_result):
    """Rule 2: bare open() in load_config must produce an Unclosed Resource Handle WARNING."""
    rules = [i["rule_name"] for i in audit_result["issues"]]
    assert "Unclosed Resource Handle" in rules, f"Missing Unclosed Resource Handle. Issues: {rules}"
    warn = [i for i in audit_result["issues"] if i["rule_name"] == "Unclosed Resource Handle"]
    assert all(i["severity"] == "WARNING" for i in warn)


def test_audit_detects_eval(audit_result):
    """Rule 3: eval() in run_user_input must produce a Dynamic Code Injection Risk CRITICAL."""
    rules = [i["rule_name"] for i in audit_result["issues"]]
    assert "Dynamic Code Injection Risk" in rules, f"Missing Dynamic Code Injection Risk. Issues: {rules}"
    crit = [i for i in audit_result["issues"] if i["rule_name"] == "Dynamic Code Injection Risk"]
    assert all(i["severity"] == "CRITICAL" for i in crit)


def test_audit_detects_silent_exception(audit_result):
    """Rule 4: except: pass in process_data must produce a Silent Exception Swallowing CRITICAL."""
    rules = [i["rule_name"] for i in audit_result["issues"]]
    assert "Silent Exception Swallowing" in rules, f"Missing Silent Exception Swallowing. Issues: {rules}"
    crit = [i for i in audit_result["issues"] if i["rule_name"] == "Silent Exception Swallowing"]
    assert all(i["severity"] == "CRITICAL" for i in crit)


# ─────────────────────────────────────────────────────────────────────────────
# T7: CRS score regression
# ─────────────────────────────────────────────────────────────────────────────

def test_crs_score_regression(audit_result):
    """
    Regression baseline for sample_bad.py fixture.

    Verified by running audit_engine.audit_codebase("tests/fixtures") directly:
        CRITICAL × 3 (credential, eval, except:pass)  → -45
        WARNING  × 1 (open())                          → -8
        INFO     × 3 (orphaned: load_config, run_user_input, process_data) → -9
        Total deductions = 62 → CRS = max(0, 100-62) = 38

    If this test fails after code changes, recompute the expected value
    by running: python -c "from app.audit_engine import audit_codebase; ..."
    and update the expected value below with a comment explaining the change.
    """
    EXPECTED_CRS = 38  # Verified 2026-09-05 against audit_engine.py scoring logic
    assert audit_result["crs_score"] == EXPECTED_CRS, (
        f"CRS score regression: expected {EXPECTED_CRS}, got {audit_result['crs_score']}. "
        "If the scoring weights changed, update EXPECTED_CRS and this comment."
    )


# ─────────────────────────────────────────────────────────────────────────────
# T8-T10: Call graph generation
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def graph_result():
    """Generate call graph for the fixtures directory."""
    resp = client.get(
        "/api/graph",
        params={"directory_path": FIXTURES_DIR},
    )
    assert resp.status_code == 200, f"Graph failed: {resp.text}"
    return resp.json()["graph"]


def test_graph_contains_expected_nodes(graph_result):
    """Fixture defines 3 functions: load_config, run_user_input, process_data."""
    labels = {n["label"] for n in graph_result["nodes"]}
    expected = {"load_config", "run_user_input", "process_data"}
    assert expected.issubset(labels), f"Missing nodes. Got: {labels}"


def test_graph_contains_expected_edges(graph_result):
    """
    Expected edges from fixtures/sample_bad.py:
      load_config -> open
      load_config -> read
      run_user_input -> eval
      process_data -> int
    """
    edges = {(e["caller"].split("::")[-1], e["callee"]) for e in graph_result["edges"]}
    expected = {
        ("load_config",    "open"),
        ("load_config",    "read"),
        ("run_user_input", "eval"),
        ("process_data",   "int"),
    }
    assert expected.issubset(edges), f"Missing edges. Got: {edges}"


def test_graph_node_count(graph_result):
    """fixtures/ contains exactly 3 user-defined functions."""
    assert graph_result["total_nodes"] == 3, (
        f"Expected 3 nodes, got {graph_result['total_nodes']}. "
        "Check for accidental new functions added to fixtures/."
    )


# ─────────────────────────────────────────────────────────────────────────────
# T11: Project report retrieval
# ─────────────────────────────────────────────────────────────────────────────

def test_project_report_not_found():
    """GET /api/projects/999999 must return 404 for a nonexistent project."""
    resp = client.get("/api/projects/999999")
    assert resp.status_code == 404


def test_project_report_after_audit():
    """Audit creates a project; fetching its report by ID returns the same CRS."""
    # Create a fresh audit
    audit_resp = client.post(
        "/api/audit",
        params={
            "project_name": "report-roundtrip-test",
            "directory_path": FIXTURES_DIR,
        },
    )
    assert audit_resp.status_code == 200
    project_id  = audit_resp.json()["project_id"]
    expected_crs = audit_resp.json()["crs_score"]

    # Retrieve by ID
    report_resp = client.get(f"/api/projects/{project_id}")
    assert report_resp.status_code == 200
    assert report_resp.json()["project"]["crs_score"] == expected_crs
