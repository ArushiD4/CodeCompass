"""explain_facts_card.py — Renders AST facts card for a selected codebase file."""
import streamlit as st
from components.primitives import esc


def _truncate_list(items: list, max_items: int = 8) -> str:
    if not items:
        return "none"
    if len(items) <= max_items:
        return ", ".join(items)
    return ", ".join(items[:max_items]) + f" (+{len(items) - max_items} more)"


def render_facts_card(fpath: str, facts: dict, called_by_list: list, calls_into_list: list):
    if facts.get("parse_error"):
        st.warning(f"Parse error: {facts['parse_error']}")
        return

    imports = [f"{n} ({k})" for n, k in facts.get("imports", [])]
    classes = [f"{n} ({m} methods)" for n, m in facts.get("classes", [])]
    functions = facts.get("functions", [])
    entry_point = "Yes" if facts.get("entry_point") else "No"
    io_calls = facts.get("io_calls", [])
    globals_list = [f"{n} ({k})" for n, k in facts.get("globals", [])]
    cb = [f"{f}::{fn}{'?' if p else ''}" for f, fn, p in called_by_list]
    ci = [f"{f}::{fn}{'?' if p else ''}" for f, fn, p in calls_into_list]

    lines = [
        f"File:        {esc(fpath)}",
        f"Imports:     {esc(_truncate_list(imports))}",
        f"Classes:     {esc(_truncate_list(classes))}",
        f"Functions:   {esc(_truncate_list(functions))}",
        f"Entry point: {esc(entry_point)}",
        f"Reads/writes:{esc(_truncate_list(io_calls))}",
        f"Global state:{esc(_truncate_list(globals_list))}",
        f"Called by:   {esc(_truncate_list(cb))}",
        f"Calls into:  {esc(_truncate_list(ci))}",
    ]
    card_html = (
        f'<div class="cc-card" style="margin:1rem 0">'
        f'<pre style="margin:0;font-family:var(--font-mono);font-size:.85rem;white-space:pre-wrap;color:var(--text)">'
        + "\n".join(lines) +
        f'</pre></div>'
    )
    st.html(card_html)
