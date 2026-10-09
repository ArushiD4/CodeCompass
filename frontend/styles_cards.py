"""Design system, part 2: classes, dark cards, hover effects, and layout."""

CARDS_CSS = """
/* Top bar */
.cc-brand{display:flex;align-items:center;gap:.65rem;font-weight:700;font-size:1.1rem;letter-spacing:-.02em;color:var(--ink)}
.cc-logo{width:30px;height:30px;border-radius:9px;background:var(--brand-gradient);display:grid;place-items:center;box-shadow:0 0 16px rgba(0,245,160,.3)}
.cc-logo::before{content:"";width:10px;height:18px;background:#07090E;clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)}
.cc-chips{display:flex;gap:.5rem;justify-content:flex-end;flex-wrap:wrap}
.cc-pill{display:inline-flex;align-items:center;gap:.45rem;font-size:.78rem;font-weight:600;
  padding:.3rem .75rem;border-radius:999px;border:1px solid var(--tline,var(--line));
  background:var(--tbg,var(--surface));color:var(--t,var(--ink-2));backdrop-filter:blur(8px)}
.cc-dot{width:7px;height:7px;border-radius:50%;background:currentColor;display:inline-block;box-shadow:0 0 8px currentColor}

/* Type */
.cc-hero-lockup{margin:2.5rem 0 1.5rem}
.cc-brand-title{
  font-size:clamp(3.2rem,6.5vw,5.5rem);font-weight:800;letter-spacing:-.04em;line-height:1.02;
  color:var(--ink);margin:0 0 .5rem;background:linear-gradient(180deg,#FFFFFF 40%,#B6BFCC 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.cc-hero-tagline{
  font-size:clamp(1.3rem,2.4vw,2rem);font-weight:600;letter-spacing:-.02em;color:var(--brand);
  margin:0 0 1.5rem;line-height:1.3;
}
.cc-h1{font-size:clamp(2.1rem,4.8vw,3.4rem);line-height:1.08;letter-spacing:-.035em;font-weight:700;
  color:var(--ink);max-width:18em;margin:2.5rem 0 .75rem}
.cc-lede{font-size:1.15rem;line-height:1.6;color:var(--ink-2);max-width:56ch;margin:0 0 1.75rem}
.cc-h2{font-size:1.15rem;font-weight:700;letter-spacing:-.02em;color:var(--ink);margin:0 0 .4rem}
.cc-muted{color:var(--mute);font-size:.92rem;line-height:1.6;margin:0}
.cc-mono{font-family:var(--mono);font-size:.82rem;color:var(--ink-2)}

/* Bento grid */
.cc-feat{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(1.25rem,2vw,2rem);margin-top:2.5rem;width:100%}
.cc-card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:clamp(1.4rem,2.2vw,2rem);backdrop-filter:blur(16px);position:relative}
.cc-card .cc-muted{max-width:65ch}
.cc-bands{display:flex;flex-direction:column;gap:.5rem;margin-top:1rem}

/* Dashboard bento */
.cc-bento{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:1rem;margin:1.25rem 0}
.cc-hero{grid-column:span 5;border-radius:18px;border:1px solid var(--tline);background:var(--tbg);
  padding:1.5rem;display:flex;flex-direction:column;gap:1.1rem;backdrop-filter:blur(16px)}
.cc-hero-head{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.cc-hero-title{font-weight:700;letter-spacing:-.01em;color:var(--ink)}
.cc-hero-body{display:flex;gap:1.5rem;align-items:center}
.cc-advice{color:var(--ink);font-size:.95rem;line-height:1.55;max-width:28ch;margin:0}
.cc-math{font-family:var(--mono);font-size:.78rem;color:var(--ink-2)}
.cc-ring{position:relative;width:168px;height:168px;flex:none}
.cc-ring-arc{position:absolute;inset:0;border-radius:50%;
  background:conic-gradient(var(--t) calc(var(--p)*1%),rgba(255,255,255,.06) 0);
  -webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 13px),#000 calc(100% - 12px));
  mask:radial-gradient(farthest-side,transparent calc(100% - 13px),#000 calc(100% - 12px));
  animation:cc-ring .9s ease-out;filter:drop-shadow(0 0 10px var(--tline))}
@property --p{syntax:'<number>';inherits:false;initial-value:0}
@keyframes cc-ring{from{--p:0}}
.cc-ring-num{position:absolute;inset:0;display:grid;place-content:center;text-align:center}
.cc-ring-num b{font-size:3.2rem;line-height:1;letter-spacing:-.04em;color:var(--t)}
.cc-ring-num span{font-size:.75rem;color:var(--mute);text-transform:uppercase;letter-spacing:.05em}
.cc-side{grid-column:span 7;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}
.cc-tile{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1.1rem;backdrop-filter:blur(16px)}
.cc-tile span{display:block;font-size:.8rem;color:var(--mute)}
.cc-tile b{font-size:2rem;letter-spacing:-.03em;color:var(--ink);font-variant-numeric:tabular-nums}
.cc-wide{grid-column:span 3;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:1.1rem;backdrop-filter:blur(16px)}
.cc-bar{display:flex;height:8px;border-radius:99px;overflow:hidden;background:rgba(255,255,255,.06);margin:.75rem 0}
.cc-bar i{display:block}
.cc-legend{display:flex;gap:1.25rem;flex-wrap:wrap;list-style:none;padding:0;margin:0;font-size:.85rem}
.cc-legend li{display:flex;gap:.4rem;align-items:center;color:var(--t)}
.cc-legend em{color:var(--mute);font-style:normal}
.cc-meta{display:flex;justify-content:space-between;gap:1rem;font-size:.85rem;flex-wrap:wrap;color:var(--ink-2)}
.cc-meta b{font-weight:600;color:var(--ink)}

/* Findings */
.cc-finds{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;margin-top:.75rem}
.cc-find{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--t);
  border-radius:14px;padding:1.15rem;backdrop-filter:blur(16px);position:relative;overflow:hidden}
.cc-find-top{display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem}
.cc-rule{font-weight:600;font-size:1.02rem;color:var(--ink);line-height:1.35}
.cc-tip{margin-top:.85rem;background:rgba(7,9,14,.6);border:1px solid var(--line);border-radius:10px;
  padding:.8rem .95rem;font-size:.88rem;line-height:1.55;color:var(--ink-2)}
.cc-tip b{color:var(--ink);display:block;margin-bottom:.25rem;font-size:.8rem}

/* Stage B: Hover system */
@media (hover:hover){
  .cc-card,.cc-tile,.cc-find{transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease}
  .cc-card:hover,.cc-tile:hover{transform:translateY(-3px);border-color:var(--line-strong);box-shadow:0 8px 24px rgba(0,0,0,.35)}
  .cc-find:hover{transform:translateY(-3px);border-color:var(--tline);box-shadow:0 8px 28px rgba(0,0,0,.45),0 0 16px var(--tbg)}
  .cc-more{display:inline-flex;align-items:center;gap:.3rem;color:var(--t);font-size:.82rem;font-weight:600;
    transform:translateX(-6px);opacity:0;transition:transform .22s ease,opacity .22s ease}
  .cc-find:hover .cc-more{transform:translateX(0);opacity:1}
  .cc-finds:has(.cc-find:hover) .cc-find:not(:hover){opacity:.55;transition:opacity .22s ease}
}

/* Auth split visual */
.cc-code-box{background:rgba(11,15,24,.9);border:1px solid var(--line);border-radius:14px;padding:1.5rem;font-family:var(--mono);font-size:.85rem;color:var(--ink-2);min-height:220px;display:flex;flex-direction:column;justify-content:center}
.cc-caret{display:inline-block;width:8px;height:15px;background:var(--brand);margin-left:4px;animation:cc-blink 1s infinite}
@keyframes cc-blink{0%,100%{opacity:1}50%{opacity:0}}

/* Footer */
.cc-footer{margin-top:4rem;padding:1.5rem 0;border-top:1px solid var(--line);text-align:center;font-size:.82rem;color:var(--mute)}
.cc-footer p{margin:0}
.cc-credit{opacity:.75}

@media (max-width:860px){
  .cc-feat{grid-template-columns:1fr}
  .cc-hero,.cc-side,.cc-wide{grid-column:1/-1}
  .cc-bento,.cc-finds{grid-template-columns:1fr}
  .cc-hero-body{flex-direction:column;align-items:flex-start}
}
"""
