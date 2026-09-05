# tests/fixtures/sample_bad.py
# ─────────────────────────────────────────────────────────────────────────────
# INTENTIONALLY DEFECTIVE FIXTURE — used by backend regression tests
# and by the "Run Sample Audit" landing-page demo button.
#
# Contains exactly one instance of each of the four detectable anti-patterns:
#   1. Hardcoded credential  → CRITICAL  (-15 pts)
#   2. Unclosed open()       → WARNING   (-8 pts)
#   3. eval() / exec()       → CRITICAL  (-15 pts)
#   4. except: pass          → CRITICAL  (-15 pts)
#
# Expected CRS baseline: 100 - (15+8+15+15) = 47
# ─────────────────────────────────────────────────────────────────────────────


# Anti-pattern 1: hardcoded credential
# Triggers visit_Assign — var name contains "SECRET"
API_SECRET = "my-super-secret-value-1234"


def load_config(filename):
    # Anti-pattern 2: unclosed open() — standalone, not in a `with` block
    # Triggers visit_Call for bare open()
    f = open(filename, "r")
    return f.read()


def run_user_input(user_code):
    # Anti-pattern 3: dynamic code injection via eval()
    # Triggers visit_Call for eval
    result = eval(user_code)
    return result


def process_data(data):
    try:
        return int(data)
    except:
        # Anti-pattern 4: silent exception swallowing
        # Triggers visit_ExceptHandler — body is only `pass`
        pass
