"""
dashboard.py — Main Application Dashboard View.

Renders the core authenticated interface. Orchestrates the display of the
scan configuration form, the high-level Code Readiness Score (CRS) hero banner,
and the tabbed content sections (Findings, Call Graph, Architecture).
"""
import streamlit as st
from config import SECTIONS
from components import architecture, findings, graph_view, hero, navbar, scan_form

EMPTY = ('<div class="cc-card" style="margin-top:1rem"><p class="cc-h2">No audit yet</p>'
         '<p class="cc-muted">Enter a project name and directory above, then run the audit. '
         'You will get a readiness score, findings with defense tips, and a call graph.</p></div>')


def render():
    """
    Renders the complete dashboard interface.
    
    Validates the presence of recent audit data in the session state. If data exists,
    it orchestrates the rendering of the top-level hero metrics and delegates the 
    lower-half rendering to the currently selected sub-view (Findings, Call graph, 
    or Architecture). If no data exists, an empty placeholder is shown.
    """
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
