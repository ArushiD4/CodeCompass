"""project_structure.py — Project structure tab built from fetched audit & graph data."""
from collections import Counter, defaultdict
import streamlit as st
from components import graph_data
from components.primitives import esc, pill


def _findings_by_file(issues):
    counts = Counter(i.get("file_path", "unknown") for i in issues)
    if not counts:
        return '<p class="cc-muted">No findings detected in any file.</p>'
    rows = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:.4rem 0;border-bottom:1px solid var(--line)">'
        f'<span class="cc-mono">{esc(f)}</span>'
        f'<span>{pill(f"{c} findings", "bad" if c > 2 else "warn")}</span></div>'
        for f, c in counts.most_common(10)
    )
    return f'<div>{rows}</div>'


def _graph_breakdown(graph):
    if not graph:
        return ""
    shaped = graph_data.shape(graph, 100, hide_isolated=False)
    mod_counts = Counter(n["module"] for n in shaped["nodes"])
    top_connected = sorted(shaped["nodes"], key=lambda n: n["degree"], reverse=True)[:5]

    mod_rows = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid var(--line)">'
        f'<span class="cc-mono">{esc(m)}</span><span class="cc-pill tone-info">{c} functions</span></div>'
        for m, c in mod_counts.most_common()
    )
    hub_rows = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:.35rem 0;border-bottom:1px solid var(--line)">'
        f'<span class="cc-mono">{esc(n["label"])}() <span style="color:var(--mute)">({esc(n["module"])})</span></span>'
        f'<span class="cc-pill tone-good">{n["degree"]} calls</span></div>'
        for n in top_connected
    )
    return (
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem">'
        f'<div class="cc-card"><p class="cc-h2">Modules & Folders</p>{mod_rows}</div>'
        f'<div class="cc-card"><p class="cc-h2">Top Connected Hubs</p>{hub_rows}</div>'
        f'</div>'
    )


def render():
    ss = st.session_state
    audit = ss.get("last_audit_data") or {}
    project_name = audit.get("project_name") or "Audited Codebase"
    issues = audit.get("issues", [])
    graph = ss.get("graph_data")

    st.html(f'<p class="cc-h2" style="font-size:1.3rem;margin:1rem 0 .5rem">'
            f'Structure of {esc(project_name)}</p>')

    tiles = "".join(f'<div class="cc-tile"><span>{k}</span><b>{v}</b></div>' for k, v in (
        ("Files Scanned", audit.get("total_files", 0)),
        ("Total Functions", audit.get("total_functions", 0)),
        ("Total Findings", len(issues))
    ))
    st.html(f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">{tiles}</div>')

    st.html(f'<div class="cc-card" style="margin-top:1rem">'
            f'<p class="cc-h2">Files with Most Findings</p>{_findings_by_file(issues)}</div>')

    if graph:
        st.html(_graph_breakdown(graph))
