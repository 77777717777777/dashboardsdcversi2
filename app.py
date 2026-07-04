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
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    load_main_data, compute_branding_stats, compute_top3_investment,
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
    return load_main_data()

df_raw = load_all_data()
dest_stats_raw = get_destination_stats(df_raw)
branding_df = compute_branding_stats(df_raw)
top3_df = compute_top3_investment(df_raw)


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
            f'<div style="position:absolute;top:10px;right:10px;font-size:10px;'
            f'font-weight:700;padding:2px 7px;border-radius:20px;'
            f'background:rgba(255,255,255,0.2);color:#FFFFFF;">{arrow} {trend}</div>'
        )
    return (
        f'<div style="background:{bg};border:none;border-radius:10px;'
        f'padding:16px 16px 14px;position:relative;'
        f'box-shadow:0 4px 12px rgba(27,67,50,0.2);'
        f'min-height:110px;box-sizing:border-box;overflow:hidden;">'  # ← min-height + box-sizing
        f'  {trend_html}'
        f'  <div style="font-size:10px;color:rgba(255,255,255,0.75);font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">{label}</div>'
        f'  <div style="font-size:24px;font-weight:800;color:#FFFFFF;line-height:1.1;'
        f'font-family:Plus Jakarta Sans,sans-serif;word-break:break-word;">{value}</div>'
        f'  <div style="font-size:11px;color:rgba(255,255,255,0.65);margin-top:6px;'
        f'line-height:1.4;">{sub}</div>'
        f'  <div style="position:absolute;bottom:-15px;right:-15px;width:65px;height:65px;'
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

# ← TAMBAHKAN TEPAT DI SINI, setelah page_header
def page_header_compact(title, subtitle='', icon=''):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;'
        f'padding:6px 14px;margin-bottom:12px;'
        f'border-left:3px solid #40916C;">'
        f'  <div>'
        f'    <div style="font-size:16px;font-weight:700;color:#0F2A4A;'
        f'letter-spacing:-0.2px;line-height:1.2;">{title}</div>'
        f'    <div style="font-size:11px;color:#74A98A;margin-top:2px;">{subtitle}</div>'
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
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
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
            "Ringkasan Utama":           "executive",
            "Peta Spasial":              "spatial",
            "Profil Destinasi":          "destination",
            "Pemodelan":                 "engine",
            "Peluang Investasi":         "investment",
            "Dinamika Pasar":            "insights",
            "Rekomendasi":               "strategy",
        }
        st.markdown(
            '<div style="font-size:9px;color:#64748B;letter-spacing:1.2px;'
            'text-transform:uppercase;margin-bottom:8px;padding:0 2px;">NAVIGASI</div>',
            unsafe_allow_html=True
        )
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'executive'
        for label, pid in nav_pages.items():
            if st.button(label, key=f"nav_{pid}", width="stretch"):
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
    st.markdown(
    '<div style="padding:18px 0 8px 0;">'
    '  <div style="font-size:35px;font-weight:800;color:#0F2A4A;letter-spacing:-0.3px;">'
    '    Peta Sebaran & Peluang Investasi Akomodasi Wisata</div>'
    '  <div style="font-size:13px;color:#4A6080;margin-top:4px;">'
    '    Destinasi Super Prioritas Indonesia · Kemenparekraf 2026</div>'
    '</div>',
    unsafe_allow_html=True
)
    page_header_compact("Ringkasan Utama",
        "Peta Persebaran & Peluang Investasi · Destinasi Super Prioritas Indonesia", "")
    st.markdown('<div style="margin-top:-20px;"></div>', unsafe_allow_html=True)
    kpis = get_national_kpis(df)

    # ── KPI Baris 1: 5 kolom seimbang ──────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    rows1 = [
        (k1, "Total Akomodasi",        f"{kpis['total_hotels']:,}",          "Jaringan Destinasi Prioritas",   'accent',  None, 'up',     ''),
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
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        with t2:
            fig = plot_national_heatmap(dest_stats, 'avg_demand', '')
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        with t3:
            fig = plot_national_heatmap(dest_stats, 'avg_competition', '')
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

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

    page_header_compact("Peta Spasial", "Analisis GIS Multi-Layer Akomodasi Wisata", "")

    col_layers, col_map = st.columns([1, 3.2])

    with col_layers:
        st.markdown('<div style="font-size:14px;color:#475569;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;font-weight:600;">MAP LAYERS</div>', unsafe_allow_html=True)
        layer_opts = {
            "Peluang Investasi": "opportunity",
            "Heatmap Permintaan":        "supply",
            "Kepadatan Persaingan":    "competition",
            "Jaringan Atraksi":    "attraction",
            "Hotel Premium":        "premium",
        }
        sel_layer = st.radio("Pilih Layer", list(layer_opts.keys()), key='map_layer', label_visibility='collapsed')
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
        # ── LEGEND DINAMIS (BERUBAH SESUAI LAYER AKTIF) ───────────
        if sel_layer == "Peluang Investasi":
            legend_items = [
                ('#16A34A', 'Peluang Tinggi'), ('#3B82F6', 'Peluang Sedang'), 
                ('#D97706', 'Peluang Rendah'), ('#DC2626', 'Pasar Jenuh')
            ]
        elif sel_layer == "Heatmap Permintaan":
            legend_items = [
                ('#DC2626', 'Demand Sangat Padat'), 
                ('#D97706', 'Demand Sedang'), 
                ('#16A34A', 'Demand Rendah')
            ]
        elif sel_layer == "Kepadatan Persaingan":
            legend_items = [
                ('#DC2626', 'Persaingan Sangat Ketat'), 
                ('#D97706', 'Persaingan Sedang'), 
                ('#16A34A', 'Persaingan Rendah')
            ]
        #elif sel_layer in ["Red vs Blue Ocean", "Klaster DBSCAN"]:
        #    legend_items = [
        #        ('#DC2626', 'Red Ocean (Clustered/Padat)'), 
        #        ('#3B82F6', 'Blue Ocean (Noise/Berpeluang)')
        #    ]
        #elif sel_layer == "Jaringan Atraksi":
        #    legend_items = [
        #        ('#22C55E', 'Ekosistem Kuat'),
        #        ('#00D4FF', 'Ekosistem Sedang'),
        #        ('#F43F5E', 'Ekosistem Lemah'),
        #    ]
        elif sel_layer == "Hotel Premium":
            legend_items = [
                ('#A855F7', 'Segmen Premium / Luxury'), 
                ('#CBD5E1', 'Segmen Standar / Budget')
            ]
        else:
            legend_items = [('#16A34A', 'Tinggi'), ('#DC2626', 'Rendah')]

        st.markdown(
            '<div style="display:flex;gap:16px;align-items:center;'
            'padding:8px 14px;background:#F8FAFC;'
            'border:1px solid #E2E8F0;border-radius:8px;margin-bottom:8px;">'
            + ''.join([
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'  <div style="width:9px;height:9px;border-radius:50%;background:{c};flex-shrink:0;"></div>'
                f'  <span style="font-size:11px;color:#334155;font-weight:500;">{lbl}</span>'
                f'</div>'
                for c, lbl in legend_items
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
            st_folium(m, height=460, width="stretch", returned_objects=[])
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
                    f'<div class="stats-card" style="border-top:3px solid {clr};">'
                    f'  <div class="stats-card-label">{lbl}</div>'
                    f'  <div class="stats-card-value" style="color:{clr};">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ════════════════════════════════════════════════════════════════════
# PAGE 3 — COMPETITION INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_competition():
    page_header_compact(
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

    # ── BARIS 1: Matrix + GWR ─────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        section_header("Matriks Risiko vs Peluang", "Persaingan vs Peluang Investasi")
        fig = plot_investment_matrix_enhanced(dest_stats)
        fig.update_traces(
            mode='markers',
            textposition=None,
        )
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    with c2:
        section_header("Efek Aglomerasi (GWR)", "Koefisien Kompetitor per Destinasi")
        if 'koef_saingan_radius_1km' in df.columns:
            fig = plot_gwr_bar(df)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    spacer(14)

    # ── BARIS 2: Peringkat Persaingan + Blue Ocean List ───────────
    c3, c4 = st.columns(2)

    with c3:
        section_header("Peringkat Persaingan", "Per Destinasi")
        fig = plot_competition_ranking(dest_stats)
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    with c4:
        section_header("5 Destinasi dengan Hotel Blue Ocean", 
                       "Persaingan Terendah · Jumlah hotel Blue Ocean ≠ besarnya peluang")
        spacer(5)
        for _, row in dest_stats.nsmallest(5, 'avg_competition').iterrows():
            opp_pct = row.get('avg_opportunity', 100 - row['avg_competition'])
            opp_color = '#1A7A4A' if opp_pct >= 40 else '#B45309' if opp_pct >= 20 else '#C0392B'
            st.markdown(
                f'<div class="prog-container">'
                f'  <div class="prog-label">'
                f'    <span>{row["dest_display"]}</span>'
                f'    <span style="color:{opp_color};font-weight:700;">'
                f'Opp: {opp_pct:.0f} · Komp: {row["avg_competition"]:.1f}%</span>'
                f'  </div>'
                f'  <div class="prog-bar">'
                f'    <div class="prog-fill" style="width:{opp_pct}%"></div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown(
            '<div style="font-size:10px;color:#B45309;background:#FFFBEB;'
            'border:1px solid #FDE68A;border-radius:6px;padding:8px 10px;margin-top:8px;">'
            '⚠️ <b>Catatan:</b> Destinasi diurutkan berdasarkan tingkat persaingan terendah. '
            'Opportunity score (Opp) menunjukkan besarnya peluang investasi aktual — '
            'keduanya tidak selalu berkorelasi.'
            '</div>',
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
    page_header_compact("Ekosistem Atraksi Wisata", "Analisis Magnet Pariwisata · Deteksi Sinyal Investasi", "")

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
            fig.update_layout(showlegend=False) 
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Peringkat Skor Ekosistem", "Kesehatan Ekosistem Destinasi")
        #st.markdown('<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:16px 14px 8px;box-shadow:0 1px 4px rgba(15,42,74,0.08);">', unsafe_allow_html=True)
        fig = plot_opportunity_ranking(dest_stats, 'avg_ecosystem', '')
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
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
                                          tickfont=dict(color='#A6B4C8',size=8), thickness=9, y = 1.0, yanchor = 'top')),
                hovertemplate='Dist: %{x:.2f}km<br>Demand: %{y:.1f}<extra></extra>',
            ))
            fig = apply_layout(fig, height=280)
            fig.update_xaxes(title='Distance to Nearest Attraction (km)')
            fig.update_yaxes(title='Demand Score')
            fig.update_layout(showlegend=False)
            valid = smp.dropna(subset=['jarak_ke_atraksi_terdekat_km','demand_score'])
            if len(valid) > 10:
                coef = np.polyfit(valid['jarak_ke_atraksi_terdekat_km'].values, valid['demand_score'].values, 1)
                xs = np.sort(valid['jarak_ke_atraksi_terdekat_km'].values)
                fig.add_trace(go.Scatter(x=xs, y=np.polyval(coef, xs), mode='lines',
                              line=dict(color='#00D4FF', width=2, dash='dot'), showlegend=False))
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
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
                    x=grp['avg_atraksi'], y=grp['n_hotels'], mode='markers',
                    name=status,
                    marker=dict(size=14, color=sc_map.get(status,'#A6B4C8'), opacity=0.85,
                    line=dict(color='white',width=1)),
                    text=grp['dest_display'],
                    hovertemplate='<b>%{text}</b><br>Avg Atraksi: %{x:.1f}<br>Jumlah Hotel: %{y}<extra></extra>',))
            fig.add_vline(x=ma, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            fig.add_hline(y=mn, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            fig = apply_layout(fig, height=280)
            fig.update_xaxes(title='Avg Attractions in 5km')
            fig.update_yaxes(title='Number of Hotels')
            fig.update_layout(showlegend=False) 
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
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
    page_header_compact("Analisis Branding NLP", "Strategi Penamaan Hotel · Branding Alam vs Standar", "")

    all_dest_nlp = ['All'] + sorted(branding_df['destinasi'].dropna().unique().tolist())
    st.markdown('<div style="font-size:11px;color:#2D6A4F;margin-bottom:3px;font-weight:600;">Filter Destinasi</div>', unsafe_allow_html=True)
    dest_nlp = st.selectbox("Filter Destinasi", all_dest_nlp, key='nlp_dest', label_visibility='collapsed')
    bf = branding_df if dest_nlp == 'All' else branding_df[branding_df['destinasi'] == dest_nlp]

    nat_df  = bf[bf['Tema_Nama'] == 'Mengandung Unsur Alam']
    std_df  = bf[bf['Tema_Nama'] == 'Nama Standar']
    avg_nat = nat_df['Skor_Popularitas_Rerata'].mean() if len(nat_df) > 0 else 0
    avg_std = std_df['Skor_Popularitas_Rerata'].mean() if len(std_df) > 0 else 0
    lift    = ((avg_nat - avg_std) / max(avg_std, 1)) * 100

    k1,k2,k3,k4 = st.columns(4)
    for col,(lbl,val,sub,clr) in zip([k1,k2,k3,k4],[
        ("Nature Branding Avg Score", f"{avg_nat:.1f}", "Hotels w/ Nature Names (Rating × Ulasan)", 'success'),
        ("Standard Branding Avg Score",f"{avg_std:.1f}","Standard Hotel Names",  'accent'),
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
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        section_header("Jumlah Akomodasi per Tema", "Distribusi Lintas Segmen")
        #st.markdown('<div style="border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:12px 10px 4px;background:rgba(13,33,55,0.65);">', unsafe_allow_html=True)
        cnt = bf.groupby('Tema_Nama')['Jumlah_Akomodasi'].sum()
        lbs = ['Nature Branding' if 'Alam' in l else 'Standard Naming' for l in cnt.index]
        fig = plot_donut(lbs, cnt.values.tolist(), colors=['#22C55E','#3B82F6']) 
        fig.update_layout( legend=dict( font=dict(color='#1B4332', size=11),  # warna teks hijau gelap
                                       bgcolor='rgba(0,0,0,0)',               # background transparan
                                       ))
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(20)

    section_header("Executive Business Insight", "AI-Generated Branding Intelligence")
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        st.markdown(
            insight_html("🌿 Nature Branding Outperformance",
                f"Hotel dengan nama bertema alam menghasilkan <strong style='color:#22C55E'>{lift:.1f}% lebih banyak ulasan</strong> "
                "dibanding kompetitor standar — proksi langsung demand & occupancy lebih tinggi.", 'success'),
            unsafe_allow_html=True
        )
    with ic2:
        st.markdown(
            insight_html("👑 Premium Naming Strategy",
                "Hotel premium yang menggabungkan tema alam dengan kualitas (mis. 'Komodo Resort & Spa') "
                "mencapai 2.3x kecepatan review vs naming generik.", 'info'),
            unsafe_allow_html=True
        )
    with ic3:
        st.markdown(
            insight_html("💡 Rekomendasi Strategis",
                "Investasi baru wajib mengintegrasikan elemen alam destinasi ke identitas brand — "
                "terutama di Raja Ampat, Wakatobi, dan Morotai.", 'warning'),
            unsafe_allow_html=True
        )

# ════════════════════════════════════════════════════════════════════
# PAGE 6 — INVESTMENT INTELLIGENCE
# ════════════════════════════════════════════════════════════════════

def page_investment():
    page_header_compact(
        "Peluang Investasi",
        "Rekomendasi Wilayah Prioritas · Top 3 Lokasi per Destinasi · Scoring Berbasis Data",
        ""
    )

    dest_inv = df.groupby('destinasi').agg(
        n_hotels        = ('nama_hotel',             'count'),
        avg_opp         = ('opportunity_score',       'mean'),
        avg_demand      = ('demand_score',            'mean'),
        avg_competition = ('competition_score',        'mean'),
        avg_quality     = ('quality_score',            'mean'),
        avg_ecosystem   = ('ecosystem_score',         'mean'),
        n_sangat        = ('rekomendasi_investasi',   lambda x: (x == 'Sangat Direkomendasikan').sum()),
        n_blue          = ('status_ocean',            lambda x: x.str.contains('Blue').sum()),
    ).reset_index()

    dest_inv['pct_sangat']  = (dest_inv['n_sangat'] / dest_inv['n_hotels'] * 100).round(1)
    dest_inv['inv_grade']   = dest_inv['avg_opp'].apply(
        lambda s: 'A' if s >= 50 else ('B' if s >= 38 else 'C')
    )

    grade_a      = (dest_inv['inv_grade'] == 'A').sum()
    total_sangat = dest_inv['n_sangat'].sum()
    total_blue   = dest_inv['n_blue'].sum()
    best_dest    = dest_inv.nlargest(1, 'avg_opp').iloc[0]

    k1, k2, k3, k4 = st.columns(4)
    for col, (lbl, val, sub, clr) in zip([k1, k2, k3, k4], [
        ("Wilayah Grade A",        f"{grade_a} DSP",             "Avg Opp Score ≥ 50",        'success'),
        ("Zona Sangat Prioritas",  f"{total_sangat:,} Hotel",    "Top 15% per Destinasi",     'accent'),
        ("Blue Ocean Tersisa",     f"{total_blue:,} Peluang",    "Pasar Minim Saingan",       'white'),
        ("DSP Terbaik",            best_dest['destinasi'],        f"Avg Opp {best_dest['avg_opp']:.1f}", 'success'),
    ]):
        with col:
            st.markdown(kpi_card(lbl, val, sub, clr, icon='💰'), unsafe_allow_html=True)

    spacer(20)

    section_header(
        "Scorecard Investasi per Destinasi",
        "Penilaian tingkat wilayah — dari 10 Destinasi Super Prioritas"
    )
    for _, row in dest_inv.sort_values('avg_opp', ascending=False).iterrows():
        # ← Tambahkan skip Manado
        if 'Manado' in str(row['destinasi']):
            continue
            
        grade     = row['inv_grade']
        grade_clr = '#1A7A4A' if grade == 'A' else ('#1D5FAD' if grade == 'B' else '#B8680A')
        bar_opp   = min(row['avg_opp'], 100)
        bar_dem   = min(row['avg_demand'], 100)
        bar_eco   = min(row['avg_ecosystem'], 100)
        bar_comp  = min(row['avg_competition'], 100)

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;'
            f'padding:14px 18px;margin-bottom:10px;box-shadow:0 1px 4px rgba(15,42,74,0.07);">'

            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
            f'  <div style="display:flex;align-items:center;gap:10px;">'
            f'    <div style="font-size:22px;font-weight:900;color:{grade_clr};'
            f'background:rgba(0,0,0,0.04);border-radius:6px;width:34px;height:34px;'
            f'display:flex;align-items:center;justify-content:center;">{grade}</div>'
            f'    <div>'
            f'      <div style="font-size:14px;font-weight:700;color:#0F2A4A;">{row["destinasi"]}</div>'
            f'      <div style="font-size:11px;color:#64748B;">'
            f'{row["n_hotels"]} hotel · {row["n_sangat"]} zona prioritas · {row["n_blue"]} blue ocean</div>'
            f'    </div>'
            f'  </div>'
            f'  <div style="text-align:right;">'
            f'    <div style="font-size:9px;color:#94A3B8;margin-bottom:1px;">OPP SCORE</div>'
            f'    <div style="font-size:28px;font-weight:900;color:{grade_clr};line-height:1;">'
            f'{row["avg_opp"]:.1f}</div>'
            f'  </div>'
            f'</div>'

            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;">'

            + ''.join([
                f'<div>'
                f'  <div style="font-size:10px;color:#94A3B8;margin-bottom:3px;">{label}</div>'
                f'  <div style="height:5px;background:#F1F5F9;border-radius:3px;overflow:hidden;">'
                f'    <div style="width:{bar_val:.0f}%;height:100%;background:{bar_clr};'
                f'border-radius:3px;"></div></div>'
                f'  <div style="font-size:11px;font-weight:600;color:#334155;margin-top:2px;">'
                f'{val_num:.1f}</div>'
                f'</div>'
                for label, bar_val, bar_clr, val_num in [
                    ('Demand',      bar_dem,  '#22C55E', row['avg_demand']),
                    ('Ecosystem',   bar_eco,  '#3B82F6', row['avg_ecosystem']),
                    ('Competition', bar_comp, '#EF4444', row['avg_competition']),
                    ('Quality',     min(row['avg_quality'], 100), '#A855F7', row['avg_quality']),
                ]
            ])

            + f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    spacer(20)

    section_header(
        "Top 3 Lokasi Investasi Prioritas per Destinasi",
        "Koordinat mikro siap-eksekusi — berdasarkan Opportunity Score tertinggi dengan demand tervalidasi"
    )

    # ── JOIN foto_url dari df_raw ─────────────────────────────────

# 1) Siapkan foto_map
    if 'foto_url' in df_raw.columns:
        foto_map = (
            df_raw[['nama_hotel', 'destinasi', 'foto_url']]
            .assign(
                nama_hotel=lambda d: d['nama_hotel'].astype(str).str.strip(),
                destinasi=lambda d: d['destinasi'].astype(str).str.strip(),
            )
            .sort_values('foto_url', na_position='last')
            .drop_duplicates(subset=['nama_hotel', 'destinasi'], keep='first')
        )
    else:
        foto_map = pd.DataFrame()

    # 2) Gabungkan foto_map ke top3_df
    if not foto_map.empty:
        top3_joined = top3_df.assign(
            nama_hotel=lambda d: d['nama_hotel'].astype(str).str.strip(),
            destinasi=lambda d: d['destinasi'].astype(str).str.strip(),
        ).merge(foto_map, on=['nama_hotel', 'destinasi'], how='left')
    else:
        top3_joined = top3_df.copy()
        top3_joined['foto_url'] = None

    # 3) INI YANG HILANG DI FILE ANDA — wajib ada sebelum loop
    all_dest_top3 = ['Semua Destinasi'] + sorted([
        d for d in top3_joined['destinasi'].unique().tolist()
        if 'Manado' not in str(d)
    ])
    sel_dest_top3 = st.selectbox(
        "Filter Destinasi", all_dest_top3,
        key='inv_dest_filter', label_visibility='collapsed'
    )
    
    filtered_top3 = (
        top3_joined if sel_dest_top3 == 'Semua Destinasi'
        else top3_joined[top3_joined['destinasi'] == sel_dest_top3]
    )# ← Tambahkan filter ini sebelum for loop groupby
    filtered_top3 = filtered_top3[
        ~filtered_top3['destinasi'].str.contains('Manado', case=False, na=False)
    ]
    
    for dest_name, grp in filtered_top3.groupby('destinasi'):
        dest_avg_opp  = dest_inv.loc[dest_inv['destinasi'] == dest_name, 'avg_opp'].values
        dest_avg_opp  = dest_avg_opp[0] if len(dest_avg_opp) > 0 else 0
        grade_local   = 'A' if dest_avg_opp >= 50 else ('B' if dest_avg_opp >= 38 else 'C')
        grade_clr_loc = '#1A7A4A' if grade_local == 'A' else ('#1D5FAD' if grade_local == 'B' else '#B8680A')

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:20px 0 10px;">'
            f'  <div style="font-size:14px;font-weight:900;color:{grade_clr_loc};'
            f'background:{grade_clr_loc}18;border:1.5px solid {grade_clr_loc}40;'
            f'border-radius:6px;width:28px;height:28px;'
            f'display:flex;align-items:center;justify-content:center;">{grade_local}</div>'
            f'  <div style="font-size:15px;font-weight:800;color:#0F2A4A;">{dest_name}</div>'
            f'  <div style="font-size:11px;color:#94A3B8;padding:2px 10px;'
            f'background:#F8FAFC;border:1px solid #E2E8F0;border-radius:20px;">'
            f'Avg Opp {dest_avg_opp:.1f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(len(grp))
        for col, (rank, (_, row)) in zip(cols, enumerate(grp.iterrows(), 1)):
            seg       = row.get('market_segment', '')
            seg_clr   = (
                '#7C3AED' if 'Luxury'    in seg else
                '#22C55E' if 'Tourism'   in seg else
                '#3B82F6' if 'Strategic' in seg else
                '#F59E0B'
            )
            opp_score = row['opportunity_score']
            demand    = row['demand_score']
            quality   = row['quality_score']
            lat       = row['latitude']
            lon       = row['longitude']
            atraksi   = row.get('jumlah_atraksi_radius_5km', 0)
            jarak_atk = row.get('jarak_ke_atraksi_terdekat_km', 0)
            medal     = '🥇' if rank == 1 else ('🥈' if rank == 2 else '🥉')

            # ── Foto ──────────────────────────────────────────────
          
            foto_url = str(row.get('foto_url', '')).strip()
            if foto_url and foto_url.lower() not in ('nan', 'none', '') and foto_url.startswith(('http://', 'https://')):
                foto_html = (
                    f'<img src="{foto_url}" referrerpolicy="no-referrer" loading="lazy" '
                    f'style="width:100%;height:140px;object-fit:cover;display:block;background:#E2E8F0;" '
                    f'onerror="this.parentElement.innerHTML=\'<div style=&quot;width:100%;height:140px;background:#E2E8F0;'
                    f'display:flex;align-items:center;justify-content:center;&quot;>'
                    f'<div style=&quot;width:44px;height:44px;border-radius:50%;background:#CBD5E1;&quot;></div></div>\';"'
                    f' />'
                )
            else:
                foto_html = ('<div style="width:100%;height:140px;background:#E2E8F0;display:flex;align-items:center;justify-content:center;">'
                 '<div style="width:44px;height:44px;border-radius:50%;background:#CBD5E1;"></div></div>')
            with col:
                st.markdown(
                    # ── Card wrapper ──────────────────────────────
                    f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
                    f'border-radius:12px;overflow:hidden;'
                    f'box-shadow:0 1px 6px rgba(15,42,74,0.07);">'

                    # ── Foto area ─────────────────────────────────
                    f'<div style="position:relative;">'
                    f'  {foto_html}'
                    # Medal badge
                    f'  <div style="position:absolute;top:10px;left:10px;'
                    f'font-size:18px;line-height:1;">{medal}</div>'
                    # Segment badge
                    f'  <div style="position:absolute;top:10px;right:10px;'
                    f'font-size:10px;font-weight:600;color:{seg_clr};'
                    f'background:rgba(255,255,255,0.92);'
                    f'border:1px solid {seg_clr}60;border-radius:4px;'
                    f'padding:2px 7px;">{seg}</div>'
                    f'</div>'

                    # ── Konten bawah ──────────────────────────────
                    f'<div style="padding:12px 14px 14px;">'

                    # Nama hotel
                    f'<div style="font-size:12px;font-weight:700;color:#0F2A4A;'
                    f'line-height:1.4;margin-bottom:10px;'
                    f'min-height:34px;">{row["nama_hotel"]}</div>'

                    # Score grid
                    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;'
                    f'gap:6px;margin-bottom:10px;">'

                    f'<div style="background:#F0FDF4;border-radius:7px;'
                    f'padding:7px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#86EFAC;font-weight:600;'
                    f'letter-spacing:0.5px;margin-bottom:1px;">OPP</div>'
                    f'  <div style="font-size:18px;font-weight:900;color:#1A7A4A;'
                    f'line-height:1;">{opp_score:.0f}</div>'
                    f'</div>'

                    f'<div style="background:#EFF6FF;border-radius:7px;'
                    f'padding:7px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#93C5FD;font-weight:600;'
                    f'letter-spacing:0.5px;margin-bottom:1px;">DEMAND</div>'
                    f'  <div style="font-size:18px;font-weight:900;color:#2563EB;'
                    f'line-height:1;">{demand:.0f}</div>'
                    f'</div>'

                    f'<div style="background:#FDF4FF;border-radius:7px;'
                    f'padding:7px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#D8B4FE;font-weight:600;'
                    f'letter-spacing:0.5px;margin-bottom:1px;">QUALITY</div>'
                    f'  <div style="font-size:18px;font-weight:900;color:#7C3AED;'
                    f'line-height:1;">{quality:.0f}</div>'
                    f'</div>'

                    f'</div>'

                    # Detail baris
                    f'<div style="font-size:11px;color:#64748B;line-height:1.8;'
                    f'border-top:1px solid #F1F5F9;padding-top:8px;margin-bottom:8px;">'
                    f'  <span>🌿 {int(atraksi)} atraksi dalam 5km</span><br>'
                    f'  <span>📍 {jarak_atk:.2f} km ke atraksi terdekat</span>'
                    f'</div>'

                    # Koordinat
                    f'<div style="padding:7px 9px;background:#F0F9FF;'
                    f'border:1px solid #BAE6FD;border-radius:7px;">'
                    f'  <div style="font-size:8px;color:#0284C7;font-weight:700;'
                    f'letter-spacing:0.5px;margin-bottom:2px;">KOORDINAT GPS</div>'
                    f'  <div style="font-family:monospace;font-size:11px;'
                    f'color:#0369A1;">{lat:.6f}, {lon:.6f}</div>'
                    f'</div>'

                    f'</div>'  # end konten bawah
                    f'</div>',  # end card
                    unsafe_allow_html=True
                )

        spacer(8)

    spacer(20)

    col_quad, col_under = st.columns([1.3, 1])

    with col_quad:
        section_header(
            "Kuadran Wilayah: Demand vs Competition",
            "Posisi strategis tiap DSP — identifikasi zona ideal investasi"
        )

        med_comp = dest_inv['avg_competition'].median()
        med_dem  = dest_inv['avg_demand'].median()

        quadrant_colors = {
            'A': '#1A7A4A',
            'B': '#1D5FAD',
            'C': '#B8680A',
        }

        fig_q = go.Figure()

        # Shading kuadran
        x_max = dest_inv['avg_competition'].max() * 1.2
        y_max = dest_inv['avg_demand'].max() * 1.2

        fig_q.add_shape(type='rect', x0=0, y0=med_dem, x1=med_comp, y1=y_max,
                        fillcolor='rgba(26,122,74,0.06)', line=dict(width=0), layer='below')
        fig_q.add_shape(type='rect', x0=med_comp, y0=med_dem, x1=x_max, y1=y_max,
                        fillcolor='rgba(196,123,0,0.05)', line=dict(width=0), layer='below')
        fig_q.add_shape(type='rect', x0=0, y0=0, x1=med_comp, y1=med_dem,
                        fillcolor='rgba(74,96,128,0.05)', line=dict(width=0), layer='below')
        fig_q.add_shape(type='rect', x0=med_comp, y0=0, x1=x_max, y1=med_dem,
                        fillcolor='rgba(192,57,43,0.06)', line=dict(width=0), layer='below')

        annotations = [
            dict(x=2, y=y_max*0.97, text="🟢 SWEET SPOT",
                 showarrow=False, font=dict(size=9, color='#1A7A4A'), xanchor='left'),
            dict(x=med_comp*1.05, y=y_max*0.97, text="⚠️ RISING TIDE",
                 showarrow=False, font=dict(size=9, color='#B8680A'), xanchor='left'),
            dict(x=2, y=med_dem*0.15, text="🔵 BLUE OCEAN",
                 showarrow=False, font=dict(size=9, color='#1D5FAD'), xanchor='left'),
            dict(x=med_comp*1.05, y=med_dem*0.15, text="🔴 RED OCEAN",
                 showarrow=False, font=dict(size=9, color='#C0392B'), xanchor='left'),
        ]

        fig_q.add_shape(type='line', x0=med_comp, x1=med_comp,
                        y0=0, y1=y_max,
                        line=dict(color='rgba(0,0,0,0.15)', dash='dot'))
        fig_q.add_shape(type='line', x0=0, x1=x_max,
                        y0=med_dem, y1=med_dem,
                        line=dict(color='rgba(0,0,0,0.15)', dash='dot'))

        for _, row in dest_inv.iterrows():
            grade = row['inv_grade']
            fig_q.add_trace(go.Scatter(
                x=[row['avg_competition']],
                y=[row['avg_demand']],
                mode='markers',
                name=row['destinasi'],
                marker=dict(
                    size=row['avg_opp'] / 3 + 10,
                    color=quadrant_colors.get(grade, '#64748B'),
                    opacity=0.85,
                    line=dict(color='white', width=2)
                ),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row['destinasi']}</b><br>"
                    f"Demand: {row['avg_demand']:.1f}<br>"
                    f"Competition: {row['avg_competition']:.1f}<br>"
                    f"Opp Score: {row['avg_opp']:.1f}<br>"
                    f"Grade: {grade}<extra></extra>"
                )
            ))

        fig_q.update_layout(
            annotations=annotations,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,250,252,1)',
            height=420,
            margin=dict(l=10, r=10, t=20, b=40),
            xaxis=dict(
                title='Tingkat Persaingan (Competition Score)',
                range=[0, x_max],
                gridcolor='#E2E8F0',
                tickfont=dict(color='#64748B', size=10),
                title_font=dict(color='#64748B', size=11),
            ),
            yaxis=dict(
                title='Tingkat Permintaan (Demand Score)',
                range=[0, y_max],
                gridcolor='#E2E8F0',
                tickfont=dict(color='#64748B', size=10),
                title_font=dict(color='#64748B', size=11),
            ),
        )
        st.plotly_chart(fig_q, width="stretch", config={'displayModeBar': False})

    with col_under:
        section_header(
            "Undersupply vs Saturated",
            "Identifikasi zona dengan gap antara demand dan jumlah hotel"
        )

        med_hotels = dest_inv['n_hotels'].median()
        med_demand = dest_inv['avg_demand'].median()

        # ── Tentukan status dulu ──────────────────────────────────
        def get_status(row):
            is_under = (row['avg_demand'] >= med_demand) and (row['n_hotels'] <= med_hotels)
            is_over  = (row['avg_competition'] >= dest_inv['avg_competition'].quantile(0.7))
            if is_over:
                return 'SATURATED', '#C0392B', '⚠️', 'critical', \
                       f"Kompetisi {row['avg_competition']:.0f}% · Hindari entry mid-range"
            elif is_under:
                return 'UNDERSUPPLY', '#1A7A4A', '📈', 'opportunity', \
                       f"Demand {row['avg_demand']:.0f} · Hanya {row['n_hotels']} hotel → peluang first-mover"
            else:
                return 'BALANCED', '#1D5FAD', '🔵', 'info', \
                       f"Avg Opp {row['avg_opp']:.1f} · {row['n_sangat']} zona prioritas"

        # ── Tambah kolom status lalu urutkan ─────────────────────
        status_order = {'SATURATED': 0, 'BALANCED': 1, 'UNDERSUPPLY': 2}
        rows_with_status = []
        for _, row in dest_inv.iterrows():
            status, clr, icon, badge_cls, desc = get_status(row)
            rows_with_status.append((status_order[status], status, clr, icon, badge_cls, desc, row))

        # Sort: SATURATED dulu, lalu BALANCED, lalu UNDERSUPPLY
        rows_with_status.sort(key=lambda x: x[0])

        for _, status, clr, icon, badge_cls, desc, row in rows_with_status:
            st.markdown(
                f'<div class="alert-item {badge_cls}" style="margin-bottom:8px;">'
                f'  <div class="alert-icon">{icon}</div>'
                f'  <div class="alert-content">'
                f'    <h5 style="color:{clr};">{row["destinasi"]} — {status}</h5>'
                f'    <p>{desc}</p>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True)

    spacer(20)

    best3 = dest_inv.nlargest(3, 'avg_opp')
    best_names = ', '.join(best3['destinasi'].tolist())
    worst = dest_inv.nlargest(1, 'avg_competition').iloc[0]

    st.markdown(insight_html(
        "Rekomendasi Wilayah Final",
        f"<strong style='color:#22C55E'>Top 3 DSP untuk investasi sekarang: {best_names}</strong> "
        f"berdasarkan kombinasi opportunity score, demand tervalidasi, dan ekosistem atraksi. "
        f"<br><br>"
        f"Hindari entry mid-range di <strong style='color:#EF4444'>{worst['destinasi']}</strong> "
        f"(kompetisi {worst['avg_competition']:.0f}%) — pivot ke segmen ultra-premium atau exit. "
        f"<br><br>"
        f"Total <strong style='color:#00D4FF'>{total_sangat} lokasi Sangat Direkomendasikan</strong> "
        f"tersebar di 10 DSP dengan {total_blue} zona Blue Ocean tersisa sebagai peluang first-mover.",
        'success'
    ), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# PAGE 7 — SPATIAL ECONOMETRICS
# ════════════════════════════════════════════════════════════════════

def page_econometrics():
    #page_header(
    #    "Analisis Spasial Lanjutan",
    #    "Pemodelan Hybrid GWR + OLS · Pola Pengelompokan per Destinasi · Faktor Performa Hotel",
    #    ""
    #)

    moran_per_dest = {
        'Labuan Bajo':            {'p': 0.001, 'lolos': True,  'model': 'GWR'},
        'Mandalika':              {'p': 0.001, 'lolos': True,  'model': 'GWR'},
        'Borobudur':              {'p': 0.001, 'lolos': True,  'model': 'GWR'},
        'Bromo Tengger Semeru':   {'p': 0.001, 'lolos': True,  'model': 'GWR'},
        'Tanjung Kelayang':       {'p': 0.001, 'lolos': True,  'model': 'GWR'},
        'Raja Ampat':             {'p': 0.006, 'lolos': True,  'model': 'GWR'},
        'Likupang':               {'p': 0.078, 'lolos': False, 'model': 'OLS'},
        'Danau Toba':             {'p': 0.156, 'lolos': False, 'model': 'OLS'},
        'Wakatobi':               {'p': 0.057, 'lolos': False, 'model': 'OLS'},
        'Morotai':                {'p': 0.119, 'lolos': False, 'model': 'OLS'},
        #'Manado (Likupang Hub)':  {'p': 0.078, 'lolos': False, 'model': 'OLS'},
    }

    n_per_dest = df.groupby('destinasi').size().to_dict()
    r2_per_dest = df.groupby(['destinasi','model_dipakai'])['r2_lokal'].mean().reset_index()

    section_header(
        "Uji Moran's I per Destinasi — Apakah Ada Pola Spasial?",
        "Uji dilakukan per destinasi untuk menentukan model yang tepat: GWR (lokal) atau OLS (global)"
    )

    #st.markdown(
    #    '<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;'
    #    'padding:14px 18px;margin-bottom:18px;">'
    #    '<div style="font-size:13px;font-weight:800;color:#0F2A4A;margin-bottom:8px;">'
    #    'Cara Membaca Peta Mitigasi Risiko (GWR):</div>'
    #    '<div style="display:flex;gap:20px;align-items:flex-start;">'

    #    '<div style="flex:1;">'
    #    '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
    #    '<div style="width:12px;height:12px;background:#1A7A4A;border-radius:3px;"></div>'
    #    '<div style="font-size:11px;font-weight:700;color:#1A7A4A;text-transform:uppercase;">Arah Kanan (Hijau)</div>'
    #    '</div>'
    #    '<div style="font-size:11px;color:#475569;line-height:1.5;">'
    #    '<b>Korelasi Searah:</b> Semakin bertambah nilainya, kinerja hotel <b>semakin naik</b>. (Contoh: Ekosistem wisata yang semakin ramai justru menguntungkan).</div>'
    #    '</div>'

    #    '<div style="width:1px;background:#E2E8F0;align-self:stretch;"></div>'

    #    '<div style="flex:1;">'
    #    '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
    #    '<div style="width:12px;height:12px;background:#C0392B;border-radius:3px;"></div>'
    #    '<div style="font-size:11px;font-weight:700;color:#C0392B;text-transform:uppercase;">Arah Kiri (Merah)</div>'
    #    '</div>'
    #    '<div style="font-size:11px;color:#475569;line-height:1.5;">'
    #    '<b>Korelasi Terbalik:</b> Semakin bertambah jaraknya/kepadatannya, kinerja hotel <b>semakin merosot</b>. (Peringatan risiko bagi investor).</div>'
    #    '</div>'

    #    '<div style="width:1px;background:#E2E8F0;align-self:stretch;"></div>'

    #    '<div style="flex:1;">'
    #    '<div style="font-size:11px;font-weight:700;color:#0F2A4A;margin-bottom:4px;">Makna Garis Batas Nol (0)</div>'
    #    '<div style="font-size:11px;color:#475569;line-height:1.5;">'
    #    'Jika kotak membentang melewati garis nol, berarti <b>faktor tersebut memiliki peluang sekaligus risiko ganda</b>, sangat bergantung pada titik koordinat spesifik hotel.</div>'
    #    '</div>'

    #    '</div>'
    #    '</div>',
    #    unsafe_allow_html=True
    #)


    col_a, col_b = st.columns(2)

    gwr_dests = {k: v for k, v in moran_per_dest.items() if v['lolos']}
    ols_dests  = {k: v for k, v in moran_per_dest.items() if not v['lolos']}

    # ── Bangun HTML kolom kiri (GWR) ─────────────────────────────
    gwr_items_html = ''
    for dest, info in gwr_dests.items():
        n = n_per_dest.get(dest, 0)
        r2_row = r2_per_dest[r2_per_dest['destinasi'] == dest]
        r2 = r2_row['r2_lokal'].values[0] if not r2_row.empty else 0
        p_display = "p < 0.01" if info['p'] <= 0.001 else f"p = {info['p']:.3f}"
        gwr_items_html += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:8px 10px;background:#FFFFFF;border-radius:8px;margin-bottom:6px;'
            f'border:1px solid #D1FAE5;">'
            f'  <div>'
            f'    <div style="font-size:12px;font-weight:600;color:#0F2A4A;">{dest}</div>'
            f'    <div style="font-size:10px;color:#64748B;">{n} hotel · R² = {r2:.3f}</div>'
            f'  </div>'
            f'  <div style="text-align:right;">'
            f'    <div style="font-size:10px;font-weight:700;color:#1A7A4A;">{p_display}</div>'
            f'    <div style="font-size:9px;background:#D1FAE5;color:#1A7A4A;'
            f'border-radius:4px;padding:1px 6px;margin-top:2px;">GWR</div>'
            f'  </div>'
            f'</div>'
        )

    # ── Bangun HTML kolom kanan (OLS) ────────────────────────────
    ols_items_html = ''
    for dest, info in ols_dests.items():
        n = n_per_dest.get(dest, 0)
        r2_row = r2_per_dest[r2_per_dest['destinasi'] == dest]
        r2 = r2_row['r2_lokal'].values[0] if not r2_row.empty else 0
        ols_items_html += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:8px 10px;background:#FFFFFF;border-radius:8px;margin-bottom:6px;'
            f'border:1px solid #FDE68A;">'
            f'  <div>'
            f'    <div style="font-size:12px;font-weight:600;color:#0F2A4A;">{dest}</div>'
            f'    <div style="font-size:10px;color:#64748B;">{n} hotel · R² = {r2:.3f}</div>'
            f'  </div>'
            f'  <div style="text-align:right;">'
            f'    <div style="font-size:10px;font-weight:700;color:#B45309;">p = {info["p"]:.3f}</div>'
            f'    <div style="font-size:9px;background:#FDE68A;color:#92400E;'
            f'border-radius:4px;padding:1px 6px;margin-top:2px;">OLS</div>'
            f'  </div>'
            f'</div>'
        )

    with col_a:
        st.markdown(
            f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:14px;">'
            f'  <div style="font-size:12px;font-weight:700;color:#1A7A4A;margin-bottom:10px;">'
            f'  Lolos Moran\'s I — Model GWR (Spasial Lokal)</div>'
            f'  {gwr_items_html}'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_b:
        st.markdown(
            f'<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:14px;">'
            f'  <div style="font-size:12px;font-weight:700;color:#B45309;margin-bottom:4px;">'
            f'  Tidak Lolos Moran\'s I — Model OLS (Global)</div>'
            f'  <div style="font-size:11px;color:#92400E;margin-bottom:10px;">'
            f'  Bukan berarti tidak ada peluang — data terlalu sedikit untuk mendeteksi pola spasial.</div>'
            f'  {ols_items_html}'
            f'  <div style="background:#FFF7ED;border-radius:8px;padding:10px 12px;margin-top:8px;">'
            f'    <div style="font-size:11px;color:#92400E;line-height:1.6;">'
            f'    <b>Kenapa destinasi ini tidak lolos?</b><br>'
            f'    Wakatobi (45 hotel), Morotai (53), Likupang (171), Danau Toba (176) — '
            f'    jumlah data terlalu kecil untuk uji spasial yang reliable. '
            f'    OLS tetap menghasilkan model yang valid, hanya tanpa komponen lokasi lokal.'
            f'    </div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True
        )
    

        #st.markdown(
        #    '<div style="background:#FFF7ED;border-radius:8px;padding:10px 12px;margin-top:6px;">'
        #    '<div style="font-size:11px;color:#92400E;line-height:1.6;">'
        #    '<b>Kenapa 4 destinasi ini tidak lolos?</b><br>'
        #    'Wakatobi (45 hotel), Morotai (53), Likupang (82) — '
        #    'jumlah data terlalu kecil untuk uji spasial yang reliable. '
        #    'OLS tetap menghasilkan model yang valid, hanya tanpa komponen lokasi lokal.'
        #    '</div>'
        #    '</div>',
        #    unsafe_allow_html=True
        #)
        st.markdown('</div>', unsafe_allow_html=True)

    spacer(24)

    section_header(
        "Faktor Apa yang Mempengaruhi Performa Hotel di Tiap Destinasi?",
        "Koefisien GWR — efek tiap faktor berbeda per lokasi · hanya untuk destinasi yang lolos GWR"
    )

    #st.markdown(
    #    '<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;'
    #    'padding:12px 18px;margin-bottom:14px;">'
    #    '<div style="display:flex;gap:20px;align-items:flex-start;">'

    #    '<div style="flex:1;">'
    #    '<div style="font-size:10px;font-weight:700;color:#B45309;text-transform:uppercase;'
    #    'letter-spacing:0.8px;margin-bottom:4px;">Bar Kanan (Hijau/Positif)</div>'
    #    '<div style="font-size:12px;color:#78350F;">Faktor ini <b>menguntungkan</b> performa hotel.</div>'
    #    '</div>'

    #    '<div style="width:1px;background:#FDE68A;align-self:stretch;"></div>'

    #    '<div style="flex:1;">'
    #    '<div style="font-size:10px;font-weight:700;color:#B45309;text-transform:uppercase;'
    #    'letter-spacing:0.8px;margin-bottom:4px;">Bar Kiri (Merah/Negatif)</div>'
    #    '<div style="font-size:12px;color:#78350F;">Faktor ini <b>merugikan</b> performa hotel.</div>'
    #    '</div>'

    #    '<div style="width:1px;background:#FDE68A;align-self:stretch;"></div>'

    #    '<div style="flex:1;">'
    #    '<div style="font-size:10px;font-weight:700;color:#B45309;text-transform:uppercase;'
    #    'letter-spacing:0.8px;margin-bottom:4px;">Garis Putus-Putus</div>'
    #    '<div style="font-size:12px;color:#78350F;">Titik nol sebagai pembatas positif dan negatif.</div>'
    #    '</div>'

    #    '<div style="width:1px;background:#FDE68A;align-self:stretch;"></div>'

    #    '<div style="flex:1;">'
    #    '<div style="font-size:10px;font-weight:700;color:#B45309;text-transform:uppercase;'
    #    'letter-spacing:0.8px;margin-bottom:4px;">Kotak Lebih Lebar</div>'
    #    '<div style="font-size:12px;color:#78350F;">Efeknya sangat bervariasi antar hotel di destinasi tersebut.</div>'
    #    '</div>'

    #    '</div>'
    #    '</div>',
    #    unsafe_allow_html=True
    #)

    factor_context = {
        'koef_jarak_ke_pusat_km': {
            'label':   'Pengaruh Jarak dari Pusat Kota',
            'finding': 'Mayoritas Hotel Harus Dekat Pusat Kota (76.6% area)',
            'color':   '#C0392B',
            'impact_pos': 'Suasana Tenang',
            'impact_neg': 'Akses Pusat Kota',
            'plain':   (
                'Secara umum, semakin jauh letak hotel dari pusat kota, kinerjanya akan semakin menurun. Akses yang mudah ke pusat keramaian adalah faktor penting untuk menarik pengunjung. Namun, terdapat pengecualian di destinasi alam seperti Borobudur dan Wakatobi, di mana wisatawan justru mencari penginapan yang tenang dan jauh dari keramaian.'
            ),
            'dest_note': (
                '<b>Mandalika:</b> Sangat bergantung pada pusat kota. Lokasi yang jauh akan sepi pengunjung.<br>'
                '<b>Borobudur & Wakatobi:</b> Lokasi yang tenang dan menyatu dengan alam lebih diminati wisatawan.'
            ),
        },
        'koef_saingan_radius_1km': {
            'label':   'Pengaruh Kepadatan Kompetitor (Radius 1km)',
            'finding': 'Berkumpulnya Hotel Cenderung Menguntungkan (57.4% area)',
            'color':   '#1A7A4A',
            'impact_pos': 'Saling Menguntungkan',
            'impact_neg': 'Persaingan Ketat',
            'plain':   (
                'Mengelompoknya banyak hotel di satu titik rata-rata memberikan keuntungan bersama, karena area tersebut menjadi pusat tujuan wisatawan. Namun, perlu diwaspadai di Mandalika dan Labuan Bajo. Di sana, jumlah hotel sudah terlalu padat. Membangun hotel baru di titik yang sama hanya akan memicu persaingan harga yang merugikan investor.'
            ),
            'dest_note': (
                '<b>Borobudur & Wakatobi:</b> Kumpulan hotel menciptakan area wisata yang hidup dan menguntungkan.<br>'
                '<b>Mandalika & Labuan Bajo:</b> Area sudah jenuh. Disarankan mencari lokasi baru agar tidak bersaing terlalu ketat.'
            ),
        },
        'koef_jarak_ke_atraksi_terdekat_km': {
            'label':   'Pengaruh Jarak ke Atraksi Wisata',
            'finding': 'Jarak ke Tempat Wisata Sangat Menentukan (64.6% area)',
            'color':   '#C0392B',
            'impact_pos': 'Jarak Fleksibel',
            'impact_neg': 'Wajib Dekat Wisata',
            'plain':   (
                'Semakin jauh jarak hotel dari objek wisata utama, daya tariknya akan semakin menurun. Kedekatan lokasi dengan tempat wisata adalah kunci utama keberhasilan akomodasi. Pengecualian terjadi di kawasan seperti Borobudur, di mana daya tarik utamanya sangat kuat sehingga wisatawan tetap bersedia menginap meskipun jaraknya sedikit lebih jauh.'
            ),
            'dest_note': (
                '<b>Tanjung Kelayang:</b> Lokasi persis di pinggir pantai (beachfront) adalah syarat utama.<br>'
                '<b>Borobudur:</b> Jarak yang sedikit lebih jauh masih bisa ditoleransi oleh wisatawan.'
            ),
        },
        'koef_jumlah_atraksi_radius_5km': {
            'label':   'Dampak Jumlah Atraksi Tambahan (Radius 5km)',
            'finding': 'Dampak Berbeda Sesuai Kondisi Destinasi',
            'color':   '#B8680A',
            'impact_pos': 'Menarik Pengunjung',
            'impact_neg': 'Kepadatan Berlebih',
            'plain':   (
                'Efek penambahan tempat wisata di sekitar hotel sangat bervariasi. Pada destinasi yang sedang berkembang (seperti Raja Ampat), banyaknya pilihan wisata akan semakin menarik tamu. Sebaliknya, pada destinasi yang sudah sangat padat (seperti Mandalika atau Bromo), terlalu banyak titik wisata justru memicu kemacetan dan kebisingan yang menurunkan kenyamanan wisatawan.'
            ),
            'dest_note': (
                '<b>Raja Ampat & Borobudur:</b> Fasilitas wisata tambahan di sekitar hotel akan meningkatkan kunjungan.<br>'
                '<b>Mandalika & Bromo:</b> Area sudah cukup padat. Penambahan atraksi berisiko menurunkan tingkat kenyamanan.'
            ),
        },
    }

    coef_map = [
        ('koef_jarak_ke_pusat_km',          'Jarak dari Pusat Kota'),
        ('koef_saingan_radius_1km',          'Kepadatan Kompetitor'),
        ('koef_jarak_ke_atraksi_terdekat_km','Jarak ke Atraksi'),
        ('koef_jumlah_atraksi_radius_5km',   'Jumlah Atraksi 5km'),
    ]
    avail = [(c, l) for c, l in coef_map if c in df.columns]

    if avail:
        ctabs = st.tabs([l for c, l in avail])
        for tab, (coef_col, coef_lbl) in zip(ctabs, avail):
            with tab:
                ctx = factor_context.get(coef_col, {})
                find_clr = ctx.get('color', '#64748B')

                # --- REVISI: Hanya menampilkan Judul Utama yang dibesarkan, "Temuan" dihapus ---
                st.markdown(
                    f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;'
                    f'padding:14px 18px;margin-bottom:12px;">'
                    f'  <div style="font-size:16px;font-weight:800;color:#0F2A4A;letter-spacing:-0.2px;">'
                    f'{ctx.get("label", coef_lbl)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # ── Chart + Panel kanan dalam container sejajar ───
                cm, cs = st.columns([2, 1])

                with cm:
                    fig = plot_gwr_coefficients(df, coef_col, f'GWR: {coef_lbl}')
                    st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

                with cs:
                    cd = df[coef_col].dropna()
                    pct_pos = (cd > 0).mean() * 100
                    pct_neg = 100 - pct_pos
                    
                    # Ambil label dinamis dari dictionary
                    lbl_pos = ctx.get('impact_pos', 'Korelasi Searah')
                    lbl_neg = ctx.get('impact_neg', 'Korelasi Terbalik')

                    # Pembersihan format teks
                    plain_raw = ctx.get('plain', '')
                    plain_clean = plain_raw.replace(' —', '.').replace('—', '').replace('<b>', '<b style="color:#0F2A4A">').strip()

                    dest_note_raw = ctx.get('dest_note', '')
                    dest_note_clean = dest_note_raw.replace(' —', ':').replace('—', '')

                    # 1. TAMPUNG SEMUA HTML KE DALAM SATU VARIABEL (html_content)
                    html_content = (
                        # --- Kotak 1: Persentase Dampak ---
                        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:14px;margin-bottom:12px;">'
                        f'  <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:10px;">Distribusi Efek Spesifik Lokasi</div>'
                        f'  <div style="display:flex;gap:8px;">'
                        f'    <div style="flex:1;text-align:center;background:#F0FDF4;border-radius:8px;padding:12px 6px;">'
                        f'      <div style="font-size:24px;font-weight:900;color:#1A7A4A;">{pct_pos:.0f}%</div>'
                        f'      <div style="font-size:10px;font-weight:700;color:#1A7A4A;line-height:1.2;margin-top:2px;">{lbl_pos}</div>'
                        f'    </div>'
                        f'    <div style="flex:1;text-align:center;background:#FFF1F2;border-radius:8px;padding:12px 6px;">'
                        f'      <div style="font-size:24px;font-weight:900;color:#C0392B;">{pct_neg:.0f}%</div>'
                        f'      <div style="font-size:10px;font-weight:700;color:#C0392B;line-height:1.2;margin-top:2px;">{lbl_neg}</div>'
                        f'    </div>'
                        f'  </div>'
                        f'</div>'
                        
                        # --- Kotak 2: Penjelasan Analisis & Catatan Wilayah ---
                        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:3px solid {find_clr};border-radius:0 8px 8px 0;padding:16px 14px;box-shadow:0 1px 3px rgba(15,42,74,0.03);">'
                        f'  <div style="font-size:11px;font-weight:800;color:#0F2A4A;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">Artinya untuk Investor</div>'
                        f'  <div style="font-size:11px;color:#334155;line-height:1.65;margin-bottom:12px;text-align:justify;">{plain_clean}</div>'
                        f'  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;padding:10px 12px;">'
                        f'    <div style="font-size:9px;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Catatan per Destinasi:</div>'
                        f'    <div style="font-size:10px;color:#475569;line-height:1.6;">{dest_note_clean}</div>'
                        f'  </div>'
                        f'</div>'
                    )

                    # 2. RENDER DI STREAMLIT
                    st.markdown(html_content, unsafe_allow_html=True)

    spacer(24)

    section_header(
        "Perbandingan Akurasi Model per Destinasi",
        "R² GWR vs OLS — seberapa baik model menjelaskan variasi performa hotel"
    )

    cg, co = st.columns([1.2, 1])
    with cg:
        r2_data = r2_per_dest.copy()
        r2_data = r2_data.sort_values('r2_lokal', ascending=True)
        colors = ['#1A7A4A' if m == 'GWR (Lokal)' else '#F59E0B'
                  for m in r2_data['model_dipakai']]
                  
        fig = go.Figure(go.Bar(
            x=r2_data['r2_lokal'],
            y=r2_data['destinasi'],
            orientation='h',
            marker=dict(color=colors, opacity=0.85),
            text=[f"R²={v:.3f} ({m.split()[0]})"
                  for v, m in zip(r2_data['r2_lokal'], r2_data['model_dipakai'])],
            textposition='inside',
            textfont=dict(color='#FFFFFF', size=10),
            cliponaxis=True,
            showlegend=False  # <--- REVISI 1: Mematikan kemunculan "trace 0"
        ))

        fig = apply_layout(fig, height=340, show_legend=False)

        max_val = r2_data['r2_lokal'].max()   # Harus sebelum update_xaxes

        fig.update_xaxes(
            title='R²',
            tickfont=dict(size=9, color='#4A6080'),
            range=[0, max_val * 1.15]
        )

        # --- REVISI 2: Trace dummy untuk memunculkan warna di legend tanpa status 'legendonly' ---
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            name='GWR (Lokal)',
            marker_color='#1A7A4A',
            showlegend=True
        ))
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            name='OLS (Global)',
            marker_color='#F59E0B',
            showlegend=True
        ))

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation='h',
                y=-0.22,
                x=0.5,             # Digeser ke tengah (0.5)
                xanchor='center',  # Biar rata tengah sempurna
                font=dict(size=10, color='#334155'),
                itemclick=False,       # <--- REVISI 3: Matikan efek klik yang mengganggu
                itemdoubleclick=False  # <--- REVISI 3: Matikan tooltip "double click..."
            ),
            margin=dict(l=10, r=10, t=20, b=60)
        )
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
      
    with co:
        gwr_avg = r2_per_dest[r2_per_dest['model_dipakai']=='GWR (Lokal)']['r2_lokal'].mean()
        ols_avg = r2_per_dest[r2_per_dest['model_dipakai']=='OLS (Global)']['r2_lokal'].mean()

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;'
            f'padding:16px 18px;margin-bottom:12px;">'
            f'<div style="font-size:13px;font-weight:700;color:#0F2A4A;margin-bottom:12px;">'
            f'Rata-rata Akurasi Model</div>'
            f'<div style="display:flex;gap:10px;margin-bottom:14px;">'
            f'  <div style="flex:1;text-align:center;background:#F0FDF4;border-radius:8px;padding:10px;">'
            f'    <div style="font-size:9px;color:#94A3B8;margin-bottom:2px;">GWR (6 destinasi)</div>'
            f'    <div style="font-size:26px;font-weight:900;color:#1A7A4A;">R²={gwr_avg:.3f}</div>'
            f'  </div>'
            f'  <div style="flex:1;text-align:center;background:#FFFBEB;border-radius:8px;padding:10px;">'
            f'    <div style="font-size:9px;color:#94A3B8;margin-bottom:2px;">OLS (5 destinasi)</div>'
            f'    <div style="font-size:26px;font-weight:900;color:#B45309;">R²={ols_avg:.3f}</div>'
            f'  </div>'
            f'</div>'
            f'<div style="font-size:12px;color:#334155;line-height:1.7;">'
            f'<b>GWR lebih akurat</b> di destinasi dengan data cukup karena '
            f'memperhitungkan bahwa pengaruh jarak, kompetitor, dan atraksi '
            f'berbeda-beda di tiap lokasi.<br><br>'
            f'<b>OLS tetap valid</b> untuk Wakatobi, Morotai, Likupang, dan Danau Toba '
            f'— bukan karena tidak ada pola, tapi jumlah hotel terlalu kecil '
            f'untuk model spasial yang reliable.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    spacer(16)

    st.markdown(
        '<div style="background:#0F2A4A;border-radius:12px;padding:18px 22px;">'
        '<div style="font-size:14px;font-weight:700;color:#FFFFFF;margin-bottom:12px;">'
        'Ringkasan Temuan Spasial untuk Investor</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">'

        '<div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px;">'
        '<div style="font-size:11px;font-weight:700;color:#22C55E;margin-bottom:6px;">'
        'Strategi Terbukti dari Data</div>'
        '<div style="font-size:11px;color:#CBD5E1;line-height:1.7;">'
        '· Masuk di kluster GWR (6 destinasi) — pola spasial terbukti signifikan<br>'
        '· Posisi hotel &lt;2km dari atraksi utama (terutama Tanjung Kelayang)<br>'
        '· Manfaatkan efek aglomerasi di Borobudur (+1.50) dan Wakatobi (+0.75)<br>'
        '· Di destinasi alam, keterpencilan bisa jadi nilai jual (Borobudur, Wakatobi)'
        '</div>'
        '</div>'

        '<div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px;">'
        '<div style="font-size:11px;font-weight:700;color:#EF4444;margin-bottom:6px;">'
        'Risiko yang Harus Dihindari</div>'
        '<div style="font-size:11px;color:#CBD5E1;line-height:1.7;">'
        '· Mandalika sudah jenuh — kompetitor baru justru merugikan (-0.35)<br>'
        '· Lokasi jauh dari pusat di destinasi non-alam (Mandalika koef -6.46)<br>'
        '· Morotai: atraksi ada tapi ekosistem belum terkoneksi — timing masih berisiko<br>'
        '· OLS destinasi = peluang first-mover, bukan zona bebas risiko'
        '</div>'
        '</div>'

        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ════════════════════════════════════════════════════════════════════
# PAGE 8 — DESTINATION DEEP DIVE
# ════════════════════════════════════════════════════════════════════

def page_destination():
    from functions.maps import render_destination_map
    from streamlit_folium import st_folium

    page_header_compact("Profil Destinasi",
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

    # ── Hitung persentase Red/Blue Ocean ───────────────────────
    oc_counts = d_df['status_ocean'].value_counts()
    total_oc  = oc_counts.sum()
    red_n     = int(sum(v for k, v in oc_counts.items() if 'Red' in k))
    blue_n    = int(sum(v for k, v in oc_counts.items() if 'Blue' in k))
    red_pct   = (red_n / total_oc * 100) if total_oc > 0 else 0
    blue_pct  = (blue_n / total_oc * 100) if total_oc > 0 else 0

    PANEL_HEIGHT = 380  # ← tinggi seragam untuk panel kiri & peta

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
            ("Avg Rating",   f"{d_df['rating'].mean():.1f}",                   "#F59E0B"),
            ("Competition",  f"{d_df['competition_score'].mean():.0f}%",          "#EF4444"),
            ("Demand Score", f"{d_df['demand_score'].mean():.0f}%",               "#22C55E"),
            ("Opportunity",  f"{d_df['opportunity_score'].mean():.0f}",            "#22C55E"),
            ("Avg IIA",      f"{d_df['investor_interest_index'].mean():.0f}",      "#F59E0B"),
            ("Ecosystem",    f"{d_df['ecosystem_score'].mean():.0f}",              "#3B82F6"),
        ]
        for lbl, val, clr in kpi_items:
            st.markdown(
                f'<div class="metric-row">'
                f'  <span class="metric-name">{lbl}</span>'
                f'  <span style="font-size:13px;font-weight:700;color:{clr};">{val}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # ── Red/Blue Ocean sebagai lanjutan list, bukan strip terpisah ──
        st.markdown(
            f'<div class="metric-row">'
            f'  <span class="metric-name">Red Ocean</span>'
            f'  <span style="font-size:13px;font-weight:700;color:#C0392B;">{red_pct:.0f}% <span style="font-size:10px;color:#94A3B8;font-weight:400;"></span></span>'
            f'</div>'
            f'<div class="metric-row">'
            f'  <span class="metric-name">Blue Ocean</span>'
            f'  <span style="font-size:13px;font-weight:700;color:#1D5FAD;">{blue_pct:.0f}% <span style="font-size:10px;color:#94A3B8;font-weight:400;"></span></span>'
            f'</div>',
            unsafe_allow_html=True
        )

    with cm:
        st.markdown('<div style="border:1px solid rgba(0,212,255,0.15);border-radius:12px;overflow:hidden;">', unsafe_allow_html=True)
        with st.spinner("Loading destination map..."):
            m = render_destination_map(d_df, sel)
            st_folium(m, height=PANEL_HEIGHT, width="stretch", returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)
    spacer(14)
    ta, tb, tc, td = st.tabs(["Penawaran", "Permintaan", "Ekosistem", "Investasi"])

    # ════════════════════════════════════════════════════
    # TAB 1 — PASAR (Penawaran + Status Persaingan)
    # ════════════════════════════════════════════════════
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
                    height=260,
                    margin=dict(l=10, r=60, t=10, b=10),
                    xaxis=dict(
                        gridcolor='rgba(64,145,108,0.1)',
                        tickfont=dict(color='#2D6A4F', size=10),
                        title='Jumlah Akomodasi',
                        title_font=dict(color='#2D6A4F', size=10),
                        range=[0, tc_cnt.values.max() * 1.2],
                    ),
                    yaxis=dict(
                        tickfont=dict(color='#1B4332', size=11),
                        autorange='reversed',
                    ),
                    showlegend=False,
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

        with cb2:
            section_header("Distribusi Bintang Hotel")
            if 'kasta_bintang' in d_df.columns:
                sc_cnt = d_df['kasta_bintang'].value_counts().head(15)
                star_colors = ['#1B4332','#2D6A4F','#40916C','#52B788','#74A98A',
                               '#E9A020','#B8680A','#7B2D8B','#1565C0','#00897B',
                               '#C2185B','#4A7C59','#8B9B6F','#B08968','#5A8A7A']
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
                max_x = sc_cnt.values.max() * 1.2 if len(sc_cnt) > 0 else 10
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=max(300, len(sc_cnt) * 24),   # ← tinggi menyesuaikan jumlah kategori
                    margin=dict(l=10, r=60, t=10, b=10),
                    xaxis=dict(
                        gridcolor='rgba(64,145,108,0.1)',
                        tickfont=dict(color='#2D6A4F', size=10),
                        title='Jumlah Hotel',
                        title_font=dict(color='#2D6A4F', size=10),
                        range=[0, max_x],
                    ),
                    yaxis=dict(
                        tickfont=dict(color='#1B4332', size=10),
                        autorange='reversed',
                    ),
                    showlegend=False,
                )
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        spacer(16)


    # ← hist_chart tetap di sini, setelah tab Pasar selesai, sebelum tab Permintaan
    def hist_chart(kolom, color, title_x):
        fig = go.Figure(go.Histogram(
            x=d_df[kolom].dropna(), nbinsx=15,
            marker=dict(color=color, opacity=0.85, line=dict(width=0))
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=280,
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

    # ════════════════════════════════════════════════════
    # TAB 2 — PERMINTAAN
    # ════════════════════════════════════════════════════
    with tb:
        ce2, cf2 = st.columns([1, 1])
        with ce2:
            section_header("Distribusi Skor Permintaan")
            st.plotly_chart(hist_chart('demand_score', '#40916C', 'Skor Permintaan'),
                            width="stretch", config={'displayModeBar': False})
        with cf2:
            section_header("Top 5 Hotel Ulasan Terbanyak", "Volume Ulasan Tertinggi di Destinasi Ini")
            if 'jumlah_ulasan' in d_df.columns:
                top5 = d_df.nlargest(5, 'jumlah_ulasan')
                medal_map = {0: '🥇', 1: '🥈', 2: '🥉'}
                for i, (_, row) in enumerate(top5.iterrows()):
                    medal = medal_map.get(i, f'{i+1}.')
                    nama  = str(row.get('nama_hotel', 'Unknown'))[:32]
                    rate  = row.get('rating', 0)
                    ulas  = int(row.get('jumlah_ulasan', 0))
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;'
                        f'padding:10px 12px;background:#FFFFFF;border:1px solid #E2E8F0;'
                        f'border-radius:8px;margin-bottom:6px;">'
                        f'  <div style="font-size:16px;min-width:26px;">{medal}</div>'
                        f'  <div style="flex:1;">'
                        f'    <div style="font-size:12px;font-weight:700;color:#0F2A4A;'
                        f'line-height:1.3;">{nama}</div>'
                        f'    <div style="font-size:10px;color:#74A98A;margin-top:2px;">'
                        f'⭐ {rate:.1f} · {ulas:,} ulasan</div>'
                        f'  </div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    # ════════════════════════════════════════════════════
    # TAB 3 — EKOSISTEM (tetap)
    # ════════════════════════════════════════════════════
    with tc:
        cg2, ch2 = st.columns(2)
        with cg2:
            section_header("Distribusi Skor Ekosistem")
            st.plotly_chart(hist_chart('ecosystem_score', '#52B788', 'Skor Ekosistem'),
                            width="stretch", config={'displayModeBar': False})
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

    # ════════════════════════════════════════════════════
    # TAB 4 — INVESTASI (tetap)
    # ════════════════════════════════════════════════════
    with td:
        ci2, cj2 = st.columns(2)
        with ci2:
            section_header("Distribusi Skor Peluang")
            st.plotly_chart(hist_chart('opportunity_score', '#1565C0', 'Skor Peluang'),
                            width="stretch", config={'displayModeBar': False})
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
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
       
# ════════════════════════════════════════════════════════════════════
# PAGE 9 — STRATEGIC RECOMMENDATIONS
# ════════════════════════════════════════════════════════════════════

def page_strategy():
    page_header_compact("Rekomendasi", "Laporan Intelijen Eksekutif · Strategi Investasi Kemenparekraf", "")

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
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    spacer(24)

    # ── INVESTOR STRATEGY ROADMAP — 3 KOLOM SEJAJAR ──────────────
    section_header("Strategi Investasi", "Prioritas Tindakan Berdasarkan Horizon Waktu")
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
            ("Land Banking Morotai & Likupang",
             "Infrastruktur belum masuk, harga tanah masih murah. Begitu KEK aktif, harga akan naik cepat dan peluang ini hilang."),
            ("Akuisisi Resort Wakatobi",
             "Tidak bisa bangun baru di sini karena regulasi konservasi. Kalau mau masuk Wakatobi, beli yang sudah ada."),
            ("Boutique Lodge Raja Ampat",
             "Persaingan paling rendah dari semua destinasi. Cocok untuk properti kecil yang tidak butuh tamu banyak untuk balik modal."),
            ("Konversi Aset Danau Toba",
             "Banyak hotel bintang 2–3 yang sepi bukan karena sepi tamu, tapi karena salah segmen. Ubah dulu, bangun nanti."),
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
            ("Resort Marine Heritage Morotai",
             "Sepi saingan, tapi pasar belum matang hari ini. Mulai bangun sekarang agar siap beroperasi tepat saat konektivitasnya membaik."),
            ("Glamping Premium Bromo",
             "Jutaan orang sudah datang ke Bromo setiap tahun, tapi tidak ada yang menawarkan pengalaman menginap yang benar-benar premium. Permintaannya ada, tawarannya belum."),
            ("Lakefront Resort Danau Toba",
             "Tol Trans-Sumatra akan selesai bertahap. Properti yang sudah berdiri saat akses terbuka akan langsung menikmati lonjakan tamu."),
            ("Kemitraan Event Mandalika",
             "MotoGP dan event lainnya mengisi kalender 8–12 kali setahun. Daripada bersaing di pasar yang sudah penuh, lebih baik jadi mitra resmi event-nya."),
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
            ("Dive Circuit Raja Ampat – Wakatobi – Labuan Bajo",
             "Wisatawan selam kelas dunia biasanya mengunjungi ketiganya secara terpisah. Belum ada satu operator pun yang menghubungkan ketiganya sebagai satu paket perjalanan."),
            ("Jaringan Resort Zona UNESCO",
             "Borobudur, Wakatobi, dan Komodo punya nama besar tapi akomodasi premium-nya masih sangat sedikit. Sulit dimasuki kompetitor karena regulasinya ketat."),
            ("Platform Data Investasi Pariwisata",
             "Sampai sekarang tidak ada tempat yang bisa dipakai investor untuk melihat data kinerja, harga aset, dan peluang transaksi properti wisata Indonesia secara terpusat."),
        ]
    },
]

    for r in roadmap:
        with r["col"]:
            items_html = ''
            for title, desc in r["items"]:
                items_html += (
                    f'<div style="padding:12px 0;border-top:1px solid {r["border"]}22;">'
                    f'  <div style="font-size:12px;font-weight:700;color:#1B4332;'
                    f'margin-bottom:4px;line-height:1.4;">{title}</div>'
                    f'  <div style="font-size:11px;color:#4A6080;line-height:1.6;">{desc}</div>'
                    f'</div>'
                )
            st.markdown(
                f'<div style="background:{r["bg"]};border:1.5px solid {r["border"]};'
                f'border-radius:12px;padding:16px;'
                f'min-height:460px;box-sizing:border-box;">'   # ← min-height seragam
                f'  <div style="display:flex;justify-content:space-between;'
                f'align-items:center;margin-bottom:14px;">'
                f'    <div style="font-size:14px;font-weight:800;color:{r["color"]};">'
                f'{r["label"]}</div>'
                f'    <div style="font-size:10px;font-weight:600;color:{r["color"]};'
                f'background:{r["badge_bg"]};border:1px solid {r["border"]};'
                f'border-radius:20px;padding:3px 12px;white-space:nowrap;">'
                f'{r["period"]}</div>'
                f'  </div>'
                f'  {items_html}'
                f'</div>',
                unsafe_allow_html=True
            )

