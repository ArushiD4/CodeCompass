"""findings.py — Audit findings: severity & rule filters, plain-language explanations."""
import streamlit as st
from config import GLOBAL_FILE, SEVERITIES, SEVERITY_TONE
from components.primitives import esc, sev_pill
from entrypoints import entrypoint

PAGE = 8
SEV_FILTERS = ("All", "Critical", "Warning", "Info")

# rule name -> (question, in simple words, how to fix, what to say if asked)
VIVA = {
    "Hardcoded Credential": (
        "I see a password or key written directly in your code. Why is that a problem, and how should it be handled?",
        "A secret typed into your code is saved in every copy of the project and in git history. "
        "Anyone who can open the code can read it. If the value is empty or only a placeholder, this finding is a false alarm.",
        "Load it from an environment variable or a secrets file that you do not upload to git. "
        "If it was already pushed, change the key.",
        "I keep secrets out of the source code and load them from the environment, and I change any key that was ever committed."),
    "Unclosed Resource Handle": (
        "How do you make sure this file gets closed, even if an error happens?",
        "A file left open uses up a limited resource, and an error before close() can leave it open. "
        "'with open(...)' closes it for you automatically. CodeCompass flags every open() call, so if yours is already inside a 'with', it is safe.",
        "Use 'with open(...) as f:' or Path(...).read_text().",
        "I open files with 'with', so they close automatically even if something fails."),
    "Dynamic Code Injection Risk": (
        "Why does your code use eval() or exec(), and what could go wrong?",
        "They run any text as Python code. If part of that text comes from a user, a file or the network, "
        "someone can make your program run their commands.",
        "Use ast.literal_eval() for plain data such as numbers, lists and dicts. For anything else, use normal functions or a lookup table.",
        "I avoid eval and exec because they run whatever text they get. I use ast.literal_eval or explicit code instead."),
    "Silent Exception Swallowing": (
        "What happens in your program when this error occurs, and why do you ignore it?",
        "'except: pass' hides the error. The program carries on as if nothing happened, and when something breaks later, nothing tells you why.",
        "Catch only the specific error you expect (such as ValueError or FileNotFoundError), "
        "and log it, show a message, or use a safe default on purpose.",
        "I catch specific errors and log them, so failures are visible and I can debug them."),
    "Orphaned Function": (
        "Is this function used anywhere? If not, why is it still in the project?",
        "Nothing in your code calls this function directly. It may be dead code you can delete. "
        "It may also be called by a framework, such as a button callback or a web route, which the tool cannot see.",
        "Search for the function's name. If nothing uses it, delete it. If a framework calls it, keep it.",
        "I checked where this function is used. It is called by a framework, or it was unused and I removed it."),
}


def _lookup(rule):
    if rule in VIVA:
        return VIVA[rule]
    return next((v for k, v in VIVA.items() if rule.startswith(k) or k.startswith(rule)), None)


def _location(issue):
    if issue.get("file_path") == GLOBAL_FILE or not issue.get("line_number"):
        return GLOBAL_FILE
    return f'{issue["file_path"]}:{issue["line_number"]}'


def _card(issue):
    tone = SEVERITY_TONE.get(issue.get("severity"), "info")
    rule = issue.get("rule_name", "Finding")
    tip = issue.get("viva_tip", "")
    v = _lookup(rule)
    question = v[0] if v else "What is the risk and the fix for this pattern?"
    p = 'style="margin:.25rem 0 .6rem;font-size:.85rem;line-height:1.5;color:var(--ink-2)"'
    h = 'style="color:var(--ink);font-size:.82rem"'
    if v:
        body = (f'<b {h}>In simple words</b><p {p}>{esc(v[1])}</p>'
                f'<b {h}>How to fix</b><p {p}>{esc(v[2])}</p>'
                f'<b {h}>What to say if asked</b><p {p}>{esc(v[3])}</p>')
    else:
        body = f'<p {p}>{esc(tip)}</p>'

    return (
        f'<article class="cc-find tone-{tone}">'
        f'<div class="cc-find-top">'
        f'<div><div class="cc-rule">{esc(rule)}</div>'
        f'<div class="cc-mono">{esc(_location(issue))}</div></div>'
        f'<div>{sev_pill(issue.get("severity", "INFO"))}</div>'
        f'</div>'
        f'<div class="cc-tip" style="margin-top:.75rem">'
        f'<b>Question:</b> {esc(question)}'
        f'<details style="margin-top:.5rem;padding:.4rem .6rem;background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:8px">'
        f'<summary style="cursor:pointer;color:var(--brand);font-size:.82rem;font-weight:600">Show simple explanation →</summary>'
        f'<div style="margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--line)">{body}</div>'
        f'</details>'
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
