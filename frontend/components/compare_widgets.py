"""compare_widgets.py — Reusable rendering tiles and cards for audit comparisons."""
import streamlit as st
from components.primitives import esc, pill, sev_pill


def render_headline_strip(diff: dict):
    pct_b = max(0, min(diff["crs_before"], 100))
    pct_a = max(0, min(diff["crs_after"], 100))
    t_b = diff["band_before"][1]
    t_a = diff["band_after"][1]
    ring_b = (f'<div class="cc-ring tone-{t_b}" style="width:90px;height:90px;margin:0 auto">'
              f'<div class="cc-ring-arc" style="--p:{pct_b};--t:var(--{t_b})"></div>'
              f'<div class="cc-ring-num"><b style="font-size:1.6rem">{diff["crs_before"]}</b>'
              f'<span style="font-size:.65rem">CRS</span></div></div>')
    ring_a = (f'<div class="cc-ring tone-{t_a}" style="width:90px;height:90px;margin:0 auto">'
              f'<div class="cc-ring-arc" style="--p:{pct_a};--t:var(--{t_a})"></div>'
              f'<div class="cc-ring-num"><b style="font-size:1.6rem">{diff["crs_after"]}</b>'
              f'<span style="font-size:.65rem">CRS</span></div></div>')
    sign = "+" if diff["delta"] > 0 else ""
    delta_p = pill(f"{sign}{diff['delta']}", diff["tone"])
    bands = f"{diff['band_before'][0]} → {diff['band_after'][0]}"
    st.html(
        f'<div class="cc-card" style="margin:1.5rem 0;text-align:center">'
        f'<div style="display:flex;align-items:center;justify-content:center;gap:2rem;flex-wrap:wrap">'
        f'<div>{ring_b}</div><div style="font-size:2rem;color:var(--tline)">→</div><div>{ring_a}</div>'
        f'<div><div style="font-size:1.1rem;font-weight:700;margin-bottom:.4rem">{delta_p}</div>'
        f'<div class="cc-muted" style="font-size:.9rem">{esc(bands)}</div></div></div>'
        f'<p class="cc-lede" style="margin:1rem 0 0;font-size:1.05rem">{esc(diff["headline"])}</p>'
        f'</div>'
    )


