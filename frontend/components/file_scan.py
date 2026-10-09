"""file_scan.py — Safe directory walking, size limits, and facts compilation."""
import os
from pathlib import Path
from components.file_facts import extract_facts

EXCLUDE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "ccenv", "env",
    "node_modules", "build", "dist", ".pytest_cache", ".idea", ".vscode"
}
MAX_FILE_SIZE = 1_000_000  # 1 MB
MAX_FILES = 500


def scan_project(root: str) -> dict:
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        return {}

    py_rel_paths = []
    for dirpath, dirnames, filenames in os.walk(str(root_path)):
        dirnames[:] = [d for d in dirnames if d.lower() not in EXCLUDE_DIRS]
        for f in filenames:
            if f.endswith(".py"):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, str(root_path)).replace("\\", "/")
                py_rel_paths.append((rel, full))
                if len(py_rel_paths) >= MAX_FILES:
                    break
        if len(py_rel_paths) >= MAX_FILES:
            break

    project_modules = {Path(rel).stem for rel, _ in py_rel_paths}
    results = {}

    for rel, full in py_rel_paths:
        try:
            if os.path.getsize(full) > MAX_FILE_SIZE:
                continue
            source = Path(full).read_text(encoding="utf-8", errors="replace")
            facts = extract_facts(source, rel, project_modules)
            results[rel] = facts
        except Exception as exc:
            results[rel] = {
                "imports": [], "classes": [], "functions": [],
                "entry_point": False, "io_calls": [], "globals": [],
                "parse_error": str(exc)
            }

    return results
