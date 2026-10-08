"""Dashboard: scan form, CRS hero bento, then one section at a time."""
import streamlit as st
from config import SECTIONS
from components import architecture, findings, graph_view, hero, navbar, scan_form

EMPTY = ('<div class="cc-card" style="margin-top:1rem"><p class="cc-h2">No audit yet</p>'
         '<p class="cc-muted">Enter a project name and directory above, then run the audit. '
         'You will get a readiness score, findings with defense tips, and a call graph.</p></div>')


def render():
    ss = st.session_state
    navbar.render("dashboard")
    scan_form.render()
    audit = ss.get("last_audit_data")
    if not audit:
        st.html(EMPTY)
        return
    hero.render(audit, ss.get("report_data"))
    section = st.segmented_control("Section", SECTIONS, default=SECTIONS[0], key="section",
                                   label_visibility="collapsed") or SECTIONS[0]
    if section == "Findings":
        findings.render(audit.get("issues", []))
    elif section == "Call graph":
        graph_view.render()
    else:
        architecture.render()
