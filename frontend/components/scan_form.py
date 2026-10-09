"""scan_form.py — Audit input card, signal-lost state, and scan pipeline."""
import os
import streamlit as st
import api_client
import state
from config import APP_NAME
from components import scan_loader
from components.primitives import esc


def _signal_lost_card():
    st.html(
        f'<div class="cc-card tone-bad" style="border-color:var(--tline);margin:1rem 0">'
        f'<div style="display:flex;align-items:center;gap:.6rem;color:var(--bad)">'
        f'<span class="cc-dot"></span><b>SIGNAL LOST — Backend Connection Failed</b></div>'
        f'<p class="cc-muted" style="margin:.6rem 0">{esc(APP_NAME)} cannot reach the FastAPI server.</p>'
        f'<div class="cc-code-box" style="padding:1rem;margin:.5rem 0">'
        f'<span>Start the backend with:</span><br>'
        f'<span style="color:var(--brand);font-weight:700">uvicorn app.main:app --reload --port 8000</span>'
        f'</div></div>'
    )
    if st.button("Retry connection", type="primary"):
        st.rerun()


def _scan(name, path):
    ss = st.session_state
    path = os.path.expanduser(path)
    if not name or not path:
        st.warning("Enter a project name and a directory path first.")
        return
    if not os.path.isdir(path):
        st.error(f"Directory not found: {path}. Use an absolute path.")
        return

    py_files = [f for _, _, files in os.walk(path) for f in files if f.endswith(".py")][:6]
    with st.status("Executing Static AST Audit...", expanded=True) as status:
        st.html(scan_loader.render_sweep(py_files))
        audit, err = api_client.run_audit(name, path)
        if err:
            status.update(label="Audit failed", state="error")
            if "Cannot reach the backend" in err:
                _signal_lost_card()
            else:
                st.error(err)
            return
        report, _ = api_client.get_project(audit.get("project_id", 0))
        graph, graph_err = api_client.get_graph(path)
        state.clear_results()
        ss.update(last_audit_data=audit, last_audit_path=path, report_data=report,
                  graph_data=graph, graph_error=graph_err)
        status.update(label=f"Scan complete · CRS {audit.get('crs_score', 0)}",
                      state="complete", expanded=False)


def render():
    ss = st.session_state
    with st.container(key="card_scan"):
        st.html(f'<p class="cc-h2" style="font-size:1.15rem">Audit Workspace</p>'
                f'<p class="cc-muted">Point {esc(APP_NAME)} at a local Python codebase. '
                f'Your code is parsed, never executed.</p>')
        c_name, c_path, c_run = st.columns([2.5, 4.5, 1.5], vertical_alignment="bottom")
        name = c_name.text_input("Project name", key="scan_name", placeholder="Codebase Name")
        path = c_path.text_input("Local directory path", key="scan_path", placeholder="D:\\Projects\\repo")
        run = c_run.button("Run audit", type="primary", width="stretch")
        with st.expander("Open a historical report"):
            c_id, c_open = st.columns([3, 1.4], vertical_alignment="bottom")
            pid = c_id.number_input("Project ID", min_value=1, step=1, key="saved_id")
            if c_open.button("Open Report", width="stretch"):
                data, err = api_client.get_project(pid)
                if not err and data:
                    p = data["project"]
                    state.clear_results()
                    ss.update(report_data=data, last_audit_data={**p, "project_id": p["id"], "issues": data["issues"]})

    if ss.pop("autorun", False) or run:
        _scan(name.strip(), path.strip())
