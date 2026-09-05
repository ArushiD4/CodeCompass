# CodeCompass — Live Demo Script

> **Evaluator / presenter:** Follow this numbered walkthrough in order. Estimated time: 8–10 minutes.

---

## Pre-demo checklist (do this 5 minutes before)

- [ ] Close any process already using ports **8000** and **8501**
- [ ] Run `run_demo.bat` from the repo root → two terminal windows open, browser opens at `http://localhost:8501`
- [ ] Confirm the landing page loads with the "Know your code before they ask about it." headline

---

## Path A — Full demo (backend running)

### Step 1: Landing page tour (1 min)

1. Point out the **navbar** (logo + wordmark, nav links, Sign In)
2. Scroll down to the **feature cards**: AST Detection · CRS Engine · Call Graph
3. Scroll to the **architecture comparison table** — explain FastAPI vs. client-side alternatives

### Step 2: Run Sample Audit (2 min)

> This requires no login. The audit runs against a **bundled Python snippet** that intentionally contains all four detectable anti-patterns.

1. Click **▶ Run Sample Audit** on the landing page
2. Wait for the spinner ("Running sample audit against bundled snippet…")
3. The browser navigates automatically to the **Dashboard → Audit tab**
4. Point out:
   - **CRS Score hero band** — should show **38/100** ("Critical Issues Detected")
   - **Four metric cards**: CRS Score · Files Scanned · Issues Detected · Functions Found
   - **Two-column findings grid**: Critical/Warnings left, Info/Dead Code right
5. Expand one CRITICAL finding → show the **paired inline layout**: finding detail on the left, **Viva Defence Tip** on the right

### Step 3: Call Graph (1 min)

1. Scroll down to the **AST Traversal — Call Graph** section
2. The directory path is pre-filled from the last audit — click **Generate Graph**
3. Show the interactive vis.js graph: drag nodes, scroll to zoom, hover for file/line details
4. Explain: "This is the caller → callee relationship map built by a second AST visitor"

### Step 4: Manual audit of your own codebase (2 min)

1. Click **⚙️ Backend settings** — update the URL if needed
2. Change the **Local directory path** to any local Python project (not a venv directory)
3. Give it a project name, click **▶ Run Static Audit**
4. Walk through a real finding with the evaluator

### Step 5: Reports tab (1 min)

1. Click **📊 Reports** in the top nav
2. Enter project ID **1** → click **Fetch Report**
3. Show the CRS band, metric cards, and the issue log with severity chips

### Step 6: About tab (1 min)

1. Click **ℹ️ About** → expand **🏗️ System Architecture**
2. Point to the **Stack Overview** and **Static Analysis Engine** sections
3. Expand **📊 Benchmarks** — point to the 38/100 demo fixture result

### Step 7: Logout

1. Click **Logout** → redirected to the landing page
2. Point out that all session data is cleared

---

## Path B — Offline fallback (backend unreachable)

> Use this if the FastAPI server won't start, Firebase auth fails, or you're on a machine without the backend installed.

### Step 1: Navigate to Auth

1. Click **Sign In →** on the landing page

### Step 2: Activate Developer Offline Mode

1. Toggle **⚡ Developer offline mode** on the Login tab
2. Click **Launch App →** — no network call is made
3. You land on the Dashboard with a fake authenticated session

### Step 3: Show the UI with mock data

1. Navigate through **Audit · Reports · About** tabs — all pages render without backend
2. Explain: "In a real run, clicking Run Static Audit would call `POST /api/audit` on the FastAPI backend; in offline mode the backend is bypassed but the UI layout and navigation are fully functional"

### Step 4: Run Sample Audit (with backend)

> If the backend came up while you were in offline mode, click **⚙️ Backend settings**, verify the URL, then navigate back to Landing and click **▶ Run Sample Audit** to demo live results.

---

## Talking points for evaluator questions

| Question | Answer |
|---|---|
| "Why SQLite not Postgres?" | Zero-config, file-based, perfect for a single-machine desktop tool. ORM layer means switching to Postgres requires changing one connection string. |
| "Why Streamlit not React?" | The entire value prop is rapid iteration on a static-analysis tool. Streamlit lets the analysis logic be Python-native; React would require a separate API design for every widget. |
| "What does CRS measure?" | Penalises each detected anti-pattern: CRITICAL −15, WARNING −8, INFO −3, floored at 0. Reproducible across commits. |
| "How does the call graph work?" | Second `ast.NodeVisitor` subclass (`CallGraphVisitor`) tracks the currently-scoped function name and records every `ast.Call` it encounters — no runtime needed, purely syntactic. |
| "What anti-patterns do you detect?" | Hardcoded credentials (variable name heuristic), unclosed `open()` (context manager check), `eval()`/`exec()` injection, silent `except: pass`, and dead/orphaned functions. |
| "Can it scan JavaScript / Java?" | Not currently — the engine uses Python's stdlib `ast` module which only parses Python. Each language would need its own parser and rule set. |

---

## Emergency commands

```powershell
# Kill port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill port 8501 (frontend)
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Re-run backend manually
cd d:\CodeCompass\backend
..\ccenv\Scripts\uvicorn app.main:app --reload --port 8000

# Re-run frontend manually
cd d:\CodeCompass\frontend
..\ccenv\Scripts\streamlit run app.py

# Run tests to confirm nothing broke
cd d:\CodeCompass
ccenv\Scripts\python -m pytest tests/ -v
```
