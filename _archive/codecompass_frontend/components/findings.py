"""Audit findings: severity filter, cards with the Viva Defense Tip, pagination."""
import streamlit as st
from config import GLOBAL_FILE, SEVERITIES, SEVERITY_TONE
from components.primitives import esc, sev_pill

PAGE = 8
FILTERS = ("All", "Critical", "Warning", "Info")


def _location(issue):
    if issue.get("file_path") == GLOBAL_FILE or not issue.get("line_number"):
        return GLOBAL_FILE
    return f'{issue["file_path"]}:{issue["line_number"]}'


def _card(issue):
    tone = SEVERITY_TONE.get(issue.get("severity"), "info")
    return (f'<article class="cc-find tone-{tone}"><div class="cc-find-top">'
            f'<div><div class="cc-rule">{esc(issue.get("rule_name", "Finding"))}</div>'
            f'<div class="cc-mono">{esc(_location(issue))}</div></div>'
            f'{sev_pill(issue.get("severity", "INFO"))}</div>'
            f'<div class="cc-tip"><b>Viva Defense Tip</b>{esc(issue.get("viva_tip", ""))}</div></article>')


def _more():
    st.session_state["findings_limit"] += PAGE


def render(issues):
    ss = st.session_state
    if not issues:
        st.html('<div class="cc-card tone-good" style="border-color:var(--tline);background:var(--tbg)">'
                '<p class="cc-h2">No findings</p><p class="cc-muted">None of the five rules matched. '
                'Be ready to explain what you checked.</p></div>')
        return
    choice = st.segmented_control("Severity", FILTERS, default="All", key="sev_filter",
                                  label_visibility="collapsed") or "All"
    rank = {s: i for i, s in enumerate(SEVERITIES)}
    shown = [i for i in issues if choice == "All" or i.get("severity") == choice.upper()]
    shown.sort(key=lambda i: (rank.get(i.get("severity"), 9), i.get("file_path", ""), i.get("line_number", 0)))
    limit = ss["findings_limit"]
    st.html(f'<div class="cc-finds">{"".join(_card(i) for i in shown[:limit])}</div>')
    if len(shown) > limit:
        st.button(f"Show {min(PAGE, len(shown) - limit)} more of {len(shown) - limit} remaining",
                  on_click=_more)
