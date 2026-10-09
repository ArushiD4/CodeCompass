"""compare_audits.py — Compares two historical audit reports and visualises diffs."""
import streamlit as st
import api_client
from components import audit_diff, compare_widgets, report_picker
from components.primitives import esc, footer


def render():
    ss = st.session_state
    st.html(
        '<p class="cc-h1" style="margin-top:1rem;font-size:2rem">Compare audits</p>'
        '<p class="cc-lede">See what changed between two audits of your project.</p>'
        '<p class="cc-muted" style="margin-bottom:1.5rem">Tip: audit your project, fix issues in the same folder, '
        'audit again, then compare the two.</p>'
    )

    base_url = ss.get("backend_url", "http://localhost:8000")
    projects, proj_map, label_map, err = report_picker.load_report_options(base_url)
    if err:
        st.error(err)
        return
    if len(projects) < 2:
        st.info("At least two saved audits are required to compare differences. Run an audit first.")
        return

    options = [p["id"] for p in projects]

    # Pre-selection handling
    if "compare_ids" in ss:
        def_a, def_b = ss.pop("compare_ids")
        if def_a in options:
            ss["cmp_a"] = def_a
        if def_b in options:
            ss["cmp_b"] = def_b
    elif "cmp_a" not in ss and "cmp_b" not in ss:
        newest_p = projects[0]
        older = [p["id"] for p in projects[1:] if p.get("project_name") == newest_p.get("project_name")]
        if older:
            ss["cmp_a"] = older[0]
            ss["cmp_b"] = newest_p["id"]
        elif len(projects) >= 2:
            ss["cmp_a"] = projects[1]["id"]
            ss["cmp_b"] = projects[0]["id"]

    c1, c2 = st.columns(2)
    idx_a = options.index(ss["cmp_a"]) if ss.get("cmp_a") in options else None
    idx_b = options.index(ss["cmp_b"]) if ss.get("cmp_b") in options else None

    id_a = c1.selectbox("Earlier audit", options=options, index=idx_a,
                        format_func=lambda pid: label_map.get(pid, f"Audit #{pid}"),
                        placeholder="Select earlier audit", key="cmp_a")
    id_b = c2.selectbox("Later audit", options=options, index=idx_b,
                        format_func=lambda pid: label_map.get(pid, f"Audit #{pid}"),
                        placeholder="Select later audit", key="cmp_b")

    if not id_a or not id_b:
        st.info("Select two audits to see the comparison.")
        return
    if id_a == id_b:
        st.warning("Please select two distinct audit records to compare.")
        return

    rep_a, err_a = api_client.get_project(id_a)
    rep_b, err_b = api_client.get_project(id_b)
    if err_a or err_b or not rep_a or not rep_b:
        msg = err_a or err_b or "Selected audit record was not found."
        st.error(f"Failed to load audit records: {msg}")
        return

    earlier, later, swapped = audit_diff.order_reports(rep_a, rep_b)
    if swapped:
        st.info("Ordered by time: earlier on the left.")

    diff = audit_diff.compare_reports(earlier, later)
    if not diff["same_project"]:
        st.warning("These look like different projects, so the differences may not be meaningful.")

    compare_widgets.render_headline_strip(diff)
    compare_widgets.render_summary_tiles(diff)
    compare_widgets.render_what_changed(diff)
    compare_widgets.render_biggest_movers(diff)
    st.html(footer())
