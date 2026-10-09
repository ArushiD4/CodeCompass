"""Unit tests for P4: file_facts and file_scan."""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.file_facts import extract_facts
from components.file_scan import safe_join, scan_project


def test_file_facts_imports_classes_entry_point():
    code = """
import os
from utils import helper
from math import sqrt

class Calculator:
    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b

def compute(): pass

ITEMS = [1, 2, 3]
MAPPING = {"a": 1}
LIMIT = 100

if __name__ == "__main__":
    compute()
"""
    facts = extract_facts(code, "calc.py", {"utils"})
    assert facts["parse_error"] is None
    imp_dict = dict(facts["imports"])
    assert imp_dict.get("os") == "external"
    assert imp_dict.get("utils.helper") == "local"
    assert ("Calculator", 2) in facts["classes"]
    assert "compute" in facts["functions"]
    assert facts["entry_point"] is True
    globals_dict = dict(facts["globals"])
    assert globals_dict.get("ITEMS") == "list"
    assert globals_dict.get("MAPPING") == "dict"
    assert globals_dict.get("LIMIT") == "constant"


def test_file_facts_open_calls():
    code = """
def test_io(dynamic_f):
    open("test.txt", "w")
    open("log.log", "a")
    open("read.txt")
    open(dynamic_f, "r")
"""
    facts = extract_facts(code)
    io = facts["io_calls"]
    assert "writes (test.txt)" in io
    assert "appends (log.log)" in io
    assert "reads (read.txt)" in io
    assert "reads (dynamic path)" in io


def test_file_facts_syntax_error_no_raise():
    bad_code = "def broken_func(:\n    pass"
    facts = extract_facts(bad_code)
    assert facts["parse_error"] is not None
    assert facts["functions"] == []
    assert facts["classes"] == []


def test_file_scan_safe_join():
    with tempfile.TemporaryDirectory() as tmpdir:
        valid = safe_join(tmpdir, "subdir/file.py")
        assert valid.startswith(os.path.abspath(tmpdir))
        with pytest.raises(ValueError):
            safe_join(tmpdir, "../outside.py")
        outside = os.path.abspath(os.path.join(tmpdir, "..", "outside.py"))
        with pytest.raises(ValueError):
            safe_join(tmpdir, outside)


def test_file_scan_skips_large_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        small_f = os.path.join(tmpdir, "small.py")
        with open(small_f, "w") as fp:
            fp.write("def small(): pass\n")
        large_f = os.path.join(tmpdir, "large.py")
        with open(large_f, "w") as fp:
            fp.write("# comment\n" * 120_000)
        results = scan_project(tmpdir)
        assert "small.py" in results
        assert "large.py" not in results
