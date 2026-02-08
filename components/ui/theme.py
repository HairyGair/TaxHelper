"""
Meridian Design System
======================
Luxury fintech theme for UK Tax Helper.
Deep midnight slate base, sapphire blue accents, emerald income, copper expense.

Typography: Instrument Sans + IBM Plex Mono
Aesthetic: Bloomberg terminal meets premium private banking
"""

import streamlit as st


def inject_obsidian_theme():
    """
    Single entry point for the Meridian design system.
    Call once at the top of app.py.
    Name kept as inject_obsidian_theme for backward compatibility.
    """
    st.markdown(_MERIDIAN_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Theme Palette (Python-side for Plotly charts, etc.)
# ---------------------------------------------------------------------------
OBSIDIAN = {
    "bg":           "#0b0e14",
    "surface":      "#12161f",
    "surface_alt":  "#181d28",
    "card":         "rgba(18, 22, 31, 0.92)",
    "border":       "rgba(79, 143, 234, 0.08)",
    "border_hover": "rgba(79, 143, 234, 0.22)",

    # Sapphire accent spectrum
    "gold":         "#4f8fea",
    "gold_light":   "#7aafff",
    "gold_muted":   "#3a6db8",
    "amber":        "#5ba0f5",

    # Semantic
    "income":       "#36c7a0",
    "income_dark":  "#1f9d7a",
    "expense":      "#e07a5f",
    "expense_dark": "#c4563c",
    "info":         "#7aafff",
    "warning":      "#e5b567",

    # Text
    "text":         "#c8cdd5",
    "text_secondary": "rgba(200, 205, 213, 0.65)",
    "text_muted":   "rgba(200, 205, 213, 0.38)",

    # Chart palette
    "chart_colors": [
        "#4f8fea", "#36c7a0", "#e07a5f", "#b68bd4",
        "#e5b567", "#5bc0de", "#f2917c", "#7dc4e4",
        "#a3d977", "#d4a0c0",
    ],
    "chart_bg":     "#12161f",
    "chart_grid":   "rgba(200, 205, 213, 0.05)",
    "chart_text":   "#c8cdd5",
}


def plotly_obsidian_layout(**overrides):
    """Return a base Plotly layout dict matching the Meridian theme."""
    base = dict(
        paper_bgcolor=OBSIDIAN["chart_bg"],
        plot_bgcolor=OBSIDIAN["chart_bg"],
        font=dict(color=OBSIDIAN["chart_text"], family="Instrument Sans, sans-serif"),
        xaxis=dict(gridcolor=OBSIDIAN["chart_grid"], zerolinecolor=OBSIDIAN["chart_grid"]),
        yaxis=dict(gridcolor=OBSIDIAN["chart_grid"], zerolinecolor=OBSIDIAN["chart_grid"]),
        colorway=OBSIDIAN["chart_colors"],
        margin=dict(l=40, r=24, t=48, b=40),
        hoverlabel=dict(
            bgcolor=OBSIDIAN["surface"],
            font_color=OBSIDIAN["text"],
            bordercolor=OBSIDIAN["gold"],
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=OBSIDIAN["text_secondary"]),
        ),
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Meridian CSS
# ---------------------------------------------------------------------------
_MERIDIAN_CSS = """
<style>
/* ==========================================================================
   MERIDIAN — Luxury Fintech Design System
   Deep midnight slate, sapphire blue, emerald + copper accents
   ========================================================================== */

/* Fonts ------------------------------------------------------------------ */
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* Variables -------------------------------------------------------------- */
:root {
    /* Base palette */
    --mr-bg:            #0b0e14;
    --mr-surface:       #12161f;
    --mr-surface-alt:   #181d28;
    --mr-surface-hover: #1e2433;
    --mr-elevated:      #232a3a;

    /* Sapphire accent spectrum */
    --mr-sapphire:      #4f8fea;
    --mr-sapphire-light:#7aafff;
    --mr-sapphire-muted:#3a6db8;
    --mr-sapphire-deep: #2a5694;
    --mr-sapphire-glow: rgba(79, 143, 234, 0.30);
    --mr-sapphire-subtle:rgba(79, 143, 234, 0.06);

    /* Semantic colours */
    --mr-income:        #36c7a0;
    --mr-income-glow:   rgba(54, 199, 160, 0.20);
    --mr-expense:       #e07a5f;
    --mr-expense-glow:  rgba(224, 122, 95, 0.20);
    --mr-info:          #7aafff;
    --mr-info-glow:     rgba(122, 175, 255, 0.20);
    --mr-warning:       #e5b567;
    --mr-warning-glow:  rgba(229, 181, 103, 0.20);
    --mr-danger:        #e05252;

    /* Text */
    --mr-text:          #c8cdd5;
    --mr-text-2:        rgba(200, 205, 213, 0.65);
    --mr-text-3:        rgba(200, 205, 213, 0.38);
    --mr-text-inv:      #0b0e14;

    /* Borders / Glass */
    --mr-border:        rgba(79, 143, 234, 0.08);
    --mr-border-hover:  rgba(79, 143, 234, 0.22);
    --mr-glass:         rgba(18, 22, 31, 0.92);
    --mr-glass-hover:   rgba(24, 29, 40, 0.95);
    --mr-blur:          blur(20px);

    /* Radius */
    --mr-r-sm:  4px;
    --mr-r-md:  8px;
    --mr-r-lg:  14px;
    --mr-r-xl:  20px;
    --mr-r-pill: 9999px;

    /* Shadows */
    --mr-shadow-sm:  0 1px 2px rgba(0,0,0,0.35);
    --mr-shadow-md:  0 4px 16px rgba(0,0,0,0.4);
    --mr-shadow-lg:  0 8px 32px rgba(0,0,0,0.45);
    --mr-shadow-xl:  0 20px 60px rgba(0,0,0,0.5);
    --mr-shadow-sapphire: 0 4px 24px rgba(79, 143, 234, 0.12);
    --mr-shadow-inset: inset 0 1px 0 rgba(255,255,255,0.03);

    /* Timing */
    --mr-ease:    cubic-bezier(0.25, 0.1, 0.25, 1);
    --mr-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);
    --mr-t-fast:  120ms;
    --mr-t-base:  200ms;
    --mr-t-slow:  350ms;
}

/* Keyframes -------------------------------------------------------------- */
@keyframes mr-fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes mr-slide-up {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes mr-pulse-blue {
    0%, 100% { box-shadow: 0 0 0 0 rgba(79,143,234,0.25); }
    50%      { box-shadow: 0 0 0 6px rgba(79,143,234,0); }
}
@keyframes mr-shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes mr-count-up {
    from { opacity: 0; transform: scale(0.85); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes mr-glow-line {
    0%   { background-position: -100% 0; }
    100% { background-position: 200% 0; }
}
@keyframes mr-breathe {
    0%, 100% { opacity: 0.4; }
    50%      { opacity: 0.7; }
}

/* Base ------------------------------------------------------------------- */
*, *::before, *::after {
    font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
code, pre, .stCodeBlock, .stCodeBlock * {
    font-family: 'IBM Plex Mono', 'Fira Code', monospace !important;
}

html { scroll-behavior: smooth; }

.stApp {
    background: var(--mr-bg);
    color: var(--mr-text);
    min-height: 100vh;
}

/* Very subtle noise overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.012'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}

/* Ambient sapphire glow - top right */
.stApp::after {
    content: '';
    position: fixed;
    top: -15%;
    right: -8%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(79,143,234,0.04) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
    animation: mr-breathe 8s ease-in-out infinite;
}

.main > div { position: relative; z-index: 1; }

.main .block-container {
    max-width: 1400px;
    padding: 1.5rem 2.5rem 4rem;
    animation: mr-fade-in 0.35s var(--mr-ease);
}

/* Typography ------------------------------------------------------------- */
h1, h2, h3, h4, h5, h6 {
    color: var(--mr-text) !important;
    font-weight: 700;
    letter-spacing: -0.025em;
    line-height: 1.15;
}
h1 { font-size: 2rem !important; font-weight: 700 !important; }
h2 { font-size: 1.55rem !important; }
h3 { font-size: 1.2rem !important; }

p, .stMarkdown, .stMarkdown p { color: var(--mr-text-2); line-height: 1.6; }
label { color: var(--mr-text-2) !important; font-weight: 500; font-size: 0.88rem; }
a { color: var(--mr-sapphire-light); text-decoration: none; }
a:hover { color: var(--mr-sapphire); text-decoration: underline; }

/* Sidebar ---------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e1219 0%, #090c11 100%);
    border-right: 1px solid var(--mr-border);
}
section[data-testid="stSidebar"] > div {
    padding: 1.25rem 0.85rem;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--mr-sapphire-light) !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: var(--mr-text-2) !important;
}

/* Sidebar nav radio items */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 1px;
}

section[data-testid="stSidebar"] .stRadio > div > label {
    color: var(--mr-text-3) !important;
    padding: 0.5rem 0.75rem;
    border-radius: var(--mr-r-md);
    transition: all var(--mr-t-fast) var(--mr-ease);
    border-left: 2px solid transparent;
    font-size: 0.88rem;
    font-weight: 500;
}

section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(79, 143, 234, 0.04);
    color: var(--mr-text) !important;
    border-left-color: rgba(79, 143, 234, 0.25);
}

section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    background: linear-gradient(90deg, rgba(79,143,234,0.1) 0%, rgba(79,143,234,0.03) 100%);
    color: var(--mr-sapphire-light) !important;
    font-weight: 600;
    border-left-color: var(--mr-sapphire);
    box-shadow: var(--mr-shadow-sapphire);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(79, 143, 234, 0.06);
    border: 1px solid rgba(79, 143, 234, 0.12);
    color: var(--mr-sapphire-light) !important;
    font-weight: 500;
    font-size: 0.85rem;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(79, 143, 234, 0.12);
    border-color: rgba(79, 143, 234, 0.25);
    box-shadow: var(--mr-shadow-sapphire);
}

section[data-testid="stSidebar"] hr {
    border-color: var(--mr-border);
    margin: 0.6rem 0;
}

section[data-testid="stSidebar"] .stAlert {
    background: rgba(79, 143, 234, 0.04);
    border: 1px solid rgba(79, 143, 234, 0.1);
    color: var(--mr-text-2) !important;
    border-radius: var(--mr-r-md);
    font-size: 0.82rem;
}

/* Cards ------------------------------------------------------------------ */
div[data-testid="metric-container"] {
    background: var(--mr-glass);
    backdrop-filter: var(--mr-blur);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-lg);
    padding: 1.15rem;
    transition: all var(--mr-t-base) var(--mr-ease);
    box-shadow: var(--mr-shadow-sm), var(--mr-shadow-inset);
}
div[data-testid="metric-container"]:hover {
    border-color: var(--mr-border-hover);
    box-shadow: var(--mr-shadow-md), var(--mr-shadow-sapphire);
    transform: translateY(-1px);
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--mr-text-3) !important;
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--mr-text) !important;
    font-size: 1.75rem;
    font-weight: 700;
    animation: mr-count-up 0.4s var(--mr-spring);
}

/* Buttons ---------------------------------------------------------------- */
.stButton > button {
    background: linear-gradient(135deg, var(--mr-sapphire-muted) 0%, var(--mr-sapphire) 100%);
    color: #ffffff !important;
    border: none;
    border-radius: var(--mr-r-md);
    padding: 0.55rem 1.3rem;
    font-weight: 600;
    font-size: 0.88rem;
    letter-spacing: 0.01em;
    box-shadow: var(--mr-shadow-sm);
    transition: all var(--mr-t-base) var(--mr-ease);
    position: relative;
    overflow: hidden;
}
.stButton > button::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    background-size: 200% 100%;
    opacity: 0;
    transition: opacity var(--mr-t-fast);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: var(--mr-shadow-md), 0 0 20px var(--mr-sapphire-glow);
}
.stButton > button:hover::after {
    opacity: 1;
    animation: mr-shimmer 1s linear infinite;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--mr-sapphire) 0%, var(--mr-sapphire-light) 100%);
    box-shadow: var(--mr-shadow-md), 0 0 16px var(--mr-sapphire-glow);
}
.stButton > button[kind="secondary"] {
    background: transparent;
    border: 1.5px solid var(--mr-sapphire-muted);
    color: var(--mr-sapphire-light) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(79, 143, 234, 0.06);
    border-color: var(--mr-sapphire);
}

/* Form inputs ------------------------------------------------------------ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
    color: var(--mr-text);
    padding: 0.6rem 0.85rem;
    font-size: 0.92rem;
    transition: all var(--mr-t-base) var(--mr-ease);
}
.stTextInput > div > div > input:hover,
.stNumberInput > div > div > input:hover,
.stDateInput > div > div > input:hover {
    border-color: var(--mr-border-hover);
    background: var(--mr-surface-alt);
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stDateInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--mr-sapphire);
    box-shadow: 0 0 0 2px rgba(79, 143, 234, 0.1);
    outline: none;
    background: var(--mr-surface-alt);
}

/* Select boxes */
.stSelectbox > div > div {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
    transition: all var(--mr-t-base) var(--mr-ease);
}
.stSelectbox > div > div:hover {
    border-color: var(--mr-border-hover);
}
[data-baseweb="popover"] {
    background: var(--mr-surface) !important;
    border: 1px solid var(--mr-border) !important;
    border-radius: var(--mr-r-md) !important;
    box-shadow: var(--mr-shadow-xl) !important;
}
[role="option"] {
    color: var(--mr-text-2) !important;
    transition: background var(--mr-t-fast);
}
[role="option"]:hover {
    background: rgba(79, 143, 234, 0.08) !important;
    color: var(--mr-text) !important;
}

/* Multiselect */
.stMultiSelect > div > div {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
}
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(79, 143, 234, 0.1);
    border: 1px solid rgba(79, 143, 234, 0.18);
    color: var(--mr-sapphire-light);
    border-radius: var(--mr-r-sm);
}

/* Tabs ------------------------------------------------------------------- */
.stTabs [data-baseweb="tab-list"] {
    background: var(--mr-surface);
    border-radius: var(--mr-r-md);
    padding: 3px;
    gap: 3px;
    border: 1px solid var(--mr-border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--mr-text-3) !important;
    border-radius: var(--mr-r-sm);
    padding: 0.5rem 1.1rem;
    font-weight: 500;
    font-size: 0.88rem;
    transition: all var(--mr-t-fast) var(--mr-ease);
    border-bottom: none;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(79, 143, 234, 0.04);
    color: var(--mr-text) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(79, 143, 234, 0.1) !important;
    color: var(--mr-sapphire-light) !important;
    font-weight: 600;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    display: none;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}

/* Expanders -------------------------------------------------------------- */
.streamlit-expanderHeader {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
    color: var(--mr-text) !important;
    font-weight: 600;
    padding: 0.7rem 1rem;
    transition: all var(--mr-t-base) var(--mr-ease);
}
.streamlit-expanderHeader:hover {
    background: var(--mr-surface-hover);
    border-color: var(--mr-border-hover);
}
.streamlit-expanderContent {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-top: none;
    border-radius: 0 0 var(--mr-r-md) var(--mr-r-md);
    padding: 1.1rem;
}

/* DataFrames ------------------------------------------------------------- */
.stDataFrame {
    border-radius: var(--mr-r-lg);
    overflow: hidden;
    border: 1px solid var(--mr-border);
    box-shadow: var(--mr-shadow-md);
}
.stDataFrame thead tr th {
    background: var(--mr-surface-alt) !important;
    color: var(--mr-sapphire-light) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.7rem !important;
    letter-spacing: 0.07em;
    padding: 0.75rem 0.9rem !important;
    border-bottom: 1px solid rgba(79, 143, 234, 0.1) !important;
}
.stDataFrame tbody tr {
    background: var(--mr-surface) !important;
    transition: background var(--mr-t-fast);
}
.stDataFrame tbody tr:hover {
    background: rgba(79, 143, 234, 0.03) !important;
}
.stDataFrame tbody tr td {
    color: var(--mr-text-2) !important;
    padding: 0.65rem 0.9rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.02) !important;
    font-size: 0.85rem;
}

/* File uploader ---------------------------------------------------------- */
.stFileUploader > div {
    background: var(--mr-surface);
    border: 2px dashed rgba(79, 143, 234, 0.12);
    border-radius: var(--mr-r-lg);
    padding: 1.75rem;
    text-align: center;
    transition: all var(--mr-t-base) var(--mr-ease);
}
.stFileUploader > div:hover {
    border-color: var(--mr-sapphire-muted);
    background: var(--mr-surface-alt);
    box-shadow: 0 0 24px rgba(79, 143, 234, 0.06);
}

/* Alerts ----------------------------------------------------------------- */
.stAlert {
    border-radius: var(--mr-r-md);
    padding: 0.75rem 1rem;
    border-left-width: 3px;
    font-size: 0.88rem;
}
.stSuccess, div[data-testid="stAlertContainer"] > div[role="alert"]:has(.icon-success) {
    background: rgba(54, 199, 160, 0.06);
    border-color: var(--mr-income);
    color: var(--mr-text) !important;
}
.stError {
    background: rgba(224, 122, 95, 0.06);
    border-color: var(--mr-expense);
    color: var(--mr-text) !important;
}
.stWarning {
    background: rgba(229, 181, 103, 0.06);
    border-color: var(--mr-warning);
    color: var(--mr-text) !important;
}
.stInfo {
    background: rgba(122, 175, 255, 0.06);
    border-color: var(--mr-info);
    color: var(--mr-text) !important;
}

/* Progress bars ---------------------------------------------------------- */
.stProgress > div > div {
    background: var(--mr-surface-alt);
    border-radius: var(--mr-r-pill);
    height: 6px;
    overflow: hidden;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--mr-sapphire-muted), var(--mr-sapphire), var(--mr-sapphire-light));
    border-radius: var(--mr-r-pill);
    box-shadow: 0 0 8px var(--mr-sapphire-glow);
}

/* Plotly charts ---------------------------------------------------------- */
.stPlotlyChart {
    background: var(--mr-glass);
    border-radius: var(--mr-r-lg);
    border: 1px solid var(--mr-border);
    padding: 0.35rem;
    box-shadow: var(--mr-shadow-sm);
}

/* Checkboxes & radios ---------------------------------------------------- */
.stCheckbox > label > span,
.stRadio > div > label > span {
    color: var(--mr-text-2);
}

/* Scrollbar -------------------------------------------------------------- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--mr-bg); }
::-webkit-scrollbar-thumb {
    background: rgba(79, 143, 234, 0.15);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(79, 143, 234, 0.3);
}
* { scrollbar-width: thin; scrollbar-color: rgba(79,143,234,0.15) var(--mr-bg); }

/* Tooltips --------------------------------------------------------------- */
[role="tooltip"] {
    background: var(--mr-surface-alt) !important;
    color: var(--mr-text) !important;
    border: 1px solid var(--mr-border) !important;
    border-radius: var(--mr-r-sm) !important;
    font-size: 0.82rem !important;
    box-shadow: var(--mr-shadow-lg);
}

/* Focus accessible ------------------------------------------------------- */
*:focus-visible {
    outline: 2px solid var(--mr-sapphire);
    outline-offset: 2px;
    border-radius: 3px;
}

/* Dividers / hr ---------------------------------------------------------- */
hr {
    border: none;
    border-top: 1px solid var(--mr-border);
    margin: 0.75rem 0;
}

/* ========================================================================
   UTILITY CLASSES (for use in st.markdown HTML)
   ======================================================================== */

/* Cards */
.ob-card {
    background: var(--mr-glass);
    backdrop-filter: var(--mr-blur);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-lg);
    padding: 1.35rem;
    transition: all var(--mr-t-base) var(--mr-ease);
    box-shadow: var(--mr-shadow-sm), var(--mr-shadow-inset);
}
.ob-card:hover {
    border-color: var(--mr-border-hover);
    box-shadow: var(--mr-shadow-md), var(--mr-shadow-sapphire);
    transform: translateY(-1px);
}

/* KPI card */
.ob-kpi {
    background: var(--mr-glass);
    backdrop-filter: var(--mr-blur);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-lg);
    padding: 1.1rem 1.35rem;
    position: relative;
    overflow: hidden;
    transition: all var(--mr-t-base) var(--mr-ease);
    box-shadow: var(--mr-shadow-sm), var(--mr-shadow-inset);
}
.ob-kpi::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--mr-sapphire-muted), var(--mr-sapphire), var(--mr-sapphire-light));
    background-size: 200% 100%;
    animation: mr-glow-line 4s linear infinite;
}
.ob-kpi:hover {
    border-color: var(--mr-border-hover);
    transform: translateY(-2px);
    box-shadow: var(--mr-shadow-lg), var(--mr-shadow-sapphire);
}
.ob-kpi-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--mr-text-3);
    margin-bottom: 0.35rem;
}
.ob-kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--mr-text);
    line-height: 1.1;
    animation: mr-count-up 0.5s var(--mr-spring);
}
.ob-kpi-delta {
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.3rem;
}
.ob-kpi-delta.positive { color: var(--mr-income); }
.ob-kpi-delta.negative { color: var(--mr-expense); }
.ob-kpi-delta.neutral  { color: var(--mr-text-3); }
.ob-kpi-icon {
    font-size: 1.5rem;
    opacity: 0.4;
    position: absolute;
    top: 1rem;
    right: 1.1rem;
}

/* Hero banner */
.ob-hero {
    background: linear-gradient(135deg, #141927 0%, #0b0e14 40%, #111724 100%);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-xl);
    padding: 2.25rem;
    margin-bottom: 1.75rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--mr-shadow-lg), var(--mr-shadow-inset);
    animation: mr-slide-down 0.4s var(--mr-ease) both;
}
@keyframes mr-slide-down {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Auto-stagger section headers */
.ob-section-header {
    animation: mr-stagger-in 0.4s var(--mr-ease) 0.15s both;
}
.ob-hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -8%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(79,143,234,0.08) 0%, transparent 65%);
    pointer-events: none;
}
.ob-hero::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--mr-sapphire), transparent);
    background-size: 200% 100%;
    animation: mr-glow-line 5s linear infinite;
}
.ob-hero h1 {
    color: var(--mr-text) !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    margin: 0 0 0.4rem 0;
    position: relative;
    z-index: 1;
}
.ob-hero p {
    color: var(--mr-text-2);
    font-size: 0.98rem;
    margin: 0;
    position: relative;
    z-index: 1;
}

/* Activity/Transaction items */
.ob-activity-item {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
    padding: 0.8rem 1rem;
    margin-bottom: 0.4rem;
    transition: all var(--mr-t-fast) var(--mr-ease);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.ob-activity-item:hover {
    border-color: var(--mr-border-hover);
    background: var(--mr-surface-hover);
    transform: translateX(3px);
}

/* Status dot */
.ob-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 0.4rem;
}
.ob-dot.green  { background: var(--mr-income); box-shadow: 0 0 5px var(--mr-income-glow); }
.ob-dot.red    { background: var(--mr-expense); box-shadow: 0 0 5px var(--mr-expense-glow); }
.ob-dot.gold   { background: var(--mr-sapphire); box-shadow: 0 0 5px var(--mr-sapphire-glow); }
.ob-dot.blue   { background: var(--mr-info); box-shadow: 0 0 5px var(--mr-info-glow); }

/* Quick action grid */
.ob-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.6rem;
}
.ob-action-btn {
    background: var(--mr-surface);
    border: 1px solid var(--mr-border);
    border-radius: var(--mr-r-md);
    padding: 0.85rem;
    text-align: center;
    cursor: pointer;
    transition: all var(--mr-t-base) var(--mr-ease);
    color: var(--mr-text-2);
    font-size: 0.85rem;
    font-weight: 500;
}
.ob-action-btn:hover {
    background: rgba(79, 143, 234, 0.04);
    border-color: var(--mr-border-hover);
    color: var(--mr-sapphire-light);
    transform: translateY(-1px);
    box-shadow: var(--mr-shadow-sapphire);
}
.ob-action-btn .ob-action-icon {
    font-size: 1.5rem;
    display: block;
    margin-bottom: 0.3rem;
}

/* Section headers */
.ob-section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 1.75rem 0 0.85rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--mr-border);
}
.ob-section-header h3 {
    margin: 0 !important;
    color: var(--mr-text) !important;
    font-size: 1.1rem !important;
}
.ob-section-icon {
    font-size: 1.15rem;
}

/* Empty state */
.ob-empty {
    text-align: center;
    padding: 2.5rem 2rem;
    background: var(--mr-surface);
    border: 1px dashed rgba(79, 143, 234, 0.1);
    border-radius: var(--mr-r-xl);
}
.ob-empty-icon { font-size: 2.5rem; margin-bottom: 0.6rem; opacity: 0.4; }
.ob-empty-title { font-size: 1.1rem; font-weight: 600; color: var(--mr-text); margin-bottom: 0.2rem; }
.ob-empty-desc { color: var(--mr-text-3); font-size: 0.88rem; }

/* Badge */
.ob-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.15rem 0.55rem;
    border-radius: var(--mr-r-pill);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.ob-badge.income  { background: rgba(54,199,160,0.1); color: var(--mr-income); }
.ob-badge.expense { background: rgba(224,122,95,0.1); color: var(--mr-expense); }
.ob-badge.gold    { background: rgba(79,143,234,0.1); color: var(--mr-sapphire-light); }
.ob-badge.info    { background: rgba(122,175,255,0.1); color: var(--mr-info); }

/* Insight card */
.ob-insight {
    background: rgba(79, 143, 234, 0.04);
    border: 1px solid rgba(79, 143, 234, 0.1);
    border-radius: var(--mr-r-md);
    padding: 0.8rem 1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin: 0.6rem 0;
}
.ob-insight-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 0.05rem; }
.ob-insight-text { color: var(--mr-text-2); font-size: 0.88rem; line-height: 1.5; }
.ob-insight-text strong { color: var(--mr-sapphire-light); }

/* Responsive ------------------------------------------------------------- */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.75rem 0.85rem 2.5rem;
    }
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.25rem !important; }
    .ob-hero { padding: 1.25rem; border-radius: var(--mr-r-lg); }
    .ob-hero h1 { font-size: 1.5rem !important; }
    .ob-kpi-value { font-size: 1.4rem; }
    .ob-actions { grid-template-columns: repeat(2, 1fr); }
    .stButton > button { width: 100%; }
}

@media (max-width: 480px) {
    .main .block-container { padding: 0.5rem 0.6rem 2rem; }
    h1 { font-size: 1.3rem !important; }
    .ob-hero { padding: 1rem; }
    .ob-actions { grid-template-columns: 1fr; }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
    .stButton > button { min-height: 44px; }
    .stButton > button:hover { transform: none !important; }
    .ob-card:hover, .ob-kpi:hover { transform: none !important; }
    .stButton > button:active { transform: scale(0.97); opacity: 0.9; }
}

/* Staggered entrance animations */
@keyframes mr-stagger-in {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
.mr-stagger-1 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.05s both; }
.mr-stagger-2 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.12s both; }
.mr-stagger-3 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.19s both; }
.mr-stagger-4 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.26s both; }
.mr-stagger-5 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.33s both; }
.mr-stagger-6 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.40s both; }
.mr-stagger-7 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.47s both; }
.mr-stagger-8 { animation: mr-stagger-in 0.45s var(--mr-ease) 0.54s both; }

/* KPI trending arrows */
.ob-kpi-trend {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 0.25rem;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
}
.ob-kpi-trend.up {
    color: var(--mr-income);
    background: rgba(54, 199, 160, 0.1);
}
.ob-kpi-trend.down {
    color: var(--mr-expense);
    background: rgba(224, 122, 95, 0.1);
}
.ob-kpi-trend.flat {
    color: var(--mr-text-3);
    background: rgba(200, 205, 213, 0.06);
}
.ob-kpi-trend .arrow {
    font-size: 0.85rem;
    line-height: 1;
}

/* Quick action pulse on hover */
.ob-qa-row .stButton > button:hover {
    animation: mr-pulse-blue 1.2s ease-in-out infinite;
}

/* Form validation feedback */
.mr-field-error {
    color: var(--mr-expense, #e07a5f);
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.mr-field-error::before {
    content: '\2717';
    font-weight: 700;
}
.mr-field-ok {
    color: var(--mr-income, #36c7a0);
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 0.2rem;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.mr-field-ok::before {
    content: '\2713';
    font-weight: 700;
}
@keyframes mr-shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-4px); }
    40% { transform: translateX(4px); }
    60% { transform: translateX(-3px); }
    80% { transform: translateX(2px); }
}
.mr-shake {
    animation: mr-shake 0.4s ease-in-out;
}

/* Chart drill-down filter banner */
.mr-chart-filter {
    background: rgba(79,143,234,0.08);
    border: 1px solid rgba(79,143,234,0.22);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    margin: 0.75rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    animation: mr-stagger-in 0.3s var(--mr-ease) both;
}
.mr-chart-filter .filter-label {
    color: #7aafff;
    font-weight: 600;
    font-size: 0.9rem;
}
.mr-chart-filter .filter-value {
    background: rgba(79,143,234,0.15);
    color: #c8cdd5;
    padding: 0.25rem 0.7rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.88rem;
}

/* Tab content fade transition */
@keyframes mr-tab-fade {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
div[data-testid="stTabs"] > div[role="tabpanel"] {
    animation: mr-tab-fade 0.35s var(--mr-ease) both;
}

/* Settings search bar */
.mr-settings-search {
    background: var(--mr-surface-alt, #181d28);
    border: 1px solid rgba(79,143,234,0.15);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: border-color 0.25s ease;
}
.mr-settings-search:focus-within {
    border-color: rgba(79,143,234,0.4);
}
.mr-settings-search .search-icon {
    color: rgba(200,205,213,0.38);
    font-size: 1.1rem;
}

/* Unsaved changes indicator */
.mr-unsaved-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #e5b567;
    margin-left: 6px;
    animation: mr-pulse-dot 1.5s ease-in-out infinite;
}
@keyframes mr-pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* Reset confirmation banner */
.mr-reset-banner {
    background: rgba(224,122,95,0.08);
    border: 1px solid rgba(224,122,95,0.25);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}
.mr-reset-banner strong { color: #e07a5f; }

/* Category tag pill */
.mr-cat-pill {
    display: inline-block;
    background: rgba(79,143,234,0.12);
    color: #7aafff;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin: 0.2rem;
    transition: all 0.2s ease;
}
.mr-cat-pill:hover {
    background: rgba(79,143,234,0.22);
}
.mr-cat-pill.income { background: rgba(54,199,160,0.12); color: #36c7a0; }
.mr-cat-pill.expense { background: rgba(224,122,95,0.12); color: #e07a5f; }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Print */
@media print {
    .stApp { background: white; color: black; }
    section[data-testid="stSidebar"] { display: none; }
    .ob-card, .ob-kpi, .ob-hero { background: white; border: 1px solid #ccc; box-shadow: none; }
}

</style>
"""
