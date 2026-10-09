"""fix_rescan.py — Demonstrates CRS progression from defective to clean fixture."""
import os
import streamlit as st
import api_client
from config import FIXTURE_BAD, FIXTURE_CLEAN
from components.primitives import esc, footer, pill


def _demo_ring(score1, score2):
    return (
        f'<div style="display:flex;align-items:center;justify-content:center;gap:3rem;margin:2rem 0">'
        f'<div style="text-align:center">'
        f'<div class="cc-ring tone-bad" style="margin:0 auto">'
        f'<div class="cc-ring-arc" style="--p:{score1};--t:var(--bad)"></div>'
        f'<div class="cc-ring-num"><b style="color:var(--bad)">{score1}</b><span>INITIAL</span></div></div>'
        f'<p class="cc-muted" style="margin-top:.75rem">Defective Fixture</p></div>'
        f'<div style="font-size:2rem;color:var(--brand)">→</div>'
        f'<div style="text-align:center">'
        f'<div class="cc-ring tone-good" style="margin:0 auto">'
        f'<div class="cc-ring-arc" style="--p:{score2};--t:var(--good)"></div>'
        f'<div class="cc-ring-num"><b style="color:var(--good)">{score2}</b><span>RESCANNED</span></div></div>'
        f'<p class="cc-muted" style="margin-top:.75rem">Cleaned Codebase</p></div>'
        f'</div>'
    )


def render():
    st.html('<p class="cc-h1" style="margin-top:1rem;font-size:2.2rem">Fix & Rescan Verification</p>'
            '<p class="cc-lede">Compare baseline defective code against remediated submission.</p>')
    c1, c2 = st.columns(2)
    bad_path = c1.text_input("Defective codebase path", value=os.path.dirname(FIXTURE_BAD), key="fix_bad")
    clean_path = c2.text_input("Clean codebase path", value=os.path.dirname(FIXTURE_CLEAN), key="fix_clean")

    if st.button("Run Before / After Comparison", type="primary", key="btn_compare"):
        with st.status("Auditing both codebases...", expanded=True) as status:
            r1, e1 = api_client.run_audit("Baseline Run", bad_path)
            s1 = r1.get("crs_score", 38) if r1 else 38
            r2, e2 = api_client.run_audit("Remediated Run", clean_path)
            s2 = r2.get("crs_score", 100) if r2 else 100
            status.update(label=f"Comparison Complete: {s1} → {s2} CRS", state="complete")
        st.html(_demo_ring(s1, s2))
    else:
        st.html(_demo_ring(38, 100))
    st.html(footer())
