"""scan_form.py — Audit input card, signal-lost state, and scan pipeline."""
import os
import streamlit as st
import api_client
import state
from config import APP_NAME
from components import report_picker, scan_loader
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
    is_sample = ss.pop("_sample_in_flight", False)
    if not ss.get("authenticated"):
        if ss.get("sample_audit_used") and not is_sample:
            ss["auth_notice"] = (
                "You have already used your 1 free sample audit for this session. "
                "Please sign in or create an account to audit additional projects."
            )
            ss["_page"] = "auth"
            st.rerun()
            return
        ss["sample_audit_used"] = True
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
        api_client.list_projects.clear()


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
            base_url = ss.get("backend_url", "http://localhost:8000")
            projects, proj_map, label_map, err = report_picker.load_report_options(base_url)
            if err:
                if "Cannot reach the backend" in err:
                    _signal_lost_card()
                else:
                    st.error(err)
            elif not projects:
                st.info("No previous audits yet.")
            else:
                visible = projects[:100]
                options = [p["id"] for p in visible]
                c_sel, c_open = st.columns([4, 1.5], vertical_alignment="bottom")
                sel_id = c_sel.selectbox(
                    "Previous audits",
                    options=options,
                    format_func=lambda pid: label_map.get(pid, f"Audit #{pid}"),
                    index=None,
                    placeholder="Search by project name",
                    key="hist_report_id"
                )
                open_clicked = c_open.button("Open report", disabled=(sel_id is None), width="stretch")
                if len(projects) > 100:
                    st.caption(f"Showing the newest 100 of {len(projects)} audits.")
                if open_clicked and sel_id is not None:
                    data, err = api_client.get_project(sel_id)
                    if err or not data:
                        st.error(err or "Failed to load report.")
                    else:
                        p = data["project"]
                        expected_name = proj_map.get(sel_id, {}).get("project_name")
                        if expected_name and p.get("project_name") != expected_name:
                            st.warning("The project name differs from the label. The database may have been reset.")
                        state.clear_results()
                        ss.update(report_data=data, last_audit_data={**p, "project_id": p["id"], "issues": data["issues"]})
                        st.rerun()

    if ss.pop("autorun", False) or run:
        _scan(name.strip(), path.strip())
