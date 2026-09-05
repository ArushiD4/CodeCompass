# frontend/sample_snippet.py
# ─────────────────────────────────────────────────────────────────────────────
# Demo code snippet — intentionally contains all four detectable anti-patterns.
# The landing page "Run Sample Audit" button audits this file's DIRECTORY.
# DO NOT import or execute this file — it is a static analysis target only.
# ─────────────────────────────────────────────────────────────────────────────

# Anti-pattern 1 — Hardcoded Credential (CRITICAL)
DB_PASSWORD = "s3cr3t-password-123"

# Anti-pattern 2 — Unclosed Resource Handle (WARNING)
def read_log(path):
    f = open(path, "r")          # bare open(), no `with` context manager
    return f.read()

# Anti-pattern 3 — Dynamic Code Injection (CRITICAL)
def evaluate_expression(expr):
    return eval(expr)            # arbitrary code execution risk

# Anti-pattern 4 — Silent Exception Swallowing (CRITICAL)
def safe_parse(raw):
    try:
        return int(raw)
    except:
        pass                     # swallows ALL exceptions silently
