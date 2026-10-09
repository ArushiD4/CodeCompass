"""Design system, part 1: tokens, global dark theme, and Streamlit overrides."""
import os
import streamlit as st
from styles_cards import CARDS_CSS

_FONTS_FILE = os.path.join(os.path.dirname(__file__), "assets", "fonts.css")
_FONTS_CSS = ""
if os.path.exists(_FONTS_FILE):
    try:
        with open(_FONTS_FILE, "r", encoding="utf-8") as f:
            _FONTS_CSS = f.read()
    except Exception:
        pass

BASE_CSS = """
:root{
  --bg:#07090E; --surface:rgba(15,20,30,.75); --surface-solid:#0F141E;
  --line:rgba(255,255,255,.08); --line-strong:rgba(255,255,255,.16);
  --ink:#FFFFFF; --ink-2:#B6BFCC; --mute:#8A94A6;
  --brand:#00F5A0; --brand-hover:#00D8F6; --brand-gradient:linear-gradient(135deg,#00F5A0,#00D8F6);
  --good:#00F5A0; --good-bg:rgba(0,245,160,.12); --good-line:rgba(0,245,160,.30);
  --warn:#FFB800; --warn-bg:rgba(255,184,0,.12); --warn-line:rgba(255,184,0,.30);
  --bad:#FF385C;  --bad-bg:rgba(255,56,92,.12);  --bad-line:rgba(255,56,92,.30);
  --info:#00D8F6; --info-bg:rgba(0,216,246,.12); --info-line:rgba(0,216,246,.30);
  --font:'Plus Jakarta Sans',system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}

.tone-good{--t:var(--good);--tbg:var(--good-bg);--tline:var(--good-line)}
.tone-warn{--t:var(--warn);--tbg:var(--warn-bg);--tline:var(--warn-line)}
.tone-bad{--t:var(--bad);--tbg:var(--bad-bg);--tline:var(--bad-line)}
.tone-info{--t:var(--info);--tbg:var(--info-bg);--tline:var(--info-line)}

.stApp{
  background-color:var(--bg)!important;color:var(--ink)!important;font-family:var(--font);
  position:relative;min-height:100vh;overflow-x:hidden!important;
}
.stApp::before{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(ellipse 60% 40% at 20% 15%,rgba(4,28,36,.55),transparent 70%),
             radial-gradient(ellipse 55% 45% at 85% 80%,rgba(18,14,36,.45),transparent 70%);
}

.stApp p,.stApp label,.stApp input,.stApp button,.stApp textarea{font-family:var(--font)}
header[data-testid="stHeader"]{background:transparent!important;height:0}
[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu{display:none!important}

[data-testid="stMainBlockContainer"],.block-container{
  width:100%!important;max-width:1440px!important;margin:0 auto!important;
  padding:0.75rem clamp(1rem,2.5vw,2.5rem) 4rem!important;position:relative;z-index:1;
  box-sizing:border-box;
}

/* Hero intro container */
.st-key-intro{
  width:100%!important;margin:0 auto 1rem auto!important;
  display:flex!important;justify-content:center!important;
}
.st-key-intro iframe{
  width:100%!important;height:calc(100vh - 120px)!important;
  min-height:480px!important;max-height:720px!important;border:0!important;display:block;
}

/* Buttons */
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--brand-gradient)!important;border:none!important;color:#07090E!important;
  font-weight:700;border-radius:10px;box-shadow:0 0 20px rgba(0,245,160,.2);transition:all .2s ease;
}
[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{
  box-shadow:0 0 28px rgba(0,216,246,.4);transform:translateY(-1px);
}
[data-testid="stBaseButton-secondary"]{
  background:var(--surface)!important;border:1px solid var(--line)!important;color:var(--ink)!important;
  font-weight:600;border-radius:10px;backdrop-filter:blur(12px);transition:all .2s ease;
}
[data-testid="stBaseButton-secondary"]:hover{
  border-color:var(--line-strong)!important;background:rgba(25,32,48,.8)!important;
}
button:focus-visible,input:focus-visible{outline:2px solid var(--brand)!important;outline-offset:2px}

/* Inputs & containers */
[data-testid="stTextInputRootElement"],[data-testid="stNumberInputContainer"]{
  border:1px solid var(--line-strong)!important;border-radius:10px!important;
  background:rgba(11,15,24,.9)!important;backdrop-filter:blur(12px);
}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stNumberInputContainer"]:focus-within{
  border-color:var(--brand)!important;box-shadow:0 0 0 1px var(--brand)!important;
}
input{color:var(--ink)!important}
button[role="tab"]{font-weight:600;color:var(--ink-2)}
button[role="tab"][aria-selected="true"]{color:var(--brand)!important}

details,[data-testid="stExpander"]{
  border-radius:12px!important;border:1px solid var(--line)!important;
  background:var(--surface)!important;backdrop-filter:blur(16px);
}
[data-testid="stSegmentedControl"]{background:rgba(11,15,24,.8);border-radius:10px;padding:3px}
[data-testid="stSegmentedControl"] button{font-weight:600;border-radius:8px!important;color:var(--ink-2)}
[data-testid="stSegmentedControl"] button[aria-checked="true"]{
  background:var(--surface-solid)!important;color:var(--brand)!important;border:1px solid var(--line-strong);
}

[class*="st-key-card_"]{
  background:var(--surface);border:1px solid var(--line);
  border-radius:16px;padding:1.4rem;backdrop-filter:blur(16px);
}
.st-key-card_auth{max-width:480px;margin:1.5rem auto 0}
.st-key-hero_cta{max-width:440px}

/* Scroll cue down chevron */
.cc-scroll-cue{display:flex;justify-content:center;margin:1.75rem 0 1.25rem;opacity:.7}
.cc-chevron{width:16px;height:16px;border-right:2px solid var(--brand);border-bottom:2px solid var(--brand);transform:rotate(45deg);animation:cc-bounce 2s infinite}
@keyframes cc-bounce{0%,100%{transform:rotate(45deg) translate(0,0);opacity:.4}50%{transform:rotate(45deg) translate(5px,5px);opacity:1}}

@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def inject():
    st.markdown(f"<style>{_FONTS_CSS}\n{BASE_CSS}\n{CARDS_CSS}</style>", unsafe_allow_html=True)
