"""
CareerIQ – Shared UI Components
Inject consistent CSS + reusable components across all pages.
"""

import streamlit as st


# ── Master CSS ───────────────────────────────────────────────────────────────
CAREERIQ_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
  --cyan:      #00D4FF;
  --cyan-dim:  #00A3CC;
  --green:     #00FF94;
  --amber:     #FFB800;
  --red:       #FF4757;
  --bg:        #0A0E1A;
  --surface:   #111827;
  --surface2:  #1A2235;
  --border:    #1E2D45;
  --text:      #E2E8F0;
  --muted:     #64748B;
}

/* ── Reset & Base ── */
html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text) !important;
}

/* ── Hide Streamlit chrome completely ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Nuke the sidebar toggle arrow entirely ── */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] > div > div > div > button,
.st-emotion-cache-1cypcdb, .st-emotion-cache-h5rgaw,
.eyeqlp53, .e1fqkh3o3 { display: none !important; }

/* ── Top navbar ── */
.careeriq-navbar {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 1.5rem;
  margin: -1rem -1rem 1.5rem -1rem;
  position: sticky;
  top: 0;
  z-index: 999;
}
.careeriq-navbar-brand {
  font-family: 'Space Mono', monospace;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--cyan);
  padding: 0.85rem 1.5rem 0.85rem 0;
  border-right: 1px solid var(--border);
  margin-right: 0.5rem;
  white-space: nowrap;
  text-decoration: none;
}
.careeriq-navbar a {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
  padding: 0.85rem 1rem;
  text-decoration: none;
  transition: color 0.15s;
  white-space: nowrap;
}
.careeriq-navbar a:hover { color: var(--text); }
.careeriq-navbar a.active { color: var(--cyan); border-bottom: 2px solid var(--cyan); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSidebarNavItems"] a {
  border-radius: 8px !important;
  margin: 2px 0 !important;
  transition: all 0.2s !important;
}
[data-testid="stSidebarNavItems"] a:hover {
  background: var(--surface2) !important;
  padding-left: 12px !important;
}

/* ── Page title override ── */
h1 {
  font-family: 'Space Mono', monospace !important;
  font-size: 1.8rem !important;
  font-weight: 700 !important;
  color: var(--cyan) !important;
  letter-spacing: -0.5px !important;
  margin-bottom: 0.2rem !important;
}
h2 {
  font-family: 'Space Mono', monospace !important;
  font-size: 1.1rem !important;
  color: var(--text) !important;
  font-weight: 700 !important;
  margin-top: 1.5rem !important;
}
h3 {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 1rem !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 1rem 1.25rem !important;
  transition: border-color 0.2s !important;
}
[data-testid="stMetric"]:hover {
  border-color: var(--cyan-dim) !important;
}
[data-testid="stMetricLabel"] {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.75rem !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Space Mono', monospace !important;
  font-size: 1.8rem !important;
  color: var(--cyan) !important;
  font-weight: 700 !important;
}

/* ── Buttons ── */
.stButton > button {
  background: transparent !important;
  border: 1.5px solid var(--cyan) !important;
  color: var(--cyan) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.8rem !important;
  letter-spacing: 1px !important;
  border-radius: 6px !important;
  padding: 0.5rem 1.5rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: var(--cyan) !important;
  color: var(--bg) !important;
}
.stButton > button[kind="primary"] {
  background: var(--cyan) !important;
  color: var(--bg) !important;
  font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--cyan-dim) !important;
  border-color: var(--cyan-dim) !important;
}

/* ── Inputs & selects ── */
[data-testid="stMultiSelect"] > div,
[data-testid="stSelectbox"] > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
[data-testid="stTextInput"] > div > div {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
  border-radius: 8px !important;
  border: none !important;
  font-family: 'DM Sans', sans-serif !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}

/* ── Divider ── */
hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1.5rem 0 !important;
}

/* ── Code blocks ── */
[data-testid="stCode"] {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.82rem !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
  background: var(--cyan) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.5px !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: var(--cyan) !important;
  border-bottom-color: var(--cyan) !important;
}

/* ── Sidebar section label ── */
.sidebar-section-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 2px;
  color: var(--muted);
  text-transform: uppercase;
  padding: 0.5rem 0 0.25rem;
}

/* ── Custom stat pill ── */
.stat-pill {
  display: inline-block;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 14px;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  color: var(--cyan);
  margin: 3px;
}

