"""dashboard.py — Main Application Dashboard with Workspace navigation."""
import streamlit as st
from config import AREAS, SECTIONS
from components import (about_codecompass, findings, fix_rescan, graph_view,
                        hero, navbar, project_structure, roadmap, scan_form)

EMPTY = ('<div class="cc-card" style="margin-top:1rem"><p class="cc-h2">No audit yet</p>'
         '<p class="cc-muted">Enter a project name and directory above, then run the audit. '
         'You will get a readiness score, findings with defense tips, and a call graph.</p></div>')


def _render_audit_area():
    ss = st.session_state
    scan_form.render()
    audit = ss.get("last_audit_data")
    if not audit:
        st.html(EMPTY)
        return
    hero.render(audit, ss.get("report_data"))
    sec = st.segmented_control("Project Section", SECTIONS,
                               default=ss.get("section", SECTIONS[0]),
                               key="section", label_visibility="collapsed") or SECTIONS[0]
    if sec == "Findings":
        findings.render(audit.get("issues", []))
    elif sec == "Call graph":
        graph_view.render()
    elif sec == "Project structure":
        project_structure.render()


def render():
    ss = st.session_state
    navbar.render("dashboard")
    area = st.segmented_control("Workspace Area", AREAS,
                                default=ss.get("area", "Audit"),
                                key="area", label_visibility="collapsed") or "Audit"

    if area == "Audit":
        _render_audit_area()
    elif area == "About CodeCompass":
        about_codecompass.render()
    elif area == "Roadmap":
        roadmap.render()
    elif area == "Fix and rescan":
        fix_rescan.render()
