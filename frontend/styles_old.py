""
styles.py ΓÇö CodeCompass "Deep Slate" design system.

Single source of truth for all colour tokens and the CSS stylesheet.
Import `inject_styles` and call it once near the top of each page/route.
Import `COLORS` anywhere you need a hex string in Python (e.g. agraph node colours).
"""
import streamlit as st

# ΓöÇΓöÇ Colour tokens ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
COLORS = {
    # Surfaces
    "bg":            "#0F172A",
    "panel":         "#1E293B",
    "border":        "#334155",
    # Text
    "text_primary":  "#E2E8F0",
    "text_secondary":"#94A3B8",
    # Accent
    "accent":        "#2DD4BF",
    # Severity
    "critical":      "#F87171",
    "warning":       "#FBBF24",
    "info":          "#60A5FA",
    "success":       "#4ADE80",
}

# ΓöÇΓöÇ Common Python builtins and low-signal function calls to exclude from graphs ΓöÇΓöÇ
BUILTIN_EXCLUDE_LIST = frozenset({
    "print", "len", "str", "int", "float", "dict", "list", "set", "tuple",
    "range", "enumerate", "zip", "open", "isinstance", "issubclass", "type",
    "super", "format", "hasattr", "getattr", "setattr", "delattr", "min", "max",
    "sum", "any", "all", "abs", "round", "repr", "id", "bool", "map", "filter",
    "sorted", "reversed", "iter", "next", "callable", "hash", "input",
})

# ΓöÇΓöÇ Module color palette mapped consistently per file/module ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
MODULE_PALETTE = [
    "#2DD4BF",  # Teal (accent)
    "#60A5FA",  # Blue (info)
    "#FBBF24",  # Amber (warning)
    "#F87171",  # Coral (critical)
    "#A78BFA",  # Purple
    "#34D399",  # Emerald (success)
    "#FB923C",  # Orange
    "#38BDF8",  # Sky
]

# ΓöÇΓöÇ Full CSS stylesheet ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
_CSS = """
<style>
/* ΓöÇΓöÇ Google Fonts ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ΓöÇΓöÇ CSS custom properties (tokens) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
:root {
    --bg:              #0F172A;
    --panel:           #1E293B;
    --border:          #334155;
    --text-primary:    #E2E8F0;
    --text-secondary:  #94A3B8;
    --accent:          #2DD4BF;
    --critical:        #F87171;
    --warning:         #FBBF24;
    --info:            #60A5FA;
    --success:         #4ADE80;

    --radius-sm:   6px;
    --radius-md:   12px;
    --radius-lg:   16px;
    --radius-pill: 999px;

    --space-xs:  6px;
    --space-sm:  12px;
    --space-md:  16px;
    --space-lg:  24px;
    --space-xl:  32px;
    --space-2xl: 48px;

    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace;

    --shadow-card: 0 1px 3px rgba(0,0,0,0.4), 0 4px 12px rgba(0,0,0,0.25);
}

/* ΓöÇΓöÇ Global reset ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
}

/* ΓöÇΓöÇ Page background ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
}

/* ΓöÇΓöÇ Hide default Streamlit sidebar when using top-nav layout ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="stSidebar"] {
    display: none !important;
}

/* ΓöÇΓöÇ Remove default top padding so our nav sits flush ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.main .block-container {
    padding-top: 0 !important;
    padding-left: var(--space-lg) !important;
    padding-right: var(--space-lg) !important;
    padding-bottom: var(--space-2xl) !important;
    max-width: 1280px !important;
}

/* ΓöÇΓöÇ Headings ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-sans) !important;
    color: var(--text-primary) !important;
}

/* ΓöÇΓöÇ Paragraphs ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
p {
    color: var(--text-secondary) !important;
    font-size: 14px;
    line-height: 1.6;
}

/* ΓöÇΓöÇ Buttons ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stButton > button,
.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div,
.stFormSubmitButton > button,
.stFormSubmitButton > button *,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span,
.stFormSubmitButton > button div,
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-primary"] *,
[data-testid="stBaseButton-primary"] p,
button[kind="primary"],
button[kind="primary"] *,
button[kind="primary"] p {
    background-color: var(--accent) !important;
    color: #041017 !important;
    border: none !important;
    border-radius: var(--radius-pill) !important;
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.15s ease, transform 0.1s ease !important;
    box-shadow: none !important;
}
.stButton > button,
.stFormSubmitButton > button {
    height: auto !important;
    padding: 10px 24px !important;
}
.stFormSubmitButton > button {
    width: 100% !important;
}
.stButton > button:hover,
.stButton > button:hover *,
.stFormSubmitButton > button:hover,
.stFormSubmitButton > button:hover *,
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover * {
    color: #041017 !important;
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0) !important;
    opacity: 1 !important;
}

/* ΓöÇΓöÇ Secondary / ghost buttons (key="*_secondary" pattern) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
button[data-testid*="secondary"],
button[data-testid*="secondary"] *,
button[data-testid*="secondary"] p,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-secondary"] *,
[data-testid="stBaseButton-secondary"] p,
button[kind="secondary"],
button[kind="secondary"] *,
button[kind="secondary"] p,
.cc-btn-secondary > button,
.cc-btn-secondary > button *,
.cc-btn-secondary > button p {
    background-color: transparent !important;
    color: #F8FAFC !important;
    border: 1px solid var(--border) !important;
    font-weight: 600 !important;
}
button[data-testid*="secondary"]:hover,
button[data-testid*="secondary"]:hover *,
button[data-testid*="secondary"]:hover p,
button[kind="secondary"]:hover,
button[kind="secondary"]:hover *,
button[kind="secondary"]:hover p,
.cc-btn-secondary > button:hover,
.cc-btn-secondary > button:hover *,
.cc-btn-secondary > button:hover p {
    border-color: var(--accent) !important;
    color: #FFFFFF !important;
}

/* ΓöÇΓöÇ High contrast for any accent background everywhere ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[style*="background: var(--accent)"],
[style*="background-color: var(--accent)"],
[style*="background: #2DD4BF"],
[style*="background-color: #2DD4BF"],
.cc-badge-accent,
.cc-pill-accent {
    color: #041017 !important;
    font-weight: 700 !important;
}

/* ΓöÇΓöÇ Text inputs ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stTextInput input,
.stNumberInput input {
    background-color: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    height: 40px !important;
    padding: 0 12px !important;
    transition: border-color 0.15s ease !important;
}
.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.15) !important;
    outline: none !important;
}
.stTextInput label,
.stNumberInput label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* ΓöÇΓöÇ Tabs ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 16px !important;
    transition: color 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: var(--space-md) !important;
    background: transparent !important;
}

/* ΓöÇΓöÇ Expanders ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stExpander {
    background-color: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
.stExpander > details > summary {
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: var(--text-primary) !important;
    padding: 14px 18px !important;
    background: var(--panel) !important;
    transition: background 0.15s ease !important;
}
.stExpander > details > summary:hover {
    background: rgba(51, 65, 85, 0.7) !important;
}
.stExpander > details[open] > summary {
    border-bottom: 1px solid var(--border) !important;
}
.stExpander > details > div {
    padding: 14px 18px 18px !important;
    background: var(--panel) !important;
}
/* Expander chevron color */
.stExpander > details > summary > span {
    color: var(--text-secondary) !important;
}

