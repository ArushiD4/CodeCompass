"""landing.py — Public Landing Page View."""
import streamlit as st
import state
from config import APP_NAME, RULES, SEVERITY_WEIGHT, TAGLINE
from components import intro, navbar
from components.primitives import esc, footer, pill, sev_pill


def _headline():
    return (
        f'<div class="cc-hero-lockup">'
        f'<h1 class="cc-brand-title">{esc(APP_NAME)}</h1>'
        f'<p class="cc-hero-tagline">{esc(TAGLINE)}</p>'
        f'<p class="cc-hero-support">Audit your code the way your examiner will read it.</p>'
        f'</div>'
    )


def _scroll_cue():
    return '<div class="cc-scroll-cue"><span class="cc-chevron"></span></div>'


def _bento():
    ring_88 = ('<div class="cc-ring" style="width:110px;height:110px;margin-top:.75rem">'
               '<div class="cc-ring-arc" style="--p:88;--t:var(--good)"></div>'
               '<div class="cc-ring-num"><b style="font-size:2rem">88</b>'
               '<span style="font-size:.65rem">READY</span></div></div>')
    ast_tags = (f'<div style="display:flex;gap:.4rem;margin-top:.85rem;flex-wrap:wrap">'
                f'{pill("ast.parse", "info")}{pill("No shell exec", "good")}'
                f'{pill("Zero runtime", "good")}</div>')
    return (
        '<div class="cc-feat">'
        f'<div class="cc-card"><p class="cc-h2">Zero-execution auditing</p>'
        f'<p class="cc-muted">Five AST rules parse your Python codebase into syntax trees without executing '
        f'a single line. Even broken code is completely safe to scan.</p>{ast_tags}</div>'
        f'<div class="cc-card tone-good"><p class="cc-h2">Code Readiness Score</p>'
        f'<p class="cc-muted">Deterministic score starting from 100 with weighted deductions.</p>'
        f'<div style="display:flex;align-items:center;gap:1.25rem">{ring_88}'
        f'<div><p style="font-weight:700;color:var(--good);margin:0">88 / 100</p>'
        f'<p class="cc-muted" style="font-size:.8rem">High Readiness band</p></div></div></div>'
        f'<div class="cc-card"><p class="cc-h2">Interactive call graph</p>'
        f'<p class="cc-muted">Visualise invocations and function dependencies grouped by module. '
        f'Pinpoint orphaned functions and identify architecture hubs.</p></div>'
        f'<div class="cc-card"><p class="cc-h2">Built-in viva defense coach</p>'
        f'<p class="cc-muted">Every detected anti-pattern includes the architectural explanation and '
        f'standard refactoring your academic examiner will expect.</p></div>'
        '</div>'
    )


def _rules_accordion():
    items = []
    for name, sev, node, what in RULES:
        pts = SEVERITY_WEIGHT.get(sev, 0)
        items.append(
            f'<details style="margin-bottom:.6rem;padding:.75rem 1rem">'
            f'<summary style="cursor:pointer;display:flex;align-items:center;justify-content:space-between">'
            f'<span><b>{esc(name)}</b> <span class="cc-mono" style="margin-left:.6rem">({esc(node)})</span></span>'
            f'<span>{sev_pill(sev)} <span class="cc-mono" style="margin-left:.5rem">-{pts} pts</span></span>'
            f'</summary>'
            f'<p class="cc-muted" style="margin-top:.6rem">{esc(what)}</p>'
            f'</details>'
        )
    return (f'<div style="margin-top:3rem">'
            f'<p class="cc-h2" style="font-size:1.3rem">The 5 CRS auditing rules</p>'
            f'<p class="cc-muted" style="margin-bottom:1rem">AST visitor checks running against student code.'
            f'</p>{"".join(items)}</div>')


def _enter_path():
    if state.is_allowed():
        state.go("dashboard")
    else:
        state.go("auth")


def render():
    navbar.render("landing")
    intro.render()
    st.html(_headline())
    with st.container(key="hero_cta"):
        c1, c2 = st.columns(2)
        c1.button("Enter project path", type="primary", width="stretch", on_click=_enter_path)
        c2.button("Run sample audit", width="stretch", on_click=state.open_sample)
    st.html(_scroll_cue())
    st.html(_bento())
    st.html(_rules_accordion())
    st.html(footer())
