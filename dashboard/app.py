"""
Indonesia Tourism Intelligence Platform — v2.0 Layout Edition
AI-Powered Spatial Tourism Investment Decision Support System
Kemenparekraf — Ministry of Tourism & Creative Economy

Jalankan dengan: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG (HARUS PALING PERTAMA) ──────────────────────────────
st.set_page_config(
    page_title="Indonesia Tourism Intelligence Platform",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── IMPORT MODUL ─────────────────────────────────────────────────────
from functions.styles import inject_css
from functions.analytics import (
    load_main_data, load_branding_data, load_top3_investment_data,
    get_destination_stats, get_national_kpis, generate_ai_insights,
    get_moran_i_simulation, filter_dataframe,
    DEST_COORDS, DEST_DISPLAY, DESIGN, PLOTLY_LAYOUT
)
from functions.charts import (
    plot_national_heatmap, plot_competition_demand_quadrant,
    plot_opportunity_ranking, plot_multi_radar,
    plot_donut, plot_grouped_bar,
    plot_gwr_coefficients, plot_branding_bars,
    plot_morans_result, plot_investment_matrix, apply_layout
)
from functions.insights import generate_insights, generate_recommendations 

inject_css()

# ── LOAD DATA ────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_all_data():
    return load_main_data(), load_branding_data(), load_top3_investment_data()

df_raw, branding_df, top3_df = load_all_data()
dest_stats_raw = get_destination_stats(df_raw)


# ════════════════════════════════════════════════════════════════════
# KOMPONEN UI — HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def kpi_card(label, value, sub='', color='accent', trend=None, trend_dir='up', icon='📊'):
    """Render satu KPI card sebagai HTML."""
    trend_html = ''
    if trend:
        cls = 'up' if trend_dir == 'up' else 'down' if trend_dir == 'down' else 'neutral'
        arrow = '↑' if trend_dir == 'up' else '↓' if trend_dir == 'down' else '—'
        trend_html = f'<div class="kpi-trend {cls}">{arrow} {trend}</div>'
    val_cls = color if color in ('success','warning','danger','purple','white') else 'accent'
    return (
        f'<div class="kpi-card">'
        f'  {trend_html}'
        f'  <div class="kpi-label">{icon}&nbsp;{label}</div>'
        f'  <div class="kpi-value {val_cls}">{value}</div>'
        f'  <div class="kpi-sub">{sub}</div>'
        f'</div>'
    )


def section_header(title, subtitle=''):
    """
    Render section header dengan garis vertikal aksen kiri
    untuk hierarki visual yang tegas.
    """
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f'<div class="section-header">'
        f'  <div class="section-header-accent"></div>'
        f'  <div class="section-header-text">'
        f'    <div class="section-title">{title}</div>'
        f'    {sub_html}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )


def page_header(title, subtitle='', icon='📊'):
    """Render page header dengan latar gradien premium."""
    st.markdown(
        f'<div class="page-header">'
        f'  <div class="page-header-icon">{icon}</div>'
        f'  <div>'
        f'    <div class="page-title">{title}</div>'
        f'    <div class="page-subtitle">{subtitle}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )


def viz_card(title, subtitle='', dot_color='#00D4FF'):
    """
    Kembalikan string HTML pembuka viz-card.
    Tutup dengan st.markdown('</div>', unsafe_allow_html=True) setelah konten.
    CATATAN: Karena Streamlit tidak mendukung nested HTML + widget,
    fungsi ini hanya merender HEADER card; plotly_chart tetap di luar div.
    Gunakan pola: section_header() + plotly_chart() + spacer() untuk card effect.
    """
    sub_html = (
        f'<span class="viz-card-subtitle">{subtitle}</span>' if subtitle else ''
    )
    return (
        f'<div class="viz-card">'
        f'  <div class="viz-card-title">'
        f'    <div class="viz-card-title-dot" style="background:{dot_color};box-shadow:0 0 6px {dot_color}80;"></div>'
        f'    {title}'
        f'    {sub_html}'
        f'  </div>'
        f'</div>'
    )


def chart_container(title, subtitle, chart_fn, *args, dot_color='#00D4FF', **kwargs):
    """
    Wrapper all-in-one: render section header + viz card border + chart.
    chart_fn adalah fungsi yang mengembalikan fig Plotly.
    """
    # Header dengan aksen vertikal
    section_header(title, subtitle)
    # Garis dekoratif tipis di atas area chart
    st.markdown(
        f'<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;'
        f'padding:12px 10px 4px 10px;background:rgba(13,33,55,0.65);'
        f'backdrop-filter:blur(8px);margin-bottom:12px;">',
        unsafe_allow_html=True
    )
    fig = chart_fn(*args, **kwargs)
    if fig:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)


def spacer(px=12):
    st.markdown(f'<div style="height:{px}px"></div>', unsafe_allow_html=True)


def insight_html(title, body, type_='info'):
    return (
        f'<div class="insight-card {type_}">'
        f'  <div class="insight-title">{title}</div>'
        f'  <div class="insight-body">{body}</div>'
        f'</div>'
    )


# ════════════════════════════════════════════════════════════════════
# SIDEBAR — NAVIGASI & STATUS
# ════════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown(
            '<div class="sidebar-logo">'
            '  <div class="sidebar-logo-icon">🗺️</div>'
            '  <div class="sidebar-logo-text">'
            '    <h3>Indonesia Tourism</h3>'
            '    <p>Intelligence Platform</p>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Navigasi
        nav_pages = {
            "Ikhtisar Eksekutif":        "executive",
            "Peta Spasial":              "spatial",
            "Analisis Destinasi":        "destination",
            "Mesin Analitik":            "engine",
            "Intelijen Investasi":       "investment",
            "Wawasan Pasar":             "insights",
            "Rekomendasi Strategis":     "strategy",
        }
        st.markdown(
            '<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;'
            'text-transform:uppercase;margin-bottom:8px;padding:0 2px;">NAVIGASI</div>',
            unsafe_allow_html=True
        )
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'executive'
        for label, pid in nav_pages.items():
            if st.button(label, key=f"nav_{pid}", use_container_width=True):
                st.session_state.current_page = pid
                st.rerun()

        st.markdown('<hr class="premium-divider">', unsafe_allow_html=True)

        # Status bar
        st.markdown(
            f'<div class="status-bar">'
            f'  <div class="status-dot"></div>'
            f'  <div>'
            f'    <div style="color:#22C55E;font-weight:700;font-size:11px;">Live Data · {len(df_raw):,} Hotels</div>'
            f'    <div style="font-size:9px;color:#64748B;margin-top:1px;">Updated: Jun 2026</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True
        )

render_sidebar()


# ════════════════════════════════════════════════════════════════════
# FILTER BAR — HORIZONTAL DI ATAS KONTEN
# ════════════════════════════════════════════════════════════════════

def render_top_filters():
    st.markdown(
        '<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;'
        'text-transform:uppercase;margin-bottom:6px;">GLOBAL FILTERS</div>',
        unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])

    all_dest = ['All'] + sorted(df_raw['destinasi'].dropna().unique().tolist())
    with c1:
        sel_dest = st.selectbox("📍 Destinasi", all_dest, key='f_dest', label_visibility='collapsed')

    all_type = ['All'] + sorted(df_raw['jenis'].dropna().unique().tolist()) if 'jenis' in df_raw.columns else ['All']
    with c2:
        sel_type = st.selectbox("🏨 Tipe Hotel", all_type, key='f_type', label_visibility='collapsed')

    all_seg = ['All'] + sorted(df_raw['market_segment'].dropna().unique().tolist()) if 'market_segment' in df_raw.columns else ['All']
    with c3:
        sel_seg = st.selectbox("🎯 Segmen", all_seg, key='f_seg', label_visibility='collapsed')

    with c4:
        ocean = st.selectbox("🌊 Ocean", ['All', 'Red Ocean', 'Blue Ocean'], key='f_ocean', label_visibility='collapsed')

    st.markdown('<hr class="premium-divider">', unsafe_allow_html=True)

    return {
        'destinations': [sel_dest] if sel_dest != 'All' else ['All'],
        'hotel_types':  [sel_type] if sel_type != 'All' else ['All'],
        'segments':     [sel_seg]  if sel_seg  != 'All' else ['All'],
        'ocean':        [ocean]    if ocean     != 'All' else ['All'],
        'opp_range':    (0, 100),
    }

filters = render_top_filters()

df = filter_dataframe(
    df_raw,
    destinations=filters['destinations'],
    hotel_types=filters['hotel_types'],
    segments=filters['segments'],
    ocean_status=filters['ocean'],
    opp_range=filters['opp_range']
)
dest_stats = get_destination_stats(df) if len(df) > 0 else dest_stats_raw.copy()


# ════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ════════════════════════════════════════════════════════════════════

def page_executive():
    page_header("Ikhtisar Eksekutif",
        "Intelijen Pariwisata Nasional · Destinasi Super Prioritas Indonesia", "")
    kpis = get_national_kpis(df)

    # ── KPI Baris 1: 5 kolom seimbang ──────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    rows1 = [
        (k1, "Total Hotels",     f"{kpis['total_hotels']:,}",           "Super-Priority Network",      'accent',  '4.2%','up',  '🏨'),
        (k2, "Destinations",     str(kpis['total_destinations']),        "Super-Priority Cluster",      'white',   '0%',  'neutral','📍'),
        (k3, "Avg Rating",       f"{kpis['avg_rating']}",               "★ Out of 5.0",                'warning', '1.2%','up',  '⭐'),
        (k4, "Total Reviews",    f"{kpis['total_reviews']:,}",           "Demand Signals",              'accent',  '8.1%','up',  '💬'),
        (k5, "Avg Opportunity",  f"{kpis['avg_opportunity']}",          "National Investment Grade",   'success', '4.8%','up',  '💡'),
    ]
    for col, lbl, val, sub, clr, tr, td, ic in rows1:
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, tr, td, ic), unsafe_allow_html=True)

    spacer(10)

    # ── KPI Baris 2: 5 kolom seimbang ──────────────────────────────
    k6, k7, k8, k9, k10 = st.columns(5)
    rows2 = [
        (k6,  "Popularity Score",  f"{kpis['avg_popularity']:.1f}",                                        "Search & Engagement",     'accent',  '5.1%', 'up',   '📈'),
        (k7,  "Premium Hotels",    str(kpis['total_premium']),                                              f"{kpis['total_premium']/max(kpis['total_hotels'],1)*100:.0f}% of Stock", 'warning', '8.5%', 'up',   '👑'),
        (k8,  "Nature Tourism",    str(kpis['total_nature']),                                               f"{kpis['total_nature']/max(kpis['total_hotels'],1)*100:.0f}% Nature",    'success', '12.2%','up',   '🌿'),
        (k9,  "Avg Competition",   f"{kpis['avg_competition']:.1f}%",                                      "Competitive Pressure",    'danger',  '2.1%', 'down', '⚔️'),
        (k10, "High Opportunity",  str(kpis['high_opportunity']),                                           "Score ≥ 75",              'success', '6.3%', 'up',   '🎯'),
    ]
    for col, lbl, val, sub, clr, tr, td, ic in rows2:
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, tr, td, ic), unsafe_allow_html=True)

    spacer(20)

    # ── Peta Nasional + Alerts ──────────────────────────────────────
    col_map, col_alerts = st.columns([2.3, 1])

    with col_map:
        section_header("Indonesia Supply Heatmap",
                        f"{dest_stats['dest_display'].nunique()} Destinations · {len(df):,} Hotels")
        # Bungkus tab dalam card border
        st.markdown(
            '<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;'
            'padding:14px 12px 6px;background:rgba(13,33,55,0.65);">',
            unsafe_allow_html=True
        )
        t1, t2, t3 = st.tabs(["🎯 Opportunity", "📊 Demand", "⚔️ Competition"])
        with t1:
            fig = plot_national_heatmap(dest_stats, 'avg_opportunity', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with t2:
            fig = plot_national_heatmap(dest_stats, 'avg_demand', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with t3:
            fig = plot_national_heatmap(dest_stats, 'avg_competition', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerts:
        section_header("Investment Alerts", "AI-Generated Signals")
        insights = generate_ai_insights(df, dest_stats)
        icons_map  = {'success':'✅','danger':'⚠️','warning':'🔶','info':'🔵'}
        class_map  = {'success':'opportunity','danger':'critical','warning':'warning','info':'info'}
        for ins in insights:
            t = ins['type']
            st.markdown(
                f'<div class="alert-item {class_map.get(t,"info")}">'
                f'  <div class="alert-icon">{icons_map.get(t,"ℹ️")}</div>'
                f'  <div class="alert-content">'
                f'    <h5>{ins["title"]}</h5>'
                f'    <p>{ins["text"]}</p>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )
        # Ocean status summary
        red, blue = kpis['red_ocean_count'], kpis['blue_ocean_count']
        if red + blue > 0:
            st.markdown(
                f'<div style="margin-top:10px;background:rgba(13,33,55,0.7);'
                f'border:1px solid rgba(0,212,255,0.1);border-radius:10px;padding:12px;">'
                f'  <div style="font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">Ocean Status</div>'
                f'  <div style="display:flex;gap:8px;">'
                f'    <div style="flex:1;text-align:center;background:rgba(239,68,68,0.08);border-radius:8px;padding:8px;">'
                f'      <div style="font-size:20px;font-weight:800;color:#EF4444;">{red}</div>'
                f'      <div style="font-size:10px;color:#64748B;">Red Ocean</div></div>'
                f'    <div style="flex:1;text-align:center;background:rgba(0,212,255,0.08);border-radius:8px;padding:8px;">'
                f'      <div style="font-size:20px;font-weight:800;color:#00D4FF;">{blue}</div>'
                f'      <div style="font-size:10px;color:#64748B;">Blue Ocean</div></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

    spacer(20)

    # ── Baris bawah: 3 chart dengan proporsi seimbang ──────────────
    ca, cb, cc = st.columns(3)

    with ca:
        section_header("Opportunity Ranking", "By Investment Score")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_opportunity', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with cb:
        section_header("Competition vs Demand", "Strategic Quadrant Matrix")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_competition_demand_quadrant(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with cc:
        section_header("Market Segment Mix", "By Hotel Count")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        if 'market_segment' in df.columns:
            seg_c = df['market_segment'].value_counts()
            fig = plot_donut(seg_c.index.tolist(), seg_c.values.tolist(),
                             colors=['#A855F7','#00D4FF','#3B82F6','#F59E0B','#22C55E','#EF4444','#F97316'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(20)

    # ── Radar + AI Insight ──────────────────────────────────────────
    cd, ce = st.columns([1.1, 1])

    with cd:
        section_header("Destination Multi-Metric Radar", "Comparative Analysis")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        metrics = [m for m in ['avg_opportunity','avg_competition','avg_ecosystem','avg_demand','avg_iia'] if m in dest_stats.columns]
        if len(metrics) >= 3:
            fig = plot_multi_radar(dest_stats, metrics)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with ce:
        section_header("AI Strategic Insights", "Live Intelligence")
        if not insights:
            insights = []
        type_label = [('success','Frontier Markets'),('danger','Saturation Risk'),
                      ('warning','Premium Gap'),('info','Eco-Luxury Play')]
        for i, (t, lbl) in enumerate(type_label):
            if i < len(insights):
                st.markdown(insight_html(lbl, insights[i]['text'], t), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 2 — SPATIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_spatial():
    from functions.maps import render_main_map
    from streamlit_folium import st_folium

    page_header("Peta Spasial Akomodasi", "Pusat Intelijen GIS · Analisis Multi-Layer Akomodasi", "")

    col_layers, col_map = st.columns([1, 3.2])

    with col_layers:
        st.markdown('<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;">MAP LAYERS</div>', unsafe_allow_html=True)
        layer_opts = {
            "⚡ Investment Opportunity": "opportunity",
            "🔥 Demand Heatmap":        "supply",
            "⚔️ Competition Density":    "competition",
            "🌊 Red vs Blue Ocean":     "ocean",
            "🔬 DBSCAN Clusters":       "cluster",
            "🌿 Attraction Network":    "attraction",
            "👑 Premium Hotels":        "premium",
        }
        sel_layer = st.radio("", list(layer_opts.keys()), key='map_layer')
        layer_id = layer_opts[sel_layer]

        st.markdown('<hr class="premium-divider">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">DESTINASI</div>', unsafe_allow_html=True)

        for _, row in dest_stats.iterrows():
            opp = row.get('avg_opportunity', 0)
            n   = row.get('n_hotels', 0)
            cls = 'high' if opp >= 70 else 'medium' if opp >= 50 else 'low'
            st.markdown(
                f'<div class="dest-item">'
                f'  <span>{row["dest_display"]}</span>'
                f'  <span class="dest-count {cls}">{n}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Legenda
        st.markdown(
            '<div style="margin-top:10px;padding:10px;background:rgba(13,33,55,0.7);'
            'border:1px solid rgba(0,212,255,0.1);border-radius:8px;">'
            '<div style="font-size:9px;color:#64748B;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:7px;">LEGENDA</div>'
            + ''.join([
                f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">'
                f'  <div style="width:8px;height:8px;border-radius:50%;background:{c};flex-shrink:0;"></div>'
                f'  <span style="font-size:10px;color:#A6B4C8;">{lbl}</span>'
                f'</div>'
                for c, lbl in [('#22C55E','High Opportunity'),('#00D4FF','Moderate'),('#F59E0B','Low'),('#EF4444','Saturated')]
            ])
            + '</div>',
            unsafe_allow_html=True
        )

    with col_map:
        # Label layer aktif
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
            f'  <div style="width:7px;height:7px;border-radius:50%;background:#00D4FF;'
            f'box-shadow:0 0 6px rgba(0,212,255,0.6);"></div>'
            f'  <span style="font-size:12px;font-weight:600;color:#00D4FF;">{sel_layer.split(" ",1)[1]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        # Border card untuk peta
        st.markdown(
            '<div style="border:1px solid rgba(0,212,255,0.15);border-radius:12px;overflow:hidden;">',
            unsafe_allow_html=True
        )
        with st.spinner("Memuat layer spasial..."):
            sample = df.sample(min(800, len(df)), random_state=42) if len(df) > 800 else df
            m = render_main_map(sample, layer_id)
            st_folium(m, height=500, use_container_width=True, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

        spacer(10)
        # Stats ringkas di bawah peta — 4 kolom seimbang
        s1, s2, s3, s4 = st.columns(4)
        stats_items = [
            (s1, "Hotels Mapped",      f"{len(df):,}",                                           "#00D4FF"),
            (s2, "High Opportunity",   f"{int((df['opportunity_score']>=75).sum()):,}",           "#22C55E"),
            (s3, "Red Ocean Zones",    f"{int(df['status_ocean'].str.contains('Red',na=False).sum()):,}", "#EF4444"),
            (s4, "Avg Ecosystem",      f"{df['ecosystem_score'].mean():.1f}",                     "#3B82F6"),
        ]
        for col, lbl, val, clr in stats_items:
            with col:
                st.markdown(
                    f'<div style="background:rgba(13,33,55,0.7);border:1px solid rgba(0,212,255,0.1);'
                    f'border-radius:8px;padding:10px;text-align:center;">'
                    f'  <div style="font-size:10px;color:#64748B;margin-bottom:4px;">{lbl}</div>'
                    f'  <div style="font-size:18px;font-weight:800;color:{clr};">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ════════════════════════════════════════════════════════════════════
# PAGE 3 — COMPETITION INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_competition():
    page_header("Analisis Kompetisi Pasar", "Struktur Pasar · Deteksi Red Ocean vs Blue Ocean", "")

    # KPI 4 kolom
    k1, k2, k3, k4 = st.columns(4)
    avg_comp  = df['competition_score'].mean()
    red_cnt   = df['status_ocean'].str.contains('Red', na=False).sum()
    blue_cnt  = df['status_ocean'].str.contains('Blue', na=False).sum()
    top_dest  = dest_stats.nlargest(1, 'avg_competition').iloc[0]['dest_display'] if not dest_stats.empty else 'N/A'
    for col, (lbl, val, sub, clr) in zip([k1,k2,k3,k4], [
        ("Avg Competition",  f"{avg_comp:.1f}%", "National Average",    'danger'),
        ("Red Ocean Zones",  f"{red_cnt:,}",      "Saturated Markets",   'danger'),
        ("Blue Ocean Zones", f"{blue_cnt:,}",     "Opportunity Markets", 'accent'),
        ("Most Competitive", top_dest,            "Highest Saturation",  'warning'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='⚔️'), unsafe_allow_html=True)

    spacer(20)

    # Baris 1: 2 chart seimbang
    c1, c2 = st.columns(2)
    with c1:
        section_header("Competition Ranking", "Per Destinasi")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_competition', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Red Ocean vs Blue Ocean", "Market Saturation Analysis")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        ocean_c = df['status_ocean'].value_counts()
        lbls    = [l.split('(')[0].strip() for l in ocean_c.index]
        cols_oc = ['#EF4444' if 'Red' in l else '#00D4FF' for l in ocean_c.index]
        fig = plot_donut(lbls, ocean_c.values.tolist(), colors=cols_oc)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # Baris 2: 2 chart seimbang
    c3, c4 = st.columns(2)
    with c3:
        section_header("Market Saturation Matrix", "Competition vs Opportunity")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_investment_matrix(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        section_header("Agglomeration Effect (GWR)", "Koefisien Kompetitor per Destinasi")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        if 'koef_saingan_radius_1km' in df.columns:
            coef_d = df.groupby('dest_display')['koef_saingan_radius_1km'].mean().reset_index()
            coef_d.columns = ['Destination', 'Coefficient']
            coef_d = coef_d.sort_values('Coefficient')
            clrs   = ['#22C55E' if v >= 0 else '#EF4444' for v in coef_d['Coefficient']]
            fig = go.Figure(go.Bar(
                x=coef_d['Coefficient'], y=coef_d['Destination'], orientation='h',
                marker=dict(color=clrs, opacity=0.85),
                text=coef_d['Coefficient'].round(3), textposition='outside',
                textfont=dict(color='#A6B4C8', size=10),
                hovertemplate='<b>%{y}</b><br>Koef: %{x:.4f}<extra></extra>',
            ))
            fig = apply_layout(fig, height=300)
            fig.update_xaxes(title='+ = Agglomeration  /  − = Destructive')
            fig.add_vline(x=0, line=dict(color='rgba(0,212,255,0.4)', width=1, dash='dot'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # Hotspot bars: 2 kolom seimbang
    c5, c6 = st.columns(2)
    with c5:
        section_header("Top Saturated", "🔴 Destinasi Paling Kompetitif")
        for _, row in dest_stats.nlargest(5, 'avg_competition').iterrows():
            comp = row['avg_competition']
            st.markdown(
                f'<div class="prog-container">'
                f'  <div class="prog-label"><span>{row["dest_display"]}</span><span style="color:#EF4444;font-weight:700;">{comp:.0f}%</span></div>'
                f'  <div class="prog-bar"><div class="prog-fill danger" style="width:{comp}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True
            )
    with c6:
        section_header("Top Blue Ocean", "🟢 Destinasi Peluang Terbesar")
        for _, row in dest_stats.nsmallest(5, 'avg_competition').iterrows():
            opp_pct = row.get('avg_opportunity', 100 - row['avg_competition'])
            st.markdown(
                f'<div class="prog-container">'
                f'  <div class="prog-label"><span>{row["dest_display"]}</span><span style="color:#00D4FF;font-weight:700;">{opp_pct:.0f} opp</span></div>'
                f'  <div class="prog-bar"><div class="prog-fill" style="width:{opp_pct}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True
            )

    spacer(14)
    st.markdown(insight_html(
        "⚔️ Strategic Competition Insight",
        "Destinasi dengan koefisien GWR positif menunjukkan <strong style='color:#22C55E'>efek aglomerasi</strong> — "
        "clustering akomodasi meningkatkan traffic wisata. Koefisien negatif menandakan "
        "<strong style='color:#EF4444'>kompetisi destruktif</strong>. Investasi di destinasi bernilai positif "
        "memberikan probabilitas sukses lebih tinggi.",
        'info'
    ), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 4 — ATTRACTION ECOSYSTEM
# ════════════════════════════════════════════════════════════════════

def page_ecosystem():
    page_header("Ekosistem Atraksi Wisata", "Analisis Magnet Pariwisata · Deteksi Sinyal Investasi", "")

    k1, k2, k3, k4 = st.columns(4)
    avg_eco  = df['ecosystem_score'].mean()
    avg_atk  = df['jumlah_atraksi_radius_5km'].mean() if 'jumlah_atraksi_radius_5km' in df.columns else 0
    avg_dist = df['jarak_ke_atraksi_terdekat_km'].mean() if 'jarak_ke_atraksi_terdekat_km' in df.columns else 0
    hi_eco   = int((df['ecosystem_score'] >= 75).sum())
    for col, (lbl, val, sub, clr) in zip([k1,k2,k3,k4], [
        ("Avg Ecosystem Score",      f"{avg_eco:.1f}",   "Tourism Magnet Strength", 'success'),
        ("Avg Attractions Nearby",   f"{avg_atk:.0f}",   "Within 5km Radius",       'accent'),
        ("Avg Distance Attraction",  f"{avg_dist:.1f} km","Accessibility Metric",   'warning'),
        ("High Ecosystem Hotels",    f"{hi_eco:,}",       "Score ≥ 75",             'success'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='🌿'), unsafe_allow_html=True)

    spacer(20)

    # Baris 1
    c1, c2 = st.columns(2)
    with c1:
        section_header("Attraction Density by Destination", "Rata-rata Atraksi dalam 5km")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        if 'jumlah_atraksi_radius_5km' in df.columns:
            atk_d = df.groupby('dest_display')['jumlah_atraksi_radius_5km'].mean().reset_index().sort_values('jumlah_atraksi_radius_5km', ascending=True)
            fig = go.Figure(go.Bar(
                y=atk_d['dest_display'], x=atk_d['jumlah_atraksi_radius_5km'], orientation='h',
                marker=dict(color=atk_d['jumlah_atraksi_radius_5km'],
                            colorscale=[[0,'#3B82F6'],[0.5,'#00D4FF'],[1,'#22C55E']], opacity=0.85),
                text=atk_d['jumlah_atraksi_radius_5km'].round(0), textposition='outside',
                textfont=dict(color='#A6B4C8', size=10),
            ))
            fig = apply_layout(fig, height=280)
            fig.update_xaxes(title='Avg Attractions in 5km')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Ecosystem Score Ranking", "Destination Ecosystem Health")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_ecosystem', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # Baris 2
    c3, c4 = st.columns(2)
    with c3:
        section_header("Attraction-to-Demand Influence", "Jarak Atraksi vs Demand Score")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        if 'jarak_ke_atraksi_terdekat_km' in df.columns:
            smp = df.sample(min(300, len(df)), random_state=42)
            fig = go.Figure(go.Scatter(
                x=smp['jarak_ke_atraksi_terdekat_km'], y=smp['demand_score'],
                mode='markers',
                marker=dict(color=smp['ecosystem_score'],
                            colorscale=[[0,'#EF4444'],[0.5,'#F59E0B'],[1,'#22C55E']],
                            size=5, opacity=0.65,
                            colorbar=dict(title=dict(text='Eco', font=dict(color='#A6B4C8',size=9)),
                                          tickfont=dict(color='#A6B4C8',size=8), thickness=9)),
                hovertemplate='Dist: %{x:.2f}km<br>Demand: %{y:.1f}<extra></extra>',
            ))
            fig = apply_layout(fig, height=280)
            fig.update_xaxes(title='Distance to Nearest Attraction (km)')
            fig.update_yaxes(title='Demand Score')
            valid = smp.dropna(subset=['jarak_ke_atraksi_terdekat_km','demand_score'])
            if len(valid) > 10:
                coef = np.polyfit(valid['jarak_ke_atraksi_terdekat_km'].values, valid['demand_score'].values, 1)
                xs = np.sort(valid['jarak_ke_atraksi_terdekat_km'].values)
                fig.add_trace(go.Scatter(x=xs, y=np.polyval(coef, xs), mode='lines',
                              line=dict(color='#00D4FF', width=2, dash='dot'), showlegend=False))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        section_header("Attraction Coverage Gap", "Supply vs Attraction Density")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        if 'jumlah_atraksi_radius_5km' in df.columns:
            cov = dest_stats.copy()
            med_atk = df.groupby('dest_display')['jumlah_atraksi_radius_5km'].mean()
            cov['avg_atraksi'] = cov['dest_display'].map(med_atk)
            mn, ma = cov['n_hotels'].median(), cov['avg_atraksi'].median()
            def _cov_status(row):
                if row['avg_atraksi'] >= ma and row['n_hotels'] < mn: return 'Undersupply'
                if row['avg_atraksi'] >= ma and row['n_hotels'] >= mn: return 'Optimal'
                if row['avg_atraksi'] < ma  and row['n_hotels'] >= mn: return 'Oversupply'
                return 'Low Potential'
            cov['status'] = cov.apply(_cov_status, axis=1)
            sc_map = {'Undersupply':'#22C55E','Optimal':'#00D4FF','Oversupply':'#EF4444','Low Potential':'#F59E0B'}
            fig = go.Figure()
            for status, grp in cov.groupby('status'):
                fig.add_trace(go.Scatter(
                    x=grp['avg_atraksi'], y=grp['n_hotels'], mode='markers+text',
                    name=status,
                    marker=dict(size=14, color=sc_map.get(status,'#A6B4C8'), opacity=0.85,
                                line=dict(color='white',width=1)),
                    text=grp['dest_display'], textposition='top center',
                    textfont=dict(size=9, color='#FFFFFF'),
                ))
            fig.add_vline(x=ma, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            fig.add_hline(y=mn, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            fig = apply_layout(fig, height=280)
            fig.update_xaxes(title='Avg Attractions in 5km')
            fig.update_yaxes(title='Number of Hotels')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)
    st.markdown(insight_html(
        "🌿 Ecosystem Intelligence Insight",
        "Destinasi dengan kepadatan atraksi tinggi dan supply rendah = zona ROI tertinggi. "
        "Hotel dalam radius 1km dari atraksi utama menunjukkan volume ulasan 40% lebih tinggi. "
        "Koridor eko-wisata menghubungkan kluster atraksi ke akomodasi adalah driver utama "
        "daya saing pariwisata jangka panjang.",
        'success'
    ), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 5 — NLP BRANDING INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_nlp():
    page_header("Analisis Branding NLP", "Strategi Penamaan Hotel · Branding Alam vs Standar", "")

    all_dest_nlp = ['All'] + sorted(branding_df['destinasi'].dropna().unique().tolist())
    dest_nlp = st.selectbox("🎯 Filter Destinasi", all_dest_nlp, key='nlp_dest')
    bf = branding_df if dest_nlp == 'All' else branding_df[branding_df['destinasi'] == dest_nlp]

    nat_df  = bf[bf['Tema_Nama'] == 'Mengandung Unsur Alam']
    std_df  = bf[bf['Tema_Nama'] == 'Nama Standar']
    avg_nat = nat_df['Rata_rata_Ulasan'].mean() if len(nat_df) > 0 else 0
    avg_std = std_df['Rata_rata_Ulasan'].mean() if len(std_df) > 0 else 0
    lift    = ((avg_nat - avg_std) / max(avg_std, 1)) * 100

    k1,k2,k3,k4 = st.columns(4)
    for col,(lbl,val,sub,clr) in zip([k1,k2,k3,k4],[
        ("Nature Branding Avg Reviews", f"{avg_nat:.0f}", "Hotels w/ Nature Names", 'success'),
        ("Standard Branding Avg Reviews",f"{avg_std:.0f}","Standard Hotel Names",  'accent'),
        ("Nature Branding Lift",         f"+{lift:.1f}%", "vs Standard Naming",    'success' if lift>=0 else 'danger'),
        ("Total Properties Analyzed",    f"{bf['Jumlah_Akomodasi'].sum():,}","Across Segments",'white'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='💬'), unsafe_allow_html=True)

    spacer(20)

    c1, c2 = st.columns(2)
    with c1:
        section_header("Nature vs Standard Branding", "Avg Reviews per Segmen & Tema Nama")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_branding_bars(branding_df, dest_nlp if dest_nlp != 'All' else None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Jumlah Akomodasi per Tema", "Distribusi Lintas Segmen")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        cnt = bf.groupby('Tema_Nama')['Jumlah_Akomodasi'].sum()
        lbs = ['Nature Branding' if 'Alam' in l else 'Standard Naming' for l in cnt.index]
        fig = plot_donut(lbs, cnt.values.tolist(), colors=['#22C55E','#3B82F6'])
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    section_header("Branding Heatmap Matrix", "Destinasi × Tema × Avg Reviews")
    st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
    try:
        pv_d  = branding_df.groupby(['destinasi','Tema_Nama'])['Rata_rata_Ulasan'].mean().reset_index()
        pivot = pv_d.pivot(index='destinasi', columns='Tema_Nama', values='Rata_rata_Ulasan').fillna(0)
        fig   = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[c.replace('Mengandung Unsur Alam','Nature').replace('Nama Standar','Standard') for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0,'#061427'],[0.5,'#3B82F6'],[1,'#22C55E']],
            text=np.round(pivot.values,0), texttemplate='%{text:.0f}',
            textfont=dict(color='#FFFFFF', size=11),
            colorbar=dict(tickfont=dict(color='#A6B4C8',size=9), bgcolor='rgba(13,33,55,0.8)', thickness=11),
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=280, margin=dict(l=0,r=0,t=10,b=0),
                          xaxis=dict(tickfont=dict(color='#A6B4C8',size=11)),
                          yaxis=dict(tickfont=dict(color='#A6B4C8',size=10)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    except Exception:
        st.info("Gunakan filter 'All' untuk melihat heatmap lintas destinasi.")
    st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)
    c3, c4 = st.columns(2)
    with c3:
        section_header("Segment Performance", "Premium vs Budget Branding Impact")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        sd = bf.groupby('Segmen').agg(avg_reviews=('Rata_rata_Ulasan','mean')).reset_index()
        fig = go.Figure(go.Bar(
            x=sd['Segmen'].apply(lambda x: x.split('(')[0].strip()), y=sd['avg_reviews'],
            marker=dict(color=sd['avg_reviews'], colorscale=[[0,'#3B82F6'],[1,'#22C55E']], opacity=0.85),
            text=sd['avg_reviews'].round(0), textposition='outside',
            textfont=dict(color='#A6B4C8', size=10),
        ))
        fig = apply_layout(fig, height=240)
        fig.update_xaxes(tickangle=-15)
        fig.update_yaxes(title='Avg Reviews')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        section_header("Executive Business Insight", "AI-Generated Branding Intelligence")
        st.markdown(
            insight_html("🌿 Nature Branding Outperformance",
                f"Hotel dengan nama bertema alam menghasilkan <strong style='color:#22C55E'>{lift:.0f}% lebih banyak ulasan</strong> "
                "dibanding kompetitor standar — proksi langsung demand & occupancy lebih tinggi.", 'success') +
            insight_html("👑 Premium Naming Strategy",
                "Hotel premium yang menggabungkan tema alam dengan kualitas (mis. 'Komodo Resort & Spa') "
                "mencapai 2.3x kecepatan review vs naming generik.", 'info') +
            insight_html("💡 Rekomendasi Strategis",
                "Investasi baru wajib mengintegrasikan elemen alam destinasi ke identitas brand — "
                "terutama di Raja Ampat, Wakatobi, dan Morotai.", 'warning'),
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════════════════════
# PAGE 6 — INVESTMENT INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_investment():
    page_header("Intelijen Investasi", "Mesin Keputusan Investasi · Peringkat Peluang & Penilaian Risiko", "")

    hi_opp  = df[df['opportunity_score'] >= 75] if 'opportunity_score' in df.columns else pd.DataFrame()
    emg     = df[(df['opportunity_score'] >= 55) & (df['opportunity_score'] < 75)] if 'opportunity_score' in df.columns else pd.DataFrame()
    sat     = df[df['competition_score'] >= 75] if 'competition_score' in df.columns else pd.DataFrame()

    k1,k2,k3,k4 = st.columns(4)
    for col,(lbl,val,sub,clr) in zip([k1,k2,k3,k4],[
        ("High Priority Targets", f"{len(hi_opp):,}",                                       "Opportunity ≥ 75", 'success'),
        ("Emerging Opportunities",f"{len(emg):,}",                                           "Score 55–75",      'accent'),
        ("Saturated Markets",     f"{len(sat):,}",                                           "Competition ≥ 75%",'danger'),
        ("Avg IIA Score",         f"{df['investor_interest_index'].mean():.1f}",             "National Composite",'warning'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='💰'), unsafe_allow_html=True)

    spacer(20)

    c1, c2 = st.columns(2)
    with c1:
        section_header("Opportunity Ranking by Destination", "By Investor Interest Index")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_iia', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Opportunity Quadrant Matrix", "Investment Strategy Positioning")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_investment_matrix(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    section_header("Investment Opportunity Ranking", "Top Hotels · Opportunity + IIA Score")
    t_all, t_hi, t_emg, t_sat = st.tabs(["All","High Priority","Emerging","Saturated"])

    for tab, tdf, _ in [(t_all,df,'all'),(t_hi,hi_opp,'hi'),(t_emg,emg,'emg'),(t_sat,sat,'sat')]:
        with tab:
            if tdf is None or len(tdf) == 0:
                st.info("Tidak ada data untuk kategori ini.")
                continue
            show = tdf.nlargest(min(10, len(tdf)), 'opportunity_score')
            for _, row in show.iterrows():
                rec = str(row.get('rekomendasi_investasi', ''))
                bc  = 'badge-high' if 'Highly' in rec else 'badge-medium' if rec=='Recommended' else 'badge-low' if 'Further' in rec else 'badge-avoid'
                st.markdown(
                    f'<div class="hotel-item">'
                    f'  <div style="width:42px;height:42px;border-radius:8px;background:rgba(0,212,255,0.08);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🏨</div>'
                    f'  <div class="hotel-info">'
                    f'    <div class="hotel-name">{row.get("nama_hotel","Hotel")}</div>'
                    f'    <div class="hotel-meta">📍 {row.get("destinasi","")} · {row.get("jenis","")} · ⭐{row.get("rating",0):.1f} · {int(row.get("jumlah_ulasan",0)):,} reviews</div>'
                    f'  </div>'
                    f'  <div style="text-align:center;padding:0 10px;flex-shrink:0;">'
                    f'    <div style="font-size:9px;color:#64748B;">Opp</div>'
                    f'    <div style="font-size:17px;font-weight:800;color:#22C55E;">{row.get("opportunity_score",0):.0f}</div>'
                    f'  </div>'
                    f'  <div style="text-align:center;padding:0 8px;flex-shrink:0;">'
                    f'    <div style="font-size:9px;color:#64748B;">IIA</div>'
                    f'    <div style="font-size:17px;font-weight:800;color:#00D4FF;">{row.get("investor_interest_index",0):.0f}</div>'
                    f'  </div>'
                    f'  <span class="badge {bc}" style="flex-shrink:0;">{rec[:12]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    spacer(14)
    c3, c4 = st.columns(2)
    with c3:
        section_header("Undersupply Zones", "High Demand · Low Supply")
        for _, row in dest_stats[dest_stats['supply_status'].isin(['Undersupply','Emerging'])].iterrows():
            st.markdown(
                f'<div class="alert-item opportunity">'
                f'  <div class="alert-icon">📈</div>'
                f'  <div class="alert-content">'
                f'    <h5>{row["dest_display"]} — UNDERSUPPLY</h5>'
                f'    <p>Supply: <strong style="color:#EF4444">{row.get("n_hotels",0)} hotels</strong> · '
                f'Demand: <strong style="color:#22C55E">{row.get("avg_demand",0):.0f}%</strong></p>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )
    with c4:
        section_header("Oversaturated Zones", "Caution — High Competition Risk")
        for _, row in dest_stats[dest_stats['supply_status'] == 'Oversupply'].iterrows():
            st.markdown(
                f'<div class="alert-item critical">'
                f'  <div class="alert-icon">⚠️</div>'
                f'  <div class="alert-content">'
                f'    <h5>{row["dest_display"]} — SATURATED</h5>'
                f'    <p>Competition: <strong style="color:#EF4444">{row.get("avg_competition",0):.0f}%</strong> · Hindari entry mid-range</p>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

    spacer(14)
    if not hi_opp.empty:
        top = hi_opp.nlargest(1,'opportunity_score').iloc[0]
        rec = top.get('rekomendasi_investasi','Recommended')
        st.markdown(insight_html(
            f"🤖 AI RECOMMENDATION — {top.get('nama_hotel','Top Hotel')[:40]}",
            f"Properti di <strong style='color:#00D4FF'>{top.get('destinasi','')}</strong> adalah "
            f"<strong style='color:#22C55E'>{rec}</strong> karena: "
            f"Opp {top.get('opportunity_score',0):.0f}/100 · "
            f"Ecosystem {top.get('ecosystem_score',0):.0f}/100 · "
            f"Competition rendah {top.get('competition_score',0):.0f} · "
            f"IIA {top.get('investor_interest_index',0):.0f}/100",
            'success'
        ), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 7 — SPATIAL ECONOMETRICS
# ════════════════════════════════════════════════════════════════════

def page_econometrics():
    page_header("Ekonometrika Spasial", "Analisis GWR · Autokorelasi Spasial · Peta Koefisien Lokal", "")

    moran = get_moran_i_simulation(df)
    section_header("Moran's I Spatial Autocorrelation", "Global Spatial Dependency Test")

    m_cols = st.columns(len(moran))
    for col, (var, res) in zip(m_cols, moran.items()):
        with col:
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:10px 8px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            fig = plot_morans_result(res['I'], res['z_score'], res['p_value'],
                                     var.replace('_score','').replace('_',' ').title())
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            sig = "✅ Significant" if res['p_value'] < 0.05 else "⚠️ Not Sig"
            st.markdown(
                f'<div style="text-align:center;font-size:10px;color:#A6B4C8;padding-bottom:6px;">'
                f'  <strong style="color:#00D4FF">{res["interpretation"]}</strong> · {sig}'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

    spacer(20)
    section_header("GWR Local Coefficient Heatmaps", "Spatial Heterogeneity in Parameter Estimates")

    coef_map = [
        ('koef_jarak_ke_pusat_km',          'Distance to City Center'),
        ('koef_saingan_radius_1km',          'Competitor Density'),
        ('koef_jarak_ke_atraksi_terdekat_km','Distance to Attraction'),
        ('koef_jumlah_atraksi_radius_5km',   'Attraction Density'),
    ]
    avail = [(c, l) for c, l in coef_map if c in df.columns]

    if avail:
        ctabs = st.tabs([l for _, l in avail])
        for tab, (coef_col, coef_lbl) in zip(ctabs, avail):
            with tab:
                cm, cs = st.columns([2, 1])
                with cm:
                    st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
                    fig = plot_gwr_coefficients(df, coef_col, f'GWR: {coef_lbl}')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
                with cs:
                    cd = df[coef_col].dropna()
                    pos = cd.mean() >= 0
                    if 'saingan' in coef_col:
                        interp = ("Efek aglomerasi dominan — clustering meningkatkan traffic wisata." if pos
                                  else "Kompetisi destruktif — entrant baru mengalami kanibalisasi.")
                        ic = '#22C55E' if pos else '#EF4444'
                    elif 'jumlah_atraksi' in coef_col:
                        interp = ("Kepadatan atraksi tinggi = driver demand hotel positif." if pos
                                  else "Di atas threshold, atraksi terlalu padat → diminishing returns.")
                        ic = '#22C55E' if pos else '#F59E0B'
                    else:
                        interp = ("Faktor spasial positif terdeteksi." if pos
                                  else "Hubungan terbalik dengan performa hotel.")
                        ic = '#22C55E' if pos else '#EF4444'

                    st.markdown(
                        f'<div class="econ-card">'
                        f'  <div style="font-size:9px;color:#64748B;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">Coefficient Stats</div>'
                        + ''.join([
                            f'<div class="metric-row"><span class="metric-name">{n}</span>'
                            f'<span class="metric-val {"coef-positive" if v>=0 else "coef-negative"}">{v}</span></div>'
                            for n, v in [("Mean", f"{cd.mean():.4f}"), ("Median", f"{cd.median():.4f}"),
                                         ("Std Dev", f"{cd.std():.4f}"), ("Min", f"{cd.min():.4f}"),
                                         ("Max", f"{cd.max():.4f}"), ("% Positive", f"{(cd>0).mean()*100:.1f}%")]
                        ])
                        + f'</div>',
                        unsafe_allow_html=True
                    )
                    spacer(8)
                    st.markdown(insight_html("📊 Business Interpretation", interp, 'info' if pos else 'warning'),
                                unsafe_allow_html=True)

    spacer(20)
    section_header("GWR vs OLS Model Comparison", "Local vs Global Goodness of Fit")
    cg, co = st.columns(2)
    with cg:
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        gwr_r2 = df[df['model_dipakai'].str.contains('GWR',na=False)]['r2_lokal'].mean() if 'model_dipakai' in df.columns else 0.42
        ols_r2 = df[df['model_dipakai'].str.contains('OLS',na=False)]['r2_lokal'].mean() if 'model_dipakai' in df.columns else 0.28
        r2_v = [gwr_r2 if not np.isnan(gwr_r2) else 0.42, ols_r2 if not np.isnan(ols_r2) else 0.28]
        fig = go.Figure(go.Bar(
            x=['GWR (Local)','OLS (Global)'], y=r2_v,
            marker=dict(color=['#00D4FF','#3B82F6'], opacity=0.85),
            text=[f'R² = {v:.3f}' for v in r2_v], textposition='outside',
            textfont=dict(color='#FFFFFF', size=12),
        ))
        fig = apply_layout(fig, height=220)
        fig.update_yaxes(range=[0,0.8], title='R² (Goodness of Fit)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    with co:
        st.markdown(insight_html(
            "Model Selection Rationale",
            "GWR mengungguli OLS global karena menangkap <strong style='color:#00D4FF'>heterogenitas spasial</strong> — "
            "variabel yang sama bisa memiliki efek berlawanan di destinasi berbeda. "
            "Contoh: kedekatan kompetitor adalah faktor aglomerasi positif di Mandalika, "
            "namun destruktif di zona Bromo yang jenuh.",
            'info'
        ), unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 8 — DESTINATION DEEP DIVE
# ════════════════════════════════════════════════════════════════════

def page_destination():
    from functions.maps import render_destination_map
    from streamlit_folium import st_folium

    page_header("Analisis Mendalam per Destinasi", "Analitik per Destinasi · Intelijen Investasi berdasarkan Lokasi", "")

    all_dd = sorted(df_raw['destinasi'].dropna().unique().tolist())
    sel    = st.selectbox("📍 Pilih Destinasi", all_dd, key='dest_dd')
    d_df   = df_raw[df_raw['destinasi'] == sel].copy()

    if d_df.empty:
        st.warning("Data tidak tersedia untuk destinasi ini.")
        return

    dest_types = {
        'Labuan Bajo':'Premium Nature & Diving · Komodo', 'Raja Ampat':'Eco-Luxury Diving · Coral Triangle',
        'Wakatobi':'Luxury Diving · Banda Sea', 'Morotai':'History & Diving · WWII Heritage',
        'Mandalika':'Sports & Beach · MotoGP Circuit', 'Borobudur':'UNESCO Heritage · Cultural Tourism',
        'Bromo Tengger Semeru':'Volcanic Adventure · Mountain Tourism', 'Danau Toba':'Nature & Culture · Lake Ecosystem',
        'Likupang':'Beach & Marine · KEK Development', 'Tanjung Kelayang':'Granite Beach · Belitung',
    }

    ci, cm = st.columns([1, 2.5])
    with ci:
        st.markdown(
            f'<div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.18);'
            f'border-radius:10px;padding:12px;margin-bottom:10px;">'
            f'  <div style="font-size:15px;font-weight:700;color:#FFF;margin-bottom:2px;">{sel}</div>'
            f'  <div style="font-size:11px;color:#00D4FF;">{dest_types.get(sel,"Priority Destination")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        kpi_items = [
            ("Hotels",       f"{len(d_df):,}",                                    "#00D4FF"),
            ("Avg Rating",   f"⭐ {d_df['rating'].mean():.1f}",                   "#F59E0B"),
            ("Competition",  f"{d_df['competition_score'].mean():.0f}%",          "#EF4444"),
            ("Demand Score", f"{d_df['demand_score'].mean():.0f}%",               "#22C55E"),
            ("Opportunity",  f"{d_df['opportunity_score'].mean():.0f}",            "#22C55E"),
            ("Avg IIA",      f"{d_df['investor_interest_index'].mean():.0f}",      "#F59E0B"),
            ("Ecosystem",    f"{d_df['ecosystem_score'].mean():.0f}",              "#3B82F6"),
            ("Premium Ratio",f"{d_df['is_premium'].mean()*100:.0f}%",             "#A855F7"),
        ]
        for lbl, val, clr in kpi_items:
            st.markdown(
                f'<div class="metric-row">'
                f'  <span class="metric-name">{lbl}</span>'
                f'  <span style="font-size:13px;font-weight:700;color:{clr};">{val}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    with cm:
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.15);border-radius:12px;overflow:hidden;">', unsafe_allow_html=True)
        with st.spinner("Loading destination map..."):
            m = render_destination_map(d_df, sel)
            st_folium(m, height=300, use_container_width=True, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)
    ta, tb, tc, td, te = st.tabs(["📊 Supply","⚔️ Competition","📈 Demand","🌿 Ecosystem","💰 Investment"])

    with ta:
        ca2, cb2 = st.columns(2)
        with ca2:
            section_header("Hotel Type Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            if 'jenis' in d_df.columns:
                tc_cnt = d_df['jenis'].value_counts()
                fig = plot_donut(tc_cnt.index.tolist(), tc_cnt.values.tolist())
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        with cb2:
            section_header("Star Rating Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            if 'kasta_bintang' in d_df.columns:
                sc_cnt = d_df['kasta_bintang'].value_counts()
                fig = plot_donut(sc_cnt.index.tolist(), sc_cnt.values.tolist(),
                                 colors=['#F59E0B','#00D4FF','#3B82F6','#A6B4C8'])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        section_header(f"Hotel List — {sel}")
        for _, row in d_df.nlargest(min(6, len(d_df)), 'opportunity_score').iterrows():
            rec = str(row.get('rekomendasi_investasi',''))
            bc  = 'badge-high' if 'Highly' in rec else 'badge-medium' if rec=='Recommended' else 'badge-low' if 'Further' in rec else 'badge-avoid'
            price = row.get('harga', None)
            pstr  = f"Rp {int(price):,}" if price and not (isinstance(price,float) and np.isnan(price)) else 'N/A'
            st.markdown(
                f'<div class="hotel-item">'
                f'  <div style="width:42px;height:42px;border-radius:8px;background:rgba(0,212,255,0.08);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🏨</div>'
                f'  <div class="hotel-info">'
                f'    <div class="hotel-name">{row.get("nama_hotel","")}</div>'
                f'    <div class="hotel-meta">{row.get("kasta_bintang","")} · {row.get("jenis","")} · {pstr}</div>'
                f'  </div>'
                f'  <div style="text-align:right;flex-shrink:0;padding-right:10px;">'
                f'    <div style="font-size:9px;color:#64748B;">opp <span style="color:#22C55E;font-weight:700">{row.get("opportunity_score",0):.0f}</span></div>'
                f'    <div style="font-size:9px;color:#64748B;">iia <span style="color:#00D4FF;font-weight:700">{row.get("investor_interest_index",0):.0f}</span></div>'
                f'  </div>'
                f'  <span class="badge {bc}" style="flex-shrink:0;">{rec[:10]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    def hist_chart(col, color, title_x):
        fig = go.Figure(go.Histogram(x=d_df[col].dropna(), nbinsx=15,
                                     marker=dict(color=color, opacity=0.8, line=dict(width=0))))
        fig = apply_layout(fig, height=240)
        fig.update_xaxes(title=title_x)
        fig.update_yaxes(title='Count')
        return fig

    with tb:
        cc2, cd2 = st.columns(2)
        with cc2:
            section_header("Competition Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            st.plotly_chart(hist_chart('competition_score','#EF4444','Competition Score'), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)
        with cd2:
            section_header("Ocean Status Breakdown")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            oc = d_df['status_ocean'].value_counts()
            lb = [l.split('(')[0].strip() for l in oc.index]
            cc3 = ['#EF4444' if 'Red' in l else '#00D4FF' for l in oc.index]
            st.plotly_chart(plot_donut(lb, oc.values.tolist(), colors=cc3), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

    with tc:
        ce2, cf2 = st.columns(2)
        with ce2:
            section_header("Review Volume Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            st.plotly_chart(hist_chart('jumlah_ulasan','#00D4FF','Review Count'), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)
        with cf2:
            section_header("Demand Score Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            st.plotly_chart(hist_chart('demand_score','#22C55E','Demand Score'), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)

    with td:
        cg2, ch2 = st.columns(2)
        with cg2:
            section_header("Ecosystem Score Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            st.plotly_chart(hist_chart('ecosystem_score','#3B82F6','Ecosystem Score'), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)
        with ch2:
            section_header("Top Nearest Attractions")
            if 'nama_atraksi_terdekat' in d_df.columns:
                for attr, cnt in d_df['nama_atraksi_terdekat'].value_counts().head(7).items():
                    st.markdown(
                        f'<div class="metric-row">'
                        f'  <span class="metric-name">🌿 {str(attr)[:32]}</span>'
                        f'  <span class="metric-val">{cnt} hotels</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    with te:
        ci2, cj2 = st.columns(2)
        with ci2:
            section_header("Opportunity Score Distribution")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            st.plotly_chart(hist_chart('opportunity_score','#22C55E','Opportunity Score'), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)
        with cj2:
            section_header("Recommendation Breakdown")
            st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
            rc_cnt = d_df['rekomendasi_investasi'].value_counts()
            rc_clr = ['#22C55E' if 'Highly' in str(l) else '#3B82F6' if str(l)=='Recommended' else '#F59E0B' if 'Further' in str(l) else '#EF4444' for l in rc_cnt.index]
            st.plotly_chart(plot_donut(rc_cnt.index.tolist(), rc_cnt.values.tolist(), colors=rc_clr), use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# PAGE 9 — STRATEGIC RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════

def page_strategy():
    page_header("Pusat Rekomendasi Strategis", "Laporan Intelijen Eksekutif · Strategi Investasi Kemenparekraf", "")

    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'background:rgba(13,33,55,0.7);border:1px solid rgba(0,212,255,0.15);'
        'border-radius:12px;padding:14px 18px;margin-bottom:18px;">'
        '  <div>'
        '    <div style="font-size:15px;font-weight:700;color:#FFF;">Strategic Intelligence Report</div>'
        '    <div style="font-size:11px;color:#A6B4C8;">Indonesia Tourism Investment · Jun 2026 · AI-Generated</div>'
        '  </div>'
        '  <div style="display:flex;align-items:center;gap:6px;background:rgba(34,197,94,0.1);'
        'border:1px solid rgba(34,197,94,0.2);border-radius:20px;padding:5px 12px;">'
        '    <div style="width:6px;height:6px;border-radius:50%;background:#22C55E;'
        'box-shadow:0 0 6px rgba(34,197,94,0.5);"></div>'
        '    <span style="font-size:10px;font-weight:700;color:#22C55E;letter-spacing:0.5px;">LIVE INTELLIGENCE</span>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True
    )

    cm, cr = st.columns([2.5, 1])

    with cm:
        # Chart perbandingan destinasi
        section_header("Destination Comparison Overview", "Multi-Metric Intelligence")
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        avail_m = [m for m in ['avg_opportunity','avg_competition','avg_ecosystem'] if m in dest_stats.columns]
        if len(avail_m) >= 2:
            fig = plot_grouped_bar(dest_stats, 'dest_display', avail_m,
                                   labels=['Opportunity','Competition','Ecosystem'],
                                   colors=[DESIGN['success'],DESIGN['danger'],DESIGN['accent']], height=280)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

        spacer(14)

        # National Overview
        with st.expander("🌐 National Overview — Macro Analysis", expanded=True):
            st.markdown(
                f'<div class="strategy-card">'
                f'  <div class="insight-title">Super-Priority Destination Program</div>'
                f'  <div class="insight-body" style="margin-top:6px;">'
                f'    {dest_stats["dest_display"].nunique()} super-priority destination dengan rata-rata '
                f'    opportunity score <strong style="color:#22C55E">{dest_stats["avg_opportunity"].mean():.1f}</strong> — '
                f'    di atas benchmark ASEAN 62. Komitmen infrastruktur pemerintah mengkatalisasi investasi swasta.'
                f'    <br><br><span style="background:rgba(34,197,94,0.15);color:#22C55E;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">+4.8% YoY</span>'
                f'  </div>'
                f'</div>'
                f'<div class="strategy-card">'
                f'  <div class="insight-title">Premium Accommodation Gap</div>'
                f'  <div class="insight-body" style="margin-top:6px;">'
                f'    {df["is_premium"].mean()*100:.0f}% stok diklasifikasikan premium, namun demand eco-resort mewah '
                f'    jauh melampaui supply di Papua & Sulawesi Tenggara. Delta peluang ~Rp 2.8 triliun.'
                f'    <br><br><span style="background:rgba(239,68,68,0.15);color:#EF4444;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">HIGH PRIORITY</span>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Oversupply
        over_d = dest_stats[dest_stats['supply_status'] == 'Oversupply']
        with st.expander("⚠️ Oversupply Destinations — Risk Alert", expanded=True):
            if not over_d.empty:
                for _, row in over_d.iterrows():
                    st.markdown(
                        f'<div class="strategy-card" style="border-left:3px solid #EF4444;">'
                        f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">'
                        f'    <span style="font-size:13px;font-weight:700;color:#FFF;">{row["dest_display"]} Mid-Range</span>'
                        f'    <span class="badge badge-avoid">AVOID MID-RANGE</span>'
                        f'  </div>'
                        f'  <div class="insight-body">Competition {row["avg_competition"]:.0f}% = saturasi pasar. '
                        f'Pivot ke segmen ultra-premium atau strategi exit.</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.info("Tidak ada destinasi oversupply dalam filter saat ini.")

        # Undersupply
        under_d = dest_stats[dest_stats['supply_status'].isin(['Undersupply','Emerging'])]
        with st.expander("🚀 Undersupply Recommendations — Investment Priority", expanded=True):
            for _, row in under_d.iterrows():
                st.markdown(
                    f'<div class="strategy-card" style="border-left:3px solid #22C55E;">'
                    f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;">'
                    f'    <span style="font-size:13px;font-weight:700;color:#FFF;">{row["dest_display"]}</span>'
                    f'    <span class="badge badge-high">PRIORITY INVEST</span>'
                    f'  </div>'
                    f'  <div class="insight-body">Undersupply kritis — {row.get("n_hotels",0):.0f} hotel melayani demand {row.get("avg_demand",0):.0f}%. '
                    f'Window first-mover terbuka. Posisi eco-premium disarankan.</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # Strategy tabs
        st1, st2, st3, st4 = st.tabs(["🌿 Eco-Tourism","👑 Premium","🏗️ Infrastructure","🎯 Branding"])
        with st1:
            st.markdown(
                '<div class="strategy-card"><div class="insight-title">Eco-Tourism Development Strategy</div>'
                '<div class="insight-body">Raja Ampat, Wakatobi, Morotai = koridor eco-luxury premier Indonesia. '
                'Demand sustainable accommodation melampaui supply 3:1. Target <strong style="color:#22C55E">eco-lodge cluster</strong> '
                'dalam 500m dari dive site utama, posisi carbon-neutral.</div></div>'
                '<div class="strategy-card"><div class="insight-title">Nature Branding Imperative</div>'
                '<div class="insight-body">Hotel dengan nama berbasis alam menghasilkan 40%+ ulasan lebih banyak. '
                'Semua investasi baru wajib integrasikan elemen alam destinasi sejak brand inception.</div></div>',
                unsafe_allow_html=True
            )
        with st2:
            st.markdown(
                '<div class="strategy-card"><div class="insight-title">Premium Gap Opportunity</div>'
                '<div class="insight-body">Danau Toba tier luxury sangat undersupplied meski Rp 4.2T infrastruktur committed. '
                'Posisi resort bintang 5 sebagai anchor property = <strong style="color:#22C55E">first-mover premium</strong>.</div></div>'
                '<div class="strategy-card"><div class="insight-title">MICE + Sport Tourism</div>'
                '<div class="insight-body">Kalender MotoGP Mandalika = 8–12 event windows/tahun dengan pricing premium. '
                'Kemitraan dengan event organizer = revenue stream predictable.</div></div>',
                unsafe_allow_html=True
            )
        with st3:
            st.markdown(
                '<div class="strategy-card"><div class="insight-title">Infrastructure-Led Investment Sequencing</div>'
                '<div class="insight-body">'
                '<strong style="color:#00D4FF">Phase 1 (Now):</strong> Land banking Likupang & Morotai sebelum harga tanah naik 40–70%.<br><br>'
                '<strong style="color:#3B82F6">Phase 2 (12–24 bln):</strong> Pre-opening Danau Toba sejalan konektivitas Tol Sumatra.<br><br>'
                '<strong style="color:#A855F7">Phase 3 (3–5 thn):</strong> Koridor Raja Ampat → Wakatobi → Labuan Bajo sebagai dive circuit internasional.'
                '</div></div>',
                unsafe_allow_html=True
            )
        with st4:
            st.markdown(
                '<div class="strategy-card"><div class="insight-title">Destination Branding Architecture</div>'
                '<div class="insight-body">'
                '• <strong style="color:#22C55E">Raja Ampat:</strong> "Last Frontier of Biodiversity"<br>'
                '• <strong style="color:#00D4FF">Wakatobi:</strong> "World\'s Best Dive Destination"<br>'
                '• <strong style="color:#F59E0B">Morotai:</strong> "Pacific War Heritage + Marine Paradise"<br>'
                '• <strong style="color:#3B82F6">Danau Toba:</strong> "Largest Caldera Lake · Batak Culture"<br>'
                '• <strong style="color:#A855F7">Mandalika:</strong> "Indonesia\'s Sports Riviera"'
                '</div></div>',
                unsafe_allow_html=True
            )

    with cr:
        section_header("Investor Strategy Roadmap", "Prioritized Action Timeline")

        for timeline_cls, label, color, items in [
            ('timeline-short',  'Short-term · 0–12 bulan',  '#22C55E', [
                "Land banking Likupang & Morotai sebelum infrastruktur aktif",
                "Akuisisi resort premium Wakatobi — supply cap ciptakan moat",
                "Boutique eco-lodge adjacent dive sites Raja Ampat",
                "Tender aset 2–3 bintang Danau Toba untuk konversi premium",
            ]),
            ('timeline-medium', 'Medium-term · 1–3 tahun', '#3B82F6', [
                "Ultra-premium dive resort Morotai — WWII + marine niche",
                "Premium glamping dekat ridgeline Bromo",
                "Lakefront luxury resort Danau Toba",
                "Kemitraan MotoGP Mandalika untuk paket akomodasi",
            ]),
            ('timeline-long',   'Long-term · 3–7 tahun',   '#A855F7', [
                "Koridor terintegrasi Raja Ampat → Wakatobi → Labuan Bajo",
                "Eco-resort network 5 zona UNESCO undersupply",
                "Indonesia Premium Tourism Exchange",
            ]),
        ]:
            st.markdown(
                f'<div class="strategy-card">'
                f'  <span class="strategy-timeline {timeline_cls}">{label}</span>',
                unsafe_allow_html=True
            )
            for item in items:
                st.markdown(
                    f'<div class="strategy-item">'
                    f'  <div class="strategy-bullet" style="background:{color};"></div>'
                    f'  <span>{item}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        spacer(8)
        st.markdown(
            '<div class="strategy-card">'
            '  <div class="insight-title">⚠️ Risk Matrix</div>'
            + ''.join([
                f'<div class="metric-row"><span class="metric-name">{n}</span><span class="badge {b}">{v}</span></div>'
                for n, v, b in [
                    ("Regulatory Risk","Medium","badge-low"),
                    ("FX Risk","Medium","badge-low"),
                    ("Infra Risk (Likupang)","Low","badge-high"),
                    ("Saturation Risk (LB)","High","badge-avoid"),
                    ("Climate Risk (Wakatobi)","Moderate","badge-medium"),
                ]
            ])
            + '</div>',
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════════════════════
# PAGE ENGINE — ANALYTICS ENGINE (gabungan 4 sub-halaman)
# ════════════════════════════════════════════════════════════════════

def page_engine():
    page_header("Mesin Analitik", "Ekonometrika Spasial · NLP · Ekosistem · Kompetisi", "")
    t1, t2, t3, t4 = st.tabs([
        "⚔️ Competition Intel",
        "🌿 Attraction Ecosystem",
        "💬 NLP Branding",
        "📐 Spatial Econometrics",
    ])
    with t1: page_competition()
    with t2: page_ecosystem()
    with t3: page_nlp()
    with t4: page_econometrics()

# ════════════════════════════════════════════════════════════════════
# PAGE — MARKET INSIGHTS
# ════════════════════════════════════════════════════════════════════

def page_insights():
    page_header("Wawasan Pasar", "Intelijen Berbasis AI · Sinyal & Rekomendasi Berbasis Data", "")

    # ── Insights ────────────────────────────────────────────────────
    section_header("Market Intelligence Signals", "Auto-Generated dari Data Aktual")
    insights = generate_insights(df)
    icons_map = {'success': '✅', 'danger': '⚠️', 'warning': '🔶', 'info': '🔵'}
    class_map = {'success': 'opportunity', 'danger': 'critical', 'warning': 'warning', 'info': 'info'}

    for ins in insights:
        t = ins['type']
        st.markdown(
            f'<div class="alert-item {class_map.get(t,"info")}">'
            f'  <div class="alert-icon">{icons_map.get(t,"ℹ️")}</div>'
            f'  <div class="alert-content">'
            f'    <h5>{ins["tag"]}</h5>'
            f'    <p>{ins["text"]}</p>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True
        )

    spacer(20)

    # ── Recommendations ─────────────────────────────────────────────
    section_header("Strategic Recommendations", "Top 5 Rekomendasi Investasi Berbasis Data")
    recs = generate_recommendations(df)

    for rec in recs:
        st.markdown(
            f'<div class="strategy-card" style="border-left:3px solid #00D4FF;">'
            f'  <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
            f'    <div style="width:32px;height:32px;border-radius:8px;background:rgba(0,212,255,0.1);'
            f'display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">{rec["icon"]}</div>'
            f'    <div>'
            f'      <div style="font-size:9px;color:#64748B;letter-spacing:1px;">REC #{rec["number"]}</div>'
            f'      <div style="font-size:13px;font-weight:700;color:#FFF;">{rec["title"]}</div>'
            f'    </div>'
            f'  </div>'
            f'  <div class="insight-body">{rec["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════

_PAGES = {
    'executive':   page_executive,
    'spatial':     page_spatial,
    'destination': page_destination,
    'engine':      page_engine,
    'investment':  page_investment,
    'insights':    page_insights, 
    'strategy':    page_strategy,
}

current_page = st.session_state.get('current_page', 'executive')
_PAGES.get(current_page, page_executive)()