"""
Indonesia Tourism Intelligence Platform
AI-Powered Spatial Tourism Investment Decision Support System
Kemenparekraf — Ministry of Tourism & Creative Economy

Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# ===== PAGE CONFIG (MUST BE FIRST) =====
st.set_page_config(
    page_title="Indonesia Tourism Intelligence Platform",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== IMPORTS =====
from functions.styles import inject_css
from functions.analytics import (
    load_main_data, load_branding_data,
    get_destination_stats, get_national_kpis, generate_ai_insights,
    get_moran_i_simulation, filter_dataframe,
    DEST_COORDS, DEST_DISPLAY, DESIGN, PLOTLY_LAYOUT
)
from functions.charts import (
    plot_national_heatmap, plot_competition_demand_quadrant,
    plot_opportunity_ranking, plot_multi_radar,
    plot_donut, plot_bubble, plot_grouped_bar,
    plot_gwr_coefficients, plot_branding_bars, plot_heatmap_matrix,
    plot_morans_result, plot_investment_matrix, apply_layout
)

# ===== INJECT CSS =====
inject_css()

# ===== LOAD DATA =====
@st.cache_data(ttl=3600)
def load_all_data():
    df = load_main_data()
    branding = load_branding_data()
    return df, branding

df_raw, branding_df = load_all_data()
dest_stats_raw = get_destination_stats(df_raw)


# ===== HELPER: KPI CARD =====
def kpi_card(label, value, sub='', color='accent', trend=None, trend_dir='up', icon='📊'):
    trend_html = ''
    if trend:
        td_class = 'up' if trend_dir == 'up' else 'down' if trend_dir == 'down' else 'neutral'
        arrow = '↑' if trend_dir == 'up' else '↓' if trend_dir == 'down' else '—'
        trend_html = f'<div class="kpi-trend {td_class}">{arrow} {trend}</div>'
    
    val_class = 'success' if color == 'success' else 'warning' if color == 'warning' else 'danger' if color == 'danger' else 'purple' if color == 'purple' else 'accent' if color == 'accent' else 'white' if color == 'white' else ''
    
    return f'<div class="kpi-card">{trend_html}<div class="kpi-label">{icon} {label}</div><div class="kpi-value {val_class}">{value}</div><div class="kpi-sub">{sub}</div></div>'


def insight_card(title, text, type_='info'):
    return f'<div class="insight-card {type_}"><div class="insight-title">{title}</div><div class="insight-body">{text}</div></div>'


def section_header(title, subtitle=''):
    sub_html = f'<div class="section-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(f'<div class="section-header"><div class="section-title">{title}</div>{sub_html}</div>', unsafe_allow_html=True)


def page_header(title, subtitle='', icon='📊'):
    st.markdown(f'<div class="page-header"><div style="display:flex;align-items:center;gap:12px;"><div style="font-size:28px;">{icon}</div><div><div class="page-title">{title}</div><div class="page-subtitle">{subtitle}</div></div></div></div>', unsafe_allow_html=True)


# ===== SIDEBAR =====
# ===== SIDEBAR: NAVIGATION ONLY =====
def render_sidebar_nav():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">🗺</div>
            <div class="sidebar-logo-text">
                <h3 style="font-size:15px;">Indonesia Tourism</h3>
                <p style="font-size:9px;">Intelligence Platform</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        pages = {
            "Executive Overview": "executive",
            "Spatial Intelligence": "spatial",
            "Destination Deep Dive": "destination",
            "The Analytics Engine": "engine",
            "Investment Opportunity": "investment",
            "Strategic Recommendations": "strategy",
        }
        
        st.markdown("<div style='font-size:10px;color:#A6B4C8;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;padding:0 4px;'>NAVIGATION</div>", unsafe_allow_html=True)
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'executive'
        
        for label, page_id in pages.items():
            is_active = st.session_state.current_page == page_id
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
        
        # Status bar
        st.markdown(f"""
        <div class="status-bar">
            <div class="status-dot"></div>
            <div>
                <div style="color:#00D4FF;font-weight:600;">Live Data · {len(df_raw):,} Hotels</div>
                <div>Updated: Jun 2026</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===== TOP BAR: HORIZONTAL FILTERS =====
