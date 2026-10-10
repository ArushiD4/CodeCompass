# CodeCompass

CodeCompass is an AST-driven static analysis and code audit platform designed to evaluate student Python projects for academic viva presentations without executing arbitrary code. It detects critical anti-patterns, models cross-file call graphs, and computes an objective Code Readiness Score (CRS) with actionable defense explanations.

---

## Anti-Pattern Rules & Penalty Scoring

CodeCompass inspects Python abstract syntax trees against five foundational rules:

| Rule Name | Target Pattern | Severity | Penalty |
|---|---|---|---|
| **Hardcoded Credential** | Assigning password/secret/token string literal directly in code | CRITICAL | -15 pts |
| **Dynamic Code Injection Risk** | Invocations of `eval()` or `exec()` on dynamic strings | CRITICAL | -15 pts |
| **Silent Exception Swallowing** | Empty `except: pass` blocks suppressing unhandled runtime errors | CRITICAL | -15 pts |
| **Unclosed Resource Handle** | Standalone `open()` invocations risking file descriptor leaks | WARNING | -8 pts |
| **Orphaned Function** | Declared functions never called or invoked across the project | INFO | -3 pts |

### Score Formulation

The **Code Readiness Score (CRS)** starts at 100 and subtracts penalties down to a minimum of 0:

$$\text{CRS} = \max\left(0, 100 - \sum \text{penalties}\right)$$

#### Benchmark Example (`sample_bad.py`)
Evaluating the canonical `tests/fixtures/sample_bad.py` benchmark triggers all five rules:
- 1 × Hardcoded Credential: $15\text{ pts}$
- 1 × Unclosed Resource Handle: $8\text{ pts}$
- 1 × Dynamic Code Injection: $15\text{ pts}$
- 1 × Silent Exception Swallowing: $15\text{ pts}$
- 3 × Orphaned Functions (`load_config`, `run_user_input`, `process_data`): $3 \times 3 = 9\text{ pts}$

$$\text{Total Deductions} = 15 + 8 + 15 + 15 + 9 = 62 \implies \mathbf{\text{CRS} = 100 - 62 = 38}$$

---

## Setup & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.11/3.13)
- Windows (PowerShell or Command Prompt)

### Environment Setup
```cmd
python -m venv ccenv
ccenv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Copy the template secrets file:
```cmd
copy frontend\.streamlit\secrets.toml.example frontend\.streamlit\secrets.toml
```

Environment variables (optional overrides):
- `CODECOMPASS_API_KEY`: API key for FastAPI communication (auto-read from `secrets.toml`).
- `CODECOMPASS_BACKEND_URL`: URL of the FastAPI backend (defaults to `http://127.0.0.1:8000`).
- `CODECOMPASS_OFFLINE_TOKEN`: Custom auth token for Developer Offline Mode.

### Starting the Services

**Option A — Automated Launcher (Windows):**
```cmd
.\run_demo.bat
```
Starts both the FastAPI backend (port 8000) and the Streamlit frontend (port 8501).

**Option B — Manual Launch:**
```cmd
REM Terminal 1 (Backend):
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

REM Terminal 2 (Frontend):
cd frontend
streamlit run app.py --server.port 8501
```

---

## Running the Demo in Developer Offline Mode

1. **Landing Page:** Open `http://localhost:8501` in your browser.
2. **Access Offline Mode:** Click **Developer Offline Mode** on the landing page or sign in via the offline bypass option.
3. **Run Sample Audit:** Click **Run sample audit** on the dashboard to immediately analyze the bundled `tests/fixtures/sample_moderate` codebase.
4. **Explore the Three Results Tabs:**
   - **Findings:** Filter findings by severity (Critical, Warning, Info) or rule category. Click any finding to expand the plain-language viva defense breakdown (*In simple words*, *How to fix*, *What to say if asked*).
   - **Call graph:** Interactive call hierarchy visualising functions, calls, and entry points with vis.js.
   - **Project structure:** File tree, line counts, and directory metrics highlighting files with the most issues.
5. **Compare Audits:** Switch to the **Compare audits** area or click **Compare with previous audit** to examine fixed issues, new regressions, and CRS differentials.
6. **Forgot Password:** Test the "Forgot password?" recovery link on the Sign In page to verify graceful offline guidance.

---

## Known Limitations

- **Context Manager Open Calls:** CodeCompass AST inspection flags every `open()` call node even if enclosed in a `with open(...)` block, encouraging explicit zero-leak idioms such as `Path.read_text()`.
- **Framework Callback Reachability:** Static AST analysis cannot trace dynamic route handlers, worker queues, or Streamlit button callbacks. Functions reachable through frameworks are annotated with `@entrypoint()`.
- **Credential Name Matching:** The secret assignment rule matches variable names (`KEY`, `SECRET`, `PASSWORD`, etc.) assigned to string literals, including empty strings (`""`) or dummy test keys.
- **Fixture Differentiation:** The single-file unit test benchmark (`sample_bad.py`) yields a CRS of **38** (7 issues), while the interactive multi-file demo fixture (`sample_moderate`) yields a CRS of **44** (9 issues).

---

## Future Enhancements

- **AST Context Manager Inspection:** Teach `visit_Call` to check parent AST nodes for `ast.With` to suppress `open()` warnings when properly managed.
- **Shannon Entropy Scoring:** Incorporate string entropy calculations to distinguish real high-entropy API secrets from dummy test literals.
- **Pre-Commit & CI Actions:** Provide a GitHub Action to enforce CRS thresholds directly in pull request workflows.
- **Multi-Language Parser Support:** Integrate Tree-sitter parsers to support JavaScript, TypeScript, and Java projects.
