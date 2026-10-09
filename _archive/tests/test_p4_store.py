"""Unit tests for P4: file_links and local_store."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.file_links import called_by, calls_into, dependents
from components import local_store


def test_file_links_cross_file_and_ambiguous():
    graph = {
        "nodes": [
            {"id": "a.py::caller_fn", "label": "caller_fn", "file": "a.py"},
            {"id": "b.py::target_fn", "label": "target_fn", "file": "b.py"},
            {"id": "c.py::target_fn", "label": "target_fn", "file": "c.py"},
        ],
        "edges": [
            {"caller": "a.py::caller_fn", "callee": "target_fn", "line": 5},
        ]
    }
    into = calls_into("a.py", graph)
    assert len(into) == 2
    assert all(p is True for _, _, p in into)

    by_b = called_by("b.py", graph)
    assert len(by_b) == 1
    assert by_b[0][0] == "a.py"
    assert by_b[0][1] == "caller_fn"
    assert by_b[0][2] is True

    file_facts = {"d.py": {"imports": [("b", "local")]}}
    deps_b = dependents("b.py", file_facts, graph)
    assert "a.py" in deps_b
    assert "d.py" in deps_b


def test_local_store_notes_roundtrip(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_notes.db")
        monkeypatch.setenv("CODECOMPASS_DB", db_path)

        assert local_store.init_ok() is True
        assert local_store.save_note("/project", "main.py", 0, "My answer to prompt 0") is True
        assert local_store.save_note("/project", "main.py", 1, "My answer to prompt 1") is True

        notes = local_store.load_notes("/project")
        assert notes.get(("main.py", 0)) == "My answer to prompt 0"
        assert notes.get(("main.py", 1)) == "My answer to prompt 1"


def test_local_store_unwritable_path_degrades(monkeypatch):
    monkeypatch.setenv("CODECOMPASS_DB", "Z:\\invalid_path\\nonexistent\\db.db")
    assert local_store.init_ok() is False
    assert local_store.save_note("/project", "main.py", 0, "text") is False
    assert local_store.load_notes("/project") == {}