/* ── Page subtitle ── */
.page-subtitle {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  color: var(--muted);
  margin-bottom: 1.5rem;
  letter-spacing: 0.2px;
}

/* ── Badge ── */
.badge-fresh {
  background: rgba(0,255,148,0.1);
  color: #00FF94;
  border: 1px solid rgba(0,255,148,0.3);
  border-radius: 4px;
  padding: 2px 10px;
  font-family: 'Space Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 1px;
}
.badge-stale {
  background: rgba(255,184,0,0.1);
  color: #FFB800;
  border: 1px solid rgba(255,184,0,0.3);
  border-radius: 4px;
  padding: 2px 10px;
  font-family: 'Space Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 1px;
}

/* ── Hero banner ── */
.hero-banner {
  background: linear-gradient(135deg, #0D1B2E 0%, #111827 60%, #0D2040 100%);
  border: 1px solid var(--border);
  border-left: 3px solid var(--cyan);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
}
.hero-title {
  font-family: 'Space Mono', monospace;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--cyan);
  margin: 0 0 0.3rem 0;
}
.hero-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
}

/* ── Insight card ── */
.insight-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin: 0.5rem 0;
}
.insight-card-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 0.3rem;
}
.insight-card-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
}

/* ── Market status bar ── */
.market-strong  { color: #00FF94; font-family: 'Space Mono', monospace; font-size: 0.85rem; }
.market-moderate { color: #FFB800; font-family: 'Space Mono', monospace; font-size: 0.85rem; }
.market-niche   { color: #FF4757; font-family: 'Space Mono', monospace; font-size: 0.85rem; }
</style>
"""


def inject_css():
    """Call this at the top of every page."""
    st.markdown(CAREERIQ_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    """Consistent page header with icon, title and subtitle."""
    inject_css()
    st.markdown(
        f"""
        <div class="hero-banner">
          <div class="hero-title">{icon} {title}</div>
          {'<div class="hero-sub">' + subtitle + '</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_logo():
    """No-op — kept for import compatibility."""
    pass


def navbar(active: str = ""):
    """
    Render a sticky top navbar. Call at the top of every page.
    active = one of: Dashboard, Skills, Explorer, WhatsApp, Refresh
    """
    pages = [
        ("📊", "Dashboard",  "1_Dashboard"),
        ("🔧", "Skills",     "2_Skills_Insights"),
        ("📂", "Explorer",   "3_Data_Explorer"),
        ("📲", "WhatsApp",   "4_WhatsApp_Insight"),
        ("🔄", "Refresh",    "6_Data_Refresh"),
        ("ℹ️",  "About",     "5_About"),
    ]
    links = ""
    for icon, label, _ in pages:
        cls = "active" if label == active else ""
        links += f'<a class="{cls}" href="#">{icon} {label}</a>'

    st.markdown(
        f"""<div class="careeriq-navbar">
          <span class="careeriq-navbar-brand">◈ CareerIQ</span>
          {links}
        </div>""",
        unsafe_allow_html=True,
    )


def metric_row(metrics: list[dict]):
    """
    Render a row of metrics.
    metrics = [{"label": "Total Jobs", "value": 1234, "delta": "+12"}, ...]
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        col.metric(
            label=m["label"],
            value=m["value"],
            delta=m.get("delta"),
        )


def freshness_badge(is_stale: bool, age_hours=None, last_scraped=None):
    """Show a data freshness indicator."""
    if last_scraped:
        if is_stale:
            age_str = f"{age_hours}h ago" if age_hours else ""
            st.markdown(
                f'<span class="badge-stale">⚠ DATA {age_str} — STALE</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<span class="badge-fresh">● LIVE — {age_hours}h ago</span>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<span class="badge-stale">● BUNDLED DATASET</span>',
            unsafe_allow_html=True,
        )


def plotly_theme() -> dict:
    """Return a consistent Plotly layout dict for all charts."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="DM Sans, sans-serif", color="#E2E8F0", size=12),
        title_font=dict(family="Space Mono, monospace", color="#00D4FF", size=14),
        xaxis=dict(
            gridcolor="#1E2D45",
            linecolor="#1E2D45",
            tickfont=dict(color="#64748B"),
        ),
        yaxis=dict(
            gridcolor="#1E2D45",
            linecolor="#1E2D45",
            tickfont=dict(color="#64748B"),
        ),
        colorway=["#00D4FF", "#00FF94", "#FFB800", "#FF6B9D", "#A78BFA", "#FB923C"],
        margin=dict(l=10, r=10, t=40, b=10),
    )
