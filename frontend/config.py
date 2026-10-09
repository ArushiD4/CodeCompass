"""Central constants for the CodeCompass frontend. No Streamlit code lives here."""
import os

BACKEND_URL = "http://localhost:8000"
# "Run sample audit" scans this folder (the frontend itself), so it always exists.
SAMPLE_PATH = os.path.dirname(os.path.abspath(__file__))
OFFLINE_EMAIL = "developer@offline"
OFFLINE_TOKEN = "offline-token"

# CRS health bands, ARCHITECTURE.md section 8.3: (minimum score, label, tone, guidance)
CRS_BANDS = (
    (80, "Highly Ready", "good", "Meets good quality standards. Remaining issues are easy to defend."),
    (50, "Needs Work", "warn", "Code smells or resource leaks found. Revise before your evaluation."),
    (0, "Critical Issues Detected", "bad", "Severe vulnerabilities. High risk of penalties in a viva."),
)

# Deduction weights, section 8.2
SEVERITIES = ("CRITICAL", "WARNING", "INFO")
SEVERITY_WEIGHT = {"CRITICAL": 15, "WARNING": 8, "INFO": 3}
SEVERITY_TONE = {"CRITICAL": "bad", "WARNING": "warn", "INFO": "info"}
SEVERITY_NAME = {"CRITICAL": "Critical", "WARNING": "Warning", "INFO": "Info"}
GLOBAL_FILE = "Global Codebase"
SECTIONS = ("Findings", "Call graph", "Architecture")

# Section 5.3: standard-library / method names removed from the call graph.
BUILTIN_EXCLUDE = frozenset("""
print len range open str int float bool list dict set tuple enumerate zip map filter
sorted sum min max abs round isinstance getattr setattr hasattr super type repr format
input next iter any all id hash vars dir reversed join append extend get items keys
values split strip lower upper replace startswith endswith add update pop read write
close
""".split())

# Section 5.3: eight-colour palette used to group functions by folder.
MODULE_PALETTE = ("#2B50E6", "#0F9D8A", "#D9822B", "#8B5CF6",
                  "#D6457A", "#4C9F38", "#0EA5E9", "#A8751A")

# Architecture tab content (sections 2 and 4 of ARCHITECTURE.md)
STACK = (
    ("Frontend", "Streamlit", "Port 8501. Session-state routing, bento dashboard, vis.js call graph."),
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

FIXTURE_BAD = r"C:\projects\codecompass\tests\fixtures\sample_bad"
FIXTURE_CLEAN = r"C:\projects\codecompass\tests\fixtures\sample_clean"