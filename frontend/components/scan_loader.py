"""scan_loader.py — Laser-sweep AST analysis animation for scan progress."""
from components.primitives import esc

LOADER_CSS = """
<style>
.cc-loader{position:relative;background:rgba(11,15,24,.9);border:1px solid var(--line);border-radius:12px;padding:1.25rem;overflow:hidden;margin:.75rem 0}
.cc-laser{position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00F5A0,transparent);box-shadow:0 0 12px #00F5A0;animation:cc-sweep 1.8s ease-in-out infinite}
@keyframes cc-sweep{0%{top:0;opacity:0}30%{opacity:1}80%{opacity:1}100%{top:100%;opacity:0}}
.cc-files-scanned{display:flex;flex-direction:column;gap:.35rem;font-family:var(--mono);font-size:.82rem}
.cc-file-item{display:flex;align-items:center;gap:.6rem;color:var(--ink-2)}
.cc-check{color:var(--good);font-weight:700}
@media (prefers-reduced-motion:reduce){.cc-laser{display:none}}
</style>
"""


def render_sweep(file_list=None):
    files = file_list or ["__init__.py", "main.py", "audit_engine.py", "models.py", "database.py"]
    rows = "".join(
        f'<div class="cc-file-item"><span class="cc-check">✓</span>'
        f'<span>AST Traversal: {esc(f)}</span></div>'
        for f in files
    )
    return (
        f'{LOADER_CSS}'
        f'<div class="cc-loader">'
        f'<div class="cc-laser"></div>'
        f'<p class="cc-h2" style="font-size:.95rem;color:var(--brand);margin-bottom:.6rem">'
        f'⚡ AST Static Analysis Sweep in Progress</p>'
        f'<div class="cc-files-scanned">{rows}</div>'
        f'</div>'
    )