/* ΓöÇΓöÇ Metrics ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="metric-container"] {
    background-color: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: var(--space-md) !important;
    box-shadow: var(--shadow-card) !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-sans) !important;
    font-size: 28px !important;
    font-weight: 600 !important;
    letter-spacing: -0.5px !important;
    color: var(--text-primary) !important;
}

/* ΓöÇΓöÇ st.info / st.warning / st.error / st.success boxes ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stAlert {
    background-color: var(--panel) !important;
    border-radius: var(--radius-md) !important;
    border-left-width: 3px !important;
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    color: var(--text-primary) !important;
}

/* ΓöÇΓöÇ Select / Radio ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stRadio [data-testid="stMarkdownContainer"] p {
    color: var(--text-secondary) !important;
    font-size: 14px !important;
}
.stRadio label { color: var(--text-primary) !important; }

/* ΓöÇΓöÇ Spinners ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stSpinner > div {
    border-color: var(--accent) transparent transparent transparent !important;
}

/* ΓöÇΓöÇ Scrollbar ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: var(--radius-pill); }
::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }

/* ΓöÇΓöÇ Horizontal divider ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
hr {
    border-color: var(--border) !important;
    margin: var(--space-md) 0 !important;
}

/* ΓöÇΓöÇ Caption text ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stCaption, [data-testid="stCaptionContainer"] p {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
}

/* ΓöÇΓöÇ st.container border=True & stForm border removal ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
}

/* ΓöÇΓöÇ Number Input Spacing ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stNumberInput {
    min-width: 130px !important;
}
.stNumberInput input {
    font-family: var(--font-mono) !important;
}

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */
/* Custom HTML components                                                     */
/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

