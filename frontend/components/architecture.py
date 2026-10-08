"""System architecture summary for evaluators (ARCHITECTURE.md sections 2, 4 and 7)."""
import streamlit as st
from config import PIPELINE, RULES, SEVERITY_WEIGHT, STACK
from components.primitives import esc, sev_pill


def _stack():
    return "".join(f'<div class="cc-tile"><span>{esc(layer)}</span><b style="font-size:1rem;'
                   f'letter-spacing:-.01em">{esc(tech)}</b><p class="cc-muted" style="margin-top:.5rem">'
                   f'{esc(note)}</p></div>' for layer, tech, note in STACK)


def _rules():
    rows = "".join(f'<tr><td><b>{esc(name)}</b></td><td>{sev_pill(sev)}</td><td class="cc-mono">'
                   f'-{SEVERITY_WEIGHT[sev]}</td><td class="cc-mono">{esc(node)}</td><td>{esc(what)}</td></tr>'
                   for name, sev, node, what in RULES)
    return ('<table class="cc-table"><tr><th>Rule</th><th>Severity</th><th>Pts</th><th>AST node</th>'
            f'<th>Detects</th></tr>{rows}</table>')



def render():
    flow = '<span class="cc-muted">→</span>'.join(f'<span class="cc-step">{esc(s)}</span>' for s in PIPELINE)
    st.html(f'<div class="cc-stack">{_stack()}</div>'
            '<div class="cc-card" style="margin-top:1rem"><p class="cc-h2">Request lifecycle</p>'
            f'<div class="cc-flow">{flow}</div>'
            '<p class="cc-muted">CRS = max(0, 100 − Σ w(severity)). Critical −15, Warning −8, Info −3.</p></div>'
            f'<div class="cc-card" style="margin-top:1rem"><p class="cc-h2">The five AST rules</p>{_rules()}</div>')
