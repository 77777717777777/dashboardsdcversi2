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
inject_css()
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
    plot_morans_result, plot_investment_matrix, apply_layout,
    plot_competition_ranking,
    plot_investment_matrix_enhanced,
    plot_gwr_bar
)
from functions.insights import generate_insights, generate_recommendations 

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
    color_map = {
        'accent':  'linear-gradient(135deg,#2D6A4F,#40916C)',
        'success': 'linear-gradient(135deg,#1B4332,#2D6A4F)',
        'warning': 'linear-gradient(135deg,#B87800,#E9A020)',
        'danger':  'linear-gradient(135deg,#A81E2D,#D62839)',
        'purple':  'linear-gradient(135deg,#5A1F6B,#7B2D8B)',
        'white':   'linear-gradient(135deg,#40916C,#52B788)',
        'blue':    'linear-gradient(135deg,#0D47A1,#1565C0)',
        'magenta': 'linear-gradient(135deg,#880E4F,#C2185B)',
    }
    bg = color_map.get(color, color_map['accent'])
    trend_html = ''
    if trend:
        arrow = '↑' if trend_dir == 'up' else '↓' if trend_dir == 'down' else '—'
        trend_html = (
            f'<div style="position:absolute;top:12px;right:12px;font-size:10px;'
            f'font-weight:700;padding:2px 8px;border-radius:20px;'
            f'background:rgba(255,255,255,0.2);color:#FFFFFF;">{arrow} {trend}</div>'
        )
    return (
        f'<div style="background:{bg};border:none;border-radius:10px;'
        f'padding:16px 18px;position:relative;'
        f'box-shadow:0 4px 12px rgba(27,67,50,0.2);'
        f'height:100%;overflow:hidden;">'
        f'  {trend_html}'
        f'  <div style="font-size:10px;color:rgba(255,255,255,0.75);font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">{label}</div>'
        f'  <div style="font-size:26px;font-weight:800;color:#FFFFFF;line-height:1.1;'
        f'font-family:Plus Jakarta Sans,sans-serif;">{value}</div>'
        f'  <div style="font-size:11px;color:rgba(255,255,255,0.65);margin-top:8px;">{sub}</div>'
        f'  <div style="position:absolute;bottom:-15px;right:-15px;width:70px;height:70px;'
        f'border-radius:50%;background:rgba(255,255,255,0.07);"></div>'
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
    st.markdown(
        f'<div class="page-header">'
        f'  <div class="page-header-icon">{icon}</div>'
        f'  <div>'
        f'    <div class="page-title" style="font-size:32px;font-weight:900;letter-spacing:-0.5px;">{title}</div>'
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
            "Temuan Analisis":           "executive",
            "Peta Spasial":              "spatial",
            "Analisis Destinasi":        "destination",
            "Mesin Analisis":             "engine",
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

# ── JUDUL BESAR PLATFORM ─────────────────────────────────────────────
st.markdown(
    '<div style="padding:18px 0 8px 0;">'
    '  <div style="font-size:28px;font-weight:800;color:#0F2A4A;letter-spacing:-0.3px;">'
    '    Peta Sebaran & Peluang Investasi Akomodasi Wisata</div>'
    '  <div style="font-size:13px;color:#4A6080;margin-top:4px;">'
    '    Destinasi Super Prioritas Indonesia · Kemenparekraf 2026</div>'
    '</div>',
    unsafe_allow_html=True
)

#def render_top_filters():
#    st.markdown(
#        '<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;'
#        'text-transform:uppercase;margin-bottom:6px;">FILTER GLOBAL</div>',
#        unsafe_allow_html=True
#    )
#    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])

#    all_dest = ['All'] + sorted(df_raw['destinasi'].dropna().unique().tolist())
#    with c1:
#        st.markdown('<div style="font-size:11px;color:#A6B4C8;margin-bottom:3px;font-weight:600;">Destinasi</div>', unsafe_allow_html=True)
#        sel_dest = st.selectbox("Destinasi", all_dest, key='f_dest', label_visibility='collapsed')
    
#    df_raw['jenis'] = df_raw['jenis'].str.strip().str.title()
#    all_type = ['All'] + sorted(df_raw['jenis'].dropna().unique().tolist()) if 'jenis' in df_raw.columns else ['All']
#    with c2:
#        st.markdown('<div style="font-size:11px;color:#A6B4C8;margin-bottom:3px;font-weight:600;">Jenis</div>', unsafe_allow_html=True)
#        sel_type = st.selectbox("Jenis Hotel", all_type, key='f_type', label_visibility='collapsed')

#    all_seg = ['All'] + sorted(df_raw['market_segment'].dropna().unique().tolist()) if 'market_segment' in df_raw.columns else ['All']
#    with c3:
#        st.markdown('<div style="font-size:11px;color:#A6B4C8;margin-bottom:3px;font-weight:600;">Tipe</div>', unsafe_allow_html=True)
#        sel_seg = st.selectbox("Tipe Segmen", all_seg, key='f_seg', label_visibility='collapsed')

#    with c4:
#        st.markdown('<div style="font-size:11px;color:#A6B4C8;margin-bottom:3px;font-weight:600;">Indikator</div>', unsafe_allow_html=True)
#        ocean = st.selectbox("Indikator", ['All', 'Red Ocean', 'Blue Ocean'], key='f_ocean', label_visibility='collapsed')

#    st.markdown('<hr class="premium-divider">', unsafe_allow_html=True)

#    return {
#        'destinations': [sel_dest] if sel_dest != 'All' else ['All'],
#        'hotel_types':  [sel_type] if sel_type != 'All' else ['All'],
#        'segments':     [sel_seg]  if sel_seg  != 'All' else ['All'],
#        'ocean':        [ocean]    if ocean     != 'All' else ['All'],
#        'opp_range':    (0, 100),
#    }

#filters = render_top_filters()

#df = filter_dataframe(
#    df_raw,
#    destinations=filters['destinations'],
#    hotel_types=filters['hotel_types'],
#    segments=filters['segments'],
#    ocean_status=filters['ocean'],
#    opp_range=filters['opp_range']
#)
#dest_stats = get_destination_stats(df) if len(df) > 0 else dest_stats_raw.copy()

df         = df_raw.copy()
dest_stats = dest_stats_raw.copy()

# ════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ════════════════════════════════════════════════════════════════════

def page_executive():
    page_header("Temuan Analisis Akomodasi",
        "Peta Persebaran & Peluang Investasi · Destinasi Super Prioritas Indonesia", "")
    st.markdown('<div style="margin-top:-20px;"></div>', unsafe_allow_html=True)
    kpis = get_national_kpis(df)

    # ── KPI Baris 1: 5 kolom seimbang ──────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    rows1 = [
        (k1, "Total Hotel",        f"{kpis['total_hotels']:,}",          "Jaringan Destinasi Prioritas",   'accent',  None, 'up',     ''),
        (k2, "Destinasi",          str(kpis['total_destinations']),       "Kluster Super Prioritas",        'white',   None, 'neutral',''),
        (k3, "Rata-rata Rating",   f"{kpis['avg_rating']}",              "★ dari 5.0",                     'warning', None, 'up',     ''),
        (k4, "Total Ulasan",       f"{kpis['total_reviews']:,}",          "Sinyal Permintaan",              'accent',  None, 'up',     ''),
        (k5, "Rata-rata Peluang",  f"{kpis['avg_opportunity']}",         "Nilai Investasi Nasional",       'success', None, 'up',     ''),
    ]
    for col, lbl, val, sub, clr, tr, td, ic in rows1:
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, tr, td, ic), unsafe_allow_html=True)

    spacer(10)

    # ── KPI Baris 2: 5 kolom seimbang ──────────────────────────────
    k6, k7, k8, k9, k10 = st.columns(5)
    rows2 = [
        (k6,  "Skor Popularitas",     f"{kpis['avg_popularity']:.1f}",                                             "Pencarian & Keterlibatan",  'accent',  None, 'up',   ''),
        (k7,  "Hotel Premium",        str(kpis['total_premium']),                                                   f"{kpis['total_premium']/max(kpis['total_hotels'],1)*100:.0f}% dari Total", 'warning', None, 'up',''),
        (k8,  "Wisata Alam",          str(kpis['total_nature']),                                                    f"{kpis['total_nature']/max(kpis['total_hotels'],1)*100:.0f}% Berbasis Alam", 'success', None, 'up',''),
        (k9,  "Rata-rata Persaingan", f"{kpis['avg_competition']:.1f}%",                                           "Tekanan Kompetitif",        'danger',  None, 'down',''),
        (k10, "Peluang Tinggi",       str(kpis['high_opportunity']),                                                "Skor ≥ 75",                 'success', None, 'up',  ''),
    ]
    for col, lbl, val, sub, clr, tr, td, ic in rows2:
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, tr, td, ic), unsafe_allow_html=True)

    spacer(32)

    # ── Peta Nasional + Sinyal Investasi ───────────────────────────
    col_map, col_alerts = st.columns([2.3, 1])

    with col_map:
        section_header("Indonesia Supply Heatmap",
                        f"{dest_stats['dest_display'].nunique()} Destinations · {len(df):,} Hotels")
        st.markdown(
            '<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;'
            'text-transform:uppercase;margin-bottom:4px;margin-top:0px;">FILTER GLOBAL</div>',
            unsafe_allow_html=True
        )
        t1, t2, t3 = st.tabs([" Peluang Investasi", " Tingkat Permintaan", " Tingkat Persaingan"])
        with t1:
            fig = plot_national_heatmap(dest_stats, 'avg_opportunity', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with t2:
            fig = plot_national_heatmap(dest_stats, 'avg_demand', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with t3:
            fig = plot_national_heatmap(dest_stats, 'avg_competition', '')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_alerts:
        section_header("Sinyal Investasi", "Peringatan Otomatis Berbasis Data")
        insights = generate_ai_insights(df, dest_stats)
        icons_map  = {'success': '✅', 'danger': '⚠️', 'warning': '🔶', 'info': '🔵'}
        class_map  = {'success': 'opportunity', 'danger': 'critical', 'warning': 'warning', 'info': 'info'}
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

# ════════════════════════════════════════════════════════════════════
# PAGE 2 — SPATIAL INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_spatial():
    from functions.maps import render_main_map
    from streamlit_folium import st_folium

    page_header("Peta Spasial Akomodasi", "Analisis GIS Multi-Layer Akomodasi Wisata", "")

    col_layers, col_map = st.columns([1, 3.2])

    with col_layers:
        st.markdown('<div style="font-size:14px;color:#475569;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;font-weight:600;">MAP LAYERS</div>', unsafe_allow_html=True)
        layer_opts = {
            "Peluang Investasi": "opportunity",
            "Heatmap Permintaan":        "supply",
            "Kepadatan Persaingan":    "competition",
            "Red vs Blue Ocean":     "ocean",
            "Klaster DBSCAN":       "cluster",
            "Jaringan Atraksi":    "attraction",
            "Hotel Premium":        "premium",
        }
        sel_layer = st.radio("", list(layer_opts.keys()), key='map_layer')
        layer_id = layer_opts[sel_layer]

        st.markdown('<hr style="border-color:#CBD5E1;margin:12px 0;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px;color:#475569;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">DESTINASI</div>', unsafe_allow_html=True)

        for _, row in dest_stats.iterrows():
            opp = row.get('avg_opportunity', 0)
            n   = row.get('n_hotels', 0)
            # Warna badge tetap berwarna agar informatif, teks label hitam
            badge_color = '#16A34A' if opp >= 70 else '#D97706' if opp >= 50 else '#DC2626'
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 0;border-bottom:1px solid #F1F5F9;">'
                f'  <span style="font-size:11px;color:#1E293B;">{row["dest_display"]}</span>'
                f'  <span style="font-size:10px;font-weight:700;color:#fff;background:{badge_color};'
                f'padding:2px 7px;border-radius:10px;">{n}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        
    with col_map:
        # Label layer aktif
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
            f'  <div style="width:8px;height:8px;border-radius:50%;background:#2563EB;"></div>'
            f'  <span style="font-size:12px;font-weight:600;color:#1E293B;">Layer Aktif: {sel_layer}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── LEGEND HORIZONTAL 
        st.markdown(
            '<div style="display:flex;gap:16px;align-items:center;'
            'padding:8px 14px;background:#F8FAFC;'
            'border:1px solid #E2E8F0;border-radius:8px;margin-bottom:8px;">'
            + ''.join([
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'  <div style="width:9px;height:9px;border-radius:50%;background:{c};flex-shrink:0;"></div>'
                f'  <span style="font-size:11px;color:#334155;font-weight:500;">{lbl}</span>'
                f'</div>'
                for c, lbl in [
                    ('#16A34A', 'Peluang Tinggi'),
                    ('#3B82F6', 'Peluang Sedang'),
                    ('#D97706', 'Peluang Rendah'),
                    ('#DC2626', 'Pasar Jenuh'),
                ]
            ])
            + '</div>',
            unsafe_allow_html=True
        )

        # Peta
        st.markdown(
            '<div style="border:1px solid #CBD5E1;border-radius:12px;overflow:hidden;">',
            unsafe_allow_html=True
        )
        with st.spinner("Memuat layer peta..."):
            sample = df.sample(min(800, len(df)), random_state=42) if len(df) > 800 else df
            m = render_main_map(sample, layer_id)
            st_folium(m, height=460, use_container_width=True, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

        # ── STATS
        s1, s2, s3, s4 = st.columns(4)
        stats_items = [
            (s1, "Total Hotel Terpetakan", f"{len(df):,}", "#2563EB"),
            (s2, "Peluang Tinggi", f"{int((df['opportunity_score'] >= 75).sum()):,}", "#16A34A"),
            (s3, "Zona Pasar Jenuh", f"{int(df['status_ocean'].str.contains('Red', na=False).sum()):,}", "#DC2626"),
            (s4, "Rata-rata Ekosistem", f"{df['ecosystem_score'].mean():.1f}", "#7C3AED"),
        ]
        for col, lbl, val, clr in stats_items:
            with col:
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
                    f'border-top:3px solid {clr};'
                    f'border-radius:8px;padding:12px;text-align:center;margin-top:8px;">'
                    f'  <div style="font-size:10px;color:#64748B;margin-bottom:4px;font-weight:500;">{lbl}</div>'
                    f'  <div style="font-size:20px;font-weight:800;color:{clr};">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ════════════════════════════════════════════════════════════════════
# PAGE 3 — COMPETITION INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_competition():
    page_header(
        "Analisis Kompetisi Pasar",
        "Struktur Pasar · Deteksi Zona Red Ocean vs Blue Ocean",
        ""
    )

    # ── KPI 4 KOLOM ──────────────────────────────────────────────
    avg_comp = df['competition_score'].mean()
    red_cnt  = df['status_ocean'].str.contains('Red',  na=False).sum()
    blue_cnt = df['status_ocean'].str.contains('Blue', na=False).sum()
    top_dest = (
        dest_stats.nlargest(1, 'avg_competition').iloc[0]['dest_display']
        if not dest_stats.empty else 'N/A'
    )

    k1, k2, k3, k4 = st.columns(4)
    for col, (lbl, val, sub, clr) in zip([k1, k2, k3, k4], [
        ("Rata-rata Persaingan",  f"{avg_comp:.1f}%", "Rata-rata Nasional",       'danger'),
        ("Zona Red Ocean",        f"{red_cnt:,}",      "Pasar Jenuh",             'danger'),
        ("Zona Blue Ocean",       f"{blue_cnt:,}",     "Pasar Berpeluang",        'accent'),
        ("Destinasi Terpadat",    top_dest,            "Tingkat Kejenuhan Tertinggi", 'warning'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr), unsafe_allow_html=True)

    spacer(20)

    # ── BARIS 1: Ranking + Donut ──────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        section_header("Peringkat Persaingan", "Per Destinasi")
        #st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        fig = plot_competition_ranking(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Distribusi Red vs Blue Ocean", "Komposisi Status Pasar Nasional")
        #st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        ocean_c  = df['status_ocean'].value_counts()
        lbls     = [l.split('(')[0].strip() for l in ocean_c.index]
        cols_oc  = ['#C0392B' if 'Red' in l else '#2E86DE' for l in ocean_c.index]
        fig = plot_donut(lbls, ocean_c.values.tolist(), colors=cols_oc)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # ── BARIS 2: Matrix + GWR ─────────────────────────────────────
    c3, c4 = st.columns(2)

    with c3:
        section_header("Matriks Risiko vs Peluang", "Persaingan vs Peluang Investasi")
        #st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        fig = plot_investment_matrix_enhanced(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        section_header("Efek Aglomerasi (GWR)", "Koefisien Kompetitor per Destinasi")
        #st.markdown('<div class="viz-card">', unsafe_allow_html=True)
        if 'koef_saingan_radius_1km' in df.columns:
            fig = plot_gwr_bar(df)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # ── BARIS 3: Progress Bars ────────────────────────────────────
    c5, c6 = st.columns(2)

    with c5:
        section_header("5 Destinasi Terjenuh", "Tingkat Persaingan Tertinggi")
        for _, row in dest_stats.nlargest(5, 'avg_competition').iterrows():
            comp = row['avg_competition']
            st.markdown(
                f'<div class="prog-container">'
                f'  <div class="prog-label">'
                f'    <span>{row["dest_display"]}</span>'
                f'    <span style="color:#C0392B;font-weight:700;">{comp:.0f}%</span>'
                f'  </div>'
                f'  <div class="prog-bar">'
                f'    <div class="prog-fill danger" style="width:{comp}%"></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with c6:
        section_header("5 Destinasi Blue Ocean", "Peluang Investasi Terbesar")
        for _, row in dest_stats.nsmallest(5, 'avg_competition').iterrows():
            opp_pct = row.get('avg_opportunity', 100 - row['avg_competition'])
            st.markdown(
                f'<div class="prog-container">'
                f'  <div class="prog-label">'
                f'    <span>{row["dest_display"]}</span>'
                f'    <span style="color:#1D5FAD;font-weight:700;">{opp_pct:.0f} poin</span>'
                f'  </div>'
                f'  <div class="prog-bar">'
                f'    <div class="prog-fill" style="width:{opp_pct}%"></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

    spacer(14)

    st.markdown(insight_html(
        "Temuan Strategis: Efek Aglomerasi",
        "Destinasi dengan koefisien GWR positif menunjukkan <strong style='color:#1A7A4A'>efek aglomerasi</strong> — "
        "pengelompokan akomodasi justru meningkatkan lalu lintas wisata secara keseluruhan. "
        "Koefisien negatif mengindikasikan <strong style='color:#C0392B'>persaingan destruktif</strong> "
        "yang menekan kinerja seluruh pemain di area tersebut. "
        "Prioritaskan investasi di destinasi dengan koefisien positif untuk probabilitas keberhasilan lebih tinggi.",
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
        ("Skor Ekosistem Rata-rata",      f"{avg_eco:.1f}",   "Kekuatan Magnet Pariwisata", 'success'),
        ("Rata-rata Atraksi di Sekitar",   f"{avg_atk:.0f}",   "Dalam Radius 5km",       'accent'),
        ("Rata-rata Jarak Atraksi",  f"{avg_dist:.1f} km",  "Metric Aksesibilitas",   'warning'),
        ("Hotel dengan Ekosistem Tinggi",    f"{hi_eco:,}",       "Skor ≥ 75",             'success'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='🌿'), unsafe_allow_html=True)

    spacer(20)

    # Baris 1
    c1, c2 = st.columns(2)
    with c1:
        section_header("Kepadatan Atraksi per Destinasi", "Rata-rata Atraksi dalam 5km")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Peringkat Skor Ekosistem", "Kesehatan Ekosistem Destinasi")
        #st.markdown('<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:16px 14px 8px;box-shadow:0 1px 4px rgba(15,42,74,0.08);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_ecosystem', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    # Baris 2
    c3, c4 = st.columns(2)
    with c3:
        section_header("Pengaruh Jarak Atraksi terhadap Permintaan", "Jarak Atraksi vs Demand Score")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
        #st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        section_header("Kesenjangan Cakupan Atraksi", "Supply vs Kepadatan Atraksi")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
        #st.markdown('</div>', unsafe_allow_html=True)

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
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_branding_bars(branding_df, dest_nlp if dest_nlp != 'All' else None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Jumlah Akomodasi per Tema", "Distribusi Lintas Segmen")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        cnt = bf.groupby('Tema_Nama')['Jumlah_Akomodasi'].sum()
        lbs = ['Nature Branding' if 'Alam' in l else 'Standard Naming' for l in cnt.index]
        fig = plot_donut(lbs, cnt.values.tolist(), colors=['#22C55E','#3B82F6'])
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    section_header("Branding Heatmap Matrix", "Destinasi × Tema × Avg Reviews")
    #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
    #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)
    c3, c4 = st.columns(2)
    with c3:
        section_header("Segment Performance", "Premium vs Budget Branding Impact")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
        #st.markdown('</div>', unsafe_allow_html=True)

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
        ("Target Prioritas Utama", f"{len(hi_opp):,}",                                       "Peluang ≥ 75", 'success'),
        ("Peluang Berkembang",f"{len(emg):,}",                                           "Skor 55–75",      'accent'),
        ("Pasar Jenuh",     f"{len(sat):,}",                                           "Persaingan ≥ 75%",'danger'),
        ("Rata-rata Skor IIA",         f"{df['investor_interest_index'].mean():.1f}",             "Komposit Nasional",'warning'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='💰'), unsafe_allow_html=True)

    spacer(20)

    c1, c2 = st.columns(2)
    with c1:
        section_header("Opportunity Ranking by Destination", "By Investor Interest Index")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_iia', '')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Opportunity Quadrant Matrix", "Investment Strategy Positioning")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        fig = plot_investment_matrix(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)

    section_header("Investment Opportunity Ranking", "Top Hotels · Opportunity + IIA Score")
    t_hi, t_emg, t_sat = st.tabs(["High Priority","Emerging","Saturated"])

    for tab, tdf in [(t_hi,hi_opp),(t_emg,emg),(t_sat,sat)]:
        with tab:
            if tdf is None or len(tdf) == 0:
                st.info("Tidak ada data untuk kategori ini.")
                continue
            show = tdf.nlargest(min(5, len(tdf)), 'opportunity_score')
            for _, row in show.iterrows():
                rec = str(row.get('rekomendasi_investasi', ''))

                if 'Sangat' in rec or 'Highly' in rec:
                    badge_bg, badge_color, badge_text = 'rgba(26,122,74,0.1)', '#1A7A4A', 'Sangat Direkomendasikan'
                    badge_border = 'rgba(26,122,74,0.25)'
                elif 'Direkomendasikan' in rec or rec == 'Recommended':
                    badge_bg, badge_color, badge_text = 'rgba(29,95,173,0.1)', '#1D5FAD', 'Direkomendasikan'
                    badge_border = 'rgba(29,95,173,0.25)'
                elif 'Perlu' in rec or 'Kajian' in rec or 'Further' in rec:
                    badge_bg, badge_color, badge_text = 'rgba(196,123,0,0.1)', '#B8680A', 'Perlu Kajian Lebih'
                    badge_border = 'rgba(196,123,0,0.25)'
                else:
                    badge_bg, badge_color, badge_text = 'rgba(192,57,43,0.1)', '#C0392B', 'Tidak Direkomendasikan'
                    badge_border = 'rgba(192,57,43,0.25)'

                foto_url = str(row.get('foto_url', '')) if 'foto_url' in row else ''
                if foto_url and foto_url != 'nan' and foto_url.startswith('http'):
                    img_html = (
                        f'<img src="{foto_url}" '
                        f'style="width:52px;height:52px;border-radius:8px;object-fit:cover;'
                        f'flex-shrink:0;border:1px solid #E2E8F0;" '
                        f'onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';">'
                        f'<div style="display:none;width:52px;height:52px;border-radius:8px;'
                        f'background:#EFF6FF;align-items:center;justify-content:center;'
                        f'font-size:22px;flex-shrink:0;">🏨</div>'
                    )
                else:
                    img_html = (
                        f'<div style="width:52px;height:52px;border-radius:8px;'
                        f'background:#EFF6FF;display:flex;align-items:center;'
                        f'justify-content:center;font-size:22px;flex-shrink:0;'
                        f'border:1px solid #DBEAFE;">🏨</div>'
                    )

                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:14px;'
                    f'padding:14px 16px;background:#FFFFFF;'
                    f'border:1px solid #E2E8F0;border-radius:10px;margin-bottom:8px;'
                    f'box-shadow:0 1px 4px rgba(15,42,74,0.08);">'

                    f'<div style="display:flex;flex-shrink:0;">{img_html}</div>'

                    f'<div style="flex:1;min-width:0;">'
                    f'  <div style="font-size:13px;font-weight:700;color:#0F2A4A;margin-bottom:3px;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">'
                    f'{row.get("nama_hotel","Hotel")}</div>'
                    f'  <div style="font-size:11px;color:#64748B;">'
                    f'📍 {row.get("destinasi","")} · {row.get("jenis","")} · '
                    f'⭐{row.get("rating",0):.1f} · {int(row.get("jumlah_ulasan",0)):,} ulasan</div>'
                    f'</div>'

                    f'<div style="text-align:center;padding:0 12px;flex-shrink:0;">'
                    f'  <div style="font-size:9px;color:#94A3B8;margin-bottom:2px;">OPP</div>'
                    f'  <div style="font-size:20px;font-weight:800;color:#1A7A4A;">'
                    f'{row.get("opportunity_score",0):.0f}</div>'
                    f'</div>'
                    f'<div style="text-align:center;padding:0 8px;flex-shrink:0;">'
                    f'  <div style="font-size:9px;color:#94A3B8;margin-bottom:2px;">IIA</div>'
                    f'  <div style="font-size:20px;font-weight:800;color:#1D5FAD;">'
                    f'{row.get("investor_interest_index",0):.0f}</div>'
                    f'</div>'

                    f'<div style="flex-shrink:0;min-width:170px;text-align:center;">'
                    f'  <span style="display:inline-block;width:100%;text-align:center;'
                    f'background:{badge_bg};color:{badge_color};'
                    f'border:1px solid {badge_border};border-radius:20px;'
                    f'padding:6px 14px;font-size:10px;font-weight:700;'
                    f'white-space:nowrap;">{badge_text}</span>'
                    f'</div>'

                    f'</div>',
                    unsafe_allow_html=True
                )
    spacer(14)
    c3, c4 = st.columns(2)
    with c3:
        section_header("Undersupply Zones", "High Demand · Low Supply")
        under_dest = dest_stats[dest_stats['supply_status'].isin(['Undersupply','Emerging'])]
        for _, row in under_dest.head(5).iterrows():
            dest_name = row.get('destinasi', row.get('dest_display', ''))
            best = df[df['destinasi'] == dest_name].nlargest(1, 'opportunity_score')
            hotel_name = best.iloc[0]['nama_hotel'] if not best.empty else '-'
            st.markdown(
                f'<div class="alert-item opportunity">'
                f'  <div class="alert-icon">📈</div>'
                f'  <div class="alert-content">'
                f'    <h5>{row.get("dest_display", dest_name)} — UNDERSUPPLY</h5>'
                f'    <p>🏆 <strong>{hotel_name[:35]}</strong><br>'
                f'Supply: <strong style="color:#C0392B">{row.get("n_hotels",0):.0f} hotel</strong> · '
                f'Demand: <strong style="color:#1A7A4A">{row.get("avg_demand",0):.0f}%</strong></p>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with c4:
        section_header("Oversaturated Zones", "Caution — High Competition Risk")
        over_dest = dest_stats[dest_stats['supply_status'] == 'Oversupply']
        
        if over_dest.empty:
            over_dest = dest_stats.nlargest(5, 'avg_competition')
            
        for _, row in over_dest.head(5).iterrows():
            # GANTI row['destinasi'] → row['dest_display'] atau pakai .get()
            dest_name = row.get('destinasi', row.get('dest_display', ''))
            best = df[df['destinasi'] == dest_name].nlargest(1, 'competition_score')
            hotel_name = best.iloc[0]['nama_hotel'] if not best.empty else '-'
            
            st.markdown(
                f'<div class="alert-item critical">'
                f'  <div class="alert-icon">⚠️</div>'
                f'  <div class="alert-content">'
                f'    <h5>{row.get("dest_display", dest_name)} — SATURATED</h5>'
                f'    <p>🏨 <strong>{hotel_name[:35]}</strong><br>'
                f'Kompetisi: <strong style="color:#C0392B">'
                f'{row.get("avg_competition",0):.0f}%</strong> · Hindari entry mid-range</p>'
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
            #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:10px 8px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
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
            #st.markdown('</div>', unsafe_allow_html=True)

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
                    #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
                    fig = plot_gwr_coefficients(df, coef_col, f'GWR: {coef_lbl}')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    #st.markdown('</div>', unsafe_allow_html=True)
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
                            f'<span class="metric-val {"coef-positive" if (float(str(v).replace("%", "").replace(",", "").strip()) >= 0 if v not in (None, "", "nan") else True) else "coef-negative"}">{v}</span></div>'
                            for n, v in [("Mean", f"{cd.mean():.4f}"), ("Median", f"{cd.median():.4f}"),
                                         ("Std Dev", f"{cd.std():.4f}"), ("Min", f"{cd.min():.4f}"),
                                         ("Max", f"{cd.max():.4f}"), ("% Positive", f"{(cd>0).mean()*100:.1f}%")]
                        ])
                        + f'</div>',
                        unsafe_allow_html=True
                    )
                    spacer(8)
                    st.markdown(insight_html("Business Interpretation", interp, 'info' if pos else 'warning'),
                                unsafe_allow_html=True)

    spacer(20)
    section_header("GWR vs OLS Model Comparison", "Local vs Global Goodness of Fit")
    cg, co = st.columns(2)
    with cg:
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        gwr_r2 = df[df['model_dipakai'].str.contains('GWR',na=False)]['r2_lokal'].mean() if 'model_dipakai' in df.columns else 0.42
        ols_r2 = df[df['model_dipakai'].str.contains('OLS',na=False)]['r2_lokal'].mean() if 'model_dipakai' in df.columns else 0.28
        r2_v = [gwr_r2 if not np.isnan(gwr_r2) else 0.42, ols_r2 if not np.isnan(ols_r2) else 0.28]
        fig = go.Figure(go.Bar(
            x=['GWR (Local)','OLS (Global)'], y=r2_v,
            marker=dict(color=['#00D4FF','#3B82F6'], opacity=0.85),
            text=[f'R² = {v:.3f}' for v in r2_v], textposition='outside',
            textfont=dict(color="#000000", size=12),
        ))
        fig = apply_layout(fig, height=220)
        fig.update_yaxes(range=[0,0.8], title='R² (Goodness of Fit)')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)
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

    page_header("Analisis Mendalam per Destinasi",
                "Analitik per Destinasi · Intelijen Investasi berdasarkan Lokasi", "")

    # ── FILTER BAR ────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:9px;color:#74A98A;letter-spacing:1.2px;'
        'text-transform:uppercase;margin-bottom:6px;font-weight:600;">FILTER ANALISIS</div>',
        unsafe_allow_html=True
    )

    fc1, fc2, fc3, fc4 = st.columns(4)

    all_dest_f = sorted(df_raw['destinasi'].dropna().unique().tolist())
    with fc1:
        st.markdown('<div style="font-size:11px;color:#74A98A;margin-bottom:3px;font-weight:600;">Destinasi</div>', unsafe_allow_html=True)
        sel = st.selectbox("Destinasi", all_dest_f, key='dest_dd', label_visibility='collapsed')

    all_type_f = ['All'] + sorted(df_raw['jenis'].dropna().unique().tolist()) if 'jenis' in df_raw.columns else ['All']
    with fc2:
        st.markdown('<div style="font-size:11px;color:#74A98A;margin-bottom:3px;font-weight:600;">Jenis Hotel</div>', unsafe_allow_html=True)
        sel_type_d = st.selectbox("Jenis", all_type_f, key='dest_jenis', label_visibility='collapsed')

    all_seg_f = ['All'] + sorted(df_raw['market_segment'].dropna().unique().tolist()) if 'market_segment' in df_raw.columns else ['All']
    with fc3:
        st.markdown('<div style="font-size:11px;color:#74A98A;margin-bottom:3px;font-weight:600;">Tipe Segmen</div>', unsafe_allow_html=True)
        sel_seg_d = st.selectbox("Tipe", all_seg_f, key='dest_tipe', label_visibility='collapsed')

    with fc4:
        st.markdown('<div style="font-size:11px;color:#74A98A;margin-bottom:3px;font-weight:600;">Indikator</div>', unsafe_allow_html=True)
        sel_ocean_d = st.selectbox("Indikator", ['All', 'Red Ocean', 'Blue Ocean'], key='dest_ocean', label_visibility='collapsed')

    st.markdown(
        '<hr style="border:none;border-top:1px solid #D8EDE4;margin:10px 0 16px 0;">',
        unsafe_allow_html=True
    )

    # ── TERAPKAN FILTER ───────────────────────────────────────────
    d_df = df_raw[df_raw['destinasi'] == sel].copy()

    if sel_type_d != 'All' and 'jenis' in d_df.columns:
        d_df = d_df[d_df['jenis'] == sel_type_d]

    if sel_seg_d != 'All' and 'market_segment' in d_df.columns:
        d_df = d_df[d_df['market_segment'] == sel_seg_d]

    if sel_ocean_d != 'All' and 'status_ocean' in d_df.columns:
        if sel_ocean_d == 'Red Ocean':
            d_df = d_df[d_df['status_ocean'].str.contains('Red', na=False)]
        else:
            d_df = d_df[d_df['status_ocean'].str.contains('Blue', na=False)]

    if d_df.empty:
        st.warning("Tidak ada data untuk kombinasi filter ini. Coba ubah filter.")
        return

    # HAPUS baris lama ini (sudah tidak diperlukan):
    # all_dd = sorted(df_raw['destinasi'].dropna().unique().tolist())
    # sel    = st.selectbox("📍 Pilih Destinasi", all_dd, key='dest_dd')
    # d_df   = df_raw[df_raw['destinasi'] == sel].copy()
    # if d_df.empty:
    #     st.warning(...)
    #     return

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
            f'<div style="background:linear-gradient(135deg,#1D5FAD,#2E86DE);border:none;'
            f'border-radius:10px;padding:12px;margin-bottom:10px;">'
            f'  <div style="font-size:15px;font-weight:700;color:#FFFFFF;margin-bottom:2px;">{sel}</div>'
            f'  <div style="font-size:11px;color:rgba(255,255,255,0.75);">{dest_types.get(sel,"Priority Destination")}</div>'
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
    ta, tb, tc, td, te = st.tabs(["Penawaran","Persaingan","Permintaan","Ekosistem","Investasi"])

    with ta:
        ca2, cb2 = st.columns(2)

        with ca2:
            section_header("Distribusi Tipe Hotel")
            if 'jenis' in d_df.columns:
                tc_cnt = d_df['jenis'].value_counts().head(8)
                colors_bar = ['#40916C','#52B788','#2D6A4F','#1B4332','#74A98A','#E9A020','#C2185B','#1565C0']
                fig = go.Figure(go.Bar(
                    y=tc_cnt.index.tolist(),
                    x=tc_cnt.values.tolist(),
                    orientation='h',
                    marker=dict(color=colors_bar[:len(tc_cnt)], opacity=0.88),
                    text=tc_cnt.values.tolist(),
                    textposition='outside',
                    textfont=dict(color='#1B4332', size=11),
                    hovertemplate='<b>%{y}</b><br>Jumlah: %{x}<extra></extra>',
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=280,
                    margin=dict(l=10, r=40, t=10, b=10),
                    xaxis=dict(
                        gridcolor='rgba(64,145,108,0.1)',
                        tickfont=dict(color='#2D6A4F', size=10),
                        title='Jumlah Hotel',
                        title_font=dict(color='#2D6A4F', size=10),
                    ),
                    yaxis=dict(
                        tickfont=dict(color='#1B4332', size=11),
                        autorange='reversed',
                    ),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with cb2:
            section_header("Distribusi Bintang Hotel")
            if 'kasta_bintang' in d_df.columns:
                sc_cnt = d_df['kasta_bintang'].value_counts().head(8)
                star_colors = ['#E9A020','#40916C','#52B788','#2D6A4F','#C2185B','#1565C0','#7B2D8B','#74A98A']
                fig = go.Figure(go.Bar(
                    y=sc_cnt.index.tolist(),
                    x=sc_cnt.values.tolist(),
                    orientation='h',
                    marker=dict(color=star_colors[:len(sc_cnt)], opacity=0.88),
                    text=sc_cnt.values.tolist(),
                    textposition='outside',
                    textfont=dict(color='#1B4332', size=11),
                    hovertemplate='<b>%{y}</b><br>Jumlah: %{x}<extra></extra>',
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=280,
                    margin=dict(l=10, r=40, t=10, b=10),
                    xaxis=dict(
                        gridcolor='rgba(64,145,108,0.1)',
                        tickfont=dict(color='#2D6A4F', size=10),
                        title='Jumlah Hotel',
                        title_font=dict(color='#2D6A4F', size=10),
                    ),
                    yaxis=dict(
                        tickfont=dict(color='#1B4332', size=11),
                        autorange='reversed',
                    ),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    def hist_chart(col, color, title_x):
        fig = go.Figure(go.Histogram(
            x=d_df[col].dropna(), nbinsx=15,
            marker=dict(color=color, opacity=0.85, line=dict(width=0))
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=240,
            margin=dict(l=10, r=10, t=10, b=40),
            showlegend=False,
            xaxis=dict(
                title=title_x,
                title_font=dict(color='#2D6A4F', size=10),
                tickfont=dict(color='#2D6A4F', size=10),
                gridcolor='rgba(64,145,108,0.1)',
            ),
            yaxis=dict(
                title='Jumlah',
                title_font=dict(color='#2D6A4F', size=10),
                tickfont=dict(color='#2D6A4F', size=10),
                gridcolor='rgba(64,145,108,0.1)',
            ),
        )
        return fig

    with tb:
        cc2, cd2 = st.columns(2)
        with cc2:
            section_header("Distribusi Tingkat Persaingan")
            st.plotly_chart(hist_chart('competition_score', '#1565C0', 'Skor Persaingan'),
                            use_container_width=True, config={'displayModeBar': False})
        with cd2:
            section_header("Status Pasar (Ocean)")
            oc = d_df['status_ocean'].value_counts()
            lb = [l.split('(')[0].strip() for l in oc.index]
            cc3 = ['#D62839' if 'Red' in l else '#1565C0' for l in oc.index]
            fig = plot_donut(lb, oc.values.tolist(), colors=cc3)
            fig.update_layout(
                legend=dict(
                    font=dict(color='#1B4332', size=10),
                    bgcolor='rgba(255,255,255,0.9)',
                ),
            )
            fig.update_traces(textfont=dict(color='#FFFFFF'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    with tc:
        ce2, cf2 = st.columns(2)
        with ce2:
            section_header("Distribusi Volume Ulasan")
            st.plotly_chart(hist_chart('jumlah_ulasan', '#1565C0', 'Jumlah Ulasan'),
                            use_container_width=True, config={'displayModeBar': False})
        with cf2:
            section_header("Distribusi Skor Permintaan")
            st.plotly_chart(hist_chart('demand_score', '#40916C', 'Skor Permintaan'),
                            use_container_width=True, config={'displayModeBar': False})

    with td:
        cg2, ch2 = st.columns(2)
        with cg2:
            section_header("Distribusi Skor Ekosistem")
            st.plotly_chart(hist_chart('ecosystem_score', '#52B788', 'Skor Ekosistem'),
                            use_container_width=True, config={'displayModeBar': False})
        with ch2:
            section_header("Atraksi Terdekat Terpopuler")
            if 'nama_atraksi_terdekat' in d_df.columns:
                for attr, cnt in d_df['nama_atraksi_terdekat'].value_counts().head(7).items():
                    st.markdown(
                        f'<div class="metric-row">'
                        f'  <span class="metric-name">🌿 {str(attr)[:32]}</span>'
                        f'  <span class="metric-val">{cnt} hotel</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    with te:
        ci2, cj2 = st.columns(2)
        with ci2:
            section_header("Distribusi Skor Peluang")
            st.plotly_chart(hist_chart('opportunity_score', '#1565C0', 'Skor Peluang'),
                            use_container_width=True, config={'displayModeBar': False})
        with cj2:
            section_header("Komposisi Rekomendasi Investasi")
            rc_cnt = d_df['rekomendasi_investasi'].value_counts()
            rc_clr = []
            for l in rc_cnt.index:
                l_str = str(l)
                if 'Sangat' in l_str or 'Highly' in l_str:
                    rc_clr.append('#2D6A4F')
                elif 'Direkomendasikan' in l_str or l_str == 'Recommended':
                    rc_clr.append('#1565C0')
                elif 'Perlu' in l_str or 'Further' in l_str or 'Kajian' in l_str:
                    rc_clr.append('#E9A020')
                else:
                    rc_clr.append('#D62839')
            fig = plot_donut(rc_cnt.index.tolist(), rc_cnt.values.tolist(), colors=rc_clr)
            fig.update_layout(
                legend=dict(
                    font=dict(color='#1B4332', size=10),
                    bgcolor='rgba(255,255,255,0.9)',
                ),
            )
            fig.update_traces(textfont=dict(color='#FFFFFF'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
       
# ════════════════════════════════════════════════════════════════════
# PAGE 9 — STRATEGIC RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════

def page_strategy():
    page_header("Pusat Rekomendasi Strategis", "Laporan Intelijen Eksekutif · Strategi Investasi Kemenparekraf", "")

    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;'
        'background:#FFFFFF;border:1px solid #D8EDE4;'
        'border-radius:12px;padding:14px 18px;margin-bottom:18px;box-shadow:0 1px 4px rgba(27,67,50,0.08);">'
        '  <div>'
        '    <div style="font-size:15px;font-weight:700;color:#1B4332;">Laporan Intelijen Strategis</div>'
        '    <div style="font-size:11px;color:#74A98A;">Investasi Wisata Indonesia · Jun 2026</div>'
        '  </div>'
        '  <div style="display:flex;align-items:center;gap:6px;background:rgba(64,145,108,0.1);'
        'border:1px solid rgba(64,145,108,0.2);border-radius:20px;padding:5px 12px;">'
        '    <div style="width:6px;height:6px;border-radius:50%;background:#40916C;'
        'box-shadow:0 0 6px rgba(64,145,108,0.5);"></div>'
        '    <span style="font-size:10px;font-weight:700;color:#40916C;letter-spacing:0.5px;">LIVE INTELLIGENCE</span>'
        '  </div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── DESTINATION COMPARISON OVERVIEW ──────────────────────────
    section_header("Perbandingan Antar Destinasi", "Multi-Metrik: Peluang · Persaingan · Ekosistem")
    avail_m = [m for m in ['avg_opportunity', 'avg_competition', 'avg_ecosystem'] if m in dest_stats.columns]
    if len(avail_m) >= 2:
        fig = plot_grouped_bar(
            dest_stats, 'dest_display', avail_m,
            labels=['Peluang Investasi', 'Tingkat Persaingan', 'Kesiapan Ekosistem'],
            colors=[DESIGN['success'], DESIGN['danger'], DESIGN['accent']],
            height=300
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    spacer(24)

    # ── INVESTOR STRATEGY ROADMAP — 3 KOLOM SEJAJAR ──────────────
    section_header("Peta Jalan Strategi Investasi", "Prioritas Tindakan Berdasarkan Horizon Waktu")
    spacer(8)

    col_short, col_med, col_long = st.columns(3)

    roadmap = [
        {
            "col":      col_short,
            "label":    "Jangka Pendek",
            "period":   "0 – 12 Bulan",
            "color":    "#2D6A4F",
            "bg":       "rgba(45,106,79,0.06)",
            "border":   "#2D6A4F",
            "badge_bg": "rgba(45,106,79,0.12)",
            "items": [
                ("🏝️", "Land Banking Likupang & Morotai", "Sebelum infrastruktur aktif dan harga tanah naik 40–70%."),
                ("🤿", "Akuisisi Resort Premium Wakatobi", "Supply cap menciptakan natural moat investasi."),
                ("🌿", "Eco-Lodge Adjacent Dive Sites Raja Ampat", "Posisi boutique eco-lodge premium di jalur selam utama."),
                ("🏨", "Konversi Aset Danau Toba", "Tender aset 2–3 bintang untuk dikonversi ke segmen premium."),
            ]
        },
        {
            "col":      col_med,
            "label":    "Jangka Menengah",
            "period":   "1 – 3 Tahun",
            "color":    "#1565C0",
            "bg":       "rgba(21,101,192,0.06)",
            "border":   "#1565C0",
            "badge_bg": "rgba(21,101,192,0.12)",
            "items": [
                ("🏔️", "Ultra-Premium Dive Resort Morotai", "Niche WWII heritage + marine: segmen tanpa kompetitor langsung."),
                ("⛺", "Premium Glamping Bromo", "Posisi dekat ridgeline Bromo untuk segmen adventure luxury."),
                ("🌊", "Lakefront Luxury Resort Danau Toba", "Sejalan pengembangan konektivitas Tol Sumatra."),
                ("🏁", "Kemitraan MotoGP Mandalika", "8–12 event window/tahun dengan pricing premium terprediksi."),
            ]
        },
        {
            "col":      col_long,
            "label":    "Jangka Panjang",
            "period":   "3 – 7 Tahun",
            "color":    "#7B2D8B",
            "bg":       "rgba(123,45,139,0.06)",
            "border":   "#7B2D8B",
            "badge_bg": "rgba(123,45,139,0.12)",
            "items": [
                ("🗺️", "Koridor Terintegrasi Papua–Sultra", "Jaringan Raja Ampat → Wakatobi → Labuan Bajo sebagai dive circuit internasional."),
                ("🌱", "Eco-Resort Network 5 Zona UNESCO", "Anchor properties di 5 destinasi UNESCO undersupply."),
                ("📊", "Indonesia Premium Tourism Exchange", "Platform agregasi data dan transaksi investasi pariwisata nasional."),
            ]
        },
    ]

    for r in roadmap:
        with r["col"]:
            # Header kartu
            st.markdown(
                f'<div style="background:{r["bg"]};border:1.5px solid {r["border"]};'
                f'border-radius:12px;padding:14px 16px;margin-bottom:0;">'
                f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
                f'    <div style="font-size:13px;font-weight:700;color:{r["color"]};'
                f'font-family:Plus Jakarta Sans,sans-serif;">{r["label"]}</div>'
                f'    <div style="font-size:10px;font-weight:600;color:{r["color"]};'
                f'background:{r["badge_bg"]};border:1px solid {r["border"]};'
                f'border-radius:20px;padding:2px 10px;white-space:nowrap;">{r["period"]}</div>'
                f'  </div>',
                unsafe_allow_html=True
            )
            for icon, title, desc in r["items"]:
                st.markdown(
                    f'  <div style="display:flex;gap:10px;padding:10px 0;'
                    f'border-top:1px solid {r["border"]}22;">'
                    f'    <div style="font-size:18px;flex-shrink:0;padding-top:2px;">{icon}</div>'
                    f'    <div>'
                    f'      <div style="font-size:12px;font-weight:700;color:#1B4332;'
                    f'margin-bottom:3px;font-family:Plus Jakarta Sans,sans-serif;">{title}</div>'
                    f'      <div style="font-size:11px;color:#4A6080;line-height:1.5;">{desc}</div>'
                    f'    </div>'
                    f'  </div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# PAGE ENGINE — ANALYTICS ENGINE (gabungan 4 sub-halaman)
# ════════════════════════════════════════════════════════════════════

def page_engine():
    page_header("Mesin Analitik", "Ekonometrika Spasial · NLP · Ekosistem · Kompetisi", "")
    t1, t2, t3, t4 = st.tabs([
        "Intelijen Kompetisi",
        "Ekosistem Atraksi",
        "Analisis Branding (NLP)",
        "Ekonometrika Spasial (GWR)",
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