"""Tiny HTML helpers. Every dynamic value passes through esc() first."""
import html
from config import APP_NAME, PROJECT_CREDIT, SEVERITY_NAME, SEVERITY_TONE, TAGLINE


def esc(value):
    return html.escape(str(value), quote=True)


def pill(text, tone="", dot=False):
    marker = '<span class="cc-dot"></span>' if dot else ""
    return f'<span class="cc-pill tone-{tone}">{marker}{esc(text)}</span>'


def sev_pill(severity):
    tone = SEVERITY_TONE.get(severity, "info")
    return pill(SEVERITY_NAME.get(severity, severity.title()), tone, dot=True)


def footer():
    return (f'<footer class="cc-footer"><p>{esc(APP_NAME)} · {esc(TAGLINE)}'
            f' <span class="cc-credit">— {esc(PROJECT_CREDIT)}</span></p></footer>')
