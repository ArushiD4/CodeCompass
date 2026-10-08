"""Audit input card and the scan pipeline (POST /api/audit, then report and graph)."""
import os
import streamlit as st
import api_client
import state


def _scan(name, path):
    ss = st.session_state
    path = os.path.expanduser(path)
    if not name or not path:
        st.warning("Enter a project name and a directory path first.")
        return
    if not os.path.isdir(path):
        st.error(f"Directory not found: {path}. Use an absolute path if the backend runs elsewhere.")
        return
    with st.status("Scanning project", expanded=True) as status:
        st.write("Parsing Python files into ASTs and applying the five rules...")
        audit, err = api_client.run_audit(name, path)
        if err:
            status.update(label="Audit failed", state="error")
            st.error(err)
            return
        st.write("Loading the saved report from SQLite...")
        report, _ = api_client.get_project(audit.get("project_id", 0))
        st.write("Building the call graph...")
        graph, graph_err = api_client.get_graph(path)
        state.clear_results()
        ss.update(last_audit_data=audit, last_audit_path=path, report_data=report,
                  graph_data=graph, graph_error=graph_err)
        status.update(label=f"Scan complete. CRS {audit.get('crs_score', 0)}",
                      state="complete", expanded=False)


def _load_saved(project_id):
    data, err = api_client.get_project(project_id)
    if err:
        st.error(err)
        return
    project = data["project"]
    state.clear_results()
    st.session_state.update(report_data=data, last_audit_data={
        **project, "project_id": project["id"], "issues": data["issues"],
        "issues_found": len(data["issues"])})


def render():
    ss = st.session_state
    with st.container(key="card_scan"):
        st.html('<p class="cc-h2">New audit</p><p class="cc-muted">Point CodeCompass at a '
                'local Python project. Code is parsed, never executed.</p>')
        c_name, c_path, c_run = st.columns([2, 4, 1.4], vertical_alignment="bottom")
        name = c_name.text_input("Project name", key="scan_name", placeholder="Final Year Project")
        path = c_path.text_input("Directory path", key="scan_path", placeholder="C:\\projects\\my-app")
        run = c_run.button("Run audit", type="primary", width="stretch")
        with st.expander("Open a saved report"):
            c_id, c_open = st.columns([3, 1.4], vertical_alignment="bottom")
            pid = c_id.number_input("Project ID", min_value=1, step=1, key="saved_id")
            if c_open.button("Open", width="stretch"):
                _load_saved(pid)
    if ss.pop("autorun", False) or run:
        _scan(name.strip(), path.strip())
