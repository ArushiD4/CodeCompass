"""Hero: Code Readiness Score ring plus KPI bento. Colour follows the CRS band."""
import streamlit as st
from config import CRS_BANDS, SEVERITIES, SEVERITY_NAME, SEVERITY_TONE, SEVERITY_WEIGHT
from components.primitives import esc, pill


def band_for(score):
    for floor, label, tone, advice in CRS_BANDS:
        if score >= floor:
            return label, tone, advice
    return CRS_BANDS[-1][1:]


def _ring(score, tone):
    pct = max(0, min(score, 100))
    return (f'<div class="cc-ring"><div class="cc-ring-arc" style="--p:{pct};--t:var(--{tone})"></div>'
            f'<div class="cc-ring-num"><b>{score}</b><span>out of 100</span></div></div>')


def _math_line(score, counts):
    parts = [f"{SEVERITY_WEIGHT[s] * n} {SEVERITY_NAME[s].lower()}" for s, n in counts.items() if n]
    if not parts:
        return "No deductions applied"
    total = sum(SEVERITY_WEIGHT[s] * n for s, n in counts.items())
    line = "100 - " + " - ".join(parts)
    return f"{line} = {score}" if max(0, 100 - total) == score else line


def _hero(score, counts):
    label, tone, advice = band_for(score)
    return (f'<div class="cc-hero tone-{tone}"><div class="cc-hero-head">'
            f'<span class="cc-hero-title">Code Readiness Score</span>{pill(label, tone, dot=True)}</div>'
            f'<div class="cc-hero-body">{_ring(score, tone)}<p class="cc-advice">{esc(advice)}</p></div>'
            f'<code class="cc-math">{esc(_math_line(score, counts))}</code></div>')


def _severity_card(counts):
    total = sum(counts.values())
    segments = "".join(f'<i style="flex:{n};background:var(--{SEVERITY_TONE[s]})"></i>'
                       for s, n in counts.items() if n)
    segments = segments or '<i style="flex:1;background:var(--good)"></i>'
    legend = "".join(
        f'<li class="tone-{SEVERITY_TONE[s]}"><span class="cc-dot"></span>{SEVERITY_NAME[s]} '
        f'<b>{n}</b><em>-{SEVERITY_WEIGHT[s] * n} pts</em></li>' for s, n in counts.items())
    title = f"{total} findings by severity" if total else "No findings"
    return (f'<div class="cc-wide"><span class="cc-muted">{title}</span>'
            f'<div class="cc-bar">{segments}</div><ul class="cc-legend">{legend}</ul></div>')


def _meta_card(audit, report):
    project = (report or {}).get("project", {})
    saved = f"Report #{audit['project_id']}" if audit.get("project_id") else "Not saved"
    created = str(project.get("created_at", ""))[:16].replace("T", " ")
    lines = project.get("total_lines") or audit.get("total_lines") or 0
    extra = f" · {created} UTC" if created else ""
    lines_html = f'<span>Lines scanned <b>{lines}</b></span>' if lines else ""
    return (f'<div class="cc-wide"><div class="cc-meta"><span>Project <b>{esc(audit.get("project_name", ""))}'
            f'</b></span>{lines_html}<span class="cc-mono">{saved}{extra}</span></div></div>')


def render(audit, report):
    issues = audit.get("issues", [])
    counts = {s: sum(1 for i in issues if i.get("severity") == s) for s in SEVERITIES}
    tiles = "".join(f'<div class="cc-tile"><span>{label}</span><b>{value}</b></div>' for label, value in (
        ("Files scanned", audit.get("total_files", 0)),
        ("Functions", audit.get("total_functions", 0)),
        ("Issues found", len(issues))))
    st.html(f'<div class="cc-bento">{_hero(int(audit.get("crs_score", 0)), counts)}'
            f'<div class="cc-side">{tiles}{_severity_card(counts)}{_meta_card(audit, report)}</div></div>')
