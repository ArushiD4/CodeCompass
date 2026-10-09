"""findings.py — Audit findings: severity & rule filters, Viva defense expander."""
import streamlit as st
from config import GLOBAL_FILE, SEVERITIES, SEVERITY_TONE
from components.primitives import esc, sev_pill
from entrypoints import entrypoint

PAGE = 8
SEV_FILTERS = ("All", "Critical", "Warning", "Info")

QUESTIONS = {
    "Hardcoded Credential": "Why use static AST analysis instead of running unit tests for secrets?",
    "Unclosed Resource Handle": "Why does bare open() pose a leak risk if Python's garbage collector frees unreferenced handles?",
    "Dynamic Code Injection": "Why is eval() prohibited rather than linting the arguments?",
    "Silent Exception Swallowing": "Why is 'except: pass' a critical defect when error handling is intentional?",
    "Orphaned Function": "How does your tool prevent false positives on entry points when flagging dead code?",
}


def _location(issue):
    if issue.get("file_path") == GLOBAL_FILE or not issue.get("line_number"):
        return GLOBAL_FILE
    return f'{issue["file_path"]}:{issue["line_number"]}'


def _card(issue):
    tone = SEVERITY_TONE.get(issue.get("severity"), "info")
    rule = issue.get("rule_name", "Finding")
    tip = issue.get("viva_tip", "")
    first_line = tip.split(".")[0] + "." if "." in tip else tip
    question = QUESTIONS.get(rule, "What is the architectural risk and remediation for this pattern?")

    return (
        f'<article class="cc-find tone-{tone}">'
        f'<div class="cc-find-top">'
        f'<div><div class="cc-rule">{esc(rule)}</div>'
        f'<div class="cc-mono">{esc(_location(issue))}</div></div>'
        f'<div>{sev_pill(issue.get("severity", "INFO"))}</div>'
        f'</div>'
        f'<div class="cc-tip" style="margin-top:.75rem">'
        f'<b>Examiner Question:</b> {esc(question)}'
        f'<details style="margin-top:.5rem;padding:.4rem .6rem;background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:8px">'
        f'<summary style="cursor:pointer;color:var(--brand);font-size:.82rem;font-weight:600">Reveal answer / defense strategy →</summary>'
        f'<div style="margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--line)">'
        f'<b style="color:var(--ink);font-size:.82rem">Viva Defense Strategy:</b>'
        f'<p style="margin:.25rem 0 0;font-size:.85rem;line-height:1.5;color:var(--ink-2)">{esc(tip)}</p>'
        f'</div></details>'
        f'</div></article>'
    )


@entrypoint()
def _more():
    st.session_state["findings_limit"] += PAGE


def render(issues):
    ss = st.session_state
    if not issues:
        st.html('<div class="cc-card tone-good" style="margin-top:1rem">'
                '<p class="cc-h2">No findings</p><p class="cc-muted">None of the five rules matched. '
                'Zero-execution AST analysis complete.</p></div>')
        return

    c_sev, c_rule = st.columns([1, 1], vertical_alignment="center")
    sev_choice = c_sev.segmented_control("Severity", SEV_FILTERS, default="All", key="f_sev",
                                         label_visibility="collapsed") or "All"
    rule_options = ["All Rules"] + sorted(list({i.get("rule_name", "") for i in issues}))
    rule_choice = c_rule.selectbox("Rule Category", rule_options, key="f_rule",
                                   label_visibility="collapsed") or "All Rules"

    shown = [
        i for i in issues
        if (sev_choice == "All" or i.get("severity") == sev_choice.upper())
        and (rule_choice == "All Rules" or i.get("rule_name") == rule_choice)
    ]
    rank = {s: idx for idx, s in enumerate(SEVERITIES)}
    shown.sort(key=lambda i: (rank.get(i.get("severity"), 9), i.get("file_path", ""), i.get("line_number", 0)))

    limit = ss["findings_limit"]
    st.html(f'<div class="cc-finds">{"".join(_card(i) for i in shown[:limit])}</div>')
    if len(shown) > limit:
        st.button(f"Show {min(PAGE, len(shown) - limit)} more ({len(shown) - limit} remaining)",
                  on_click=_more)
