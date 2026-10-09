"""dashboard.py — Main Application Dashboard with Workspace navigation."""
import streamlit as st
import api_client
from config import AREAS, SECTIONS
from components import (about_codecompass, compare_audits, findings, graph_view,
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

    curr_pid = audit.get("project_id") or (ss.get("report_data") or {}).get("project", {}).get("id")
    pname = audit.get("project_name") or (ss.get("report_data") or {}).get("project", {}).get("project_name")
    if curr_pid and pname:
        base_url = ss.get("backend_url", "http://localhost:8000")
        projects, _ = api_client.list_projects(base_url)
        older = [p["id"] for p in projects if p.get("project_name") == pname and p.get("id") < curr_pid]
        if older:
            older_id = max(older)
            def _go_compare():
                st.session_state["compare_ids"] = (older_id, curr_pid)
                st.session_state["area"] = "Compare audits"
            st.button("Compare with previous audit", key="btn_cmp_prev", on_click=_go_compare)

    if ss.get("section") not in SECTIONS:
        ss["section"] = SECTIONS[0]
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
    if ss.get("area") not in AREAS:
        ss["area"] = "Audit"
    area = st.segmented_control("Workspace Area", AREAS,
                                default=ss.get("area", "Audit"),
                                key="area", label_visibility="collapsed") or "Audit"

    if area == "Audit":
        _render_audit_area()
    elif area == "About CodeCompass":
        about_codecompass.render()
    elif area == "Roadmap":
        roadmap.render()
    elif area == "Compare audits":
        compare_audits.render()
