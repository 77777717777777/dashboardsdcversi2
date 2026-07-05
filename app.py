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

from functions.analytics import load_top3_data, load_branding_data  # tambahkan di import

df_raw = load_all_data()
dest_stats_raw = get_destination_stats(df_raw)
branding_df = load_branding_data()
top3_df = load_top3_data()


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
            "Kekuatan Ekosistem":    "attraction",
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
        elif sel_layer == "Kekuatan Ekosistem":
            legend_items = [
                ('#22C55E', 'Ekosistem Tinggi'),
                ('#00D4FF', 'Ekosistem Sedang'),
                ('#F43F5E', 'Ekosistem Lemah'),
            ]
        elif sel_layer == "Hotel Premium":
            legend_items = [
                ('#A855F7', 'Segmen Premium / Luxury'), 
                ('#64748B', 'Segmen Standar / Budget')
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
        #s1, s2, s3, s4 = st.columns(4)
        #stats_items = [
        #    (s1, "Total Hotel Terpetakan", f"{len(df):,}", "#2563EB"),
        #    (s2, "Peluang Tinggi", f"{int((df['opportunity_score'] >= 75).sum()):,}", "#16A34A"),
        #    (s3, "Zona Pasar Jenuh", f"{int(df['status_ocean'].str.contains('Red', na=False).sum()):,}", "#DC2626"),
        #    (s4, "Rata-rata Ekosistem", f"{df['ecosystem_score'].mean():.1f}", "#7C3AED"),
        #]
        #for col, lbl, val, clr in stats_items:
        #    with col:
        #        st.markdown(
        #            f'<div class="stats-card" style="border-top:3px solid {clr};">'
        #            f'  <div class="stats-card-label">{lbl}</div>'
        #            f'  <div class="stats-card-value" style="color:{clr};">{val}</div>'
        #            f'</div>',
        #            unsafe_allow_html=True
        #        )


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

    # ── BARIS 1: Matriks Risiko vs Peluang + 5 Destinasi Blue Ocean ──
    c1, c2 = st.columns(2)

    with c1:
        section_header("Matriks Risiko vs Peluang", "Persaingan vs Peluang Investasi")
        fig = plot_investment_matrix_enhanced(dest_stats)
        fig.update_traces(mode='markers', textposition=None)
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    with c2:
        section_header("5 Destinasi dengan Akomodasi Blue Ocean",
                       "Persaingan Terendah · Jumlah akomodasi Blue Ocean ≠ besarnya peluang")
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

    spacer(20)

    # ── BARIS 2: Efek Aglomerasi (GWR) + Temuan Strategis ──────
    c3, c4 = st.columns(2)

    with c3:
        section_header("Efek Aglomerasi (GWR)", "Koefisien Kompetitor per Destinasi")
        if 'koef_saingan_radius_1km' in df.columns:
            fig = plot_gwr_bar(df, height=290)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
            st.markdown(
                '<div style="display:flex;gap:5px;justify-content:center;flex-wrap:wrap;'
                'margin-top:-35px;font-size:9px;color:#94A3B8;position:relative;z-index:10;">' # ← Ubah di sini
                '<div style="display:flex;align-items:center;gap:4px;">'
                '<div style="width:9px;height:9px;background:#1A7A4A;border-radius:2px;"></div>'
                'Lokal (GWR) — positif</div>'
                '<div style="display:flex;align-items:center;gap:4px;">'
                '<div style="width:9px;height:9px;background:#86C9A5;border-radius:2px;"></div>'
                'Global (OLS/SLM) — positif</div>'
                '<div style="display:flex;align-items:center;gap:4px;">'
                '<div style="width:9px;height:9px;background:#C0392B;border-radius:2px;"></div>'
                'Lokal (GWR) — negatif</div>'
                '<div style="display:flex;align-items:center;gap:4px;">'
                '<div style="width:9px;height:9px;background:#E8A0A0;border-radius:2px;"></div>'
                'Global (OLS/SLM) — negatif</div>'
                '</div>',
                unsafe_allow_html=True
            )

    with c4:
        section_header("Temuan Strategis: Efek Aglomerasi", "Interpretasi Koefisien Kompetitor")

        dest_level_coef = df.dropna(subset=['koef_saingan_radius_1km']).groupby('destinasi')['koef_saingan_radius_1km'].mean()
        top_pos_dest = dest_level_coef.idxmax()
        top_pos_val  = dest_level_coef.max()
        top_neg_dest = dest_level_coef.idxmin()
        top_neg_val  = dest_level_coef.min()
        pct_positif  = (dest_level_coef > 0).mean() * 100

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;'
            f'padding:18px 20px;min-height:290px;box-sizing:border-box;">'
            f'<div style="font-size:12px;color:#334155;line-height:1.8;text-align:justify;">'
            f'Koefisien positif pada model GWR mengindikasikan adanya <b>efek aglomerasi</b>, '
            f'yaitu kondisi ketika pengelompokan akomodasi di suatu area justru meningkatkan '
            f'kunjungan wisatawan secara keseluruhan. Sebaliknya, koefisien negatif menunjukkan '
            f'<b>persaingan destruktif</b>, di mana penambahan hotel baru justru menekan kinerja '
            f'seluruh pemain yang sudah ada di area tersebut.'
            f'Dari {len(dest_level_coef)} destinasi yang dianalisis, sebanyak <b style="color:#1A7A4A">'
            f'{pct_positif:.0f}%</b> menunjukkan koefisien positif. Efek aglomerasi paling kuat '
            f'ditemukan di <b style="color:#1A7A4A">{top_pos_dest}</b> (koefisien {top_pos_val:.3f}), '
            f'sedangkan indikasi persaingan destruktif paling besar terjadi di '
            f'<b style="color:#C0392B">{top_neg_dest}</b> (koefisien {top_neg_val:.3f}).'
            f'Berdasarkan temuan ini, investasi baru sebaiknya diprioritaskan pada destinasi '
            f'dengan koefisien positif, karena penambahan akomodasi di lokasi tersebut cenderung '
            f'memperkuat daya tarik kawasan secara keseluruhan, bukan justru memperketat persaingan.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

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
            fig.update_xaxes(title='Rata-rata jarak dalam 5km')
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
            fig.update_xaxes(title='Jarak ke atraksi terdekat (km)')
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
            fig.update_xaxes(title='Rata-rata jarak dalam 5km')
            fig.update_yaxes(title='Number of Hotels')
            fig.update_layout(showlegend=False) 
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
        #st.markdown('</div>', unsafe_allow_html=True)

    spacer(14)
    st.markdown(insight_html(
        "🌿 Ecosystem Intelligence Insight",
        "Destinasi dengan jumlah atraksi yang tinggi namun jumlah akomodasi yang masih rendah "
        "berpotensi menjadi lokasi dengan peluang investasi yang lebih baik. "
        "Hotel yang berada dalam radius 1 km dari atraksi utama menunjukkan rata-rata jumlah ulasan "
        "yang lebih tinggi dibandingkan hotel yang berjarak lebih jauh. "
        "Kedekatan antara kluster atraksi dan akomodasi menjadi salah satu faktor penting "
        "yang mempengaruhi daya saing pariwisata dalam jangka panjang.",
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
    avg_nat = nat_df['Median_Popularitas'].mean() if len(nat_df) > 0 else 0
    avg_std = std_df['Median_Popularitas'].mean() if len(std_df) > 0 else 0
    lift    = ((avg_nat - avg_std) / max(avg_std, 1)) * 100

    k1,k2,k3,k4 = st.columns(4)
    for col,(lbl,val,sub,clr) in zip([k1,k2,k3,k4],[
        ("Nature Branding Median Score", f"{avg_nat:.1f}", "Hotels w/ Nature Names (Median)", 'success'),
        ("Standard Branding Median Score", f"{avg_std:.1f}", "Standard Hotel Names (Median)",  'accent'),
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

    all_dest_top3 = ['Semua Destinasi'] + sorted([
        d for d in top3_df['destinasi'].unique().tolist()
        if 'Manado' not in str(d)
    ])
    sel_dest_top3 = st.selectbox(
        "Filter Destinasi", all_dest_top3,
        key='inv_dest_filter', label_visibility='collapsed'
    )

    filtered_top3 = (
        top3_df if sel_dest_top3 == 'Semua Destinasi'
        else top3_df[top3_df['destinasi'] == sel_dest_top3]
    )
    filtered_top3 = filtered_top3[
        ~filtered_top3['destinasi'].str.contains('Manado', case=False, na=False)
    ]

    rank_colors = {
        1: ('#E9A020', '#FFFBEB'),   # emas
        2: ('#94A3B8', '#F8FAFC'),   # perak
        3: ('#B8680A', '#FFF7ED'),   # perunggu
    }

    for dest_name, grp in filtered_top3.groupby('destinasi'):
        dest_avg_opp  = dest_inv.loc[dest_inv['destinasi'] == dest_name, 'avg_opp'].values
        dest_avg_opp  = dest_avg_opp[0] if len(dest_avg_opp) > 0 else 0
        grade_local   = 'A' if dest_avg_opp >= 50 else ('B' if dest_avg_opp >= 38 else 'C')
        grade_clr_loc = '#1A7A4A' if grade_local == 'A' else ('#1D5FAD' if grade_local == 'B' else '#B8680A')

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:18px 0 8px;">'
            f'  <div style="font-size:13px;font-weight:900;color:{grade_clr_loc};'
            f'background:{grade_clr_loc}18;border:1.5px solid {grade_clr_loc}40;'
            f'border-radius:6px;width:26px;height:26px;'
            f'display:flex;align-items:center;justify-content:center;">{grade_local}</div>'
            f'  <div style="font-size:14px;font-weight:800;color:#0F2A4A;">{dest_name}</div>'
            f'  <div style="font-size:10px;color:#74A98A;padding:2px 10px;'
            f'background:#F0FDF4;border:1px solid #D1FAE5;border-radius:20px;">'
            f'Avg Opp {dest_avg_opp:.1f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        cols = st.columns(len(grp))
        for col, (rank, (_, row)) in zip(cols, enumerate(grp.iterrows(), 1)):
            badge_clr, badge_bg = rank_colors.get(rank, ('#CBD5E1', '#F8FAFC'))
            seg_raw = row.get('market_segment', '')
            if 'Blue Ocean' in seg_raw:
                seg_clr, seg = '#1D5FAD', 'Blue Ocean'
            elif 'Red Ocean' in seg_raw:
                seg_clr, seg = '#C0392B', 'Red Ocean'
            else:
                seg_clr, seg = '#94A3B8', str(seg_raw)[:20]
            opp_score = row['opportunity_score']
            demand    = row['demand_score']
            quality   = row['quality_score']
            lat       = row['latitude']
            lon       = row['longitude']
            atraksi   = row.get('jumlah_atraksi_radius_5km', 0)
            jarak_atk = row.get('jarak_ke_atraksi_terdekat_km', 0)

            with col:
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #D8EDE4;'
                    f'border-radius:10px;padding:14px 16px;'
                    f'box-shadow:0 1px 4px rgba(27,67,50,0.06);">'

                    # Header: rank badge + nama hotel
                    f'<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:10px;">'
                    f'  <div style="width:22px;height:22px;border-radius:50%;'
                    f'background:{badge_bg};border:1.5px solid {badge_clr};'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:10px;font-weight:800;color:{badge_clr};flex-shrink:0;margin-top:1px;">{rank}</div>'
                    f'  <div style="font-size:12px;font-weight:700;color:#0F2A4A;line-height:1.35;">'
                    f'{row["nama_hotel"]}</div>'
                    f'</div>'

                    # Segment badge kecil
                    f'<div style="font-size:9px;font-weight:600;color:#2D6A4F;'
                    f'background:#F0FDF4;border:1px solid #D1FAE5;border-radius:4px;'
                    f'padding:2px 7px;display:inline-block;margin-bottom:10px;">{seg}</div>'

                    # Score grid
                    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;'
                    f'gap:6px;margin-bottom:10px;">'
                    f'<div style="background:#F0FDF4;border-radius:6px;padding:6px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#74A98A;font-weight:600;letter-spacing:0.5px;">OPP</div>'
                    f'  <div style="font-size:16px;font-weight:900;color:#1A7A4A;line-height:1;">{opp_score:.0f}</div>'
                    f'</div>'
                    f'<div style="background:#EFF6FF;border-radius:6px;padding:6px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#93C5FD;font-weight:600;letter-spacing:0.5px;">DEMAND</div>'
                    f'  <div style="font-size:16px;font-weight:900;color:#1D5FAD;line-height:1;">{demand:.0f}</div>'
                    f'</div>'
                    f'<div style="background:#FFFBEB;border-radius:6px;padding:6px 4px;text-align:center;">'
                    f'  <div style="font-size:8px;color:#E9A020;font-weight:600;letter-spacing:0.5px;">QUALITY</div>'
                    f'  <div style="font-size:16px;font-weight:900;color:#B8680A;line-height:1;">{quality:.0f}</div>'
                    f'</div>'
                    f'</div>'

                    # Detail baris — tanpa emoji
                    f'<div style="font-size:10px;color:#64748B;line-height:1.7;'
                    f'border-top:1px solid #F1F5F9;padding-top:8px;margin-bottom:8px;">'
                    f'  <div>{int(atraksi)} atraksi dalam radius 5km</div>'
                    f'  <div>{jarak_atk:.2f} km ke atraksi terdekat</div>'
                    f'</div>'

                    # Koordinat
                    f'<div style="padding:6px 9px;background:#F8FAFC;'
                    f'border:1px solid #E2E8F0;border-radius:6px;">'
                    f'  <div style="font-size:8px;color:#74A98A;font-weight:700;'
                    f'letter-spacing:0.5px;margin-bottom:2px;">KOORDINAT GPS</div>'
                    f'  <div style="font-family:monospace;font-size:10px;color:#1B4332;">'
                    f'{lat:.6f}, {lon:.6f}</div>'
                    f'</div>'

                    f'</div>',
                    unsafe_allow_html=True
                )

        spacer(6)

    spacer(20)

    col_quad, col_under = st.columns([1.3, 1])

    #with col_quad:
    #    section_header(
    #        "Kuadran Wilayah: Demand vs Competition",
    #        "Posisi strategis tiap DSP — identifikasi zona ideal investasi"
    #    )

    #    med_comp = dest_inv['avg_competition'].median()
    #    med_dem  = dest_inv['avg_demand'].median()

    #    quadrant_colors = {
    #        'A': '#1A7A4A',
    #        'B': '#1D5FAD',
    #        'C': '#B8680A',
    #    }

    #    fig_q = go.Figure()

    #    # Shading kuadran
    #    x_max = dest_inv['avg_competition'].max() * 1.2
    #    y_max = dest_inv['avg_demand'].max() * 1.2

    #    fig_q.add_shape(type='rect', x0=0, y0=med_dem, x1=med_comp, y1=y_max,
    #                    fillcolor='rgba(26,122,74,0.06)', line=dict(width=0), layer='below')
    #    fig_q.add_shape(type='rect', x0=med_comp, y0=med_dem, x1=x_max, y1=y_max,
    #                    fillcolor='rgba(196,123,0,0.05)', line=dict(width=0), layer='below')
    #    fig_q.add_shape(type='rect', x0=0, y0=0, x1=med_comp, y1=med_dem,
    #                    fillcolor='rgba(74,96,128,0.05)', line=dict(width=0), layer='below')
    #    fig_q.add_shape(type='rect', x0=med_comp, y0=0, x1=x_max, y1=med_dem,
    #                    fillcolor='rgba(192,57,43,0.06)', line=dict(width=0), layer='below')

    #    annotations = [
    #        dict(x=2, y=y_max*0.97, text="🟢 SWEET SPOT",
    #             showarrow=False, font=dict(size=9, color='#1A7A4A'), xanchor='left'),
    #        dict(x=med_comp*1.05, y=y_max*0.97, text="⚠️ RISING TIDE",
    #             showarrow=False, font=dict(size=9, color='#B8680A'), xanchor='left'),
    #        dict(x=2, y=med_dem*0.15, text="🔵 BLUE OCEAN",
    #             showarrow=False, font=dict(size=9, color='#1D5FAD'), xanchor='left'),
    #        dict(x=med_comp*1.05, y=med_dem*0.15, text="🔴 RED OCEAN",
    #             showarrow=False, font=dict(size=9, color='#C0392B'), xanchor='left'),
    #    ]

    #    fig_q.add_shape(type='line', x0=med_comp, x1=med_comp,
    #                    y0=0, y1=y_max,
    #                    line=dict(color='rgba(0,0,0,0.15)', dash='dot'))
    #    fig_q.add_shape(type='line', x0=0, x1=x_max,
    #                    y0=med_dem, y1=med_dem,
    #                    line=dict(color='rgba(0,0,0,0.15)', dash='dot'))

    #    for _, row in dest_inv.iterrows():
    #        grade = row['inv_grade']
    #        fig_q.add_trace(go.Scatter(
    #            x=[row['avg_competition']],
    #            y=[row['avg_demand']],
    #            mode='markers',
    #            name=row['destinasi'],
    #            marker=dict(
    #                size=row['avg_opp'] / 3 + 10,
    #                color=quadrant_colors.get(grade, '#64748B'),
    #                opacity=0.85,
    #                line=dict(color='white', width=2)
    #            ),
    #            showlegend=False,
    #            hovertemplate=(
    #                f"<b>{row['destinasi']}</b><br>"
    #                f"Demand: {row['avg_demand']:.1f}<br>"
    #                f"Competition: {row['avg_competition']:.1f}<br>"
    #                f"Opp Score: {row['avg_opp']:.1f}<br>"
    #                f"Grade: {grade}<extra></extra>"
    #            )
    #        ))

    #    fig_q.update_layout(
    #        annotations=annotations,
    #        paper_bgcolor='rgba(0,0,0,0)',
    #        plot_bgcolor='rgba(248,250,252,1)',
    #        height=420,
    #        margin=dict(l=10, r=10, t=20, b=40),
    #        xaxis=dict(
    #            title='Tingkat Persaingan (Competition Score)',
    #            range=[0, x_max],
    #            gridcolor='#E2E8F0',
    #            tickfont=dict(color='#64748B', size=10),
    #            title_font=dict(color='#64748B', size=11),
    #        ),
    #        yaxis=dict(
    #            title='Tingkat Permintaan (Demand Score)',
    #            range=[0, y_max],
    #            gridcolor='#E2E8F0',
    #            tickfont=dict(color='#64748B', size=10),
    #            title_font=dict(color='#64748B', size=11),
    #        ),
    #    )
    #    st.plotly_chart(fig_q, width="stretch", config={'displayModeBar': False})

    spacer(10)

    section_header(
        "Undersupply vs Saturated",
        "Identifikasi zona dengan gap antara demand dan jumlah hotel"
    )

    med_hotels = dest_inv['n_hotels'].median()
    med_demand = dest_inv['avg_demand'].median()

    def get_status(row):
        is_under = (row['avg_demand'] >= med_demand) and (row['n_hotels'] <= med_hotels)
        is_over  = (row['avg_competition'] >= dest_inv['avg_competition'].quantile(0.7))
        if is_over:
            return 'SATURATED', '#C0392B', '⚠️', \
                   f"Kompetisi {row['avg_competition']:.0f}% · Hindari entry mid-range"
        elif is_under:
            return 'UNDERSUPPLY', '#1A7A4A', '📈', \
                   f"Demand {row['avg_demand']:.0f} · Hanya {row['n_hotels']} hotel → peluang first-mover"
        else:
            return 'BALANCED', '#1D5FAD', '🔵', \
                   f"Avg Opp {row['avg_opp']:.1f} · {row['n_sangat']} zona prioritas"

    def card_html(status, clr, icon, desc, row):
        return (
            f'<div style="display:flex;gap:10px;padding:10px 12px;background:#FFFFFF;'
            f'border:1px solid #E2E8F0;border-left:3px solid {clr};border-radius:8px;margin-bottom:8px;">'
            f'  <div style="font-size:15px;line-height:1.2;">{icon}</div>'
            f'  <div>'
            f'    <div style="font-size:12px;font-weight:700;color:{clr};">{row["destinasi"]} — {status}</div>'
            f'    <div style="font-size:10px;color:#64748B;margin-top:2px;line-height:1.4;">{desc}</div>'
            f'  </div>'
            f'</div>'
        )

    # ── Kelompokkan berdasarkan status ──────────────────────────
    balanced_rows   = []
    saturated_rows  = []
    undersupply_rows = []

    for _, row in dest_inv.iterrows():
        status, clr, icon, desc = get_status(row)
        item = (status, clr, icon, desc, row)
        if status == 'BALANCED':
            balanced_rows.append(item)
        elif status == 'SATURATED':
            saturated_rows.append(item)
        else:
            undersupply_rows.append(item)

    col_left, col_right = st.columns(2)

    with col_left:
        for status, clr, icon, desc, row in balanced_rows:
            st.markdown(card_html(status, clr, icon, desc, row), unsafe_allow_html=True)

    with col_right:
        for status, clr, icon, desc, row in saturated_rows:
            st.markdown(card_html(status, clr, icon, desc, row), unsafe_allow_html=True)
        for status, clr, icon, desc, row in undersupply_rows:
            st.markdown(card_html(status, clr, icon, desc, row), unsafe_allow_html=True)

    spacer(20)

    # ── Cegah destinasi yang sama muncul di top3 dan worst sekaligus ──
    best3 = dest_inv.nlargest(3, 'avg_opp')
    worst_candidates = dest_inv[~dest_inv['destinasi'].isin(best3['destinasi'])]
    worst = (
        worst_candidates.nlargest(1, 'avg_competition').iloc[0]
        if not worst_candidates.empty
        else dest_inv.nlargest(1, 'avg_competition').iloc[0]
    )
    best_names = ', '.join(best3['destinasi'].tolist())

    st.markdown(insight_html(
        "Rekomendasi Wilayah Final",
        (
            f"<b>Prioritas Utama:</b> <strong style='color:#22C55E'>{best_names}</strong>.<br>"
            f"Ketiga destinasi ini memiliki keseimbangan paling baik antara skor peluang, tingkat permintaan wisatawan, dan kelengkapan fasilitas di sekitarnya.<br><br>"
            
            f"<b>Risiko Persaingan Tinggi:</b> <strong style='color:#EF4444'>{worst['destinasi']}</strong>.<br>"
            f"Tingkat persaingan di wilayah ini sudah mencapai {worst['avg_competition']:.0f}%. Sangat tidak disarankan untuk membangun hotel kelas menengah biasa. Pilihan terbaik adalah membangun hotel mewah dengan konsep yang sangat unik, atau memindahkan rencana investasi ke destinasi lain.<br><br>"
            
            f"<b>Ringkasan Peluang Nasional:</b><br>"
            f"Terdapat <strong style='color:#00D4FF'>{total_sangat} lokasi yang sangat direkomendasikan</strong> secara nasional. {total_blue} lokasi di antaranya masih tergolong sepi pesaing, sehingga sangat menguntungkan bagi investor yang memutuskan untuk membangun lebih awal."
        ),
        'success'
    ), unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════════════
# PAGE 7 — SPATIAL ECONOMETRICS
# ════════════════════════════════════════════════════════════════════

def page_econometrics():
    section_header(
        "Reliabilitas Model per Destinasi — Apakah Ada Pola Spasial?",
        "Dihitung otomatis dari data — Tinggi (GWR, pola spasial kuat), Cukup (OLS signifikan), Rendah (model belum signifikan)"
    )

    rel_per_dest = df.groupby('destinasi').agg(
        reliabilitas=('reliabilitas_model', 'first'),
        model=('model_dipakai', 'first'),
        n_hotels=('nama_hotel', 'count'),
        r2=('r2_lokal', 'mean'),
    ).reset_index()

    def tier_of(rel):
        if 'Tinggi' in str(rel): return 'Tinggi'
        if 'Cukup' in str(rel): return 'Cukup'
        return 'Rendah'

    rel_per_dest['tier'] = rel_per_dest['reliabilitas'].apply(tier_of)

    tinggi_df = rel_per_dest[rel_per_dest['tier'] == 'Tinggi'].sort_values('r2', ascending=False)
    cukup_df  = rel_per_dest[rel_per_dest['tier'] == 'Cukup'].sort_values('r2', ascending=False)
    rendah_df = rel_per_dest[rel_per_dest['tier'] == 'Rendah'].sort_values('r2', ascending=False)

    def render_tier_card(df_tier, title, border_color, bg_color, badge_bg, badge_text_color):
        items_html = ''
        for _, row in df_tier.iterrows():
            items_html += (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:8px 10px;background:#FFFFFF;border-radius:8px;margin-bottom:6px;'
                f'border:1px solid {border_color}55;">'
                f'  <div>'
                f'    <div style="font-size:12px;font-weight:600;color:#0F2A4A;">{row["destinasi"]}</div>'
                f'    <div style="font-size:10px;color:#64748B;">{int(row["n_hotels"])} hotel · R² = {row["r2"]:.3f}</div>'
                f'  </div>'
                f'  <div style="font-size:9px;background:{badge_bg};color:{badge_text_color};'
                f'border-radius:4px;padding:2px 7px;font-weight:700;white-space:nowrap;">{row["model"]}</div>'
                f'</div>'
            )
        if not items_html:
            items_html = '<div style="font-size:11px;color:#94A3B8;">Tidak ada destinasi</div>'
        return (
            f'<div style="background:{bg_color};border:1px solid {border_color}55;border-radius:10px;'
            f'padding:14px;box-sizing:border-box;height:100%;">'
            f'  <div style="font-size:12px;font-weight:700;color:{border_color};margin-bottom:10px;">{title}</div>'
            f'  {items_html}'
            f'</div>'
        )

    tinggi_html = render_tier_card(
        tinggi_df, f'Reliabilitas Tinggi',
        '#1A7A4A', '#F0FDF4', '#D1FAE5', '#1A7A4A'
    )
    rendah_html = render_tier_card(
        rendah_df, f'Reliabilitas Rendah',
        '#B45309', '#FFFBEB', '#FDE68A', '#92400E'
    )
    cukup_html = render_tier_card(
        cukup_df, f'Reliabilitas Cukup',
        '#1D5FAD', '#EFF6FF', '#DBEAFE', '#1D5FAD'
    )

    legend_html = (
        '<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;'
        'padding:12px 14px;font-size:11px;color:#475569;line-height:1.6;box-sizing:border-box;height:100%;text-align:justify;">'
        '<b>Tinggi</b> adalah pola spasial kuat dimana model GWR paling akurat, kemudian '
        '<b>Cukup</b> adalah OLS signifikan tanpa komponen lokasi lokal, dan '
        '<b>Rendah</b> adalah model belum signifikan secara statistik.'
        '</div>'
    )

    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:stretch;">'
        f'  <div style="display:flex;flex-direction:column;gap:10px;">'
        f'    <div>{cukup_html}</div>'
        f'    <div style="flex:1;">{legend_html}</div>'
        f'  </div>'
        f'  <div style="display:flex;flex-direction:column;gap:10px;">'
        f'    <div>{tinggi_html}</div>'
        f'    <div style="flex:1;">{rendah_html}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )

    spacer(24)

    n_per_dest = df.groupby('destinasi').size().to_dict()
    r2_per_dest = df.groupby(['destinasi','model_dipakai'])['r2_lokal'].mean().reset_index()

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
        'koef_saingan_radius_1km': {
            'label':   'Pengaruh Kepadatan Kompetitor (Radius 1km)',
            'color':   '#1A7A4A',
            'impact_pos': 'Saling Menguntungkan',
            'impact_neg': 'Persaingan Ketat',
            'plain':   (
                'Mengelompoknya banyak hotel di satu titik rata-rata memberikan keuntungan bersama, karena area tersebut menjadi pusat tujuan wisatawan. Namun, perlu diwaspadai di destinasi yang sudah sangat padat — di sana, jumlah hotel sudah terlalu banyak dan membangun hotel baru di titik yang sama hanya akan memicu persaingan harga yang merugikan investor.'
            ),
            'dest_note': (
                'Destinasi yang masih berkembang (seperti Borobudur, Wakatobi): kumpulan hotel menciptakan area wisata yang hidup dan menguntungkan.<br>'
                'Destinasi yang sudah jenuh (seperti Mandalika, Labuan Bajo): disarankan mencari lokasi baru agar tidak bersaing terlalu ketat.'
            ),
        },
        'koef_jarak_ke_atraksi_terdekat_km': {
            'label':   'Pengaruh Jarak ke Atraksi Wisata',
            'color':   '#C0392B',
            'impact_pos': 'Jarak Fleksibel',
            'impact_neg': 'Wajib Dekat Wisata',
            'plain':   (
                'Semakin jauh jarak hotel dari objek wisata utama, daya tariknya akan semakin menurun di sebagian besar destinasi. Kedekatan lokasi dengan tempat wisata adalah kunci utama keberhasilan akomodasi. Pengecualian terjadi di destinasi dengan daya tarik utama yang sangat kuat, di mana wisatawan tetap bersedia menginap meskipun jaraknya sedikit lebih jauh.'
            ),
            'dest_note': (
                'Tanjung Kelayang: lokasi persis di pinggir pantai (beachfront) adalah syarat utama.<br>'
                'Borobudur: jarak yang sedikit lebih jauh masih bisa ditoleransi oleh wisatawan karena daya tarik budayanya sangat kuat.'
            ),
        },
        'koef_jumlah_atraksi_radius_5km': {
            'label':   'Dampak Jumlah Atraksi Tambahan (Radius 5km)',
            'color':   '#B8680A',
            'impact_pos': 'Menarik Pengunjung',
            'impact_neg': 'Kepadatan Berlebih',
            'plain':   (
                'Efek penambahan tempat wisata di sekitar hotel sangat bervariasi. Pada destinasi yang sedang berkembang, banyaknya pilihan wisata akan semakin menarik tamu. Sebaliknya, pada destinasi yang sudah sangat padat, terlalu banyak titik wisata justru memicu kemacetan dan kebisingan yang menurunkan kenyamanan wisatawan.'
            ),
            'dest_note': (
                'Raja Ampat & Borobudur: fasilitas wisata tambahan di sekitar hotel akan meningkatkan kunjungan.<br>'
                'Mandalika & Bromo: area sudah cukup padat, penambahan atraksi berisiko menurunkan tingkat kenyamanan.'
            ),
        },
        'koef_is_premium': {
            'label':   'Pengaruh Status Hotel Premium',
            'color':   '#7B2D8B',
            'impact_pos': 'Premium Menguntungkan',
            'impact_neg': 'Premium Kurang Optimal',
            'plain':   (
                'Faktor ini menunjukkan apakah status hotel sebagai properti premium (bintang 4-5, resort, atau luxury) berkorelasi dengan performa yang lebih baik di lokasi tersebut. Di destinasi yang wisatawannya mencari pengalaman eksklusif, status premium jadi nilai jual kuat. Di destinasi yang pasarnya lebih didominasi wisatawan budget, status premium belum tentu memberi keuntungan tambahan.'
            ),
            'dest_note': (
                'Cek boxplot di sebelah kiri untuk melihat destinasi mana yang paling terpengaruh positif oleh status premium — biasanya destinasi dengan segmen wisatawan kelas atas yang jelas (seperti dive resort atau heritage site).'
            ),
        },
        'koef_is_red_ocean': {
            'label':   'Pengaruh Status Zona Red Ocean',
            'color':   '#C0392B',
            'impact_pos': 'Red Ocean Tidak Masalah',
            'impact_neg': 'Red Ocean Merugikan',
            'plain':   (
                'Faktor ini mengukur dampak berada di zona kepadatan tinggi (Red Ocean) terhadap performa hotel. Koefisien negatif berarti hotel yang berada di zona padat cenderung memiliki performa yang tertekan akibat persaingan ketat. Koefisien positif (di beberapa lokasi) bisa mengindikasikan bahwa kepadatan justru menciptakan destinasi yang ramai dan menarik lebih banyak wisatawan secara keseluruhan.'
            ),
            'dest_note': (
                'Destinasi dengan koefisien negatif kuat: hindari entry baru di zona Red Ocean tanpa diferensiasi produk yang jelas.<br>'
                'Destinasi dengan koefisien mendekati nol atau positif: kepadatan bukan penghalang utama, faktor lain lebih menentukan.'
            ),
        },
        'koef_total_demand_area': {
            'label':   'Pengaruh Total Demand di Area Sekitar',
            'color':   '#1D5FAD',
            'impact_pos': 'Demand Area Mendukung',
            'impact_neg': 'Demand Area Tidak Cukup',
            'plain':   (
                'Faktor ini menunjukkan apakah volume permintaan wisata secara keseluruhan di sekitar lokasi (bukan cuma hotel itu sendiri) turut mendorong performa. Koefisien positif berarti hotel diuntungkan oleh tingginya minat wisatawan ke area tersebut secara umum — sinyal bahwa destinasi tersebut sedang tumbuh sebagai pusat wisata.'
            ),
            'dest_note': (
                'Destinasi dengan koefisien tinggi: permintaan area sekitar jadi pendorong kuat, cocok untuk investasi yang mengandalkan trafik wisatawan secara umum, bukan hanya keunikan properti.'
            ),
        },
    }

    coef_map = [
        ('koef_saingan_radius_1km',           'Kepadatan Kompetitor'),
        ('koef_jarak_ke_atraksi_terdekat_km',  'Jarak ke Atraksi'),
        ('koef_jumlah_atraksi_radius_5km',     'Jumlah Atraksi 5km'),
        ('koef_is_premium',                    'Status Premium'),
        ('koef_is_red_ocean',                  'Status Red Ocean'),
        ('koef_total_demand_area',             'Total Demand Area'),
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
                        #f'  <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;padding:10px 12px;">'
                        #f'    <div style="font-size:9px;color:#64748B;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Catatan per Destinasi:</div>'
                        #f'    <div style="font-size:10px;color:#475569;line-height:1.6;">{dest_note_clean}</div>'
                        f'  </div>'
                        f'</div>'
                    )

                    # 2. RENDER DI STREAMLIT
                    st.markdown(html_content, unsafe_allow_html=True)

    spacer(24)

    spacer(24)

    section_header(
        "Perbandingan Akurasi Model per Destinasi",
        "R² per model — seberapa baik tiap model menjelaskan variasi performa hotel"
    )

    model_color_map = {
        'GWR (Lokal)':          '#1A7A4A',
        'GWR (Parsial)':        '#2D6A4F',
        'Spatial Lag (Global)': '#1D5FAD',
        'OLS (Global)':         '#F59E0B',
    }
    model_short_map = {
        'GWR (Lokal)':          'GWR',
        'GWR (Parsial)':        'GWR-P',
        'Spatial Lag (Global)': 'SLM',
        'OLS (Global)':         'OLS',
    }
    default_color = '#94A3B8'

    cg, co = st.columns([1.3, 1])
    with cg:
        r2_data = r2_per_dest.copy().sort_values('r2_lokal', ascending=True)
        colors = [model_color_map.get(m, default_color) for m in r2_data['model_dipakai']]
        short_labels = [model_short_map.get(m, m) for m in r2_data['model_dipakai']]

        fig = go.Figure(go.Bar(
            x=r2_data['r2_lokal'],
            y=r2_data['destinasi'],
            orientation='h',
            marker=dict(color=colors, opacity=0.85),
            text=[f"R²={v:.3f} ({s})" for v, s in zip(r2_data['r2_lokal'], short_labels)],
            textposition='inside',
            textfont=dict(color='#FFFFFF', size=10),
            cliponaxis=True,
            showlegend=False,
        ))

        fig = apply_layout(fig, height=320, show_legend=False)
        max_val = r2_data['r2_lokal'].max()
        fig.update_xaxes(title='R²', tickfont=dict(size=9, color='#4A6080'), range=[0, max_val * 1.15])

        # Legend dinamis — 1 baris, kecil, digeser ke kiri
        present_models = r2_data['model_dipakai'].unique().tolist()
        for m in present_models:
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                name=model_short_map.get(m, m),
                marker_color=model_color_map.get(m, default_color),
                showlegend=True,
            ))

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation='h',
                y=-0.16, x=0, xanchor='left',
                font=dict(size=8, color='#334155'),
                itemsizing='constant',
                itemwidth=30,
                tracegroupgap=2,
                itemclick=False, itemdoubleclick=False,
            ),
            margin=dict(l=10, r=10, t=10, b=40)
        )
        st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})

    with co:
        model_summary = r2_per_dest.groupby('model_dipakai')['r2_lokal'].agg(['mean', 'count']).reset_index()
        model_summary = model_summary.sort_values('mean', ascending=False)

        # Grid 2x2 — kanan 2, kiri 2 (urut berdasarkan rata-rata R² tertinggi)
        summary_boxes = ''
        for _, row in model_summary.iterrows():
            m = row['model_dipakai']
            clr = model_color_map.get(m, default_color)
            summary_boxes += (
                f'<div style="text-align:center;'
                f'background:{clr}12;border:1px solid {clr}40;border-radius:8px;padding:12px 8px;">'
                f'  <div style="font-size:9px;color:#94A3B8;margin-bottom:3px;">{m} ({int(row["count"])} destinasi)</div>'
                f'  <div style="font-size:20px;font-weight:900;color:{clr};">R²={row["mean"]:.3f}</div>'
                f'</div>'
            )

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;'
            f'padding:18px 20px;min-height:320px;display:flex;flex-direction:column;'
            f'justify-content:space-between;box-sizing:border-box;">'
            f'<div>'
            f'  <div style="font-size:13px;font-weight:700;color:#0F2A4A;margin-bottom:14px;">Rata-rata Akurasi per Jenis Model</div>'
            f'  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px;">{summary_boxes}</div>'
            f'</div>'
            f'<div style="font-size:12px;color:#334155;line-height:1.75;">'
            f'Model berbasis <b>GWR/Spatial</b> lebih akurat di destinasi dengan data cukup karena '
            f'memperhitungkan bahwa pengaruh jarak, kompetitor, dan atraksi berbeda-beda di tiap lokasi.<br><br>'
            f'Model <b>OLS (Global)</b> tetap valid untuk destinasi dengan jumlah hotel lebih kecil — '
            f'bukan karena tidak ada pola, tapi datanya belum cukup untuk model spasial yang reliabel.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    n_spatial = int((r2_per_dest['model_dipakai'] != 'OLS (Global)').sum())
    n_ols     = int((r2_per_dest['model_dipakai'] == 'OLS (Global)').sum())

    #st.markdown(
    #    f'<div style="background:#0F2A4A;border-radius:12px;padding:18px 22px;margin-top:16px;">'
    #    f'<div style="font-size:14px;font-weight:700;color:#FFFFFF;margin-bottom:12px;">'
    #    f'Ringkasan Temuan Spasial untuk Investor</div>'
    #    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">'

    #    f'<div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px;">'
    #    f'<div style="font-size:11px;font-weight:700;color:#22C55E;margin-bottom:6px;">'
    #    f'Strategi Terbukti dari Data</div>'
    #    f'<div style="font-size:11px;color:#CBD5E1;line-height:1.7;">'
    #    f'· Masuk di kluster model spasial ({n_spatial} destinasi) — pola lokasi terbukti signifikan<br>'
    #    f'· Posisi hotel &lt;2km dari atraksi utama (terutama Tanjung Kelayang)<br>'
    #    f'· Manfaatkan efek aglomerasi di destinasi dengan koefisien kompetitor positif<br>'
    #    f'· Di destinasi alam, keterpencilan bisa jadi nilai jual (Borobudur, Wakatobi)'
    #    f'</div>'
    #    f'</div>'

    #    f'<div style="background:rgba(255,255,255,0.07);border-radius:8px;padding:12px;">'
    #    f'<div style="font-size:11px;font-weight:700;color:#EF4444;margin-bottom:6px;">'
    #    f'Risiko yang Harus Dihindari</div>'
    #    f'<div style="font-size:11px;color:#CBD5E1;line-height:1.7;">'
    #    f'· Destinasi yang sudah jenuh — kompetitor baru justru merugikan<br>'
    #    f'· Lokasi jauh dari atraksi utama di destinasi non-alam<br>'
    #    f'· Morotai: atraksi ada tapi ekosistem belum terkoneksi — timing masih berisiko<br>'
    #    f'· Model OLS ({n_ols} destinasi) = peluang first-mover, bukan zona bebas risiko'
    #    f'</div>'
    #    f'</div>'

    #    f'</div>'
    #    f'</div>',
    #    unsafe_allow_html=True
    #)


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
        st.markdown('<div style="font-size:11px;color:#74A98A;margin-bottom:3px;font-weight:600;">Jenis Akomodasi</div>', unsafe_allow_html=True)
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
            ("Akomodasi",       f"{len(d_df):,}",                                    "#00D4FF"),
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
            section_header("Distribusi Tipe Akomodasi")
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
            section_header("Klasifikasi Kelas Bintang", "Akomodasi dengan rating bintang")

            if 'kasta_bintang' in d_df.columns:
                import re

                def reklasifikasi_kasta(val):
                    if pd.isna(val):
                        return 'Tidak Ada Data'

                    val_str = str(val).strip()
                    val_lower = val_str.lower()

                    if val_lower in ('tidak ada data', 'nan', 'none', ''):
                        return 'Tidak Ada Data'

                    # Regex fleksibel: nangkep "5-star", "5 star", "5star", "bintang 5", dst
                    match = re.search(r'(\d)\s*-?\s*star', val_lower)
                    if not match:
                        match = re.search(r'bintang\s*(\d)', val_lower)

                    if match:
                        angka = match.group(1)
                        if angka in ('1', '2', '3', '4', '5'):
                            return f'Hotel bintang {angka}'

                    return 'Lainnya'

                d_df_kasta = d_df['kasta_bintang'].apply(reklasifikasi_kasta)
                sc_cnt = d_df_kasta.value_counts()

                color_map = {
                    'Hotel bintang 5': '#1A7A4A',
                    'Hotel bintang 4': '#2D6A4F',
                    'Hotel bintang 3': '#40916C',
                    'Hotel bintang 2': '#52B788',
                    'Hotel bintang 1': '#74A98A',
                    'Lainnya': '#B8680A',
                    'Tidak Ada Data': '#C0392B',
                }
                bar_colors = [color_map.get(k, '#94A3B8') for k in sc_cnt.index]

                fig = go.Figure(go.Bar(
                    y=sc_cnt.index.tolist(),
                    x=sc_cnt.values.tolist(),
                    orientation='h',
                    marker=dict(color=bar_colors, opacity=0.88),
                    text=sc_cnt.values.tolist(),
                    textposition='outside',
                    textfont=dict(color='#1B4332', size=11),
                    hovertemplate='<b>%{y}</b><br>Jumlah: %{x}<extra></extra>',
                ))
                max_x = sc_cnt.values.max() * 1.2 if len(sc_cnt) > 0 else 10
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=max(280, len(sc_cnt) * 32),
                    margin=dict(l=10, r=60, t=10, b=10),
                    xaxis=dict(
                        gridcolor='rgba(64,145,108,0.1)',
                        tickfont=dict(color='#2D6A4F', size=10),
                        title='Jumlah Akomodasi',
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
            section_header("Top 5 Akomodasi Ulasan Terbanyak", "Volume Ulasan Tertinggi di Destinasi Ini")
            if 'jumlah_ulasan' in d_df.columns:
                top5 = d_df.nlargest(5, 'jumlah_ulasan')
                rank_colors = {
                    0: ('#E9A020', '#FFFBEB'),  # emas
                    1: ('#94A3B8', '#F8FAFC'),  # perak
                    2: ('#B8680A', '#FFF7ED'),  # perunggu
                }
                for i, (_, row) in enumerate(top5.iterrows()):
                    badge_clr, badge_bg = rank_colors.get(i, ('#CBD5E1', '#F8FAFC'))
                    nama  = str(row.get('nama_hotel', 'Unknown'))[:32]
                    rate  = row.get('rating', 0)
                    ulas  = int(row.get('jumlah_ulasan', 0))
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:12px;'
                        f'padding:10px 12px;background:#FFFFFF;border:1px solid #E2E8F0;'
                        f'border-radius:8px;margin-bottom:6px;">'
                        f'  <div style="width:26px;height:26px;border-radius:50%;'
                        f'background:{badge_bg};border:1.5px solid {badge_clr};'
                        f'display:flex;align-items:center;justify-content:center;'
                        f'font-size:12px;font-weight:800;color:{badge_clr};flex-shrink:0;">{i+1}</div>'
                        f'  <div style="flex:1;">'
                        f'    <div style="font-size:12px;font-weight:700;color:#0F2A4A;'
                        f'line-height:1.3;">{nama}</div>'
                        f'    <div style="font-size:10px;color:#74A98A;margin-top:2px;">'
                        f'{rate:.1f} rating · {ulas:,} ulasan</div>'
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
             "Kompetisi hotel di kedua destinasi ini sudah cukup tinggi, tapi harga tanahnya masih murah "
             "karena infrastruktur belum sepenuhnya masuk. Begitu KEK aktif, harga akan naik cepat — "
             "peluang ini soal timing tanah, bukan soal bersaing hotel yang sudah ada."),
            ("Akuisisi Resort Wakatobi",
             "Opportunity score-nya tertinggi secara nasional, tapi kompetisinya juga sudah menengah-tinggi "
             "dan ada regulasi konservasi yang membatasi pembangunan baru. Kalau mau masuk Wakatobi, "
             "jalan yang lebih realistis adalah membeli resort yang sudah berdiri."),
            ("Boutique Lodge Raja Ampat",
             "Kompetisi paling rendah dari seluruh destinasi, sementara permintaan wisatawannya justru "
             "paling tinggi. Kombinasi ini pas untuk properti kecil yang tidak butuh volume tamu besar "
             "untuk balik modal."),
            ("Konversi Aset Danau Toba",
             "Permintaan wisatawannya cukup baik, tapi banyak hotel bintang 2–3 yang sepi bukan karena "
             "sepi tamu, melainkan karena salah segmen. Ubah dulu konsepnya, baru pertimbangkan bangun baru."),
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
            ("Resort Pantai Tanjung Kelayang",
             "Kompetisinya masih di level menengah, belum sepadat destinasi utama seperti Labuan Bajo "
             "atau Morotai. Cocok untuk investor yang mau masuk ke pasar yang belum terlalu ramai "
             "tapi juga tidak harus menunggu terlalu lama seperti destinasi yang benar-benar baru berkembang."),
            ("Glamping Premium Bromo",
             "Bromo sudah lama jadi tujuan wisata gunung yang ramai, tapi belum ada yang menawarkan "
             "pengalaman menginap yang benar-benar premium. Permintaannya ada, tawarannya belum."),
            ("Lakefront Resort Danau Toba",
             "Tol Trans-Sumatra akan selesai bertahap. Properti yang sudah berdiri saat akses terbuka "
             "akan langsung menikmati lonjakan tamu — ini taruhan pada infrastruktur yang sedang berjalan."),
            ("Kemitraan Event Mandalika",
             "MotoGP dan event lainnya mengisi kalender rutin sepanjang tahun. Daripada bersaing langsung "
             "di pasar yang sudah cukup padat, lebih realistis jadi mitra resmi event-nya."),
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
             "Wisatawan selam kelas dunia biasanya mengunjungi ketiganya secara terpisah. Belum ada "
             "satu operator pun yang menghubungkan ketiganya sebagai satu paket perjalanan."),
            ("Jaringan Resort Zona UNESCO",
             "Borobudur, Wakatobi, dan Komodo punya nama besar tapi akomodasi premiumnya masih sangat "
             "sedikit. Sulit dimasuki kompetitor karena regulasinya ketat."),
            ("Platform Data Investasi Pariwisata",
             "Sampai sekarang belum ada tempat yang bisa dipakai investor untuk melihat data kinerja, "
             "harga aset, dan peluang transaksi properti wisata Indonesia secara terpusat."),
        ]
    },
]

    max_items = max(len(r["items"]) for r in roadmap)
    dynamic_min_height = 90 + (max_items * 120)  # 90px untuk header, ~130px per item

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
                f'min-height:{dynamic_min_height}px;box-sizing:border-box;">'
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
        "Analisis Branding",
        "Ekonometrika Spasial",
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
        f"Temuan Kunci dari {len(df):,} Data Hotel · {df['destinasi'].nunique()} Destinasi Super Prioritas",
        ""
    )

    st.markdown(
        '<div style="background:#FFFBEB;border:1px solid #FDE68A;border-radius:8px;'
        'padding:12px 16px;margin-bottom:20px;font-size:11px;color:#92400E;line-height:1.7;">'
        '<b>Catatan cara membaca:</b> '
        'Demand score dihitung secara relatif di dalam masing-masing destinasi (skala 0–100 per DSP), '
        'bukan perbandingan volume absolut antar destinasi. '
        'Artinya, demand score yang tinggi di satu destinasi tidak selalu berarti volume permintaannya '
        'lebih besar dari destinasi lain — keduanya hanya menunjukkan posisi relatif hotel tersebut '
        'di dalam destinasinya sendiri. '
        'Untuk melihat volume permintaan aktual, gunakan data total ulasan per destinasi.'
        '</div>',
        unsafe_allow_html=True
    )

    section_header(
        "Apa yang Sebenarnya Terjadi di Pasar?",
        "Temuan langsung dari data — bukan asumsi"
    )

    # ── Hitung ulang seluruh statistik dari data aktual ──────────
    top_opp   = dest_stats.nlargest(1, 'avg_opportunity').iloc[0]
    low_opp   = dest_stats.nsmallest(1, 'avg_opportunity').iloc[0]
    top_comp  = dest_stats.nlargest(1, 'avg_competition').iloc[0]
    low_comp  = dest_stats.nsmallest(1, 'avg_competition').iloc[0]
    top_dem   = dest_stats.nlargest(1, 'avg_demand').iloc[0]
    top_hotel_count = dest_stats.nlargest(1, 'n_hotels').iloc[0]

    red_pct = (df['status_ocean'].str.contains('Red', na=False).mean() * 100) if 'status_ocean' in df.columns else 0
    med_opp = dest_stats['avg_opportunity'].median()

    insights = [
        {
            'type': 'danger',
            'tag':  'Sebagian Besar Destinasi Berada di Zona Kepadatan Tinggi',
            'text': (
                f"Sebanyak {red_pct:.0f}% dari {len(df):,} akomodasi berada di zona kepadatan tinggi "
                f"(Red Ocean) — bersaing langsung dengan hotel lain dalam radius yang berdekatan. "
                f"Status ini diukur dari kepadatan geografis, bukan dari tingkat profitabilitas — "
                f"artinya padat secara lokasi belum tentu berarti pasarnya sudah jenuh sepenuhnya."
            ),
        },
        {
            'type': 'success',
            'tag':  f"{top_dem['dest_display']}: Tingkat Permintaan Wisatawan Tertinggi",
            'text': (
                f"{top_dem['dest_display']} mencatat demand score rata-rata tertinggi secara nasional "
                f"({top_dem['avg_demand']:.1f}), sekaligus memiliki tingkat persaingan yang relatif "
                f"rendah ({top_dem['avg_competition']:.1f}%). Kombinasi ini menunjukkan bahwa minat "
                f"wisatawan terhadap destinasi ini belum diikuti oleh jumlah akomodasi yang sebanding, "
                f"sehingga masih terbuka ruang bagi investor baru."
            ),
        },
        {
            'type': 'warning',
            'tag':  f"{top_opp['dest_display']}: Peluang Investasi Tertinggi, Perlu Dicermati Konteksnya",
            'text': (
                f"{top_opp['dest_display']} memimpin dengan opportunity score rata-rata "
                f"{top_opp['avg_opportunity']:.1f} — tertinggi dari seluruh destinasi. Skor tinggi ini "
                f"mencerminkan kombinasi ekosistem atraksi yang kuat dan tingkat permintaan yang "
                f"memadai, bukan berarti destinasi ini otomatis mudah dimasuki. Tingkat persaingannya "
                f"tercatat {top_opp['avg_competition']:.1f}%, sehingga investor baru tetap perlu "
                f"mempertimbangkan strategi diferensiasi yang jelas."
            ),
        },
        {
            'type': 'info',
            'tag':  f"{top_hotel_count['dest_display']}: Jumlah Hotel Terbanyak, Bukan Berarti Peluang Terbesar",
            'text': (
                f"{top_hotel_count['dest_display']} tercatat sebagai destinasi dengan jumlah hotel "
                f"terbanyak ({int(top_hotel_count['n_hotels']):,} hotel dari total {len(df):,} data nasional). "
                f"Namun, opportunity score rata-ratanya ({top_hotel_count['avg_opportunity']:.1f}) "
                f"tidak menempati posisi tertinggi dibanding destinasi lain. Hal ini mengindikasikan "
                f"bahwa ruang bagi investor baru di destinasi ini sudah jauh lebih terbatas dibanding "
                f"destinasi dengan supply yang lebih sedikit."
            ),
        },
        {
            'type': 'danger',
            'tag':  f"{top_comp['dest_display']}: Tingkat Persaingan Tertinggi Secara Nasional",
            'text': (
                f"{top_comp['dest_display']} mencatat competition score rata-rata tertinggi "
                f"({top_comp['avg_competition']:.1f}%), dengan opportunity score {top_comp['avg_opportunity']:.1f}. "
                f"Investor yang ingin masuk ke segmen menengah di destinasi ini kemungkinan besar "
                f"akan langsung bersaing ketat sejak awal, sehingga diperlukan diferensiasi produk "
                f"yang kuat agar tidak sekadar menambah kepadatan pasar yang sudah tinggi."
            ),
        },
        {
            'type': 'success',
            'tag':  f"{low_comp['dest_display']}: Persaingan Paling Rendah Secara Nasional",
            'text': (
                f"{low_comp['dest_display']} mencatat competition score rata-rata terendah "
                f"({low_comp['avg_competition']:.1f}%), dengan opportunity score {low_comp['avg_opportunity']:.1f} "
                f"dan demand score {low_comp['avg_demand']:.1f}. Destinasi ini berpotensi menjadi lokasi "
                f"yang tepat bagi investor yang ingin memasuki pasar lebih awal, sebelum tingkat "
                f"persaingannya meningkat."
            ),
        },
        {
            'type': 'warning',
            'tag':  f"{low_opp['dest_display']}: Belum Menunjukkan Sinyal Pasar yang Cukup untuk Investasi Baru",
            'text': (
                f"{low_opp['dest_display']} mencatat opportunity score rata-rata terendah dari seluruh "
                f"destinasi ({low_opp['avg_opportunity']:.1f}). Kondisi ini mengindikasikan bahwa "
                f"data belum mendukung rekomendasi investasi akomodasi baru di destinasi tersebut "
                f"pada saat ini, sehingga perlu dipertimbangkan kembali sebelum melakukan ekspansi."
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
        f"Langkah konkret yang didukung temuan dari {len(df):,} hotel"
    )

    # ── Susun rekomendasi otomatis berdasarkan kombinasi skor ────
    # ── Susun rekomendasi otomatis berdasarkan kombinasi skor ────
    dest_sorted_opp = dest_stats.sort_values('avg_opportunity', ascending=False).reset_index(drop=True)
    best_stable = dest_sorted_opp[dest_sorted_opp['avg_competition'] <= dest_stats['avg_competition'].median()]
    best_stable_dest = best_stable.iloc[0] if not best_stable.empty else dest_sorted_opp.iloc[0]

    worst_dest_candidates = dest_stats[~dest_stats['dest_display'].isin([best_stable_dest['dest_display']])]
    worst_dest = worst_dest_candidates.nlargest(1, 'avg_competition').iloc[0]# ── Susun rekomendasi otomatis berdasarkan kombinasi skor ────
    dest_sorted_opp = dest_stats.sort_values('avg_opportunity', ascending=False).reset_index(drop=True)
    best_stable = dest_sorted_opp[dest_sorted_opp['avg_competition'] <= dest_stats['avg_competition'].median()]
    best_stable_dest = best_stable.iloc[0] if not best_stable.empty else dest_sorted_opp.iloc[0]

    worst_dest_candidates = dest_stats[~dest_stats['dest_display'].isin([best_stable_dest['dest_display']])]
    worst_dest = worst_dest_candidates.nlargest(1, 'avg_competition').iloc[0]
    recs = [
        {
            'number': 1,
            'title':  f"{best_stable_dest['dest_display']} untuk Investor yang Butuh Kepastian Pasar",
            'text':   (
                f"Memiliki kombinasi paling seimbang antara opportunity score "
                f"({best_stable_dest['avg_opportunity']:.1f}) dan tingkat persaingan yang masih "
                f"terkendali ({best_stable_dest['avg_competition']:.1f}%). Cocok bagi investor yang "
                f"ingin masuk ke pasar dengan risiko yang lebih terukur dibanding destinasi lain "
                f"yang persaingannya sudah sangat tinggi."
            ),
        },
        {
            'number': 2,
            'title':  f"{top_dem['dest_display']} untuk Investor yang Ingin Menangkap Permintaan Tertinggi",
            'text':   (
                f"Mencatat demand score tertinggi secara nasional ({top_dem['avg_demand']:.1f}) "
                f"dengan tingkat persaingan yang relatif rendah ({top_dem['avg_competition']:.1f}%). "
                f"Cocok untuk konsep akomodasi yang menyasar segmen wisatawan dengan minat tinggi "
                f"namun belum terlayani sepenuhnya oleh suplai yang ada."
            ),
        },
        {
            'number': 3,
            'title':  f"{top_opp['dest_display']} Hanya untuk Segmen dengan Diferensiasi Kuat",
            'text':   (
                f"Opportunity score tertinggi ({top_opp['avg_opportunity']:.1f}) mencerminkan "
                f"ekosistem wisata yang sudah kuat, namun tingkat persaingannya juga tergolong "
                f"tinggi ({top_opp['avg_competition']:.1f}%). Investor yang ingin masuk sebaiknya "
                f"tidak membangun akomodasi kelas menengah yang serupa dengan yang sudah ada, "
                f"melainkan menawarkan sesuatu yang tidak mudah ditiru oleh kompetitor."
            ),
        },
        {
            'number': 4,
            'title':  f"{low_comp['dest_display']} untuk Investor dengan Horizon Jangka Panjang",
            'text':   (
                f"Tingkat persaingannya paling rendah secara nasional ({low_comp['avg_competition']:.1f}%), "
                f"namun perlu dicatat bahwa pasar di destinasi ini kemungkinan belum sepenuhnya matang. "
                f"Cocok bagi investor yang siap menunggu pertumbuhan destinasi ini secara bertahap, "
                f"dengan potensi menjadi pemain awal sebelum persaingan meningkat."
            ),
        },
        {
            'number': 5,
            'title':  f"Pertimbangkan Ulang Investasi Baru di {worst_dest['dest_display']} dan {low_opp['dest_display']}",
            'text':   (
                f"{worst_dest['dest_display']} mencatat tingkat persaingan yang sangat tinggi "
                f"({worst_dest['avg_competition']:.1f}%), sementara {low_opp['dest_display']} "
                f"mencatat opportunity score terendah secara nasional ({low_opp['avg_opportunity']:.1f}). "
                f"Bagi investor yang sudah memiliki aset di kedua wilayah ini, disarankan untuk "
                f"fokus pada optimasi dan diferensiasi produk yang ada, bukan menambah unit baru."
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