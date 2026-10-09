"""Design system, part 1: tokens and Streamlit widget overrides."""
import streamlit as st
from styles_cards import CARDS_CSS

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{
  --bg:#F5F6F8; --surface:#FFFFFF; --line:#E2E5EA; --line-strong:#CDD2DA;
  --ink:#0E1624; --ink-2:#465165; --mute:#7C8798; --brand:#2B50E6;
  --good:#0F7B55; --good-bg:#E5F5EE; --good-line:#B7E2D0;
  --warn:#A65A00; --warn-bg:#FFF2D9; --warn-line:#F2D49B;
  --bad:#B42318;  --bad-bg:#FDEBE9;  --bad-line:#F4C3BE;
  --info:#2B50E6; --info-bg:#EBEFFD; --info-line:#C5D1FA;
  --mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
.tone-good{--t:var(--good);--tbg:var(--good-bg);--tline:var(--good-line)}
.tone-warn{--t:var(--warn);--tbg:var(--warn-bg);--tline:var(--warn-line)}
.tone-bad{--t:var(--bad);--tbg:var(--bad-bg);--tline:var(--bad-line)}
.tone-info{--t:var(--info);--tbg:var(--info-bg);--tline:var(--info-line)}

.stApp{background:var(--bg);color:var(--ink)}
.stApp,.stApp p,.stApp label,.stApp input,.stApp button,.stApp textarea{
  font-family:'Inter',ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif}
header[data-testid="stHeader"]{background:transparent;height:0}
[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu{display:none!important}

/* One centred column: nothing stretches across an ultrawide monitor. */
[data-testid="stMainBlockContainer"],.block-container{
  max-width:1160px;margin:0 auto;padding:1.25rem 1.5rem 4rem}

/* Buttons */
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stBaseButton-primaryFormSubmit"]{
  border-radius:8px;font-weight:600;box-shadow:none;transition:background .15s,border-color .15s}
[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{
  background:var(--brand);border:1px solid var(--brand);color:#fff}
[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{
  background:#1F3FC4;border-color:#1F3FC4;color:#fff}
[data-testid="stBaseButton-secondary"]{background:var(--surface);border:1px solid var(--line-strong);color:var(--ink)}
[data-testid="stBaseButton-secondary"]:hover{border-color:var(--ink-2);color:var(--ink)}
button:focus-visible,input:focus-visible{outline:2px solid var(--brand)!important;outline-offset:2px}

/* Inputs, tabs, status */
[data-testid="stTextInputRootElement"],[data-testid="stNumberInputContainer"]{
  border:1px solid var(--line-strong)!important;border-radius:8px!important;background:var(--surface)!important}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stNumberInputContainer"]:focus-within{
  border-color:var(--brand)!important}
button[role="tab"]{font-weight:500}
details,[data-testid="stExpander"]{border-radius:12px!important;border-color:var(--line)!important;background:var(--surface)}
[data-testid="stSegmentedControl"] button{font-weight:500}

/* Keyed containers become cards. Key names start with "card_". */
[class*="st-key-card_"]{background:var(--surface);border:1px solid var(--line);
  border-radius:14px;padding:1.1rem 1.25rem}
.st-key-card_auth{max-width:440px;margin:2.5rem auto 0}
.st-key-hero_cta{max-width:380px}

@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""


def inject():
    st.markdown(f"<style>{BASE_CSS}{CARDS_CSS}</style>", unsafe_allow_html=True)
