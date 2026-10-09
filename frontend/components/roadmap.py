"""roadmap.py — Engineering Roadmap & Future Expansion (ARCHITECTURE.md 10.2)."""
import streamlit as st
from config import APP_NAME
from components.primitives import esc, footer, pill

MILESTONES = (
    ("Multi-Language AST via Tree-sitter", "Engine Expansion",
     "Extend beyond Python to TypeScript, Go, and Java using Tree-sitter native bindings, enabling polyglot project auditing with unified grammar abstractions."),
    ("Production PostgreSQL Migration", "Data Layer",
     "Transition the SQLite metadata store to PostgreSQL, supporting enterprise multi-tenancy and distributed horizontal workers."),
    ("Real-time IDE Language Server", "Developer Experience",
     "Package the AST rule engine as a Language Server Protocol (LSP) daemon, displaying Viva Defense tips inline within VS Code and Cursor."),
)


def render():
    st.html(f'<p class="cc-h1" style="margin-top:1rem;font-size:2.2rem">{esc(APP_NAME)} Future Enhancements</p>'
            f'<p class="cc-lede">Planned capabilities for {esc(APP_NAME)}</p>')
    cards = "".join(
        f'<div class="cc-card" style="margin-bottom:1rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem">'
        f'{pill(stage, "good")}<span class="cc-mono" style="color:var(--brand)">Planned</span></div>'
        f'<p class="cc-h2" style="font-size:1.15rem;margin:.5rem 0">{esc(title)}</p>'
        f'<p class="cc-muted" style="line-height:1.6">{esc(desc)}</p>'
        f'</div>'
        for title, stage, desc in MILESTONES
    )
    st.html(f'<div class="cc-feat" style="margin-top:1.5rem">{cards}</div>')
    st.html(footer())
