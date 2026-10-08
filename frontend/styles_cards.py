"""Design system, part 2: classes used by the HTML components."""

CARDS_CSS = """
/* Top bar */
.cc-brand{display:flex;align-items:center;gap:.6rem;font-weight:700;font-size:1.05rem;letter-spacing:-.01em}
.cc-logo{width:28px;height:28px;border-radius:8px;background:var(--ink);display:grid;place-items:center}
.cc-logo::before{content:"";width:9px;height:16px;background:#fff;clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}
.cc-chips{display:flex;gap:.5rem;justify-content:flex-end;flex-wrap:wrap}
.cc-pill{display:inline-flex;align-items:center;gap:.4rem;font-size:.78rem;font-weight:500;
  padding:.25rem .65rem;border-radius:999px;border:1px solid var(--tline,var(--line));
  background:var(--tbg,var(--surface));color:var(--t,var(--ink-2))}
.cc-dot{width:7px;height:7px;border-radius:50%;background:currentColor;display:inline-block}

/* Type */
.cc-h1{font-size:clamp(2rem,4.6vw,3.2rem);line-height:1.06;letter-spacing:-.035em;font-weight:700;
  max-width:16em;margin:3.5rem 0 1rem}
.cc-lede{font-size:1.1rem;line-height:1.6;color:var(--ink-2);max-width:54ch;margin:0 0 1.5rem}
.cc-h2{font-size:1.05rem;font-weight:600;letter-spacing:-.01em;margin:0 0 .25rem}
.cc-muted{color:var(--ink-2);font-size:.9rem;line-height:1.55;margin:0}
.cc-mono{font-family:var(--mono);font-size:.8rem;color:var(--ink-2)}

/* Landing bento */
.cc-feat{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:1rem;margin-top:3rem}
.cc-card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1.4rem}
.cc-card .cc-muted{max-width:46ch}
.s2{grid-column:span 2}.s3{grid-column:span 3}.s4{grid-column:span 4}
.cc-bands{display:flex;flex-direction:column;gap:.45rem;margin-top:1rem}

/* Dashboard bento */
.cc-bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:1rem;margin:1.25rem 0}
.cc-hero{grid-column:span 5;border-radius:18px;border:1px solid var(--tline);background:var(--tbg);
  padding:1.5rem;display:flex;flex-direction:column;gap:1.1rem}
.cc-hero-head{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.cc-hero-title{font-weight:600}
.cc-hero-body{display:flex;gap:1.5rem;align-items:center}
.cc-advice{color:var(--ink);font-size:.95rem;line-height:1.55;max-width:28ch;margin:0}
.cc-math{font-family:var(--mono);font-size:.78rem;color:var(--ink-2)}
.cc-ring{position:relative;width:168px;height:168px;flex:none}
.cc-ring-arc{position:absolute;inset:0;border-radius:50%;
  background:conic-gradient(var(--t) calc(var(--p)*1%),rgba(14,22,36,.08) 0);
  -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 12px),#000 calc(100% - 11px));
  mask:radial-gradient(farthest-side,transparent calc(100% - 12px),#000 calc(100% - 11px));
  animation:cc-ring .9s ease-out}
@property --p{syntax:'<number>';inherits:false;initial-value:0}
@keyframes cc-ring{from{--p:0}}
.cc-ring-num{position:absolute;inset:0;display:grid;place-content:center;text-align:center}
.cc-ring-num b{font-size:3rem;line-height:1;letter-spacing:-.04em;color:var(--t)}
.cc-ring-num span{font-size:.75rem;color:var(--ink-2)}
.cc-side{grid-column:span 7;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}
.cc-tile{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:1rem 1.15rem}
.cc-tile span{display:block;font-size:.8rem;color:var(--ink-2)}
.cc-tile b{font-size:2rem;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.cc-wide{grid-column:span 3;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:1rem 1.15rem}
.cc-bar{display:flex;height:10px;border-radius:99px;overflow:hidden;background:var(--line);margin:.7rem 0}
.cc-bar i{display:block}
.cc-legend{display:flex;gap:1.25rem;flex-wrap:wrap;list-style:none;padding:0;margin:0;font-size:.85rem}
.cc-legend li{display:flex;gap:.4rem;align-items:center;color:var(--t)}
.cc-legend em{color:var(--ink-2);font-style:normal}
.cc-meta{display:flex;justify-content:space-between;gap:1rem;font-size:.85rem;flex-wrap:wrap}
.cc-meta b{font-weight:600}

/* Findings */
.cc-finds{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem;margin-top:.5rem}
.cc-find{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--t);
  border-radius:12px;padding:1rem 1.15rem}
.cc-find-top{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem}
.cc-rule{font-weight:600;line-height:1.35}
.cc-tip{margin-top:.8rem;background:var(--bg);border-radius:8px;padding:.7rem .85rem;
  font-size:.86rem;line-height:1.55;color:var(--ink-2)}
.cc-tip b{color:var(--ink);display:block;margin-bottom:.2rem;font-size:.8rem}

/* Architecture */
.cc-stack{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.85rem}
.cc-flow{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center;margin:.75rem 0}
.cc-step{font-size:.82rem;border:1px solid var(--line-strong);border-radius:8px;padding:.4rem .7rem;background:var(--surface)}
.cc-table{width:100%;border-collapse:collapse;font-size:.88rem}
.cc-table th{text-align:left;font-weight:500;color:var(--ink-2);padding:.5rem .6rem;border-bottom:1px solid var(--line)}
.cc-table td{padding:.6rem;border-bottom:1px solid var(--line);vertical-align:top}

@media (max-width:860px){
  .cc-feat>*,.cc-hero,.cc-side,.cc-wide{grid-column:1/-1}
  .cc-bento{grid-template-columns:1fr}.cc-finds{grid-template-columns:1fr}
  .cc-stack{grid-template-columns:1fr 1fr}.cc-hero-body{flex-direction:column;align-items:flex-start}
}
"""