/* ΓöÇΓöÇ Top navigation bar ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-global-navbar-wrap {
    margin-bottom: var(--space-md);
    padding-bottom: var(--space-xs);
    border-bottom: 1px solid var(--border);
}
.cc-nav-brand button {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 6px 10px !important;
    box-shadow: none !important;
    transform: none !important;
}
.cc-nav-brand button:hover {
    color: var(--accent) !important;
    background: transparent !important;
}
.cc-nav-link button {
    background: transparent !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    border-radius: var(--radius-pill) !important;
    box-shadow: none !important;
    transform: none !important;
}
.cc-nav-link button:hover {
    color: var(--text-primary) !important;
    background: rgba(51, 65, 85, 0.4) !important;
}
.cc-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-lg);
    height: 60px;
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    margin-bottom: var(--space-lg);
    margin-left: calc(-1 * var(--space-lg));
    margin-right: calc(-1 * var(--space-lg));
    margin-top: 0;
    position: sticky;
    top: 0;
    z-index: 999;
}
.cc-navbar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
}
.cc-navbar-logo-icon {
    width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #2DD4BF 0%, #60A5FA 50%, #A78BFA 100%);
    border-radius: 6px;
    flex-shrink: 0;
}
.cc-navbar-wordmark {
    font-family: var(--font-sans);
    font-size: 17px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.3px;
}
.cc-navbar-right {
    display: flex;
    align-items: center;
    gap: var(--space-sm);
}
.cc-user-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(51,65,85,0.6);
    border: 1px solid var(--border);
    border-radius: var(--radius-pill);
    padding: 4px 10px 4px 8px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-secondary);
}
.cc-user-dot {
    width: 7px; height: 7px;
    background: var(--success);
    border-radius: 50%;
    flex-shrink: 0;
}

/* ΓöÇΓöÇ Section eyebrow label ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: var(--space-sm);
    padding-bottom: var(--space-xs);
    border-bottom: 1px solid var(--border);
}

/* ΓöÇΓöÇ Hero CRS gradient band ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-crs-band {
    background: linear-gradient(135deg, #0F4C5C 0%, #0F2A3C 40%, #1A1040 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    margin-bottom: var(--space-lg);
    position: relative;
    overflow: hidden;
}
.cc-crs-band::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -10%;
    width: 280px;
    height: 280px;
    background: radial-gradient(circle, rgba(45,212,191,0.12) 0%, transparent 65%);
    pointer-events: none;
}
.cc-crs-score {
    font-family: var(--font-sans);
    font-size: 64px;
    font-weight: 700;
    letter-spacing: -2px;
    color: #FFFFFF;
    line-height: 1;
}
.cc-crs-denom {
    font-size: 28px;
    font-weight: 400;
    color: rgba(255,255,255,0.45);
}
.cc-crs-label {
    font-family: var(--font-sans);
    font-size: 16px;
    font-weight: 500;
    color: rgba(255,255,255,0.75);
    margin-top: 4px;
}
.cc-crs-meta {
    font-family: var(--font-mono);
    font-size: 11px;
    color: rgba(255,255,255,0.4);
    margin-top: 6px;
}

/* ΓöÇΓöÇ Severity chips ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-chip {
    display: inline-block;
    font-family: var(--font-sans);
    font-size: 11px;
    font-weight: 600;
    border-radius: var(--radius-pill);
    padding: 2px 9px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.cc-chip-critical { background: rgba(248,113,113,0.15); color: #F87171; }
.cc-chip-warning  { background: rgba(251,191,36,0.15);  color: #FBBF24; }
.cc-chip-info     { background: rgba(96,165,250,0.15);  color: #60A5FA; }
.cc-chip-success  { background: rgba(74,222,128,0.15);  color: #4ADE80; }

/* ΓöÇΓöÇ Issue finding card (inside expander header) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-issue-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    width: 100%;
}
.cc-issue-rule {
    font-family: var(--font-sans);
    font-weight: 500;
    font-size: 14px;
    color: var(--text-primary);
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cc-file-mono {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text-secondary);
    background: rgba(15,23,42,0.6);
    border-radius: 4px;
    padding: 2px 6px;
    display: inline-block;
}

/* ΓöÇΓöÇ Graph panel ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-graph-panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-md) var(--space-lg) var(--space-lg);
    margin-top: var(--space-lg);
}
.cc-graph-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-md);
}
.cc-graph-title {
    font-family: var(--font-sans);
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
}
.cc-graph-meta {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-secondary);
}

/* ΓöÇΓöÇ Auth card (login page) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-auth-wordmark {
    font-family: var(--font-sans);
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--text-primary);
}
.cc-auth-sub {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 4px;
}
.cc-auth-accent-bar {
    height: 3px;
    background: linear-gradient(90deg, #2DD4BF, #60A5FA, #A78BFA, #F472B6);
    border-radius: var(--radius-pill);
    margin: 14px 0;
}

/* ΓöÇΓöÇ About tab content ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-about-section {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin-bottom: var(--space-md);
}
.cc-about-section h3 {
    font-size: 16px;
    font-weight: 600;
    color: var(--accent) !important;
    margin-bottom: var(--space-sm);
}
.cc-about-section p {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary) !important;
}
.cc-about-section ul {
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.8;
    padding-left: var(--space-md);
}
.cc-about-section code {
    font-family: var(--font-mono);
    font-size: 12px;
    background: rgba(15,23,42,0.7);
    color: var(--accent);
    border-radius: 4px;
    padding: 1px 5px;
}
.cc-arch-row {
    display: flex;
    gap: var(--space-md);
    flex-wrap: wrap;
    margin-top: var(--space-md);
}
.cc-arch-badge {
    background: rgba(15,23,42,0.6);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 6px 12px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--text-secondary);
}

/* ΓöÇΓöÇ Reports page ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-report-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: var(--space-lg);
    margin-bottom: var(--space-md);
}

/* ΓöÇΓöÇ Empty state ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-empty {
    text-align: center;
    padding: var(--space-2xl) var(--space-lg);
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}
.cc-empty-icon { font-size: 36px; margin-bottom: var(--space-sm); }
.cc-empty-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
}
.cc-empty-sub {
    font-size: 13px;
    color: var(--text-secondary);
    font-family: var(--font-mono);
}

/* ΓöÇΓöÇ Agraph container background ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-agraph-wrap {
    width: 100% !important;
    height: 850px !important;
    min-height: 850px !important;
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    margin-top: 10px !important;
    margin-bottom: 16px !important;
}
.cc-agraph-wrap iframe {
    background: var(--bg) !important;
    border-radius: var(--radius-md) !important;
    border: none !important;
    width: 100% !important;
    height: 850px !important;
    min-height: 850px !important;
    display: block !important;
}

/* ΓöÇΓöÇ Graph Status & Filter Summary ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-graph-status {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(30, 41, 59, 0.85);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 8px 14px;
    font-size: 13px;
    color: var(--text-primary);
    margin: 8px 0 12px 0;
}
.cc-graph-status-count {
    font-family: var(--font-mono);
    color: var(--accent);
    font-weight: 600;
}

/* ΓöÇΓöÇ Module Legend Badges ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-module-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    margin-bottom: 10px;
}
.cc-module-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-primary);
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid var(--border);
    border-radius: var(--radius-pill);
    padding: 3px 10px;
}
.cc-module-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

/* ΓöÇΓöÇ Orphaned Functions Box ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-orphan-box {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 18px;
    margin-top: 14px;
}
.cc-orphan-title {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.cc-orphan-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.cc-orphan-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid var(--border);
    border-radius: var(--radius-pill);
    padding: 3px 10px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-secondary);
}
.cc-orphan-chip:hover {
    border-color: var(--accent);
    color: var(--text-primary);
}

/* ΓöÇΓöÇ Streamlit table ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stTable table { background: var(--panel) !important; }
.stTable th {
    background: rgba(15,23,42,0.5) !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-mono) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.stTable td { color: var(--text-primary) !important; font-size: 13px !important; }

/* ΓöÇΓöÇ Number input arrows ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.stNumberInput button {
    background: var(--border) !important;
    border: none !important;
    border-radius: 4px !important;
    color: var(--text-primary) !important;
}

/* ΓöÇΓöÇ st.success / st.error / st.warning ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="stAlert"] { border-radius: var(--radius-md) !important; }

/* ΓöÇΓöÇ Nav radio buttons (hidden label, styled as tab row) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
div[data-testid="stHorizontalBlock"] .stRadio > div {
    flex-direction: row !important;
    gap: 4px !important;
}
div[data-testid="stHorizontalBlock"] .stRadio label {
    padding: 8px 16px !important;
    border-radius: var(--radius-pill) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.15s ease, color 0.15s ease !important;
    color: var(--text-secondary) !important;
}
div[data-testid="stHorizontalBlock"] .stRadio label:has(input:checked) {
    background: rgba(45,212,191,0.12) !important;
    color: var(--accent) !important;
}
div[data-testid="stHorizontalBlock"] .stRadio label:hover {
    background: rgba(51,65,85,0.5) !important;
    color: var(--text-primary) !important;
}
div[data-testid="stHorizontalBlock"] .stRadio input { display: none !important; }
div[data-testid="stHorizontalBlock"] .stRadio [data-baseweb="radio"] { display: none !important; }

/* ΓöÇΓöÇ Landing page ΓÇö hero section ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-hero {
    padding: var(--space-2xl) var(--space-lg) var(--space-xl);
    max-width: 760px;
    margin: 0 auto;
    text-align: center;
}
.cc-hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: var(--space-sm);
}
.cc-hero-title {
    font-family: var(--font-sans);
    font-size: 48px;
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1.1;
    color: var(--text-primary);
    margin-bottom: var(--space-md);
}
.cc-hero-sub {
    font-family: var(--font-sans);
    font-size: 18px;
    font-weight: 400;
    line-height: 1.65;
    color: var(--text-secondary);
    margin-bottom: var(--space-xl);
}

/* ΓöÇΓöÇ Feature cards ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-feature-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    height: 100%;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.cc-feature-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 0 1px rgba(45,212,191,0.2), var(--shadow-card);
}
.cc-feature-icon {
    font-size: 28px;
    margin-bottom: var(--space-sm);
}
.cc-feature-title {
    font-family: var(--font-sans);
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--space-xs);
    letter-spacing: -0.2px;
}
.cc-feature-body {
    font-family: var(--font-sans);
    font-size: 14px;
    line-height: 1.65;
    color: var(--text-secondary);
}
.cc-feature-body code {
    font-family: var(--font-mono);
    font-size: 12px;
    background: rgba(15,23,42,0.7);
    color: var(--accent);
    border-radius: 4px;
    padding: 1px 4px;
}

/* ΓöÇΓöÇ Architecture comparison table ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-arch-table-wrap {
    overflow-x: auto;
    margin-top: var(--space-md);
}
.cc-arch-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-sans);
    font-size: 14px;
}
.cc-arch-table th {
    background: rgba(15,23,42,0.6);
    color: var(--text-secondary);
    font-family: var(--font-mono);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 10px 16px;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.cc-arch-table td {
    color: var(--text-primary);
    padding: 10px 16px;
    border-bottom: 1px solid rgba(51,65,85,0.4);
    vertical-align: top;
}
.cc-arch-table td:first-child {
    color: var(--accent);
    font-weight: 500;
    white-space: nowrap;
}
.cc-arch-table td code {
    font-family: var(--font-mono);
    font-size: 12px;
    background: rgba(15,23,42,0.7);
    color: var(--accent);
    border-radius: 4px;
    padding: 1px 4px;
}
.cc-arch-table tr:hover td {
    background: rgba(51,65,85,0.2);
}

/* ΓöÇΓöÇ Navbar links row (landing) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-navbar-links {
    display: flex;
    align-items: center;
    gap: var(--space-xs);
}
.cc-navbar-link {
    font-family: var(--font-sans);
    font-size: 14px;
    font-weight: 500;
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: var(--radius-pill);
    cursor: pointer;
    transition: color 0.15s ease, background 0.15s ease;
}
.cc-navbar-link:hover {
    color: var(--text-primary);
    background: rgba(51,65,85,0.5);
}

/* ΓöÇΓöÇ Form submit button ΓÇö constrain width in auth card ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
/* Scoped only to the 3-column center layout, not global */
.cc-btn-centered { display: flex; justify-content: center; }
.cc-btn-centered .stFormSubmitButton > button {
    max-width: 240px !important;
    width: auto !important;
}

