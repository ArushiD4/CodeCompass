"""Landing page: value proposition, two entry points, feature bento."""
import streamlit as st
import state
from components import navbar
from components.primitives import pill

HEADLINE = ('<h1 class="cc-h1">Audit your code the way your examiner will read it.</h1>'
            '<p class="cc-lede">CodeCompass parses your Python project with the AST, scores its '
            'readiness from 0 to 100, and gives you a defense tip for every finding.</p>')


def _features():
    bands = "".join((pill("80-100  Highly Ready", "good", True), pill("50-79  Needs Work", "warn", True),
                     pill("0-49  Critical Issues", "bad", True)))
    chips = "".join(f'<span class="cc-step">{r}</span>' for r in (
        "Hardcoded secrets", "Unclosed files", "eval / exec", "except: pass", "Dead functions"))
    return (
        '<div class="cc-feat">'
        '<div class="cc-card s4"><p class="cc-h2">AST auditing</p><p class="cc-muted">Five rules walk the '
        'abstract syntax tree. Your code is parsed, never executed, so even broken submissions are safe '
        f'to scan.</p><div class="cc-flow" style="margin-top:1rem">{chips}</div></div>'
        '<div class="cc-card s2"><p class="cc-h2">Code Readiness Score</p><p class="cc-muted">One number '
        f'from deterministic severity weights.</p><div class="cc-bands">{bands}</div></div>'
        '<div class="cc-card s2"><p class="cc-h2">Viva Defense Tips</p><p class="cc-muted">Each finding '
        'ships with the explanation an examiner expects: the risk, and the standard fix.</p></div>'
        '<div class="cc-card s4"><p class="cc-h2">Interactive call graph</p><p class="cc-muted">See which '
        'functions call which, grouped by folder, with the most connected functions highlighted so you '
        'can walk through the design confidently.</p></div></div>')


def render():
    navbar.render("landing")
    st.html(HEADLINE)
    with st.container(key="hero_cta"):
        start, sample = st.columns(2)
        start.button("Get started", type="primary", width="stretch", on_click=state.go, args=("auth",))
        sample.button("Run sample audit", width="stretch", on_click=state.open_sample)
    st.html(_features())
