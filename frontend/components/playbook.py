"""playbook.py — Viva Defense Playbook: rules and architecture defense guide."""
import streamlit as st
from config import APP_NAME
from components.primitives import esc, footer, pill

PLAYBOOK_CARDS = (
    ("AST Static Analysis", "Architecture Defense", "3 min read",
     "Why did you choose AST over regex or runtime execution?",
     "Regex fails on nested structures, multiline assignments, and comments. AST converts code into a rigorous syntax tree. We never execute student code (unlike flake8/pylint plugins), protecting the server from untrusted code injection."),
    ("FastAPI + Uvicorn", "Architecture Defense", "2 min read",
     "Why FastAPI instead of Flask or Django?",
     "FastAPI provides asynchronous request handling with automatic OpenAPI schemas, Pydantic type validation, and dependency injection guards for API key authentication with minimal boilerplate."),
    ("SQLite + SQLAlchemy 2.0", "Architecture Defense", "2 min read",
     "Why SQLite for an enterprise-styled tool?",
     "Zero-configuration, serverless single-file database ideal for local evaluation and portable viva defense demos. Foreign key constraints with cascade deletes ensure audit reports remain referentially sound."),
    ("Hardcoded Credentials", "Rule 1 Defense", "2 min read",
     "What is the defense for detected hardcoded keys?",
     "API secrets committed to repositories persist in git history forever. Best practice is twelve-factor environment configuration loaded via os.environ or .env files excluded via .gitignore."),
    ("Resource Leakage", "Rule 2 Defense", "2 min read",
     "Why enforce 'with open(...)' context managers?",
     "Unclosed file descriptors exhaust operating system handles and cause file-lock collisions. Python context managers guarantee __exit__() cleanup even when exceptions occur."),
    ("Dynamic Code Execution", "Rule 3 Defense", "2 min read",
     "Why are eval() and exec() prohibited?",
     "eval() parses arbitrary string inputs with full interpreter permissions, enabling remote code execution and namespace pollution."),
    ("Silent Exception Swallowing", "Rule 4 Defense", "2 min read",
     "Why is 'except: pass' a critical defect?",
     "Bare except blocks catch SystemExit and KeyboardInterrupt, concealing bugs and preventing clean server shutdowns."),
)


def render():
    st.html(f'<p class="cc-h1" style="margin-top:1rem;font-size:2.2rem">{esc(APP_NAME)} Defense Playbook</p>'
            f'<p class="cc-lede">Architectural rationales and Viva answers directly from evaluation criteria.</p>')
    cards = "".join(
        f'<div class="cc-card cc-find tone-info" style="margin-bottom:1rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
        f'<div>{pill(cat, "info")}<span class="cc-mono" style="margin-left:.75rem">{read}</span></div>'
        f'<span class="cc-more">Read tips →</span></div>'
        f'<p class="cc-h2" style="font-size:1.15rem;margin:.5rem 0">{esc(title)}</p>'
        f'<div class="cc-tip" style="margin-top:.5rem"><b>Examiner Question:</b> {esc(q)}</div>'
        f'<p class="cc-muted" style="margin-top:.75rem;line-height:1.6">{esc(ans)}</p>'
        f'</div>'
        for title, cat, read, q, ans in PLAYBOOK_CARDS
    )
    st.html(f'<div class="cc-finds" style="grid-template-columns:1fr">{cards}</div>')
    st.html(footer())