def render_summary_tiles(diff: dict):
    c1, c2, c3 = st.columns(3)
    c1.html(f'<div class="cc-card tone-good" style="text-align:center"><div class="cc-muted">Fixed Findings</div>'
            f'<div style="font-size:2rem;font-weight:800;color:var(--good)">{len(diff["fixed"])}</div></div>')
    c2.html(f'<div class="cc-card tone-bad" style="text-align:center"><div class="cc-muted">New Findings</div>'
            f'<div style="font-size:2rem;font-weight:800;color:var(--bad)">{len(diff["new"])}</div></div>')
    c3.html(f'<div class="cc-card" style="text-align:center"><div class="cc-muted">Still There</div>'
            f'<div style="font-size:2rem;font-weight:800;color:var(--muted)">{len(diff["remaining"])}</div></div>')

    rows = []
    for sev in ("CRITICAL", "WARNING", "INFO"):
        b, a = diff["severity_before"].get(sev, 0), diff["severity_after"].get(sev, 0)
        chg = a - b
        sign = "+" if chg > 0 else ""
        chg_markup = pill(f"{sign}{chg}", "bad" if chg > 0 else ("good" if chg < 0 else "")) if chg != 0 else "0"
        rows.append(f'<tr style="border-bottom:1px solid var(--tline)"><td style="padding:.5rem">{sev_pill(sev)}</td>'
                    f'<td style="padding:.5rem">{b}</td><td style="padding:.5rem">{a}</td>'
                    f'<td style="padding:.5rem">{chg_markup}</td></tr>')
    st.html(
        f'<div class="cc-card" style="margin-top:1rem">'
        f'<p class="cc-h2" style="font-size:1.1rem;margin-bottom:.75rem">Severity Distribution</p>'
        f'<table style="width:100%;border-collapse:collapse;font-size:.9rem">'
        f'<thead><tr style="border-bottom:1px solid var(--tline);color:var(--muted);text-align:left">'
        f'<th style="padding:.5rem">Severity</th><th style="padding:.5rem">Earlier</th>'
        f'<th style="padding:.5rem">Later</th><th style="padding:.5rem">Change</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _render_group(title: str, issues: list, group_key: str):
    if not issues:
        return
    ss = st.session_state
    limit_key = f"cmp_limit_{group_key}"
    limit = ss.get(limit_key, 5)
    visible = issues[:limit]

    items_html = []
    for iss in visible:
        s_pill = sev_pill(iss.get("severity", "INFO"))
        rule = esc(iss.get("rule_name", "Rule"))
        loc = esc(f"{iss.get('file_path', '')}:{iss.get('line_number', 0)}")
        items_html.append(
            f'<li style="display:flex;align-items:center;gap:.75rem;padding:.4rem 0;'
            f'border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'{s_pill}<span>{rule}</span><span class="cc-mono cc-muted" style="margin-left:auto">{loc}</span></li>'
        )

    st.html(
        f'<div class="cc-card" style="margin-top:1rem">'
        f'<p class="cc-h2" style="font-size:1.1rem;margin-bottom:.6rem">{esc(title)} ({len(issues)})</p>'
        f'<ul style="list-style:none;padding:0;margin:0">{ "".join(items_html) }</ul></div>'
    )
    if len(issues) > 5 and limit < len(issues):
        def _expand():
            st.session_state[limit_key] = len(issues)
        st.button(f"Show all {len(issues)}", key=f"btn_all_{group_key}", on_click=_expand)


def render_what_changed(diff: dict):
    _render_group("Fixed findings", diff["fixed"], "fixed")
    _render_group("New findings", diff["new"], "new")
    _render_group("Still there", diff["remaining"], "remaining")


def render_biggest_movers(diff: dict):
    rules_top = [f"<li><b>{esc(r)}</b>: {b} → {a} ({'+' if d > 0 else ''}{d})</li>"
                 for r, b, a, d in diff["by_rule"][:3] if d != 0]
    files_top = [f"<li><span class=\"cc-mono\">{esc(f)}</span>: {b} → {a} ({'+' if d > 0 else ''}{d})</li>"
                 for f, b, a, d in diff["by_file"][:3] if d != 0]

    rules_markup = f'<ul style="margin:.4rem 0;padding-left:1.2rem">{"".join(rules_top)}</ul>' if rules_top else '<p class="cc-muted">No rule changes</p>'
    files_markup = f'<ul style="margin:.4rem 0;padding-left:1.2rem">{"".join(files_top)}</ul>' if files_top else '<p class="cc-muted">No file changes</p>'

    meta_parts = []
    if diff["files_delta"] != 0:
        meta_parts.append(f"Files scanned changed by {'+' if diff['files_delta'] > 0 else ''}{diff['files_delta']}")
    if diff["functions_delta"] != 0:
        meta_parts.append(f"Functions scanned changed by {'+' if diff['functions_delta'] > 0 else ''}{diff['functions_delta']}")
    meta_html = "".join(f'<p class="cc-muted" style="margin:.3rem 0">{esc(m)}</p>' for m in meta_parts)

    st.html(
        f'<div class="cc-card" style="margin-top:1rem">'
        f'<p class="cc-h2" style="font-size:1.1rem;margin-bottom:.5rem">Biggest Movers</p>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem">'
        f'<div><b>Top Rules Changed</b>{rules_markup}</div>'
        f'<div><b>Top Files Changed</b>{files_markup}</div></div>'
        f'{meta_html}</div>'
    )
    st.caption("Findings are matched between audits by rule, file and description, not line number. "
               "Renaming a function or file can show as one fixed and one new issue.")