/* ΓöÇΓöÇ Remove default borders on forms and form containers ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="stForm"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

/* ΓöÇΓöÇ Stepper and control spacing (prevents Min Degree clipping) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
[data-testid="stNumberInput"] {
    min-width: 110px !important;
}
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label {
    white-space: nowrap !important;
}

/* ΓöÇΓöÇ Call graph canvas container ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-agraph-wrap {
    width: 100% !important;
    height: 850px !important;
    min-height: 850px !important;
    overflow: hidden !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background-color: var(--bg) !important;
    margin-top: var(--space-md) !important;
    margin-bottom: var(--space-lg) !important;
}
.cc-agraph-wrap iframe,
.cc-agraph-wrap [data-testid="stIFrame"],
iframe[title="streamlit_agraph.agraph"] {
    width: 100% !important;
    height: 850px !important;
    min-height: 850px !important;
    border: none !important;
    background-color: var(--bg) !important;
}

/* ΓöÇΓöÇ Global Navbar styling ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ */
.cc-global-nav-divider {
    margin: 4px 0 16px 0 !important;
    border: none !important;
    border-bottom: 1px solid var(--border) !important;
}

/* Bug 1 fix: kill border/background on the col_brand column wrapper itself */
div[class*="st-key-nav_brand_btn"] > div,
div[class*="st-key-nav_brand_btn"] [data-testid="stVerticalBlockBorderWrapper"],
div[class*="st-key-nav_brand_btn"] [data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* Nav brand button: ≡ƒº¡ CodeCompass */
div[class*="st-key-nav_brand"] button,
button[data-testid*="nav_brand"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: var(--font-sans) !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 6px 4px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
}
div[class*="st-key-nav_brand"] button:hover,
button[data-testid*="nav_brand"]:hover {
    color: var(--accent) !important;
    background: transparent !important;
}

/* Nav links: Overview, Live Audit, Documentation */
div[class*="st-key-nav_link"] button,
button[data-testid*="nav_link"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: var(--font-sans) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    box-shadow: none !important;
    border-radius: var(--radius-pill) !important;
    white-space: nowrap !important;
    transition: color 0.15s ease, background 0.15s ease !important;
}
div[class*="st-key-nav_link"] button:hover,
button[data-testid*="nav_link"]:hover {
    color: var(--text-primary) !important;
    background: rgba(51, 65, 85, 0.4) !important;
}

/* Nav logout button */
div[class*="st-key-nav_logout"] button,
button[data-testid*="nav_logout"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-secondary) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 4px 14px !important;
    border-radius: var(--radius-pill) !important;
    height: 36px !important;
    white-space: nowrap !important;
}
div[class*="st-key-nav_logout"] button:hover,
button[data-testid*="nav_logout"]:hover {
    border-color: var(--critical) !important;
    color: var(--critical) !important;
    background: rgba(248, 113, 113, 0.1) !important;
}

