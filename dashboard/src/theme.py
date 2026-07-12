"""Shared visual theme: one CSS injection called once from app.py.

Color/typography choices live here so every page inherits them consistently
instead of hand-rolling inline styles. Semantic score colors stay in
formatting.py (score_color/score_badge) — this file only styles the chrome
around them (cards, headers, spacing, sidebar).
"""
import streamlit as st

PRIMARY = "#1F6F78"       # deep teal — primary actions, active nav, accents
PRIMARY_DARK = "#153F45"
INK = "#1C2B2E"            # body text
MUTED = "#5B6B6E"          # secondary text
SURFACE = "#F4F7F7"        # card/section backgrounds
BORDER = "#E1E8E8"
CANVAS = "#FFFFFF"


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* ── Headings ─────────────────────────────────────────────── */
        h1 {{
            font-weight: 700 !important;
            color: {PRIMARY_DARK} !important;
            letter-spacing: -0.02em;
        }}
        h2, h3 {{
            font-weight: 600 !important;
            color: {INK} !important;
        }}

        /* ── Sidebar ──────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background-color: {PRIMARY_DARK};
            border-right: none;
        }}
        section[data-testid="stSidebar"] * {{
            color: #EAF3F3 !important;
        }}
        section[data-testid="stSidebar"] .stButton button {{
            background-color: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
            color: #EAF3F3 !important;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background-color: rgba(255,255,255,0.16);
            border-color: rgba(255,255,255,0.3);
        }}
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background-color: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.25);
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.15);
        }}

        /* ── Metric cards ─────────────────────────────────────────── */
        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 14px 16px 10px 16px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {MUTED} !important;
        }}
        div[data-testid="stMetricValue"] {{
            color: {PRIMARY_DARK} !important;
        }}

        /* ── Bordered containers (st.container(border=True)) ────────── */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 12px !important;
        }}

        /* ── Buttons ──────────────────────────────────────────────── */
        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {PRIMARY};
            border-color: {PRIMARY};
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {PRIMARY_DARK};
            border-color: {PRIMARY_DARK};
        }}

        /* ── Tabs ─────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab"] {{
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            color: {PRIMARY} !important;
        }}

        /* ── Progress bars ───────────────────────────────────────── */
        div[data-testid="stProgress"] > div > div {{
            background-color: {PRIMARY};
        }}

        /* ── Reduce default Streamlit chrome noise ───────────────── */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        /* ── Custom "banner" card used for university context ───── */
        .cl-banner {{
            background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
            color: white;
            border-radius: 12px;
            padding: 16px 22px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .cl-banner .cl-banner-label {{
            font-size: 0.78em;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.8;
        }}
        .cl-banner .cl-banner-value {{
            font-size: 1.3em;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
