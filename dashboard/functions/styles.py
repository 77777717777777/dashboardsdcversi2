import streamlit as st

def inject_css():
    css = """
    <style>
    /* =========================================
       GLOBAL THEME & TYPOGRAPHY
       ========================================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark Navy Background for main app */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #061427 0%, #0A1931 60%, #051020 100%);
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A1931 0%, #061427 100%) !important;
        border-right: 1px solid rgba(0,212,255,0.15);
    }

    /* Hide standard Streamlit header/footer */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* =========================================
       SIDEBAR ELEMENTS
       ========================================= */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0 20px 0;
        border-bottom: 1px solid rgba(0,212,255,0.15);
        margin-bottom: 20px;
    }
    .sidebar-logo-icon {
        font-size: 32px;
        background: -webkit-linear-gradient(45deg, #00D4FF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-logo-text h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.2;
    }
    .sidebar-logo-text p {
        margin: 0;
        font-size: 10px;
        color: #00D4FF;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .premium-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent);
        margin: 20px 0;
    }
    .status-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(13,33,55,0.7);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 8px;
        padding: 12px;
        font-size: 11px;
        color: #A6B4C8;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #22C55E;
        border-radius: 50%;
        box-shadow: 0 0 8px #22C55E;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    /* =========================================
       HEADERS & TYPOGRAPHY
       ========================================= */
    .page-header {
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .page-title {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 13px;
        color: #00D4FF;
        font-weight: 500;
        margin-top: 4px;
    }
    .section-header {
        margin: 24px 0 16px 0;
    }
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-subtitle {
        font-size: 12px;
        color: #A6B4C8;
        margin-top: 2px;
    }

    /* =========================================
       CARDS & CONTAINERS (Glassmorphism)
       ========================================= */
    .kpi-card {
        background: rgba(17, 40, 75, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
        position: relative;
        transition: all 0.3s ease;
        height: 100%;
    }
    .kpi-card:hover {
        border-color: rgba(0, 212, 255, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .kpi-label { font-size: 12px; color: #A6B4C8; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
    .kpi-value { font-size: 28px; font-weight: 800; line-height: 1.1; }
    .kpi-sub { font-size: 11px; color: #64748B; margin-top: 8px; font-weight: 500; }
    
    .kpi-trend {
        position: absolute;
        top: 16px;
        right: 16px;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
    }
    .kpi-trend.up { background: rgba(34,197,94,0.15); color: #22C55E; }
    .kpi-trend.down { background: rgba(239,68,68,0.15); color: #EF4444; }
    .kpi-trend.neutral { background: rgba(255,255,255,0.1); color: #A6B4C8; }

    /* Colors for metrics */
    .accent { color: #00D4FF; }
    .success { color: #22C55E; }
    .warning { color: #F59E0B; }
    .danger { color: #EF4444; }
    .purple { color: #A855F7; }
    .white { color: #FFFFFF; }

    /* =========================================
       INSIGHTS & ALERTS
       ========================================= */
    .insight-card {
        background: rgba(13, 33, 55, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-left: 3px solid #00D4FF;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .insight-card.success { border-left-color: #22C55E; background: rgba(34,197,94,0.05); }
    .insight-card.warning { border-left-color: #F59E0B; background: rgba(245,158,11,0.05); }
    .insight-card.danger { border-left-color: #EF4444; background: rgba(239,68,68,0.05); }
    
    .insight-title { font-size: 13px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px; }
    .insight-body { font-size: 12px; color: #A6B4C8; line-height: 1.6; }

    .alert-item {
        display: flex;
        gap: 12px;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
    }
    .alert-item.opportunity { border-color: rgba(34,197,94,0.3); background: rgba(34,197,94,0.05); }
    .alert-item.critical { border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.05); }
    .alert-icon { font-size: 18px; }
    .alert-content h5 { margin: 0 0 4px 0; font-size: 13px; font-weight: 700; color: #FFF; }
    .alert-content p { margin: 0; font-size: 11px; color: #A6B4C8; line-height: 1.4; }

    /* =========================================
       CUSTOM LISTS & COMPONENTS
       ========================================= */
    .hotel-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        background: rgba(17,40,75,0.3);
        border-radius: 8px;
        margin-bottom: 8px;
        transition: background 0.2s;
    }
    .hotel-item:hover { background: rgba(0,212,255,0.05); }
    .hotel-info { flex-grow: 1; margin-left: 12px; }
    .hotel-name { font-size: 13px; font-weight: 700; color: #FFF; margin-bottom: 4px; }
    .hotel-meta { font-size: 11px; color: #A6B4C8; }
    
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-high { background: rgba(34,197,94,0.15); color: #22C55E; border: 1px solid rgba(34,197,94,0.3); }
    .badge-medium { background: rgba(0,212,255,0.15); color: #00D4FF; border: 1px solid rgba(0,212,255,0.3); }
    .badge-low { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.3); }
    .badge-avoid { background: rgba(239,68,68,0.15); color: #EF4444; border: 1px solid rgba(239,68,68,0.3); }

    .prog-container { margin-bottom: 12px; }
    .prog-label { display: flex; justify-content: space-between; font-size: 12px; color: #A6B4C8; margin-bottom: 4px; }
    .prog-bar { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
    .prog-fill { height: 100%; background: #00D4FF; border-radius: 3px; }
    .prog-fill.danger { background: #EF4444; }

    .dest-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 12px; color: #FFF; }
    .dest-count { font-weight: 700; }
    .dest-count.high { color: #22C55E; }
    .dest-count.medium { color: #00D4FF; }
    .dest-count.low { color: #F59E0B; }

    /* =========================================
       STRATEGY REPORT STYLING
       ========================================= */
    .strategy-card {
        background: rgba(13,33,55,0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .strategy-timeline {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 12px;
    }
    .timeline-short { background: rgba(34,197,94,0.15); color: #22C55E; }
    .timeline-medium { background: rgba(59,130,246,0.15); color: #3B82F6; }
    .timeline-long { background: rgba(168,85,247,0.15); color: #A855F7; }
    
    .strategy-item {
        display: flex;
        gap: 12px;
        margin-bottom: 12px;
        font-size: 12px;
        color: #A6B4C8;
        line-height: 1.5;
    }
    .strategy-bullet {
        width: 6px;
        height: 6px;
        background: #22C55E;
        border-radius: 50%;
        margin-top: 6px;
        flex-shrink: 0;
    }

    .econ-card { background: rgba(17,40,75,0.4); border-radius: 8px; padding: 16px; border: 1px solid rgba(255,255,255,0.05); }
    .metric-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .metric-name { font-size: 12px; color: #A6B4C8; }
    .metric-val { font-size: 12px; font-weight: 700; color: #FFF; }
    .coef-positive { color: #22C55E !important; }
    .coef-negative { color: #EF4444 !important; }
    
    /* Modify Streamlit Expander */
    .streamlit-expanderHeader {
        background-color: rgba(17,40,75,0.4) !important;
        border-radius: 8px !important;
        color: #00D4FF !important;
        font-weight: 600 !important;
    }
    /* =========================================
       PANGKAS JARAK ATAS (STREAMLIT DEFAULT PADDING)
       ========================================= */
    /* Mepetkan halaman utama ke atas */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Mepetkan Sidebar (Logo) ke atas */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }
    
    /* Perbaiki margin logo */
    .sidebar-logo {
        padding-top: 0 !important;
        margin-top: -15px !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)