"""Central constants for the CodeCompass frontend. No Streamlit code lives here."""
import os

APP_NAME = "CodeCompass"
TAGLINE = "Navigate your code. Defend your logic."
PROJECT_CREDIT = "Final Year Academic Evaluation"
INTRO_ENABLED = True

BACKEND_URL = "http://localhost:8000"
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
SAMPLE_PATH = str((FIXTURES_DIR / "sample_moderate").resolve())
OFFLINE_EMAIL = "developer@offline"
OFFLINE_TOKEN = "offline-token"

AREAS = ("Audit", "About CodeCompass", "Roadmap", "Compare audits")
SECTIONS = ("Findings", "Call graph", "Project structure")

# CRS health bands, ARCHITECTURE.md section 8.3: (minimum score, label, tone, guidance)
CRS_BANDS = (
    (80, "Highly Ready", "good", "Meets good quality standards. Remaining issues are easy to defend."),
    (50, "Needs Work", "warn", "Code smells or resource leaks found. Revise before your evaluation."),
    (0, "Critical Issues Detected", "bad", "Severe vulnerabilities. High risk of penalties in a viva."),
)

SEVERITIES = ("CRITICAL", "WARNING", "INFO")
SEVERITY_WEIGHT = {"CRITICAL": 15, "WARNING": 8, "INFO": 3}
SEVERITY_TONE = {"CRITICAL": "bad", "WARNING": "warn", "INFO": "info"}
SEVERITY_NAME = {"CRITICAL": "Critical", "WARNING": "Warning", "INFO": "Info"}
GLOBAL_FILE = "Global Codebase"

BUILTIN_EXCLUDE = frozenset("""
print len range open str int float bool list dict set tuple enumerate zip map filter
sorted sum min max abs round isinstance getattr setattr hasattr super type repr format
input next iter any all id hash vars dir reversed join append extend get items keys
values split strip lower upper replace startswith endswith add update pop read write
close
""".split())

MODULE_PALETTE = ("#00F5A0", "#00D8F6", "#FFB800", "#8B5CF6",
                  "#FF385C", "#4C9F38", "#38BDF8", "#F59E0B")

STACK = (
    ("Frontend", "Streamlit", "Port 8501. Session-state routing, dark bento dashboard, vis.js graph."),
    ("Backend", "FastAPI + Uvicorn", "Port 8000. Four stateless REST endpoints, typed with Pydantic."),
    ("Analysis", "Python ast module", "Visitor-based rules. Student code is parsed, never executed."),
    ("Storage", "SQLite + SQLAlchemy 2.0", "projects to audit_issues, cascade delete, zero-config file."),
    ("Identity", "Firebase Identity Toolkit", "REST sign-in, with an offline bypass for live demos."),
)

RULES = (
    ("Hardcoded Credential", "CRITICAL", "ast.Assign", "Secret-like name assigned a string literal"),
    ("Unclosed Resource Handle", "WARNING", "ast.Call", "open() used outside a with statement"),
    ("Dynamic Code Injection", "CRITICAL", "ast.Call", "eval() or exec() call"),
    ("Silent Exception Swallowing", "CRITICAL", "ast.ExceptHandler", "except block whose body is only pass"),
    ("Orphaned Function", "INFO", "Post-traversal", "Defined but never called"),
)

PIPELINE = ("Directory path", "POST /api/audit", "AST rules", "CRS score",
            "SQLite report", "GET /api/graph")

# ARCHITECTURE.md 8.4: bad fixture scores 38; clean scores 100.
FIXTURE_BAD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "sample_bad.py"))
FIXTURE_CLEAN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "sample_clean.py"))