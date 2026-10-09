"""about_codecompass.py — System architecture & interactive CRS calculator."""
import streamlit as st
from config import APP_NAME, RULES, SEVERITY_WEIGHT, STACK, TAGLINE
from components.primitives import esc, footer, pill, sev_pill


def _header():
    return (
        f'<div style="margin-bottom:1.5rem">'
        f'<p class="cc-h1" style="margin-top:1rem;font-size:2.2rem">About {esc(APP_NAME)}</p>'
        f'<p class="cc-lede" style="margin-bottom:.5rem">{esc(TAGLINE)}</p>'
        f'<div class="cc-pill tone-info" style="margin-top:.25rem">'
        f'<span class="cc-dot"></span>This page describes {esc(APP_NAME)} itself, not the project you scanned.</div>'
        f'</div>'
    )


def _stack():
    return "".join(
        f'<div class="cc-tile"><span>{esc(layer)}</span>'
        f'<b style="font-size:1.05rem;color:var(--ink)">{esc(tech)}</b>'
        f'<p class="cc-muted" style="margin-top:.5rem">{esc(note)}</p></div>'
        for layer, tech, note in STACK
    )


def _rules_table():
    rows = "".join(
        f'<tr><td><b>{esc(name)}</b></td><td>{sev_pill(sev)}</td><td class="cc-mono">-{SEVERITY_WEIGHT[sev]}</td>'
        f'<td class="cc-mono">{esc(node)}</td><td>{esc(what)}</td></tr>'
        for name, sev, node, what in RULES
    )
    return (f'<table class="cc-table"><tr><th>Rule</th><th>Severity</th><th>Pts</th><th>AST node</th>'
            f'<th>Detects</th></tr>{rows}</table>')


def _calculator():
    st.html('<div class="cc-card" style="margin-top:1.5rem">'
            '<p class="cc-h2">Interactive CRS Calculator</p>'
            '<p class="cc-muted">Verify the exact formula: CRS = max(0, 100 - 15×Critical - 8×Warning - 3×Info)</p></div>')
    c1, c2, c3 = st.columns(3)
    crit = c1.slider("Critical findings (-15 pts)", 0, 8, 3, key="calc_crit")
    warn = c2.slider("Warning findings (-8 pts)", 0, 8, 1, key="calc_warn")
    info = c3.slider("Info findings (-3 pts)", 0, 8, 3, key="calc_info")
    deductions = 15 * crit + 8 * warn + 3 * info
    score = max(0, 100 - deductions)
    tone = "good" if score >= 80 else ("warn" if score >= 50 else "bad")
    band_name = "Highly Ready" if score >= 80 else ("Needs Work" if score >= 50 else "Critical Issues Detected")
    st.html(
        f'<div class="cc-card tone-{tone}" style="border-color:var(--tline);margin-top:.75rem">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<div><span style="font-size:2.2rem;font-weight:700;color:var(--t)">{score} / 100</span>'
        f'<span class="cc-mono" style="margin-left:1rem">(-{deductions} pts)</span></div>'
        f'<div>{pill(band_name, tone, dot=True)}</div></div></div>'
    )


def render():
    st.html(_header())
    st.html(f'<div class="cc-stack">{_stack()}</div>')
    st.html(f'<div class="cc-card" style="margin-top:1.25rem"><p class="cc-h2">The five AST rules</p>{_rules_table()}</div>')
    _calculator()
    st.html(footer())
