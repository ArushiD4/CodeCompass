"""Unit tests for F5: audit_diff pure logic module."""
import copy
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.audit_diff import fingerprint, order_reports, compare_reports


def test_fingerprint_identical_when_only_line_number_differs():
    iss1 = {"rule_name": "Hardcoded Credential", "file_path": "app\\auth.py", "line_number": 10, "viva_tip": "Line 10 secret"}
    iss2 = {"rule_name": "Hardcoded Credential", "file_path": "app/auth.py", "line_number": 99, "viva_tip": "Line 99 secret"}
    # Note digits in viva_tip are normalized to '#'
    fp1 = fingerprint(iss1, occurrence=0)
    fp2 = fingerprint(iss2, occurrence=0)
    assert fp1 == fp2


def test_two_identical_findings_in_one_run_get_different_fingerprints():
    # If the same rule/file/tip appears twice in one run, occurrence increments
    iss1 = {"rule_name": "Dynamic Code Injection Risk", "file_path": "utils.py", "line_number": 5, "viva_tip": "eval used"}
    iss2 = {"rule_name": "Dynamic Code Injection Risk", "file_path": "utils.py", "line_number": 15, "viva_tip": "eval used"}
    fp1 = fingerprint(iss1, occurrence=0)
    fp2 = fingerprint(iss2, occurrence=1)
    assert fp1 != fp2


def test_order_reports_swaps_by_created_at_and_id():
    # Newer created_at should be later
    r_old = {"project": {"id": 1, "created_at": "2026-10-01T10:00:00"}}
    r_new = {"project": {"id": 2, "created_at": "2026-10-05T10:00:00"}}
    e, l, swapped = order_reports(r_new, r_old)
    assert swapped is True
    assert e["project"]["id"] == 1
    assert l["project"]["id"] == 2

    # Equal created_at -> order by id
    r1 = {"project": {"id": 10, "created_at": "2026-10-05T10:00:00"}}
    r2 = {"project": {"id": 20, "created_at": "2026-10-05T10:00:00"}}
    e, l, swapped = order_reports(r2, r1)
    assert swapped is True
    assert e["project"]["id"] == 10
    assert l["project"]["id"] == 20

    # Already earlier first
    e, l, swapped = order_reports(r1, r2)
    assert swapped is False
    assert e["project"]["id"] == 10


def test_compare_reports_improvement():
    earlier = {
        "project": {"id": 1, "project_name": "MyProject", "crs_score": 40, "total_files": 2, "total_functions": 5},
        "issues": [
            {"rule_name": "Hardcoded Credential", "severity": "CRITICAL", "file_path": "auth.py", "line_number": 10, "viva_tip": "Secret"},
            {"rule_name": "Unclosed Resource Handle", "severity": "WARNING", "file_path": "db.py", "line_number": 20, "viva_tip": "open()"},
        ]
    }
    later = {
        "project": {"id": 2, "project_name": "MyProject", "crs_score": 85, "total_files": 2, "total_functions": 5},
        "issues": [
            # Hardcoded Credential was fixed! Unclosed Resource Handle remains but line moved
            {"rule_name": "Unclosed Resource Handle", "severity": "WARNING", "file_path": "db.py", "line_number": 25, "viva_tip": "open()"},
        ]
    }
    earlier_copy = copy.deepcopy(earlier)
    later_copy = copy.deepcopy(later)

    diff = compare_reports(earlier, later)
    # Check no mutation
    assert earlier == earlier_copy
    assert later == later_copy

    assert diff["crs_before"] == 40
    assert diff["crs_after"] == 85
    assert diff["delta"] == 45
    assert diff["tone"] == "good"
    assert diff["same_project"] is True
    assert len(diff["fixed"]) == 1
    assert diff["fixed"][0]["rule_name"] == "Hardcoded Credential"
    assert len(diff["new"]) == 0
    assert len(diff["remaining"]) == 1
    # Kept later issue's line number
    assert diff["remaining"][0]["line_number"] == 25


def test_compare_reports_regression_and_identical():
    # Regression
    earlier = {
        "project": {"id": 1, "project_name": "Proj", "crs_score": 80},
        "issues": []
    }
    later = {
        "project": {"id": 2, "project_name": "Proj", "crs_score": 60},
        "issues": [{"rule_name": "Silent Exception Swallowing", "severity": "CRITICAL", "file_path": "main.py", "line_number": 12, "viva_tip": "pass"}]
    }
    diff = compare_reports(earlier, later)
    assert diff["delta"] == -20
    assert diff["tone"] == "bad"
    assert len(diff["new"]) == 1
    assert len(diff["fixed"]) == 0

    # Identical reports
    diff_same = compare_reports(earlier, earlier)
    assert diff_same["delta"] == 0
    assert diff_same["headline"] == "No changes between these two audits."


def test_same_project_false_for_different_names():
    r1 = {"project": {"id": 1, "project_name": "Project Alpha", "crs_score": 50}, "issues": []}
    r2 = {"project": {"id": 2, "project_name": "Project Beta", "crs_score": 60}, "issues": []}
    diff = compare_reports(r1, r2)
    assert diff["same_project"] is False
