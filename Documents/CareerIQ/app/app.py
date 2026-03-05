import streamlit as st
import sys, os, time, pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotly.express as px
from utils.data_loader import load_data, force_reload, get_data_stats, should_auto_refresh
from utils.data_processing import preprocess_data
from utils.scraper import run_scrape_pipeline, SCRAPE_QUERIES, get_api_key, test_api_connection
from utils.ui_components import inject_css, page_header, freshness_badge, plotly_theme

try:
    from utils.whatsapp_utils import send_whatsapp_message
    WHATSAPP_AVAILABLE = True
except Exception:
    try:
        from whatsapp_utils import send_whatsapp_message
        WHATSAPP_AVAILABLE = True
    except Exception:
        WHATSAPP_AVAILABLE = False

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPE_LOG    = os.path.join(BASE_DIR, "Data", "Processed", "scrape_log.csv")

st.set_page_config(page_title="CareerIQ", page_icon="🎯", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()

# ── Nuke sidebar completely ───────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] { display: none !important; }
</style>""", unsafe_allow_html=True)

# ── Dropdown nav ──────────────────────────────────────────────────────────────
PAGES = ["🏠 Home","📊 Dashboard","🔧 Skills","📂 Data Explorer",
         "📲 WhatsApp","ℹ️ About","🔄 Data Refresh"]

if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

nav_col, _ = st.columns([2, 5])
with nav_col:
    selected = st.selectbox("nav", PAGES,
        index=PAGES.index(st.session_state.page),
        label_visibility="collapsed", key="nav_dropdown")
st.session_state.page = selected
page = selected

# ═══════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    if "auto_refresh_done" not in st.session_state:
        st.session_state.auto_refresh_done = False
    if should_auto_refresh() and not st.session_state.auto_refresh_done:
        st.session_state.auto_refresh_done = True
        with st.spinner("Fetching latest job data..."):
            run_scrape_pipeline(pages_per_query=1)
            force_reload()
        st.toast("Data refreshed", icon="✅")

    df    = load_data()
    df    = preprocess_data(df)
    stats = get_data_stats()

    col_hero, col_badge = st.columns([5, 1])
    with col_hero:
        st.markdown("""<div style="padding:2rem 0 0.5rem;">
          <div style="font-family:'Space Mono',monospace;font-size:0.7rem;color:#64748B;
                      letter-spacing:3px;text-transform:uppercase;margin-bottom:0.5rem;">
            ◈ AI-POWERED CAREER INTELLIGENCE</div>
          <div style="font-family:'Space Mono',monospace;font-size:2.2rem;
                      font-weight:700;color:#00D4FF;line-height:1.2;margin-bottom:0.5rem;">
            CareerIQ</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:1rem;
                      color:#94A3B8;max-width:560px;line-height:1.6;">
            Real-time job market analytics for Data, AI, ML &amp; Cloud roles across India.
            Understand hiring trends. Identify skill gaps. Navigate your career with data.
          </div></div>""", unsafe_allow_html=True)
    with col_badge:
        st.markdown("<div style='padding-top:2.5rem;'>", unsafe_allow_html=True)
        freshness_badge(stats.get("is_stale",True), stats.get("age_hours"), stats.get("last_scraped"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Jobs",     f"{len(df):,}")
    k2.metric("Unique Roles",   df["job_group"].nunique())
    k3.metric("Cities Covered", df["clean_location"].nunique())
    k4.metric("Data Sources",   df["source_dataset"].nunique() if "source_dataset" in df.columns else "2")
    st.divider()

    st.markdown("""<div style="font-family:'Space Mono',monospace;font-size:0.7rem;
        color:#64748B;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;">
        MARKET SNAPSHOT</div>""", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        rc = df["job_group"].value_counts().reset_index(); rc.columns=["Role","Jobs"]
        fig = px.bar(rc, x="Jobs", y="Role", orientation="h", title="Top Hiring Roles",
            color="Jobs", color_continuous_scale=[[0,"#1E2D45"],[1,"#00D4FF"]])
        fig.update_layout(**plotly_theme(), showlegend=False, coloraxis_showscale=False, height=300)
        fig.update_traces(texttemplate="%{x}", textposition="outside", textfont_color="#94A3B8")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        lc = df["clean_location"].value_counts().head(6).reset_index(); lc.columns=["City","Jobs"]
        fig2 = px.pie(lc, names="City", values="Jobs", title="Jobs by City", hole=0.55,
            color_discrete_sequence=["#00D4FF","#00FF94","#FFB800","#FF6B9D","#A78BFA","#FB923C"])
        fig2.update_layout(**plotly_theme(), height=300)
        fig2.update_traces(textfont_color="#E2E8F0")
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.75rem;
        color:#334155;text-align:center;padding:2rem 0 0.5rem;">
        ◈ CareerIQ — Job Market Intelligence System · 2026</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    df = load_data(); df = preprocess_data(df)
    page_header("📊","Market Dashboard","Hiring trends across Data · AI · ML · Cloud roles")

    with st.expander("🔽  Filters", expanded=False):
        fc1,fc2,fc3 = st.columns(3)
        job_filter = fc1.multiselect("Job Role", sorted(df["job_group"].dropna().unique()),      placeholder="All roles",  key="d_roles")
        loc_filter = fc2.multiselect("Location", sorted(df["clean_location"].dropna().unique()), placeholder="All cities", key="d_locs")
        compact    = fc3.toggle("Compact charts", value=False, key="d_compact")

    fdf = df.copy()
    if job_filter: fdf = fdf[fdf["job_group"].isin(job_filter)]
    if loc_filter: fdf = fdf[fdf["clean_location"].isin(loc_filter)]

    mr = len(fdf)/len(df) if len(df) else 0
    badge = '<span class="market-strong">● STRONG</span>' if mr>0.4 else \
            '<span class="market-moderate">◐ MODERATE</span>' if mr>0.2 else \
            '<span class="market-niche">○ NICHE</span>'
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Jobs Found",f"{len(fdf):,}"); k2.metric("Unique Roles",fdf["job_group"].nunique())
    k3.metric("Active Cities",fdf["clean_location"].nunique()); k4.metric("vs Total Market",f"{mr:.0%}")
    st.markdown(f"<div style='padding:0.25rem 0 1rem;'>{badge}</div>", unsafe_allow_html=True)
    st.divider()

    h = 320 if compact else 420
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Job Demand by Role")
        rc = fdf["job_group"].value_counts().reset_index(); rc.columns=["Role","Jobs"]
        fig = px.bar(rc, x="Role", y="Jobs", text="Jobs", color="Jobs",
            color_continuous_scale=[[0,"#1E2D45"],[1,"#00D4FF"]])
        fig.update_layout(**plotly_theme(), coloraxis_showscale=False, height=h)
        fig.update_traces(textfont_color="#94A3B8", marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("#### Jobs by Location")
        lc = fdf["clean_location"].value_counts().head(6).reset_index(); lc.columns=["City","Jobs"]
        fig2 = px.pie(lc, names="City", values="Jobs", hole=0.52,
            color_discrete_sequence=["#00D4FF","#00FF94","#FFB800","#FF6B9D","#A78BFA","#FB923C"])
        fig2.update_layout(**plotly_theme(), height=h)
        fig2.update_traces(textfont_color="#E2E8F0", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    st.markdown("#### Experience Demand Breakdown")
    ec = fdf["experience"].value_counts().reindex(["0-1","1-2","2-5","5-10","10+"],fill_value=0).reset_index()
    ec.columns=["Experience","Jobs"]; ec["pct"]=(ec["Jobs"]/ec["Jobs"].sum()*100).round(1)
    fig3 = px.bar(ec, x="Jobs", y="Experience", orientation="h", text="pct", color="Jobs",
        color_continuous_scale=[[0,"#1E2D45"],[0.5,"#0066CC"],[1,"#00D4FF"]])
    fig3.update_layout(**plotly_theme(), coloraxis_showscale=False, height=280 if compact else 320)
    fig3.update_traces(texttemplate="%{text}%", textposition="outside", textfont_color="#94A3B8")
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    st.markdown("#### Career Insight")
    if not fdf.empty:
        c1,c2,c3 = st.columns(3)
        for col,label,value,sub in [
            (c1,"Most In-Demand Role",   fdf["job_group"].value_counts().idxmax(),         f"{int(fdf['job_group'].value_counts().max())} openings"),
            (c2,"Top Hiring City",       fdf["clean_location"].value_counts().idxmax(),    ""),
            (c3,"Experience Sweet Spot", f"{fdf['experience'].value_counts().idxmax()} yrs","highest demand band"),
        ]:
            col.markdown(f"""<div class="insight-card">
                <div class="insight-card-label">{label}</div>
                <div class="insight-card-value">{value}</div>
                {'<div style="font-size:0.75rem;color:#64748B;margin-top:4px;">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)
    else:
        st.warning("No data for selected filters.")


# ═══════════════════════════════════════════════════════════════════════
# SKILLS
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔧 Skills":
    df = load_data(); df = preprocess_data(df)
    page_header("🔧","Skills Intelligence","Discover the most in-demand skills by role")

    with st.expander("🔽  Filters", expanded=False):
        fc1,fc2 = st.columns([3,1])
        role_filter = fc1.selectbox("Select Role",["All Roles"]+sorted(df["job_group"].dropna().unique()), key="sk_role")
        top_n       = fc2.slider("Top N", 5, 20, 10, key="sk_topn")

    fdf = df.copy()
    if role_filter != "All Roles": fdf = fdf[fdf["job_group"]==role_filter]

    top_skills, skills_series = None, None
    if "skills_extracted" in fdf.columns:
        skills_series = fdf["skills_extracted"].dropna().str.lower().str.split(",").explode().str.strip()
        skills_series = skills_series[skills_series!=""]
        top_skills = skills_series.value_counts().head(top_n).reset_index()
        top_skills.columns=["Skill","Count"]; top_skills["Skill"]=top_skills["Skill"].str.title()

    k1,k2,k3 = st.columns(3)
    k1.metric("Jobs Analysed",f"{len(fdf):,}")
    k2.metric("Roles with Skill Data",f"{df[df['skills_extracted'].notna()]['job_group'].nunique() if 'skills_extracted' in df.columns else 0} / {df['job_group'].nunique()}")
    k3.metric("Unique Skills",f"{skills_series.nunique():,}" if skills_series is not None else "—")
    st.divider()

    if top_skills is not None and not top_skills.empty:
        c1,c2 = st.columns([3,2])
        with c1:
            st.markdown(f"#### Top {top_n} Skills — {role_filter}")
            fig = px.bar(top_skills.sort_values("Count"), x="Count", y="Skill",
                orientation="h", text="Count", color="Count",
                color_continuous_scale=[[0,"#0D2040"],[0.5,"#005580"],[1,"#00D4FF"]])
            fig.update_layout(**plotly_theme(), coloraxis_showscale=False, height=max(320,top_n*36))
            fig.update_traces(textposition="outside", textfont_color="#94A3B8", marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("#### Skill Share")
            fig2 = px.pie(top_skills.head(8), names="Skill", values="Count", hole=0.5,
                color_discrete_sequence=["#00D4FF","#00FF94","#FFB800","#FF6B9D","#A78BFA","#FB923C","#34D399","#60A5FA"])
            fig2.update_layout(**plotly_theme(), height=max(320,top_n*36))
            fig2.update_traces(textfont_color="#E2E8F0", textinfo="percent")
            st.plotly_chart(fig2, use_container_width=True)
        st.divider()
        top3   = top_skills.head(3)["Skill"].tolist()
        detail = f'Most frequent in <strong style="color:#E2E8F0;">{role_filter}</strong> listings.' \
                 if role_filter!="All Roles" else "Select a specific role above for targeted recommendations."
        st.markdown(f"""<div class="insight-card">
            <div class="insight-card-label">Focus Skills for {role_filter}</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
              {"".join(f'<span class="stat-pill">{s}</span>' for s in top3)}
            </div>
            <div style="font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#94A3B8;margin-top:10px;line-height:1.6;">{detail}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning("No skill data available for the selected filter.")


# ═══════════════════════════════════════════════════════════════════════
# DATA EXPLORER
# ═══════════════════════════════════════════════════════════════════════
elif page == "📂 Data Explorer":
    df = load_data(); df = preprocess_data(df)
    page_header("📂","Data Explorer","Browse, filter and export structured job market data")

    allowed = {"Job Title":"job_title","Role":"job_group","City":"clean_location",
               "Experience":"experience","Skills":"skills_extracted"}

    with st.expander("🔽  Filters & Columns", expanded=False):
        fc1,fc2,fc3 = st.columns(3)
        role_filter = fc1.multiselect("Role",       sorted(df["job_group"].dropna().unique()),      placeholder="All roles",  key="ex_roles")
        loc_filter  = fc2.multiselect("City",       sorted(df["clean_location"].dropna().unique()), placeholder="All cities", key="ex_locs")
        exp_filter  = fc3.multiselect("Experience", ["0-1","1-2","2-5","5-10","10+"],               placeholder="All levels", key="ex_exp")
        sel_labels  = st.multiselect("Columns to show", list(allowed.keys()),
            default=["Job Title","Role","City","Experience"], key="ex_cols")

    fdf = df.copy()
    if role_filter: fdf = fdf[fdf["job_group"].isin(role_filter)]
    if loc_filter:  fdf = fdf[fdf["clean_location"].isin(loc_filter)]
    if exp_filter:  fdf = fdf[fdf["experience"].isin(exp_filter)]

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Matching Records",f"{len(fdf):,}"); k2.metric("Unique Roles",fdf["job_group"].nunique())
    k3.metric("Cities",fdf["clean_location"].nunique()); k4.metric("Filter Rate",f"{len(fdf)/len(df):.0%}" if len(df) else "—")
    st.divider()

    sel_cols   = [allowed[l] for l in sel_labels] if sel_labels else list(allowed.values())
    display_df = fdf[sel_cols].reset_index(drop=True)
    st.markdown(f'<div class="page-subtitle">Showing <strong style="color:#00D4FF;">{min(200,len(display_df))}'
                f'</strong> of <strong style="color:#E2E8F0;">{len(display_df):,}</strong> records</div>',
                unsafe_allow_html=True)
    st.dataframe(display_df.head(200), use_container_width=True, height=420, hide_index=True,
        column_config={
            "job_title":        st.column_config.TextColumn("Job Title",  width="large"),
            "job_group":        st.column_config.TextColumn("Role",       width="medium"),
            "clean_location":   st.column_config.TextColumn("City",       width="medium"),
            "experience":       st.column_config.TextColumn("Experience", width="small"),
            "skills_extracted": st.column_config.TextColumn("Skills",     width="large"),
        })
    st.divider()
    c_dl,c_info = st.columns([2,3])
    with c_dl:
        st.markdown("#### Export")
        st.download_button("⬇  Download as CSV", data=display_df.to_csv(index=False),
            file_name="careeriq_export.csv", mime="text/csv", use_container_width=True)
    with c_info:
        st.markdown("#### Dataset Info")
        st.markdown(f"""<div class="insight-card">
          <div style="display:flex;gap:2rem;flex-wrap:wrap;">
            <div><div class="insight-card-label">Total</div><div class="insight-card-value">{len(df):,}</div></div>
            <div><div class="insight-card-label">Filtered</div><div class="insight-card-value">{len(fdf):,}</div></div>
            <div><div class="insight-card-label">Columns</div><div class="insight-card-value">{len(sel_cols)}</div></div>
          </div></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# WHATSAPP
# ═══════════════════════════════════════════════════════════════════════
elif page == "📲 WhatsApp":
    df = load_data(); df = preprocess_data(df)
    page_header("📲","WhatsApp Market Insight","Generate and share hiring intelligence reports")
    st.markdown("""<div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
               border-radius:8px;padding:0.75rem 1rem;margin-bottom:1rem;">
      <span style="font-family:'Space Mono',monospace;font-size:0.7rem;color:#00D4FF;letter-spacing:1px;">DEMO MODE</span>
      <span style="font-family:'DM Sans',sans-serif;font-size:0.85rem;color:#94A3B8;margin-left:0.75rem;">
        WhatsApp delivery works to the registered demo number via Twilio Sandbox.</span>
    </div>""", unsafe_allow_html=True)

    with st.expander("🔽  Filters", expanded=False):
        fc1,fc2 = st.columns(2)
        role_filter = fc1.multiselect("Role", sorted(df["job_group"].dropna().unique()),      placeholder="All", key="wa_roles")
        loc_filter  = fc2.multiselect("City", sorted(df["clean_location"].dropna().unique()), placeholder="All", key="wa_locs")

    fdf = df.copy()
    if role_filter: fdf = fdf[fdf["job_group"].isin(role_filter)]
    if loc_filter:  fdf = fdf[fdf["clean_location"].isin(loc_filter)]

    if fdf.empty:
        st.warning("No data for selected filters.")
    else:
        top_roles   = fdf["job_group"].value_counts().head(3)
        top_cities  = fdf["clean_location"].value_counts().head(3)
        exp_dist    = fdf["experience"].value_counts(normalize=True)*100
        top_exp     = exp_dist.idxmax(); top_exp_pct = round(exp_dist.max())
        role_lines  = "\n".join(f"  {i+1}. {r} — {c} jobs"     for i,(r,c) in enumerate(top_roles.items()))
        city_lines  = "\n".join(f"  {i+1}. {c} — {n} openings" for i,(c,n) in enumerate(top_cities.items()))
        message = f"""◈ CareerIQ — Market Intelligence Report

📌 Jobs Analysed: {len(fdf):,}

🔥 Top Hiring Roles:
{role_lines}

🌍 Top Hiring Cities:
{city_lines}

🎯 Experience Sweet Spot:
  {top_exp} years  ({top_exp_pct}% of roles)

💡 Insight:
  Target {top_roles.index[0]} roles in {top_cities.index[0]}
  if you have {top_exp} yrs experience.

Stay skilled. Stay relevant.
——
Powered by CareerIQ"""

        cp,cs = st.columns([3,2])
        with cp:
            st.markdown("#### Message Preview")
            st.markdown(f"""<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
                            padding:1.25rem 1.5rem;font-family:'Space Mono',monospace;
                            font-size:0.78rem;color:#E2E8F0;white-space:pre-wrap;line-height:1.8;">
{message}</div>""", unsafe_allow_html=True)
        with cs:
            st.markdown("#### Send Report")
            k1,k2 = st.columns(2)
            k1.metric("Jobs",f"{len(fdf):,}"); k2.metric("Top Role",top_roles.index[0].split()[0])
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            if st.button("📲  Send to WhatsApp", type="primary", use_container_width=True):
                if WHATSAPP_AVAILABLE:
                    try: send_whatsapp_message(message); st.success("✅ Sent!")
                    except Exception as e: st.error(f"Send failed: {e}")
                else: st.error("whatsapp_utils not loaded.")
            st.markdown("""<div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;
                           color:#475569;margin-top:0.75rem;line-height:1.5;">
              Delivery via Twilio Sandbox.<br>Only the registered demo number receives messages.</div>""",
                        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# ABOUT
# ═══════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    page_header("◈","About CareerIQ","Data-driven job market intelligence for India's tech sector")
    c1,c2 = st.columns([3,2])
    with c1:
        for label, body in [
            ("What is CareerIQ?","CareerIQ transforms raw job listing data into structured career intelligence. It helps students understand hiring demand, professionals identify skill gaps, and researchers observe market trends — all from a single unified platform."),
            ("Problem It Solves","Job seekers rely on scattered portals with no structured insight. CareerIQ converts raw listings into analytics — role demand, skill frequency, experience distribution, and location-based hiring intensity."),
        ]:
            st.markdown(f"""<div class="insight-card" style="margin-bottom:1rem;">
              <div class="insight-card-label">{label}</div>
              <div style="font-family:'DM Sans',sans-serif;font-size:0.9rem;color:#94A3B8;line-height:1.8;margin-top:8px;">{body}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="insight-card"><div class="insight-card-label">Tech Stack</div><div style="margin-top:10px;">', unsafe_allow_html=True)
        for tech,desc in [("Python","Core language"),("Streamlit","Web framework"),
                          ("Pandas","Data processing"),("Plotly","Visualisations"),
                          ("JSearch API","Live job data"),("Twilio API","WhatsApp")]:
            st.markdown(f"""<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1E2D45;">
              <span style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#00D4FF;">{tech}</span>
              <span style="font-family:'DM Sans',sans-serif;font-size:0.75rem;color:#64748B;">{desc}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("#### System Architecture")
    for col,(num,title,desc) in zip(st.columns(4),[
        ("01","Data Layer",       "LinkedIn jobs via JSearch API · CSV pipeline"),
        ("02","Processing Layer", "Skill extraction · Role mapping · Location cleanup"),
        ("03","Analytics Layer",  "Dashboard · Skills intelligence · Trend analysis"),
        ("04","Comms Layer",      "WhatsApp automation via Twilio sandbox"),
    ]):
        col.markdown(f"""<div class="insight-card" style="height:140px;">
          <div style="font-family:'Space Mono',monospace;font-size:1.4rem;color:#1E2D45;font-weight:700;">{num}</div>
          <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#00D4FF;margin:4px 0;">{title}</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;color:#64748B;line-height:1.6;">{desc}</div>
        </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("#### Future Scope")
    for col,(icon,title,desc) in zip(st.columns(3),[
        ("🔐","User Auth","Personalised dashboards per user profile"),
        ("🤖","AI Recommendations","Resume ↔ skill gap analysis with LLMs"),
        ("☁️","SaaS Deployment","Scalable cloud deployment with live APIs"),
    ]):
        col.markdown(f"""<div class="insight-card">
          <div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>
          <div style="font-family:'Space Mono',monospace;font-size:0.78rem;color:#E2E8F0;font-weight:700;">{title}</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;color:#64748B;margin-top:4px;line-height:1.5;">{desc}</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# DATA REFRESH
# ═══════════════════════════════════════════════════════════════════════
elif page == "🔄 Data Refresh":
    page_header("🔄","Live Data Refresh","Fetch latest LinkedIn job listings via JSearch API")
    api_key = get_api_key()

    if not api_key:
        st.markdown("""<div style="background:rgba(255,184,0,0.08);border:1px solid rgba(255,184,0,0.3);
                       border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;">
          <div style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#FFB800;
                      letter-spacing:1px;margin-bottom:0.75rem;">⚠ RAPIDAPI KEY REQUIRED</div>
          <div style="font-family:'DM Sans',sans-serif;font-size:0.88rem;color:#94A3B8;line-height:2;">
            <strong style="color:#E2E8F0;">Step 1</strong> →
            <a href="https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch" target="_blank"
               style="color:#00D4FF;">rapidapi.com → JSearch</a> — sign up, subscribe to Basic (free)<br>
            <strong style="color:#E2E8F0;">Step 2</strong> → Copy your X-RapidAPI-Key<br>
            <strong style="color:#E2E8F0;">Step 3</strong> → Open
            <code style="background:#1A2235;padding:2px 8px;border-radius:4px;color:#00FF94;">
            app/.streamlit/secrets.toml</code> and add:<br>
            <code style="background:#0D2040;display:block;padding:10px 14px;border-radius:6px;
                          margin-top:6px;color:#00FF94;">RAPIDAPI_KEY = "paste_your_key_here"</code>
          </div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-fresh">✅ API KEY CONFIGURED</span>', unsafe_allow_html=True)
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    st.markdown("#### Current Dataset")
    stats = get_data_stats()
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Records", f"{stats['total_records']:,}" if stats["total_records"] else "0")
    k2.metric("Data Age",      f"{stats['age_hours']}h"      if stats.get("age_hours")   else "Unknown")
    k3.metric("Last Fetched",  stats["last_scraped"].split(" ")[0] if stats.get("last_scraped") else "Never")
    k4.metric("Status",        "🔴 Stale" if stats["is_stale"] else "🟢 Fresh")
    st.divider()

    st.markdown("#### Manual Fetch")
    with st.expander("⚙️ Settings", expanded=False):
        n_pages   = st.slider("Pages per query", 1, 5, 2, help="~10 jobs per page")
        total_req = n_pages * len(SCRAPE_QUERIES)
        st.caption(f"Uses ~{total_req} API requests · Free plan: 200 req/month")
        cols = st.columns(3)
        for i,q in enumerate(SCRAPE_QUERIES):
            cols[i%3].markdown(f'<span class="stat-pill">{q["keyword"]}</span>', unsafe_allow_html=True)

    if st.button("🚀  Fetch Latest Jobs", type="primary", use_container_width=True, disabled=not api_key):
        progress = st.progress(0, text="Starting...")
        status_box = st.empty()
        for i,q in enumerate(SCRAPE_QUERIES):
            progress.progress(int(i/len(SCRAPE_QUERIES)*75), text=f"Fetching: {q['keyword']}...")
            time.sleep(0.15)
        with st.spinner("Calling JSearch API — this takes ~30 seconds..."):
            result = run_scrape_pipeline(pages_per_query=n_pages)
            force_reload()
        progress.progress(100, text="Done!")
        if result["error"] and result["new_records"]==0:
            status_box.error(f"**Fetch failed:** `{result['error']}`")
        elif result["new_records"]>0:
            status_box.success(f"✅ **+{result['new_records']} new jobs** · Total: {result['total_records']:,} · {result['elapsed_seconds']}s")
        else:
            status_box.warning("Fetch ran but 0 new jobs found — all listings already exist or API returned empty.")

    st.divider()
    st.markdown("#### API Debug")
    if st.button("🔬  Run API Test", disabled=not api_key):
        with st.spinner("Testing..."):
            r = test_api_connection()
        c1,c2 = st.columns(2)
        c1.metric("HTTP Status",   r.get("status_code","—"))
        c2.metric("Jobs Returned", r.get("jobs_count",0))
        if r["ok"]:
            st.success("✅ API working!")
            job = r.get("sample_job",{})
            st.markdown(f"""<div class="insight-card">
              <div class="insight-card-label">Sample Result</div>
              <div class="insight-card-value" style="font-size:1rem;">{job.get('job_title','—')}</div>
              <div style="color:#94A3B8;font-size:0.85rem;margin-top:6px;">
                {job.get('employer_name','—')} · {job.get('job_city','') or job.get('job_country','—')}
              </div></div>""", unsafe_allow_html=True)
        else:
            err = r.get("error","Unknown")
            if "401" in str(r.get("status_code","")) or "INVALID" in err: st.error("Invalid API key. Check secrets.toml.")
            elif "403" in str(r.get("status_code","")) or "FORBIDDEN" in err: st.error("Not subscribed to JSearch on RapidAPI.")
            elif "429" in str(r.get("status_code","")) or "RATE" in err: st.warning("Rate limited. Wait a minute and retry.")
            else: st.error(f"API error: `{err}`")
    if not api_key:
        st.info("Add your RAPIDAPI_KEY to secrets.toml to enable the test.")

    st.divider()
    st.markdown("#### Fetch History")
    if os.path.exists(SCRAPE_LOG):
        log_df = pd.read_csv(SCRAPE_LOG)
        if not log_df.empty:
            log_df = log_df.sort_values("timestamp", ascending=False).head(15)
            log_df.columns = [c.replace("_"," ").title() for c in log_df.columns]
            st.dataframe(log_df, use_container_width=True, hide_index=True)
        else:
            st.info("No fetch history yet.")
    else:
        st.info("No fetch history yet. Run your first fetch above.")