# ════════════════════════════════════════════════════════════════════
# PAGE ENGINE — ANALYTICS ENGINE (gabungan 4 sub-halaman)
# ════════════════════════════════════════════════════════════════════

def page_engine():
    page_header_compact("Pemodelan", "Ekonometrika Spasial · NLP · Ekosistem · Kompetisi", "")
    t1, t2, t3, t4 = st.tabs([
        "Kompetisi Pasar",
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
    page_header_compact(
        "Dinamika Pasar",
        "Temuan Kunci dari 3.082 Data Hotel · 10 Destinasi Super Prioritas",
        ""
    )

    # ── Catatan metodologi ─────────────────────────────────────────
    st.markdown(
        '<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;'
        'padding:12px 16px;margin-bottom:20px;font-size:11px;color:#92400E;line-height:1.7;">'
        '<b>Catatan cara membaca:</b> '
        'Demand score dihitung secara relatif di dalam masing-masing destinasi (skala 0–100 per DSP), '
        'bukan perbandingan volume absolut antar destinasi. '
        'Artinya, demand score 80 di Raja Ampat tidak berarti permintaannya lebih tinggi dari '
        'demand score 60 di Borobudur — keduanya hanya menunjukkan posisi relatif hotel tersebut '
        'di dalam destinasinya sendiri. '
        'Untuk melihat volume permintaan aktual, gunakan data total ulasan per destinasi.'
        '</div>',
        unsafe_allow_html=True
    )

    section_header(
        "Apa yang Sebenarnya Terjadi di Pasar?",
        "Temuan langsung dari data — bukan asumsi"
    )

    insights = [
        {
            'type': 'danger',
            'tag':  'Pasar Sudah Sangat Padat di Hampir Semua Destinasi',
            'text': (
                '93% dari 3.082 hotel berada di zona kepadatan tinggi (Red Ocean) — bersaing langsung '
                'dengan hotel lain dalam radius 2 km. Labuan Bajo paling padat: rata-rata satu hotel '
                'dikelilingi 83 hotel lain dalam radius 1 km. Mandalika 58, Borobudur 50. '
                'Status Red Ocean ini diukur dari kepadatan geografis, bukan dari tingkat '
                'profitabilitas — artinya padat secara lokasi, belum tentu pasarnya jenuh sepenuhnya.'
            ),
        },
        {
            'type': 'success',
            'tag':  'Raja Ampat: Persaingan Paling Rendah, Distribusi Permintaan Paling Merata',
            'text': (
                'Raja Ampat mencatat competition score terendah (3.0) — rata-rata hanya 5 hotel '
                'bersaing dalam radius 1 km. Distribusi permintaan di dalam destinasi ini juga '
                'paling merata dibanding destinasi lain (demand score rata-rata 43.1). '
                'Perlu dicatat: volume ulasan absolutnya masih kecil (6.017 total) dibanding '
                'Borobudur (81.086) atau Bromo (80.112) — ini destinasi yang masih berkembang, '
                'bukan yang sudah ramai. Peluang first-mover ada, tapi pasar belum matang sepenuhnya.'
            ),
        },
        {
            'type': 'warning',
            'tag':  'Labuan Bajo: Opportunity Score Tertinggi tapi Risiko Persaingan Paling Berat',
            'text': (
                'Labuan Bajo memimpin dengan opportunity score rata-rata 53.7 — tertinggi dari semua '
                'destinasi. Namun 100% hotelnya masuk zona kepadatan tinggi dengan rata-rata 83 saingan '
                'per km. Opportunity score yang tinggi ini mencerminkan kombinasi ekosistem atraksi '
                'yang kuat dan aksesibilitas baik — bukan berarti mudah masuk. '
                'Investor baru di segmen mid-range akan langsung bersaing keras dari hari pertama.'
            ),
        },
        {
            'type': 'info',
            'tag':  'Mandalika: Terbanyak Hotel, tapi Bukan Pilihan Utama untuk Investasi Baru',
            'text': (
                'Dengan 789 hotel — hampir seperempat dari total data nasional — Mandalika adalah '
                'destinasi dengan supply paling besar. Opportunity score rata-ratanya 38.0, berada '
                'di bawah Labuan Bajo, Borobudur, Morotai, Raja Ampat, dan Wakatobi. '
                '96% hotelnya berada di zona kepadatan tinggi. Bukan tidak ada peluang, '
                'tapi ruangnya sudah jauh lebih sempit dibanding destinasi lain.'
            ),
        },
        {
            'type': 'success',
            'tag':  'Borobudur: Kombinasi Terbaik antara Peluang, Volume Pasar, dan Persaingan',
            'text': (
                'Borobudur mencatat opportunity score 48.8 dengan competition score 29.2 dan '
                'total ulasan tertinggi dari semua destinasi (81.086) — bukti bahwa pasar di sini '
                'sudah terbentuk dengan baik. Persaingannya lebih terukur dibanding Labuan Bajo. '
                'Untuk investor yang ingin masuk ke pasar yang sudah terbukti dengan ruang kompetisi '
                'yang masih lebih sehat, Borobudur adalah pilihan paling solid secara data.'
            ),
        },
        {
            'type': 'success',
            'tag':  'Morotai: Persaingan Rendah dengan Opportunity Score di Atas Rata-rata',
            'text': (
                'Morotai mencatat opportunity score 44.1 dengan competition score hanya 6.3 — '
                'salah satu yang paling rendah. Tapi volume pasarnya masih sangat kecil: '
                'total ulasan hanya 1.209, terendah ketiga. Ini destinasi untuk investor '
                'dengan horizon jangka panjang yang siap masuk sebelum infrastruktur dan '
                'ekosistem wisatanya benar-benar matang.'
            ),
        },
        {
            'type': 'warning',
            'tag':  'Zona Sepi Saingan Tidak Otomatis Berarti Peluang Lebih Besar',
            'text': (
                '212 hotel (7% dari total) berada di zona geografis yang relatif terisolasi dari '
                'kluster hotel lain. Terbanyak ada di Bromo Tengger Semeru (41 hotel), Mandalika (34), '
                'dan Borobudur (33). Namun rata-rata opportunity score zona ini (28.8) justru lebih '
                'rendah dari zona yang padat (42.1) — lokasi yang sepi hotel kadang memang karena '
                'posisinya kurang strategis, bukan karena pasarnya belum digarap.'
            ),
        },
        {
            'type': 'danger',
            'tag':  'Manado Belum Menunjukkan Sinyal Pasar yang Cukup untuk Investasi Baru',
            'text': (
                'Manado (Likupang Hub) mencatat opportunity score rata-rata 12.8 — terendah dari '
                'semua destinasi. Total ulasan hanya 10.635 dengan median 2 ulasan per hotel, '
                'menunjukkan tingkat kunjungan yang masih sangat rendah di level properti individual. '
                '83% hotelnya berada di zona kepadatan tinggi meski jumlah hotelnya hanya 89. '
                'Data belum mendukung rekomendasi investasi akomodasi baru di wilayah ini saat ini.'
            ),
        },
    ]

    class_map = {'success': 'opportunity', 'danger': 'critical', 'warning': 'warning', 'info': 'info'}
    label_map = {'success': 'Peluang', 'danger': 'Perhatian', 'warning': 'Catatan', 'info': 'Temuan'}
    color_map = {'success': '#1A7A4A', 'danger': '#C0392B', 'warning': '#B45309', 'info': '#1D5FAD'}

    for ins in insights:
        t = ins['type']
        clr = color_map.get(t, '#64748B')
        lbl = label_map.get(t, 'Info')
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;'
            f'border-left:4px solid {clr};border-radius:0 10px 10px 0;'
            f'padding:14px 18px;margin-bottom:10px;">'
            f'  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'    <div style="font-size:9px;font-weight:700;color:{clr};'
            f'background:{clr}18;border-radius:4px;padding:2px 8px;'
            f'letter-spacing:0.8px;text-transform:uppercase;">{lbl}</div>'
            f'    <div style="font-size:13px;font-weight:700;color:#0F2A4A;">{ins["tag"]}</div>'
            f'  </div>'
            f'  <div style="font-size:12px;color:#475569;line-height:1.7;">{ins["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    spacer(24)

    section_header(
        "Rekomendasi Berdasarkan Data",
        "5 langkah konkret yang didukung temuan dari 3.082 hotel"
    )

    recs = [
        {
            'number': 1,
            'title':  'Borobudur untuk Investor yang Butuh Kepastian Pasar',
            'text':   (
                'Dari semua destinasi, Borobudur punya kombinasi paling seimbang: opportunity score '
                'tinggi (48.8), volume ulasan terbesar (81.086 — bukti pasar sudah terbentuk), '
                'dan persaingan lebih terukur dari Labuan Bajo. Cocok untuk konsep boutique heritage '
                'atau akomodasi berbasis wisata budaya yang memanfaatkan ekosistem atraksi yang sudah matang.'
            ),
        },
        {
            'number': 2,
            'title':  'Raja Ampat untuk Investor Jangka Panjang di Segmen Eco-Premium',
            'text':   (
                'Persaingan paling rendah (competition score 3.0) dengan distribusi permintaan '
                'paling merata di dalam destinasi. Tapi volume pasarnya masih kecil (6.017 ulasan total) '
                '— ini bukan destinasi yang langsung ramai. Masuk sekarang berarti menjadi pemain awal '
                'sebelum infrastruktur matang. Paling cocok untuk eco-resort atau dive lodge '
                'yang tidak butuh volume tamu tinggi untuk profitable.'
            ),
        },
        {
            'number': 3,
            'title':  'Labuan Bajo Hanya untuk Segmen Premium dengan Diferensiasi Kuat',
            'text':   (
                'Opportunity score tertinggi (53.7) mencerminkan ekosistem wisata yang sudah sangat '
                'kuat, tapi 100% pasarnya sudah padat secara geografis dengan 83 saingan per km. '
                'Masuk di segmen mid-range hampir pasti berujung perang harga. '
                'Kalau masuk, diferensiasi harus tidak bisa ditiru: lokasi eksklusif, '
                'akses langsung ke Komodo, atau fasilitas yang benar-benar unik.'
            ),
        },
        {
            'number': 4,
            'title':  'Morotai untuk Early-Mover yang Siap Menunggu',
            'text':   (
                'Persaingan sangat rendah (competition score 6.3) dengan opportunity score 44.1. '
                'Tapi ini destinasi yang pasarnya belum matang — total ulasan hanya 1.209. '
                'Cocok untuk investor dengan horizon 5–10 tahun yang ingin masuk sebelum '
                'ekosistem wisata dan infrastrukturnya berkembang penuh. Risiko lebih tinggi, '
                'tapi potensi first-mover advantage juga lebih besar.'
            ),
        },
        {
            'number': 5,
            'title':  'Tunda Investasi Baru di Mandalika dan Manado',
            'text':   (
                'Mandalika sudah sangat padat — 789 hotel dengan 96% di zona kepadatan tinggi '
                'dan opportunity score yang relatif rendah (38.0). '
                'Manado bahkan lebih jelas: opportunity score 12.8, terendah dari semua destinasi, '
                'dengan volume kunjungan per hotel yang masih sangat kecil. '
                'Kalau sudah punya aset di dua wilayah ini, fokus pada optimasi dan diferensiasi — '
                'bukan menambah unit baru.'
            ),
        },
    ]

    for rec in recs:
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;'
            f'padding:16px 20px;margin-bottom:10px;'
            f'box-shadow:0 1px 4px rgba(15,42,74,0.06);">'
            f'  <div style="display:flex;align-items:flex-start;gap:14px;">'
            f'    <div style="min-width:36px;height:36px;border-radius:8px;'
            f'background:#0F2A4A;display:flex;align-items:center;justify-content:center;'
            f'font-size:16px;font-weight:900;color:#FFFFFF;flex-shrink:0;">{rec["number"]}</div>'
            f'    <div>'
            f'      <div style="font-size:13px;font-weight:700;color:#0F2A4A;margin-bottom:6px;">'
            f'{rec["title"]}</div>'
            f'      <div style="font-size:12px;color:#475569;line-height:1.7;">{rec["text"]}</div>'
            f'    </div>'
            f'  </div>'
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