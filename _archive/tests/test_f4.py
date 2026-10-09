"""Unit tests for F4: discover_projects and fmt_time."""
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api_client import discover_projects
from components.report_picker import fmt_time, report_label


def test_discover_projects_stops_after_empty_batch():
    # Only IDs 1, 2 exist. Batch of 5. Next batch 6..10 returns None, None. Should stop at 10 without going to 500.
    called = []

    def mock_fetch(pid):
        called.append(pid)
        if pid in (1, 2):
            return {"id": pid, "project_name": f"P{pid}", "created_at": f"2026-10-0{pid}T10:00:00"}, None
        return None, None

    projects, err = discover_projects(mock_fetch, batch=5, workers=2, limit=100)
    assert err is None
    assert len(projects) == 2
    assert max(called) <= 10  # Stopped after batch 6..10


def test_discover_projects_tolerates_gaps():
    # IDs 1, 3, 5 exist (2 and 4 are missing)
    def mock_fetch(pid):
        if pid in (1, 3, 5):
            return {"id": pid, "project_name": f"P{pid}", "created_at": f"2026-10-0{pid}T10:00:00"}, None
        return None, None

    projects, err = discover_projects(mock_fetch, batch=10, workers=2, limit=50)
    assert err is None
    assert [p["id"] for p in projects] == [5, 3, 1]  # Sorted newest first


def test_discover_projects_fatal_error_immediately():
    def mock_fetch(pid):
        if pid == 2:
            return None, "Connection refused"
        return {"id": pid, "project_name": f"P{pid}"}, None

    projects, err = discover_projects(mock_fetch, batch=5, workers=1, limit=50)
    assert err == "Connection refused"
    assert projects == []


def test_discover_projects_sorts_newest_first():
    def mock_fetch(pid):
        timestamps = {
            1: "2026-10-01T12:00:00",
            2: "2026-10-05T12:00:00",
            3: "2026-10-03T12:00:00",
        }
        if pid in timestamps:
            return {"id": pid, "project_name": f"P{pid}", "created_at": timestamps[pid]}, None
        return None, None

    projects, err = discover_projects(mock_fetch, batch=5, workers=1, limit=10)
    assert err is None
    assert [p["id"] for p in projects] == [2, 3, 1]


def test_fmt_time_naive_iso_treated_as_utc():
    # ISO string without timezone: 2026-10-08T17:31:00
    formatted = fmt_time("2026-10-08T17:31:00")
    # Verify it parsed and formatted into "08 Oct 2026, ..."
    assert "08 Oct 2026" in formatted
    # Check that naive is converted as UTC
    dt_utc = datetime(2026, 10, 8, 17, 31, 0, tzinfo=timezone.utc)
    expected_local = dt_utc.astimezone().strftime("%d %b %Y, %I:%M %p")
    assert formatted == expected_local


def test_report_label_appends_id_on_duplicate():
    p1 = {"id": 1, "project_name": "App", "created_at": "2026-10-08T12:00:00", "crs_score": 80}
    p2 = {"id": 2, "project_name": "App", "created_at": "2026-10-08T12:00:00", "crs_score": 80}
    base = f"App · {fmt_time('2026-10-08T12:00:00')} · CRS 80"
    dupes = {base}
    lbl1 = report_label(p1, dupes)
    lbl2 = report_label(p2, dupes)
    assert lbl1 == f"{base} (#1)"
    assert lbl2 == f"{base} (#2)"
