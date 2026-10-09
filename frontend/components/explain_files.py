"""explain_files.py — Interactive viva rehearsal and file defense rehearsal."""
import os
import streamlit as st
from components import explain_facts_card, file_links, file_scan, local_store
from components.primitives import esc, pill

PROMPTS = (
    "In one sentence, what is this file's job?",
    "What are its inputs and outputs?",
    "What breaks if this file is deleted?",
    "Which function would you explain first, and why?",
    "One thing you would improve here",
)


def _count_answered(notes: dict, fpath: str) -> int:
    return sum(1 for idx in range(5) if len(notes.get((fpath, idx), "").replace(" ", "")) >= 10)


def render():
    ss = st.session_state
    audit = ss.get("last_audit_data")
    path = ss.get("last_audit_path")
    if not audit or not path:
        st.info("Run an audit to explain your files.")
        return

    with st.expander("ℹ️ How CodeCompass reads your code & connections (Plain English Guide)", expanded=False):
        st.markdown(
            "**How CodeCompass reads your code**\n\n"
            "CodeCompass examines your Python code's structure to identify things like functions, classes, "
            "imports, and function calls. It uses this information to build a map of how parts of your code connect.\n\n"
            "**What do 'Calls into' and 'Called by' mean?**\n\n"
            "- **Calls into:** Functions or methods that this function appears to call.\n"
            "- **Called by:** Functions or methods that appear to call this function.\n"
            "- **Possible connection (?):** CodeCompass found a potential match based on function names, but it cannot confirm that the connection is real.\n\n"
            "**Important limitation:**\n\n"
            "Python can resolve function calls dynamically, so matching names alone does not always prove which function "
            "will execute. Treat connections marked '?' as possibilities, not confirmed relationships."
        )

    db_ok = local_store.init_ok()
    if not db_ok:
        st.warning("Notes could not be saved on this computer; they will last until you close the page.")

    proj_path = os.path.normpath(path)
    saved_notes = local_store.load_notes(proj_path) if db_ok else {}

    if "file_facts" not in ss:
        with st.spinner("Analyzing codebase files with AST..."):
            ss["file_facts"] = file_scan.scan_project(path)
    file_facts = ss.get("file_facts", {})
    if not file_facts:
        st.info("No Python files found in this project.")
        return

    graph = ss.get("graph_data") or {}
    issues = audit.get("issues", [])

    # Priority calculation
    def _prio(f):
        norm_f = f.replace("\\", "/")
        c = sum(1 for i in issues if i.get("file_path", "").replace("\\", "/") == norm_f and i.get("severity") == "CRITICAL")
        w = sum(1 for i in issues if i.get("file_path", "").replace("\\", "/") == norm_f and i.get("severity") == "WARNING")
        inf = sum(1 for i in issues if i.get("file_path", "").replace("\\", "/") == norm_f and i.get("severity") == "INFO")
        fan_in = len(file_links.called_by(f, graph))
        entry = 2 if file_facts.get(f, {}).get("entry_point") else 0
        return (3 * c + 2 * w + 1 * inf + fan_in + entry, f)

    files_sorted = sorted(file_facts.keys(), key=_prio, reverse=True)

    # Progress tracking
    total_files = len(files_sorted)
    full_answered = sum(1 for f in files_sorted if _count_answered(saved_notes, f) == 5)
    st.write(f"{full_answered} of {total_files} files fully answered")

    # Start here pills
    top3 = files_sorted[:3]
    top_pills = "".join(f'<span style="margin-right:.5rem">{pill(f, "info")}</span>' for f in top3)
    st.html(f'<div style="display:flex;align-items:center;gap:.5rem;margin:.5rem 0">'
            f'<span style="font-size:.85rem;color:var(--muted)">Start here:</span>{top_pills}</div>')

    # Status glyphs
    labels = {}
    for f in files_sorted:
        ans_count = _count_answered(saved_notes, f)
        glyph = "●" if ans_count == 5 else ("◐" if ans_count > 0 else "○")
        labels[f] = f"{glyph} {f}"

    selected = st.selectbox("Select a file to rehearse", options=files_sorted,
                            format_func=lambda f: labels.get(f, f), key="explain_file_sel")
    if not selected:
        return

    cb = file_links.called_by(selected, graph)
    ci = file_links.calls_into(selected, graph)
    explain_facts_card.render_facts_card(selected, file_facts.get(selected, {}), cb, ci)

    st.html('<p class="cc-h2" style="font-size:1.1rem;margin-top:1.5rem">Defense Rehearsal Prompts</p>')
    for idx, prompt in enumerate(PROMPTS):
        key = f"note_{selected}_{idx}"
        if key not in ss:
            ss[key] = saved_notes.get((selected, idx), "")

        def _on_change(i=idx, k=key):
            val = ss.get(k, "")
            saved_notes[(selected, i)] = val
            if db_ok:
                local_store.save_note(proj_path, selected, i, val)

        st.text_area(prompt, key=key, on_change=_on_change, height=80)
        if idx == 2:
            rev_key = f"reveal_deps_{selected}"
            if not ss.get(rev_key):
                if st.button("Reveal answer", key=f"btn_rev_{selected}"):
                    ss[rev_key] = True
                    st.rerun()
            else:
                deps = file_links.dependents(selected, file_facts, graph)
                dep_items = "".join(f"<li><code>{esc(d)}</code></li>" for d in deps) if deps else "<li><em>No other files depend on this file.</em></li>"
                st.html(f'<div class="cc-tip" style="margin:.5rem 0"><b>Files that depend on this one:</b><ul style="margin:.25rem 0 0 1.2rem">{dep_items}</ul></div>')
                if st.button("Hide answer", key=f"btn_hide_{selected}"):
                    ss[rev_key] = False
                    st.rerun()
