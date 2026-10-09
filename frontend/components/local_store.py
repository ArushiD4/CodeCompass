"""local_store.py — SQLite persistence for viva defense rehearsal notes."""
import contextlib
import os
from pathlib import Path
import sqlite3
import time


def _db_path():
    override = os.getenv("CODECOMPASS_DB")
    if override:
        p = Path(override)
        p.parent.mkdir(parents=True, exist_ok=True)
        return str(p)
    folder = Path.home() / ".codecompass"
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder / "history.db")


def init_ok() -> bool:
    try:
        path = _db_path()
        with contextlib.closing(sqlite3.connect(path)) as conn:
            with conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS notes ("
                    "project_path TEXT, rel_file TEXT, prompt_idx INT, text TEXT, updated REAL, "
                    "PRIMARY KEY(project_path, rel_file, prompt_idx))"
                )
        return True
    except Exception:
        return False


def save_note(project_path: str, rel_file: str, prompt_idx: int, text: str) -> bool:
    try:
        path = _db_path()
        with contextlib.closing(sqlite3.connect(path)) as conn:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO notes (project_path, rel_file, prompt_idx, text, updated) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (str(project_path), str(rel_file), int(prompt_idx), str(text), time.time())
                )
        return True
    except Exception:
        return False


def load_notes(project_path: str) -> dict:
    try:
        path = _db_path()
        with contextlib.closing(sqlite3.connect(path)) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT rel_file, prompt_idx, text FROM notes WHERE project_path = ?",
                (str(project_path),)
            )
            return {(row[0], row[1]): row[2] for row in cur.fetchall()}
    except Exception:
        return {}