/* Nav signin button ΓÇö filled teal pill, identical in ALL states (guest, anon, landing) */
div[class*="st-key-nav_guest_signin"] button,
div[class*="st-key-nav_anon_signin"] button,
div[class*="st-key-landing_nav_signin"] button {
    background: var(--accent) !important;
    border: none !important;
    color: #041017 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    padding: 6px 16px !important;
    border-radius: var(--radius-pill) !important;
    height: auto !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    letter-spacing: 0.02em !important;
}
div[class*="st-key-nav_guest_signin"] button:hover,
div[class*="st-key-nav_anon_signin"] button:hover,
div[class*="st-key-landing_nav_signin"] button:hover {
    opacity: 0.9 !important;
    background: var(--accent) !important;
    color: #041017 !important;
}

/* Nav Back to Home (anon on auth page) ΓÇö ghost pill, distinct from Sign In */
div[class*="st-key-nav_anon_home"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 4px 14px !important;
    border-radius: var(--radius-pill) !important;
    height: 36px !important;
    white-space: nowrap !important;
}
div[class*="st-key-nav_anon_home"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
</style>
"""


def inject_styles() -> None:
    """Inject the Deep Slate stylesheet into the current Streamlit page.

    Call this once near the top of every page function (before rendering any
    Streamlit widgets). Subsequent calls within the same script run are safe
    but redundant.
    """
    st.markdown(_CSS, unsafe_allow_html=True)