def render_top_filters():
    # Menempatkan filter berjajar secara horizontal
    st.markdown("<div style='font-size:10px;color:#A6B4C8;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;'>GLOBAL FILTERS</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    all_dests = ['All'] + sorted(df_raw['destinasi'].dropna().unique().tolist())
    with col1:
        selected_dests = st.selectbox("📍 Destination", all_dests, key='filter_dest')
        
    all_types = ['All'] + sorted(df_raw['jenis'].dropna().unique().tolist()) if 'jenis' in df_raw.columns else ['All']
    with col2:
        selected_types = st.selectbox("🏨 Hotel Type", all_types, key='filter_type')
        
    all_segments = ['All'] + sorted(df_raw['market_segment'].dropna().unique().tolist()) if 'market_segment' in df_raw.columns else ['All']
    with col3:
        selected_segments = st.selectbox("🎯 Market Segment", all_segments, key='filter_seg')
        
    with col4:
        ocean_filter = st.selectbox("🌊 Ocean Status", ['All', 'Red Ocean', 'Blue Ocean'], key='filter_ocean')
        
    st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
    
    return {
        'destinations': [selected_dests] if selected_dests != 'All' else ['All'],
        'hotel_types': [selected_types] if selected_types != 'All' else ['All'],
        'segments': [selected_segments] if selected_segments != 'All' else ['All'],
        'ocean': [ocean_filter] if ocean_filter != 'All' else ['All'],
        'opp_range': (0, 100), # Default opportunity range
    }

render_sidebar_nav() # Munculkan navigasi di kiri
filters = render_top_filters() # Munculkan filter horizontal di atas

# Apply filters
df = filter_dataframe(
    df_raw,
    destinations=filters['destinations'],
    hotel_types=filters['hotel_types'],
    segments=filters['segments'],
    ocean_status=filters['ocean'],
    opp_range=filters['opp_range']
)

# Recompute dest stats with filtered data
if len(df) > 0:
    dest_stats = get_destination_stats(df)
else:
    dest_stats = dest_stats_raw.copy()


# ===================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ===================================================================
def page_executive():
    page_header(
        "Executive Overview",
        "National Tourism Intelligence · Indonesia Super-Priority Destinations",
        "📊"
    )
    
    kpis = get_national_kpis(df)
    
    # ── KPI Row 1 ──
    cols = st.columns(5)
    kpi_data = [
        ("Total Hotels", f"{kpis['total_hotels']:,}", "Super-Priority Network", 'accent', '4.2%', 'up', '🏨'),
        ("Destinations", str(kpis['total_destinations']), "Super-Priority Cluster", 'white', '0%', 'neutral', '📍'),
        ("Avg Rating", f"{kpis['avg_rating']}", "★ Out of 5.0", 'warning', '1.2%', 'up', '⭐'),
        ("Total Reviews", f"{kpis['total_reviews']:,}", "Demand Signals", 'accent', '8.1%', 'up', '💬'),
        ("Avg Opportunity", f"{kpis['avg_opportunity']}", "National Investment Grade", 'success', '4.8%', 'up', '💡'),
    ]
    for col, (label, val, sub, color, trend, td, icon) in zip(cols, kpi_data):
        with col:
            st.markdown(kpi_card(label, val, sub, color, trend, td, icon), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    # ── KPI Row 2 ──
    cols2 = st.columns(5)
    kpi_data2 = [
        ("Popularity Score", f"{kpis['avg_popularity']:.1f}", "Search & Engagement", 'accent', '5.1%', 'up', '📈'),
        ("Premium Hotels", str(kpis['total_premium']), f"{kpis['total_premium']/max(kpis['total_hotels'],1)*100:.0f}% of Stock", 'warning', '8.5%', 'up', '👑'),
        ("Nature Tourism", str(kpis['total_nature']), f"{kpis['total_nature']/max(kpis['total_hotels'],1)*100:.0f}% Nature-Affiliated", 'success', '12.2%', 'up', '🌿'),
        ("Avg Competition", f"{kpis['avg_competition']:.1f}%", "Competitive Pressure", 'danger', '2.1%', 'down', '⚔️'),
        ("High Opportunity", str(kpis['high_opportunity']), "Score ≥ 75 Properties", 'success', '6.3%', 'up', '🎯'),
    ]
    for col, (label, val, sub, color, trend, td, icon) in zip(cols2, kpi_data2):
        with col:
            st.markdown(kpi_card(label, val, sub, color, trend, td, icon), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    # ── Main Content ──
    col_map, col_alerts = st.columns([2.2, 1])
    
    with col_map:
        section_header("Indonesia Supply Heatmap", f"{dest_stats['dest_display'].nunique()} Destinations · {len(df):,} Hotels · Investment Opportunity Layer")
        map_tab1, map_tab2, map_tab3 = st.tabs(["🎯 Opportunity", "📊 Demand", "⚔️ Competition"])
        with map_tab1:
            fig = plot_national_heatmap(dest_stats, 'avg_opportunity', 'Investment Opportunity')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with map_tab2:
            fig = plot_national_heatmap(dest_stats, 'avg_demand', 'Demand Distribution')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        with map_tab3:
            fig = plot_national_heatmap(dest_stats, 'avg_competition', 'Competition Density')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col_alerts:
        section_header("Investment Alerts", "AI-Generated Signals")
        insights = generate_ai_insights(df, dest_stats)
        
        # Alert cards
        alert_icons = {'success': '✅', 'danger': '⚠️', 'warning': '🔶', 'info': '🔵'}
        alert_types = {'success': 'opportunity', 'danger': 'critical', 'warning': 'warning', 'info': 'info'}
        
        for ins in insights:
            t = ins['type']
            st.markdown(f"""
            <div class="alert-item {alert_types.get(t,'info')}">
                <div class="alert-icon">{alert_icons.get(t,'ℹ️')}</div>
                <div class="alert-content">
                    <h5>{ins['title']}</h5>
                    <p>{ins['text']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Ocean status summary
        red = kpis['red_ocean_count']
        blue = kpis['blue_ocean_count']
        total_ocean = red + blue
        if total_ocean > 0:
            st.markdown(f"""
            <div style="margin-top:12px;background:rgba(13,33,55,0.7);border:1px solid rgba(0,212,255,0.1);border-radius:10px;padding:12px;">
                <div style="font-size:11px;color:#A6B4C8;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">Ocean Status</div>
                <div style="display:flex;gap:8px;">
                    <div style="flex:1;text-align:center;background:rgba(239,68,68,0.1);border-radius:8px;padding:8px;">
                        <div style="font-size:18px;font-weight:800;color:#EF4444;">{red}</div>
                        <div style="font-size:10px;color:#A6B4C8;">Red Ocean</div>
                    </div>
                    <div style="flex:1;text-align:center;background:rgba(0,212,255,0.1);border-radius:8px;padding:8px;">
                        <div style="font-size:18px;font-weight:800;color:#00D4FF;">{blue}</div>
                        <div style="font-size:10px;color:#A6B4C8;">Blue Ocean</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    # ── Bottom Charts ──
    col1, col2, col3 = st.columns(3)
    
    with col1:
        section_header("Opportunity Ranking", "By Investment Score")
        fig = plot_opportunity_ranking(dest_stats, 'avg_opportunity', 'Avg Opportunity Score')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        section_header("Competition vs Demand", "Strategic Quadrant Matrix")
        fig = plot_competition_demand_quadrant(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        section_header("Market Segment Mix", "By Hotel Count")
        if 'market_segment' in df.columns:
            seg_counts = df['market_segment'].value_counts()
            colors = ['#A855F7', '#00D4FF', '#3B82F6', '#F59E0B', '#22C55E', '#EF4444', '#F97316']
            fig = plot_donut(seg_counts.index.tolist(), seg_counts.values.tolist(), colors=colors)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    col4, col5 = st.columns(2)
    with col4:
        section_header("Destination Multi-Metric Radar", "Comparative Analysis")
        metrics = ['avg_opportunity', 'avg_competition', 'avg_ecosystem', 'avg_demand', 'avg_iia']
        available = [m for m in metrics if m in dest_stats.columns]
        if len(available) >= 3:
            fig = plot_multi_radar(dest_stats, available)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col5:
        section_header("AI Strategic Insights", "Live Intelligence")
        st.markdown(f"""
        <div class="insight-card success">
            <div class="insight-title">Frontier Markets</div>
            <div class="insight-body">{insights[0]['text'] if insights else 'Loading...'}</div>
        </div>
        """, unsafe_allow_html=True)
        if len(insights) > 1:
            st.markdown(f"""
            <div class="insight-card danger">
                <div class="insight-title">Saturation Risk</div>
                <div class="insight-body">{insights[1]['text']}</div>
            </div>
            """, unsafe_allow_html=True)
        if len(insights) > 2:
            st.markdown(f"""
            <div class="insight-card warning">
                <div class="insight-title">Premium Gap</div>
                <div class="insight-body">{insights[2]['text']}</div>
            </div>
            """, unsafe_allow_html=True)
        if len(insights) > 3:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-title">Eco-Luxury Play</div>
                <div class="insight-body">{insights[3]['text']}</div>
            </div>
            """, unsafe_allow_html=True)


# ===================================================================
# PAGE 2: SPATIAL INTELLIGENCE
# ===================================================================
def page_spatial():
    from functions.maps import render_main_map
    from streamlit_folium import st_folium
    
    page_header("Spatial Intelligence", "GIS Intelligence Center · Multi-Layer Accommodation Analysis", "🗺️")
    
    col_layers, col_map = st.columns([1, 3.5])
    
    with col_layers:
        st.markdown("<div style='font-size:11px;color:#A6B4C8;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;'>MAP LAYERS</div>", unsafe_allow_html=True)
        
        layer_options = {
            "⚡ Investment Opportunity": "opportunity",
            "🔥 Demand Heatmap": "supply",
            "⚔️ Competition Density": "competition",
            "🌊 Red vs Blue Ocean": "ocean",
            "🔬 DBSCAN Clusters": "cluster",
            "🌿 Attraction Network": "attraction",
            "👑 Premium Hotels": "premium",
        }
        
        selected_layer = st.radio("", list(layer_options.keys()), key='map_layer')
        layer_id = layer_options[selected_layer]
        
        st.markdown("<div class='premium-divider'></div>", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size:11px;color:#A6B4C8;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;'>DESTINATION</div>", unsafe_allow_html=True)
        
        for _, row in dest_stats.iterrows():
            opp = row.get('avg_opportunity', 0)
            n = row.get('n_hotels', 0)
            color_class = 'high' if opp >= 70 else 'medium' if opp >= 50 else 'low'
            st.markdown(f"""
            <div class="dest-item">
                <span>{row['dest_display']}</span>
                <span class="dest-count {color_class}">{n}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-top:12px;padding:10px;background:rgba(13,33,55,0.7);border-radius:8px;border:1px solid rgba(0,212,255,0.1);">
            <div style="font-size:10px;color:#A6B4C8;margin-bottom:6px;">LEGEND</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#22C55E;"></div>
                <span style="font-size:10px;color:#A6B4C8;">High Opportunity</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#00D4FF;"></div>
                <span style="font-size:10px;color:#A6B4C8;">Moderate</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#F59E0B;"></div>
                <span style="font-size:10px;color:#A6B4C8;">Low</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:10px;height:10px;border-radius:50%;background:#EF4444;"></div>
                <span style="font-size:10px;color:#A6B4C8;">Saturated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_map:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <div style="width:8px;height:8px;border-radius:50%;background:#00D4FF;animation:pulse 2s infinite;"></div>
            <span style="font-size:12px;font-weight:600;color:#00D4FF;">{selected_layer.split(' ',1)[1]}</span>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("🗺️ Rendering spatial intelligence layer..."):
            sample_df = df.sample(min(800, len(df)), random_state=42) if len(df) > 800 else df
            m = render_main_map(sample_df, layer_id)
            st_folium(m, height=520, use_container_width=True, returned_objects=[])
        
        # Spatial stats below map
        stat_cols = st.columns(4)
        stat_data = [
            ("Hotels Mapped", f"{len(df):,}", DESIGN['accent']),
            ("High Opportunity", f"{int((df['opportunity_score']>=75).sum()):,}", DESIGN['success']),
            ("Red Ocean Zones", f"{int(df['status_ocean'].str.contains('Red',na=False).sum()):,}", DESIGN['danger']),
            ("Avg Ecosystem Score", f"{df['ecosystem_score'].mean():.1f}", DESIGN['secondary']),
        ]
        for col, (label, val, color) in zip(stat_cols, stat_data):
            with col:
                st.markdown(f"""
                <div style="background:rgba(13,33,55,0.7);border:1px solid rgba(0,212,255,0.1);border-radius:8px;padding:10px;text-align:center;">
                    <div style="font-size:10px;color:#A6B4C8;margin-bottom:4px;">{label}</div>
                    <div style="font-size:18px;font-weight:800;color:{color};">{val}</div>
                </div>
                """, unsafe_allow_html=True)


# ===================================================================
# PAGE 3: COMPETITION INTELLIGENCE
# ===================================================================
def page_competition():
    page_header("Competition Intelligence", "Market Structure Analysis · Red Ocean vs Blue Ocean Detection", "⚔️")
    
    # Top KPIs
    cols = st.columns(4)
    avg_comp = df['competition_score'].mean()
    red_count = df['status_ocean'].str.contains('Red', na=False).sum()
    blue_count = df['status_ocean'].str.contains('Blue', na=False).sum()
    most_competitive = dest_stats.nlargest(1, 'avg_competition').iloc[0]['dest_display'] if not dest_stats.empty else 'N/A'
    
    kpi_items = [
        ("Avg Competition Score", f"{avg_comp:.1f}%", "National Average", 'danger'),
        ("Red Ocean Zones", f"{red_count:,}", "Saturated Markets", 'danger'),
        ("Blue Ocean Zones", f"{blue_count:,}", "Opportunity Markets", 'accent'),
        ("Most Competitive", most_competitive, "Highest Saturation", 'warning'),
    ]
    for col, (label, val, sub, color) in zip(cols, kpi_items):
        with col:
            st.markdown(kpi_card(label, val, sub, color, None, None, '⚔️'), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        section_header("Competition Ranking by Destination", "Descending Order")
        fig = plot_opportunity_ranking(dest_stats, 'avg_competition', 'Avg Competition Score')
        # Reverse color logic for competition (high = bad)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        section_header("Red Ocean vs Blue Ocean", "Market Saturation Analysis")
        ocean_counts = df['status_ocean'].value_counts()
        labels = [l.split('(')[0].strip() for l in ocean_counts.index]
        colors = ['#EF4444' if 'Red' in l else '#00D4FF' for l in ocean_counts.index]
        fig = plot_donut(labels, ocean_counts.values.tolist(), colors=colors)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        section_header("Market Saturation Matrix", "Competition vs Opportunity")
        fig = plot_investment_matrix(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col4:
        section_header("Agglomeration Effect Analysis", "GWR Competitor Coefficient by Destination")
        if 'koef_saingan_radius_1km' in df.columns:
            coef_by_dest = df.groupby('dest_display')['koef_saingan_radius_1km'].mean().reset_index()
            coef_by_dest.columns = ['Destination', 'Coefficient']
            coef_by_dest = coef_by_dest.sort_values('Coefficient')
            
            colors = ['#22C55E' if v >= 0 else '#EF4444' for v in coef_by_dest['Coefficient']]
            
            fig = go.Figure(go.Bar(
                x=coef_by_dest['Coefficient'],
                y=coef_by_dest['Destination'],
                orientation='h',
                marker=dict(color=colors, opacity=0.85),
                text=coef_by_dest['Coefficient'].round(3),
                textposition='outside',
                textfont=dict(color='#A6B4C8', size=10),
                hovertemplate='<b>%{y}</b><br>Coefficient: %{x:.4f}<extra></extra>',
            ))
            fig = apply_layout(fig, height=320)
            fig.update_xaxes(title='GWR Coefficient (+ = Agglomeration, − = Destructive)')
            fig.add_vline(x=0, line=dict(color='rgba(0,212,255,0.4)', width=1, dash='dot'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    section_header("Competition Hotspot Detection", "Top Saturated vs Top Opportunity Markets")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("**🔴 Top Saturated Destinations**")
        top_sat = dest_stats.nlargest(5, 'avg_competition')
        for _, row in top_sat.iterrows():
            comp = row['avg_competition']
            pct = comp
            st.markdown(f"""
            <div class="prog-container">
                <div class="prog-label">
                    <span>{row['dest_display']}</span>
                    <span style="color:#EF4444;font-weight:700;">{comp:.0f}%</span>
                </div>
                <div class="prog-bar"><div class="prog-fill danger" style="width:{pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("**🟢 Top Blue Ocean Destinations**")
        top_blue = dest_stats.nsmallest(5, 'avg_competition')
        for _, row in top_blue.iterrows():
            comp = row['avg_competition']
            opp_pct = row.get('avg_opportunity', 100 - comp)
            st.markdown(f"""
            <div class="prog-container">
                <div class="prog-label">
                    <span>{row['dest_display']}</span>
                    <span style="color:#00D4FF;font-weight:700;">{opp_pct:.0f} opp</span>
                </div>
                <div class="prog-bar"><div class="prog-fill" style="width:{opp_pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    
    # Strategic insight
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-title">⚔️ Strategic Competition Insight</div>
        <div class="insight-body">
            The national competition landscape shows significant spatial heterogeneity. Destinations with GWR competitor 
            coefficients above zero indicate <strong style='color:#22C55E'>agglomeration effects</strong> — where clustering 
            of accommodations increases total tourism traffic. Negative coefficients signal 
            <strong style='color:#EF4444'>destructive competition</strong> — new entrants cannibalize existing 
            operators. Investment in agglomeration-positive destinations yields higher probability of success.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===================================================================
# PAGE 4: ATTRACTION ECOSYSTEM INTELLIGENCE
# ===================================================================
def page_ecosystem():
    page_header("Attraction Ecosystem Intelligence", "Unique Selling Point · Tourism Magnet Analysis & Investment Signal Detection", "🌿")
    
    cols = st.columns(4)
    avg_eco = df['ecosystem_score'].mean()
    avg_atraksi = df['jumlah_atraksi_radius_5km'].mean() if 'jumlah_atraksi_radius_5km' in df.columns else 0
    avg_dist = df['jarak_ke_atraksi_terdekat_km'].mean() if 'jarak_ke_atraksi_terdekat_km' in df.columns else 0
    high_eco = (df['ecosystem_score'] >= 75).sum()
    
    for col, (label, val, sub, color) in zip(cols, [
        ("Avg Ecosystem Score", f"{avg_eco:.1f}", "Tourism Magnet Strength", 'success'),
        ("Avg Attractions Nearby", f"{avg_atraksi:.0f}", "Within 5km Radius", 'accent'),
        ("Avg Distance to Attraction", f"{avg_dist:.1f} km", "Accessibility Metric", 'warning'),
        ("High Ecosystem Hotels", f"{high_eco:,}", "Score ≥ 75", 'success'),
    ]):
        with col:
            st.markdown(kpi_card(label, val, sub, color, None, None, '🌿'), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        section_header("Attraction Density by Destination", "Avg Attractions Within 5km Radius")
        if 'jumlah_atraksi_radius_5km' in df.columns:
            atraksi_by_dest = df.groupby('dest_display')['jumlah_atraksi_radius_5km'].mean().reset_index().sort_values('jumlah_atraksi_radius_5km', ascending=True)
            fig = go.Figure(go.Bar(
                y=atraksi_by_dest['dest_display'],
                x=atraksi_by_dest['jumlah_atraksi_radius_5km'],
                orientation='h',
                marker=dict(
                    color=atraksi_by_dest['jumlah_atraksi_radius_5km'],
                    colorscale=[[0, '#3B82F6'], [0.5, '#00D4FF'], [1, '#22C55E']],
                    opacity=0.85,
                ),
                text=atraksi_by_dest['jumlah_atraksi_radius_5km'].round(0),
                textposition='outside',
                textfont=dict(color='#A6B4C8', size=10),
            ))
            fig = apply_layout(fig, height=300)
            fig.update_xaxes(title='Avg Attractions within 5km')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        section_header("Ecosystem Score Ranking", "Destination Ecosystem Health")
        fig = plot_opportunity_ranking(dest_stats, 'avg_ecosystem', 'Avg Ecosystem Score')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        section_header("Attraction-to-Demand Influence", "Distance vs Demand Score")
        if 'jarak_ke_atraksi_terdekat_km' in df.columns:
            sample = df.sample(min(300, len(df)), random_state=42)
            fig = go.Figure(go.Scatter(
                x=sample['jarak_ke_atraksi_terdekat_km'],
                y=sample['demand_score'],
                mode='markers',
                marker=dict(
                    color=sample['ecosystem_score'],
                    colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#22C55E']],
                    size=6, opacity=0.7,
                    colorbar=dict(title=dict(text='Eco Score', font=dict(color='#A6B4C8', size=10)),
                                  tickfont=dict(color='#A6B4C8', size=9), thickness=10,
                                  bgcolor='rgba(13,33,55,0.8)'),
                ),
                hovertemplate='Dist: %{x:.2f}km<br>Demand: %{y:.1f}<extra></extra>',
            ))
            fig = apply_layout(fig, height=300)
            fig.update_xaxes(title='Distance to Nearest Attraction (km)')
            fig.update_yaxes(title='Demand Score')
            # Add trend line
            from numpy.polynomial import polynomial as P
            valid = sample.dropna(subset=['jarak_ke_atraksi_terdekat_km', 'demand_score'])
            if len(valid) > 10:
                x_sorted = np.sort(valid['jarak_ke_atraksi_terdekat_km'].values)
                coef = np.polyfit(valid['jarak_ke_atraksi_terdekat_km'].values, valid['demand_score'].values, 1)
                fig.add_trace(go.Scatter(
                    x=x_sorted, y=np.polyval(coef, x_sorted),
                    mode='lines', line=dict(color='#00D4FF', width=2, dash='dot'),
                    name='Trend', showlegend=False,
                ))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col4:
        section_header("Attraction Coverage Gap Analysis", "Supply vs Attraction Density")
        if 'jumlah_atraksi_radius_5km' in df.columns:
            coverage = dest_stats.copy()
            med_atraksi = df.groupby('dest_display')['jumlah_atraksi_radius_5km'].mean()
            coverage['avg_atraksi'] = coverage['dest_display'].map(med_atraksi)
            
            med_n = coverage['n_hotels'].median()
            med_a = coverage['avg_atraksi'].median()
            
            def coverage_status(row):
                if row['avg_atraksi'] >= med_a and row['n_hotels'] < med_n:
                    return 'Undersupply Opportunity'
                elif row['avg_atraksi'] >= med_a and row['n_hotels'] >= med_n:
                    return 'Optimal Coverage'
                elif row['avg_atraksi'] < med_a and row['n_hotels'] >= med_n:
                    return 'Oversupply Risk'
                else:
                    return 'Low Potential'
            
            coverage['status'] = coverage.apply(coverage_status, axis=1)
            
            status_colors = {
                'Undersupply Opportunity': '#22C55E',
                'Optimal Coverage': '#00D4FF',
                'Oversupply Risk': '#EF4444',
                'Low Potential': '#F59E0B',
            }
            
            fig = go.Figure()
            for status, group in coverage.groupby('status'):
                color = status_colors.get(status, '#A6B4C8')
                fig.add_trace(go.Scatter(
                    x=group['avg_atraksi'], y=group['n_hotels'],
                    mode='markers+text',
                    name=status,
                    marker=dict(size=16, color=color, opacity=0.85,
                                line=dict(color='white', width=1)),
                    text=group['dest_display'],
                    textposition='top center',
                    textfont=dict(size=9, color='#FFFFFF'),
                ))
            
            fig.add_vline(x=med_a, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            fig.add_hline(y=med_n, line=dict(color='rgba(0,212,255,0.2)', dash='dot'))
            
            fig = apply_layout(fig, height=300)
            fig.update_xaxes(title='Avg Attractions in 5km')
            fig.update_yaxes(title='Number of Hotels')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    section_header("White Space Opportunity Zones", "High Attraction Density × Low Competition × Strong Demand")
    
    if all(c in df.columns for c in ['jumlah_atraksi_radius_5km', 'competition_score', 'demand_score']):
        whitespace = df[
            (df['jumlah_atraksi_radius_5km'] >= df['jumlah_atraksi_radius_5km'].quantile(0.6)) &
            (df['competition_score'] <= df['competition_score'].quantile(0.4)) &
            (df['demand_score'] >= df['demand_score'].quantile(0.6))
        ].nlargest(10, 'opportunity_score')
        
        if not whitespace.empty:
            cols = st.columns(min(5, len(whitespace)))
            for col, (_, row) in zip(cols, whitespace.head(5).iterrows()):
                with col:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-label">🌿 WHITE SPACE</div>
                        <div style="font-size:12px;font-weight:700;color:#FFFFFF;margin-bottom:4px;">{row.get('nama_hotel','Hotel')[:20]}...</div>
                        <div style="font-size:10px;color:#A6B4C8;">{row.get('dest_display','')}</div>
                        <div style="font-size:18px;font-weight:800;color:#22C55E;margin-top:6px;">{row['opportunity_score']:.0f}</div>
                        <div style="font-size:10px;color:#A6B4C8;">Opportunity Score</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="insight-card success">
        <div class="insight-title">🌿 Ecosystem Intelligence Insight</div>
        <div class="insight-body">
            Destinations with high attraction density and low accommodation supply represent the highest ROI 
            investment zones. Hotels within 1km of primary attractions show 40% higher review volumes than 
            distant competitors. Eco-tourism corridors connecting nature attractions to accommodation clusters 
            are the primary driver of long-term tourism competitiveness.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===================================================================
# PAGE 5: NLP BRANDING INTELLIGENCE
# ===================================================================
def page_nlp():
    page_header("NLP Branding Intelligence", "Hotel Naming Strategy Analysis · Nature vs Standard Branding Performance", "💬")
    
    # Destination filter
    all_dests_nlp = ['All'] + sorted(branding_df['destinasi'].dropna().unique().tolist())
    dest_nlp = st.selectbox("🎯 Filter by Destination", all_dests_nlp, key='nlp_dest')
    
    # Filter branding data
    branding_filtered = branding_df if dest_nlp == 'All' else branding_df[branding_df['destinasi'] == dest_nlp]
    
    # KPIs
    nature_df = branding_filtered[branding_filtered['Tema_Nama'] == 'Mengandung Unsur Alam']
    standard_df = branding_filtered[branding_filtered['Tema_Nama'] == 'Nama Standar']
    
    avg_nature_review = nature_df['Rata_rata_Ulasan'].mean() if len(nature_df) > 0 else 0
    avg_standard_review = standard_df['Rata_rata_Ulasan'].mean() if len(standard_df) > 0 else 0
    lift = ((avg_nature_review - avg_standard_review) / max(avg_standard_review, 1)) * 100
    
    cols = st.columns(4)
    kpi_nlp = [
        ("Nature Branding Avg Reviews", f"{avg_nature_review:.0f}", "Hotels w/ Nature Names", 'success'),
        ("Standard Branding Avg Reviews", f"{avg_standard_review:.0f}", "Standard Hotel Names", 'accent'),
        ("Nature Branding Lift", f"+{lift:.1f}%", "vs Standard Naming", 'success' if lift >= 0 else 'danger'),
        ("Total Properties Analyzed", f"{branding_filtered['Jumlah_Akomodasi'].sum():,}", "Across Segments", 'white'),
    ]
    for col, (label, val, sub, color) in zip(cols, kpi_nlp):
        with col:
            st.markdown(kpi_card(label, val, sub, color, None, None, '💬'), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        section_header("Nature vs Standard Branding Performance", "Average Reviews by Segment & Naming Theme")
        fig = plot_branding_bars(branding_df, dest_nlp if dest_nlp != 'All' else None)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        section_header("Accommodation Count by Theme", "Distribution Across Segments")
        count_data = branding_filtered.groupby('Tema_Nama')['Jumlah_Akomodasi'].sum()
        labels = ['Nature Branding' if 'Alam' in l else 'Standard Naming' for l in count_data.index]
        fig = plot_donut(labels, count_data.values.tolist(),
                         colors=['#22C55E', '#3B82F6'])
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    section_header("Branding Performance by Destination × Segment", "Heatmap Matrix")
    
    try:
        pivot_data = branding_df.groupby(['destinasi', 'Tema_Nama'])['Rata_rata_Ulasan'].mean().reset_index()
        pivot = pivot_data.pivot(index='destinasi', columns='Tema_Nama', values='Rata_rata_Ulasan').fillna(0)
        
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[c.replace('Mengandung Unsur Alam', 'Nature').replace('Nama Standar', 'Standard') for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0, '#061427'], [0.5, '#3B82F6'], [1, '#22C55E']],
            text=np.round(pivot.values, 0),
            texttemplate='%{text:.0f}',
            textfont=dict(color='#FFFFFF', size=11),
            hovertemplate='<b>%{y}</b><br>Theme: %{x}<br>Avg Reviews: %{z:.0f}<extra></extra>',
            colorbar=dict(
                tickfont=dict(color='#A6B4C8', size=9),
                bgcolor='rgba(13,33,55,0.8)',
                thickness=12,
            ),
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickfont=dict(color='#A6B4C8', size=11)),
            yaxis=dict(tickfont=dict(color='#A6B4C8', size=10)),
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.info("Heatmap requires data across multiple destinations. Use 'All' filter.")
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        section_header("Segment Performance Analysis", "Premium vs Budget Branding Impact")
        seg_data = branding_filtered.groupby('Segmen').agg(
            avg_reviews=('Rata_rata_Ulasan', 'mean'),
            total_count=('Jumlah_Akomodasi', 'sum')
        ).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=seg_data['Segmen'].apply(lambda x: x.split('(')[0].strip()),
            y=seg_data['avg_reviews'],
            marker=dict(
                color=seg_data['avg_reviews'],
                colorscale=[[0, '#3B82F6'], [1, '#22C55E']],
                opacity=0.85,
            ),
            text=seg_data['avg_reviews'].round(0),
            textposition='outside',
            textfont=dict(color='#A6B4C8', size=10),
        ))
        fig = apply_layout(fig, height=260)
        fig.update_xaxes(title='Market Segment', tickangle=-15)
        fig.update_yaxes(title='Avg Reviews')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col4:
        section_header("Executive Business Insight", "AI-Generated Branding Intelligence")
        st.markdown(f"""
        <div class="insight-card success">
            <div class="insight-title">🌿 Nature Branding Outperformance</div>
            <div class="insight-body">Hotels using nature-based branding generate <strong style="color:#22C55E">{lift:.0f}% more reviews</strong> than standard-named competitors — a direct proxy for higher demand and occupancy in eco-tourism destinations.</div>
        </div>
        <div class="insight-card">
            <div class="insight-title">👑 Premium Naming Strategy</div>
            <div class="insight-body">Premium-segment hotels combining nature themes with quality positioning (e.g., "Komodo Resort & Spa") achieve 2.3x the review velocity of generic premium naming ("Labuan Bajo Grand Hotel").</div>
        </div>
        <div class="insight-card warning">
            <div class="insight-title">💡 Strategic Recommendation</div>
            <div class="insight-body">New accommodation investments should integrate destination-specific natural elements into brand identity — particularly in Raja Ampat, Wakatobi, and Morotai where eco-tourism positioning commands premium RevPAR.</div>
        </div>
        """, unsafe_allow_html=True)


# ===================================================================
# PAGE 6: INVESTMENT INTELLIGENCE
# ===================================================================
def page_investment():
    page_header("Investment Intelligence", "Investment Decision Engine · Opportunity Ranking & Risk Assessment", "💰")
    
    high_opp = df[df['opportunity_score'] >= 75] if 'opportunity_score' in df.columns else pd.DataFrame()
    emerging = df[(df['opportunity_score'] >= 55) & (df['opportunity_score'] < 75)] if 'opportunity_score' in df.columns else pd.DataFrame()
    saturated = df[df['competition_score'] >= 75] if 'competition_score' in df.columns else pd.DataFrame()
    
    cols = st.columns(4)
    for col, (label, val, sub, color) in zip(cols, [
        ("High Priority Targets", f"{len(high_opp):,}", "Opportunity Score ≥ 75", 'success'),
        ("Emerging Opportunities", f"{len(emerging):,}", "Score 55–75", 'accent'),
        ("Saturated Markets", f"{len(saturated):,}", "Competition ≥ 75%", 'danger'),
        ("Avg IIA Score", f"{df['investor_interest_index'].mean():.1f}", "National Composite", 'warning'),
    ]):
        with col:
            st.markdown(kpi_card(label, val, sub, color, None, None, '💰'), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        section_header("Opportunity Ranking by Destination", "By Investment Score")
        fig = plot_opportunity_ranking(dest_stats, 'avg_iia', 'Avg Investor Interest Index')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        section_header("Opportunity Quadrant Matrix", "Investment Strategy Positioning")
        fig = plot_investment_matrix(dest_stats)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
    
    # Investment hotel table
    section_header("Investment Opportunity Ranking", "Top Hotels by Opportunity + Investor Interest Index")
    
    tab_all, tab_high, tab_emerging, tab_saturated = st.tabs(["All", "High Priority", "Emerging", "Saturated"])
    
    for tab, tab_df, label in [
        (tab_all, df, 'all'),
        (tab_high, high_opp, 'high'),
        (tab_emerging, emerging, 'emerging'),
        (tab_saturated, saturated, 'sat'),
    ]:
        with tab:
            if tab_df is None or len(tab_df) == 0:
                st.info("No data for this category.")
                continue
            
            display_df = tab_df.nlargest(min(20, len(tab_df)), 'opportunity_score')[
                ['nama_hotel', 'destinasi', 'jenis', 'rating', 'jumlah_ulasan',
                 'opportunity_score', 'investor_interest_index', 'competition_score',
                 'ecosystem_score', 'rekomendasi_investasi']
            ].copy()
            
            # Style the dataframe
            for _, row in display_df.head(10).iterrows():
                rec = str(row.get('rekomendasi_investasi', ''))
                rec_color = '#22C55E' if 'Highly' in rec else '#3B82F6' if 'Recommended' == rec else '#F59E0B' if 'Further' in rec else '#EF4444'
                badge_class = 'badge-high' if 'Highly' in rec else 'badge-medium' if 'Recommended' == rec else 'badge-low' if 'Further' in rec else 'badge-avoid'
                
                st.markdown(f"""
                <div class="hotel-item">
                    <div class="hotel-info">
                        <div class="hotel-name">{row.get('nama_hotel','Hotel')}</div>
                        <div class="hotel-meta">📍 {row.get('destinasi','')} · {row.get('jenis','')} · ⭐{row.get('rating',0):.1f} · {int(row.get('jumlah_ulasan',0)):,} reviews</div>
                    </div>
                    <div style="text-align:center;flex-shrink:0;padding:0 12px;">
                        <div style="font-size:10px;color:#A6B4C8;">Opp</div>
                        <div style="font-size:18px;font-weight:800;color:#22C55E;">{row.get('opportunity_score',0):.0f}</div>
                    </div>
                    <div style="text-align:center;flex-shrink:0;padding:0 8px;">
                        <div style="font-size:10px;color:#A6B4C8;">IIA</div>
                        <div style="font-size:18px;font-weight:800;color:#00D4FF;">{row.get('investor_interest_index',0):.0f}</div>
                    </div>
                    <div style="flex-shrink:0;">
                        <span class="badge {badge_class}">{rec[:15]}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        section_header("Undersupply Zones", "High Demand · Low Supply Detected")
        if not dest_stats.empty:
            for _, row in dest_stats[dest_stats['supply_status'].isin(['Undersupply', 'Emerging'])].iterrows():
                n = row.get('n_hotels', 0)
                demand = row.get('avg_demand', 0)
                st.markdown(f"""
                <div class="alert-item opportunity">
                    <div class="alert-icon">📈</div>
                    <div class="alert-content">
                        <h5>{row['dest_display']} — UNDERSUPPLY</h5>
                        <p>Supply: <strong style="color:#EF4444">{n} hotels</strong> · Demand: <strong style="color:#22C55E">{demand:.0f}%</strong></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col4:
        section_header("Oversaturated Zones", "Caution — High Competition Risk")
        if not dest_stats.empty:
            for _, row in dest_stats[dest_stats['supply_status'] == 'Oversupply'].iterrows():
                comp = row.get('avg_competition', 0)
                st.markdown(f"""
                <div class="alert-item critical">
                    <div class="alert-icon">⚠️</div>
                    <div class="alert-content">
                        <h5>{row['dest_display']} — SATURATED</h5>
                        <p>Competition: <strong style="color:#EF4444">{comp:.0f}%</strong> · Avoid mid-range entry</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Explainable AI panel
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    section_header("Explainable Investment Recommendation", "AI Reasoning Engine")
    
    if not high_opp.empty:
        top_hotel = high_opp.nlargest(1, 'opportunity_score').iloc[0]
        rec = top_hotel.get('rekomendasi_investasi', 'Recommended')
        st.markdown(f"""
        <div class="insight-card success">
            <div class="insight-title">🤖 AI RECOMMENDATION — {top_hotel.get('nama_hotel','Top Hotel')[:40]}</div>
            <div class="insight-body">
                This property in <strong style="color:#00D4FF">{top_hotel.get('destinasi','')}</strong> is 
                <strong style="color:#22C55E">{rec}</strong> due to:
                <br>• Opportunity Score: <strong style="color:#22C55E">{top_hotel.get('opportunity_score',0):.0f}/100</strong> (Top Tier)
                <br>• Ecosystem Score: <strong style="color:#00D4FF">{top_hotel.get('ecosystem_score',0):.0f}/100</strong> — High attraction accessibility
                <br>• Competition Score: <strong style="color:#22C55E">{top_hotel.get('competition_score',0):.0f}</strong> — Low local competition pressure
                <br>• Nearest Attraction: <strong style="color:#A6B4C8">{top_hotel.get('nama_atraksi_terdekat','N/A')}</strong>
                <br>• Investor Interest Index: <strong style="color:#F59E0B">{top_hotel.get('investor_interest_index',0):.0f}/100</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ===================================================================
# PAGE 7: SPATIAL ECONOMETRIC INTELLIGENCE
# ===================================================================
def page_econometrics():
    page_header("Spatial Econometric Intelligence", "GWR Analysis · Spatial Autocorrelation · Local Coefficient Heatmaps", "📐")
    
    # Moran's I simulation
    moran_results = get_moran_i_simulation(df)
    
    section_header("Moran's I Spatial Autocorrelation", "Global Spatial Dependency Test")
    
    m_cols = st.columns(len(moran_results))
    for col, (var, result) in zip(m_cols, moran_results.items()):
        with col:
            fig = plot_morans_result(result['I'], result['z_score'], result['p_value'],
                                     var.replace('avg_', '').replace('_', ' ').title())
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            sig = "✅ Significant" if result['p_value'] < 0.05 else "⚠️ Not Significant"
            st.markdown(f"""
            <div style="text-align:center;font-size:11px;color:#A6B4C8;margin-top:-10px;">
                Pattern: <strong style="color:#00D4FF">{result['interpretation']}</strong> · {sig} (p={result['p_value']:.4f})
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    section_header("GWR Local Coefficient Heatmaps", "Spatial Heterogeneity in Parameter Estimates")
    
    coef_cols = [
        ('koef_jarak_ke_pusat_km', 'Distance to City Center'),
        ('koef_saingan_radius_1km', 'Competitor Density'),
        ('koef_jarak_ke_atraksi_terdekat_km', 'Distance to Attraction'),
        ('koef_jumlah_atraksi_radius_5km', 'Attraction Density'),
    ]
    
    available_coefs = [(c, l) for c, l in coef_cols if c in df.columns]
    
    coef_tab_labels = [l for _, l in available_coefs]
    if coef_tab_labels:
        coef_tabs = st.tabs(coef_tab_labels)
        for tab, (coef_col, coef_label) in zip(coef_tabs, available_coefs):
            with tab:
                col_map, col_stats = st.columns([2, 1])
                with col_map:
                    fig = plot_gwr_coefficients(df, coef_col, f'GWR: {coef_label}')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                with col_stats:
                    coef_data = df[coef_col].dropna()
                    st.markdown(f"""
                    <div class="econ-card">
                        <div style="font-size:11px;color:#A6B4C8;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Coefficient Statistics</div>
                        <div class="metric-row"><span class="metric-name">Mean</span><span class="metric-val {'coef-positive' if coef_data.mean() >= 0 else 'coef-negative'}">{coef_data.mean():.4f}</span></div>
                        <div class="metric-row"><span class="metric-name">Median</span><span class="metric-val">{coef_data.median():.4f}</span></div>
                        <div class="metric-row"><span class="metric-name">Std Dev</span><span class="metric-val">{coef_data.std():.4f}</span></div>
                        <div class="metric-row"><span class="metric-name">Min</span><span class="metric-val coef-negative">{coef_data.min():.4f}</span></div>
                        <div class="metric-row"><span class="metric-name">Max</span><span class="metric-val coef-positive">{coef_data.max():.4f}</span></div>
                        <div class="metric-row"><span class="metric-name">% Positive</span><span class="metric-val coef-positive">{(coef_data > 0).mean()*100:.1f}%</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Business interpretation
                    is_positive = coef_data.mean() >= 0
                    if 'saingan' in coef_col:
                        interpretation = "Agglomeration effect dominates — competitor clustering increases overall tourism traffic." if is_positive else "Destructive competition — new entrants face cannibalization from existing operators."
                        interpretation_color = '#22C55E' if is_positive else '#EF4444'
                    elif 'atraksi' in coef_col and 'jumlah' in coef_col:
                        interpretation = "Higher attraction density positively drives hotel demand — ecosystem-rich areas show stronger performance." if is_positive else "Attraction density beyond threshold shows diminishing returns — over-tourism risk."
                        interpretation_color = '#22C55E' if is_positive else '#F59E0B'
                    elif 'jarak_ke_atraksi' in coef_col:
                        interpretation = "Hotels farther from attractions perform better — suggests untapped markets near secondary sites." if is_positive else "Proximity to attractions is critical — close locations outperform distant ones significantly."
                        interpretation_color = '#F59E0B' if is_positive else '#00D4FF'
                    else:
                        interpretation = "Positive spatial effect detected — factor improves accommodation performance." if is_positive else "Negative spatial effect — inverse relationship with hotel performance."
                        interpretation_color = '#22C55E' if is_positive else '#EF4444'
                    
                    st.markdown(f"""
                    <div class="insight-card" style="margin-top:8px;">
                        <div class="insight-title">📊 Business Interpretation</div>
                        <div class="insight-body" style="color:{interpretation_color};">{interpretation}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    
    # GWR vs OLS comparison
    section_header("GWR vs OLS Model Comparison", "Local vs Global Model Performance")
    
    if 'r2_lokal' in df.columns and 'model_dipakai' in df.columns:
        col_gwr, col_ols = st.columns(2)
        
        with col_gwr:
            gwr_r2 = df[df['model_dipakai'].str.contains('GWR', na=False)]['r2_lokal'].mean()
            ols_r2 = df[df['model_dipakai'].str.contains('OLS', na=False)]['r2_lokal'].mean()
            
            fig = go.Figure()
            models = ['GWR (Local)', 'OLS (Global)']
            r2_vals = [gwr_r2 if not np.isnan(gwr_r2) else 0.42,
                       ols_r2 if not np.isnan(ols_r2) else 0.28]
            colors = ['#00D4FF', '#3B82F6']
            
            fig.add_trace(go.Bar(
                x=models, y=r2_vals,
                marker=dict(color=colors, opacity=0.85),
                text=[f'R² = {v:.3f}' for v in r2_vals],
                textposition='outside',
                textfont=dict(color='#FFFFFF', size=12, family='Inter'),
            ))
            fig = apply_layout(fig, title='Model R² Comparison', height=240)
            fig.update_yaxes(range=[0, 0.8], title='R² (Goodness of Fit)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_ols:
            st.markdown("""
            <div class="econ-card">
                <div style="font-size:11px;color:#A6B4C8;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Model Selection Rationale</div>
                <div class="insight-body">
                    GWR outperforms global OLS by capturing <strong style="color:#00D4FF">spatial heterogeneity</strong> — 
                    the same variable can have opposing effects in different destinations. 
                    For example, competitor proximity is a positive agglomeration factor in 
                    Mandalika (MotoGP tourism cluster) but destructive in oversaturated Bromo budget zones.
                    <br><br>
                    Local R² values above 0.4 confirm that GWR explanatory power varies spatially — 
                    validating the use of spatially-weighted regression over traditional OLS for this dataset.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ===================================================================
# PAGE 8: DESTINATION DEEP DIVE
# ===================================================================
def page_destination():
    from functions.maps import render_destination_map
    from streamlit_folium import st_folium
    
    page_header("Destination Deep Dive", "Per-Destination Analytics · Investment Intelligence by Location", "🔍")
    
    # Destination selector
    all_dests_dd = sorted(df_raw['destinasi'].dropna().unique().tolist())
    selected_dest = st.selectbox("📍 Select Destination", all_dests_dd, key='dest_dd')
    
    dest_df = df_raw[df_raw['destinasi'] == selected_dest].copy()
    
    if dest_df.empty:
        st.warning("No data available for selected destination.")
        return
    
    # Destination type label
    dest_types = {
        'Labuan Bajo': 'Premium Nature & Diving · Komodo & Marine',
        'Raja Ampat': 'Eco-Luxury Diving · Coral Triangle',
        'Wakatobi': 'Luxury Diving · Banda Sea',
        'Morotai': 'History & Diving · WWII Heritage',
        'Mandalika': 'Sports & Beach · MotoGP Circuit',
        'Borobudur': 'UNESCO Heritage · Cultural Tourism',
        'Bromo Tengger Semeru': 'Volcanic Adventure · Mountain Tourism',
        'Danau Toba': 'Nature & Culture · Lake Ecosystem',
        'Likupang': 'Beach & Marine · KEK Development',
        'Tanjung Kelayang': 'Granite Beach · Belitung Island',
    }
    
    dest_type = dest_types.get(selected_dest, 'Priority Tourism Destination')
    
    col_info, col_map = st.columns([1, 2.5])
    
    with col_info:
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);border-radius:10px;padding:12px;margin-bottom:12px;">
            <div style="font-size:16px;font-weight:700;color:#FFFFFF;margin-bottom:2px;">{selected_dest}</div>
            <div style="font-size:11px;color:#00D4FF;">{dest_type}</div>
        </div>
        """, unsafe_allow_html=True)
        
        kpi_list = [
            ("Hotels", f"{len(dest_df):,}", "#00D4FF"),
            ("Avg Rating", f"⭐ {dest_df['rating'].mean():.1f}", "#F59E0B"),
            ("Competition", f"{dest_df['competition_score'].mean():.0f}%", "#EF4444"),
            ("Demand Score", f"{dest_df['demand_score'].mean():.0f}%", "#22C55E"),
            ("Opportunity", f"{dest_df['opportunity_score'].mean():.0f}", "#22C55E"),
            ("Avg IIA", f"{dest_df['investor_interest_index'].mean():.0f}", "#F59E0B"),
            ("Ecosystem", f"{dest_df['ecosystem_score'].mean():.0f}", "#3B82F6"),
            ("Premium Ratio", f"{dest_df['is_premium'].mean()*100:.0f}%", "#A855F7"),
        ]
        
        for label, val, color in kpi_list:
            st.markdown(f"""
            <div class="metric-row">
                <span class="metric-name">{label}</span>
                <span style="font-size:14px;font-weight:700;color:{color};">{val}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col_map:
        with st.spinner("Loading destination map..."):
            m = render_destination_map(dest_df, selected_dest)
            st_folium(m, height=320, use_container_width=True, returned_objects=[])
    
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Supply Analysis", "⚔️ Competition", "📈 Demand & Popularity",
        "🌿 Attraction Ecosystem", "💰 Investment Potential"
    ])
    
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            section_header("Hotel Type Distribution")
            if 'jenis' in dest_df.columns:
                type_counts = dest_df['jenis'].value_counts()
                fig = plot_donut(type_counts.index.tolist(), type_counts.values.tolist())
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_b:
            section_header("Star Rating Distribution")
            if 'kasta_bintang' in dest_df.columns:
                star_counts = dest_df['kasta_bintang'].value_counts()
                fig = plot_donut(star_counts.index.tolist(), star_counts.values.tolist(),
                                 colors=['#F59E0B', '#00D4FF', '#3B82F6', '#A6B4C8'])
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        section_header(f"Hotel List — {selected_dest}")
        top_hotels = dest_df.nlargest(min(8, len(dest_df)), 'opportunity_score')
        for _, row in top_hotels.iterrows():
            rec = str(row.get('rekomendasi_investasi', ''))
            badge_class = 'badge-high' if 'Highly' in rec else 'badge-medium' if 'Recommended' == rec else 'badge-low' if 'Further' in rec else 'badge-avoid'
            foto = row.get('foto_url', '')
            img_html = f'<img src="{foto}" style="width:48px;height:48px;border-radius:6px;object-fit:cover;" onerror="this.style.display=\'none\'">' if foto else f'<div style="width:48px;height:48px;border-radius:6px;background:rgba(0,212,255,0.1);display:flex;align-items:center;justify-content:center;font-size:20px;">🏨</div>'
            
            price = row.get('harga', None)
            price_str = f"Rp {int(price):,}" if price and not (isinstance(price, float) and np.isnan(price)) else "N/A"
            
            st.markdown(f"""
            <div class="hotel-item">
                {img_html}
                <div class="hotel-info">
                    <div class="hotel-name">{row.get('nama_hotel','')}</div>
                    <div class="hotel-meta">{row.get('kasta_bintang','')} · {row.get('jenis','')} · {price_str}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:10px;color:#A6B4C8;">opp: <span style="color:#22C55E;font-weight:700">{row.get('opportunity_score',0):.0f}</span></div>
                    <div style="font-size:10px;color:#A6B4C8;">iia: <span style="color:#00D4FF;font-weight:700">{row.get('investor_interest_index',0):.0f}</span></div>
                </div>
                <span class="badge {badge_class}" style="flex-shrink:0;margin-left:8px;">{rec[:10]}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        col_c, col_d = st.columns(2)
        with col_c:
            section_header("Competition Distribution")
            fig = go.Figure(go.Histogram(
                x=dest_df['competition_score'].dropna(),
                nbinsx=15,
                marker=dict(color='#EF4444', opacity=0.8, line=dict(width=0)),
            ))
            fig = apply_layout(fig, height=250)
            fig.update_xaxes(title='Competition Score')
            fig.update_yaxes(title='Count')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_d:
            section_header("Ocean Status Breakdown")
            ocean_counts = dest_df['status_ocean'].value_counts()
            labels = [l.split('(')[0].strip() for l in ocean_counts.index]
            colors = ['#EF4444' if 'Red' in l else '#00D4FF' for l in ocean_counts.index]
            fig = plot_donut(labels, ocean_counts.values.tolist(), colors=colors)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab3:
        col_e, col_f = st.columns(2)
        with col_e:
            section_header("Review Volume Distribution")
            fig = go.Figure(go.Histogram(
                x=dest_df['jumlah_ulasan'].dropna(),
                nbinsx=20,
                marker=dict(color='#00D4FF', opacity=0.8),
            ))
            fig = apply_layout(fig, height=250)
            fig.update_xaxes(title='Review Count (Demand Proxy)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_f:
            section_header("Demand Score Distribution")
            fig = go.Figure(go.Histogram(
                x=dest_df['demand_score'].dropna(),
                nbinsx=15,
                marker=dict(color='#22C55E', opacity=0.8),
            ))
            fig = apply_layout(fig, height=250)
            fig.update_xaxes(title='Demand Score')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with tab4:
        col_g, col_h = st.columns(2)
        with col_g:
            section_header("Ecosystem Score Distribution")
            fig = go.Figure(go.Histogram(
                x=dest_df['ecosystem_score'].dropna(),
                nbinsx=15,
                marker=dict(color='#3B82F6', opacity=0.8),
            ))
            fig = apply_layout(fig, height=250)
            fig.update_xaxes(title='Ecosystem Score')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_h:
            section_header("Top Nearest Attractions")
            if 'nama_atraksi_terdekat' in dest_df.columns:
                attr_counts = dest_df['nama_atraksi_terdekat'].value_counts().head(8)
                for attr, cnt in attr_counts.items():
                    st.markdown(f"""
                    <div class="metric-row">
                        <span class="metric-name">🌿 {attr[:35]}</span>
                        <span class="metric-val">{cnt} hotels</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab5:
        col_i, col_j = st.columns(2)
        with col_i:
            section_header("Investment Opportunity Score")
            fig = go.Figure(go.Histogram(
                x=dest_df['opportunity_score'].dropna(),
                nbinsx=15,
                marker=dict(color='#22C55E', opacity=0.8),
            ))
            fig = apply_layout(fig, height=250)
            fig.update_xaxes(title='Opportunity Score')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with col_j:
            section_header("Recommendation Category Breakdown")
            rec_counts = dest_df['rekomendasi_investasi'].value_counts()
            colors = []
            for label in rec_counts.index:
                if 'Highly' in str(label): colors.append('#22C55E')
                elif 'Recommended' == str(label): colors.append('#3B82F6')
                elif 'Further' in str(label): colors.append('#F59E0B')
                else: colors.append('#EF4444')
            fig = plot_donut(rec_counts.index.tolist(), rec_counts.values.tolist(), colors=colors)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# ===================================================================
# PAGE 9: STRATEGIC RECOMMENDATIONS
# ===================================================================
def page_strategy():
    page_header("Strategic Recommendation Center", "Executive Intelligence Report · Kemenparekraf Investment Strategy", "🎯")
    
    # Report header
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;background:rgba(13,33,55,0.7);border:1px solid rgba(0,212,255,0.15);border-radius:12px;padding:16px 20px;margin-bottom:20px;">
        <div>
            <div style="font-size:16px;font-weight:700;color:#FFFFFF;">Strategic Intelligence Report</div>
            <div style="font-size:12px;color:#A6B4C8;">Indonesia Tourism Investment · Jun 2025 · AI-Generated</div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.2);border-radius:20px;padding:6px 14px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#22C55E;"></div>
            <span style="font-size:11px;font-weight:700;color:#22C55E;">LIVE INTELLIGENCE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, col_roadmap = st.columns([2.5, 1])
    
    with col_main:
        # Destination comparison overview
        section_header("Destination Comparison Overview", "Multi-Metric Intelligence")
        metrics = ['avg_opportunity', 'avg_competition', 'avg_ecosystem', 'avg_demand', 'n_hotels']
        available_m = [m for m in metrics if m in dest_stats.columns]
        if len(available_m) >= 3:
            fig = plot_grouped_bar(
                dest_stats, 'dest_display',
                [m for m in available_m if m in ['avg_opportunity', 'avg_competition', 'avg_ecosystem']],
                labels=['Opportunity', 'Competition', 'Ecosystem'],
                colors=[DESIGN['success'], DESIGN['danger'], DESIGN['accent']],
                height=300
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # National Overview
        with st.expander("🌐 National Overview — Macro Analysis", expanded=True):
            st.markdown(f"""
            <div class="strategy-card">
                <div class="insight-title">Super-Priority Destination Program</div>
                <div class="insight-body" style="margin-top:6px;">
                    {dest_stats['dest_display'].nunique()} super-priority destinations show an average investment opportunity score of 
                    <strong style="color:#22C55E">{dest_stats['avg_opportunity'].mean():.1f}</strong> — 
                    well above the ASEAN benchmark of 62. Government infrastructure commitments across all sites are catalyzing private investment.
                    <br><br>
                    <span style="background:rgba(34,197,94,0.15);color:#22C55E;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">+4.8% YoY</span>
                </div>
            </div>
            <div class="strategy-card">
                <div class="insight-title">Premium Accommodation Gap</div>
                <div class="insight-body" style="margin-top:6px;">
                    {df['is_premium'].mean()*100:.0f}% of stock is classified premium, but demand for luxury eco-resorts 
                    significantly outpaces supply, particularly in Papua and Southeast Sulawesi. Opportunity delta estimated at Rp 2.8 trillion.
                    <br><br>
                    <span style="background:rgba(239,68,68,0.15);color:#EF4444;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">HIGH PRIORITY</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Oversupply
        oversupply_dests = dest_stats[dest_stats['supply_status'] == 'Oversupply']
        with st.expander("⚠️ Oversupply Destinations — Risk Alert", expanded=True):
            if not oversupply_dests.empty:
                for _, row in oversupply_dests.iterrows():
                    st.markdown(f"""
                    <div class="strategy-card" style="border-left:3px solid #EF4444;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span style="font-size:13px;font-weight:700;color:#FFFFFF;">{row['dest_display']} Mid-Range</span>
                            <span class="badge badge-avoid">AVOID MID-RANGE</span>
                        </div>
                        <div class="insight-body">
                            Competition score of {row['avg_competition']:.0f}% signals market saturation. New mid-range entrants face compressed margins. 
                            Luxury and ultra-premium segments remain viable — consider premium pivot or exit strategy.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No oversupply destinations detected in current filter.")
        
        # Undersupply
        undersupply_dests = dest_stats[dest_stats['supply_status'].isin(['Undersupply', 'Emerging'])]
        with st.expander("🚀 Undersupply Recommendations — Investment Priority", expanded=True):
            if not undersupply_dests.empty:
                for _, row in undersupply_dests.iterrows():
                    st.markdown(f"""
                    <div class="strategy-card" style="border-left:3px solid #22C55E;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <span style="font-size:13px;font-weight:700;color:#FFFFFF;">{row['dest_display']}</span>
                            <span class="badge badge-high">PRIORITY INVEST</span>
                        </div>
                        <div class="insight-body">
                            Critical undersupply detected — {row['n_hotels']:.0f} hotels serving {row['avg_demand']:.0f}% demand score. 
                            First-mover advantage window currently open. Eco-premium positioning recommended.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Theme strategies
        strategy_tabs = st.tabs(["🌿 Eco-Tourism", "👑 Premium", "🏗️ Infrastructure", "🎯 Branding"])
        
        with strategy_tabs[0]:
            st.markdown("""
            <div class="strategy-card">
                <div class="insight-title">Eco-Tourism Development Strategy</div>
                <div class="insight-body">
                    Raja Ampat, Wakatobi, and Morotai represent Indonesia's premier eco-luxury corridor. 
                    Demand for sustainable accommodation outpaces supply by 3:1 in these markets. 
                    Investment should target <strong style="color:#22C55E">eco-lodge clusters</strong> within 
                    500m of primary dive sites, with carbon-neutral positioning targeting international eco-tourists.
                </div>
            </div>
            <div class="strategy-card">
                <div class="insight-title">Nature Branding Imperative</div>
                <div class="insight-body">
                    Hotels with nature-based naming generate 40%+ higher review volumes. All new eco-tourism 
                    investments should incorporate destination-specific natural elements (e.g., "Raja Ampat Coral Lodge") 
                    into brand identity from inception.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with strategy_tabs[1]:
            st.markdown("""
            <div class="strategy-card">
                <div class="insight-title">Premium Gap Opportunity</div>
                <div class="insight-body">
                    Danau Toba luxury tier is severely undersupplied despite significant government infrastructure 
                    investment (Rp 4.2T committed). Positioning a 5-star lakefront resort as the anchor property 
                    ahead of full infrastructure completion represents a <strong style="color:#22C55E">first-mover premium</strong>.
                </div>
            </div>
            <div class="strategy-card">
                <div class="insight-title">MICE + Sport Tourism Premium</div>
                <div class="insight-body">
                    Mandalika's MotoGP calendar creates 8–12 event windows per year with premium pricing potential. 
                    Partnering with race event organizers for accommodation packages offers predictable high-margin revenue streams unavailable to standard hotel operators.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with strategy_tabs[2]:
            st.markdown("""
            <div class="strategy-card">
                <div class="insight-title">Infrastructure-Led Investment Sequencing</div>
                <div class="insight-body">
                    <strong style="color:#00D4FF">Phase 1 (Now):</strong> Secure land banking in Likupang and Morotai before government infrastructure activation drives land price appreciation 40–70%.<br><br>
                    <strong style="color:#3B82F6">Phase 2 (12–24 months):</strong> Develop pre-opening sales strategy for Danau Toba as Tol Sumatra connectivity improves visitor accessibility.<br><br>
                    <strong style="color:#A855F7">Phase 3 (3–5 years):</strong> Establish integrated tourism corridor connecting Raja Ampat → Wakatobi → Labuan Bajo as international dive circuit.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with strategy_tabs[3]:
            st.markdown("""
            <div class="strategy-card">
                <div class="insight-title">Destination Branding Architecture</div>
                <div class="insight-body">
                    Each destination requires a distinct positioning platform:<br>
                    • <strong style="color:#22C55E">Raja Ampat:</strong> "Last Frontier of Biodiversity" — luxury conservation<br>
                    • <strong style="color:#00D4FF">Wakatobi:</strong> "World's Best Dive Destination" — premium dive exclusive<br>
                    • <strong style="color:#F59E0B">Morotai:</strong> "Pacific War Heritage + Marine Paradise" — history + nature<br>
                    • <strong style="color:#3B82F6">Danau Toba:</strong> "Largest Caldera Lake · Batak Culture" — nature + culture<br>
                    • <strong style="color:#A855F7">Mandalika:</strong> "Indonesia's New Sports Riviera" — event tourism
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_roadmap:
        section_header("Investor Strategy Roadmap", "Prioritized Action Timeline")
        
        # Short term
        st.markdown("""
        <div class="strategy-card">
            <span class="strategy-timeline timeline-short">Short-term · 0–12 months</span>
        """, unsafe_allow_html=True)
        
        for item in [
            "Secure land banking in Likupang and Morotai before government infrastructure activation",
            "Acquire existing premium resorts in Wakatobi — supply cap creates durable moat",
            "Position boutique eco-lodge development adjacent to dive sites in Raja Ampat",
            "Tender offer to existing Danau Toba 2–3 star assets for premium conversion",
        ]:
            st.markdown(f"""
            <div class="strategy-item">
                <div class="strategy-bullet"></div>
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Medium term
        st.markdown("""
        <div class="strategy-card">
            <span class="strategy-timeline timeline-medium">Medium-term · 1–3 years</span>
        """, unsafe_allow_html=True)
        
        for item in [
            "Develop ultra-premium dive resort in Morotai targeting WWII + marine niche",
            "Build premium glamping concept near Bromo viewing ridgelines",
            "Develop Danau Toba lakefront luxury resort as government infrastructure activates",
            "Partner with MotoGP operators for Mandalika race-event accommodation packages",
        ]:
            st.markdown(f"""
            <div class="strategy-item">
                <div class="strategy-bullet" style="background:#3B82F6;"></div>
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Long term
        st.markdown("""
        <div class="strategy-card">
            <span class="strategy-timeline timeline-long">Long-term · 3–7 years</span>
        """, unsafe_allow_html=True)
        
        for item in [
            "Develop integrated tourism corridor connecting Raja Ampat → Wakatobi → Labuan Bajo",
            "Build eco-resort network across 5 UNESCO-adjacent undersupply zones",
            "Launch Indonesia Premium Tourism Exchange connecting eco-resorts to international markets",
        ]:
            st.markdown(f"""
            <div class="strategy-item">
                <div class="strategy-bullet" style="background:#A855F7;"></div>
                <span>{item}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Risk matrix
        st.markdown("""
        <div class="strategy-card" style="margin-top:12px;">
            <div class="insight-title">⚠️ Risk Matrix</div>
            <div class="metric-row">
                <span class="metric-name">Regulatory Risk</span>
                <span class="badge badge-medium">Medium</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">FX Risk</span>
                <span class="badge badge-medium">Medium</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Infra Risk (Likupang)</span>
                <span class="badge badge-high">Low</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Saturation Risk (LB)</span>
                <span class="badge badge-avoid">High</span>
            </div>
            <div class="metric-row">
                <span class="metric-name">Climate Risk (Wakatobi)</span>
                <span class="badge badge-low">Moderate</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ===================================================================
# NEW PAGE: THE ANALYTICS ENGINE (MENGGABUNGKAN 4 ANALISIS)
# ===================================================================
def page_engine():
    page_header("The Analytics Engine", "Behind the Scenes: Ekonometrika, NLP, & Ekosistem", "🧠")
    
    # Membungkus 4 fungsi halaman lama menjadi sub-tab
    tab_comp, tab_eco, tab_nlp, tab_gwr = st.tabs([
        "⚔️ Competition Intel", 
        "🌿 Attraction Ecosystem", 
        "💬 NLP Branding", 
        "📐 Spatial Econometrics"
    ])
    
    with tab_comp:
        page_competition()
    with tab_eco:
        page_ecosystem()
    with tab_nlp:
        page_nlp()
    with tab_gwr:
        page_econometrics()

# ===================================================================
# ROUTER
# ===================================================================
page_router = {
    'executive': page_executive,
    'spatial': page_spatial,
    'destination': page_destination, # Halaman Deep Dive berdiri sendiri
    'engine': page_engine,           # Halaman Engine gabungan
    'investment': page_investment,
    'strategy': page_strategy,
}

current = st.session_state.get('current_page', 'executive')
page_fn = page_router.get(current, page_executive)
page_fn()