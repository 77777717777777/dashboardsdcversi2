import streamlit as st

def inject_css():
    css = """
    <style>
    /* =========================================
       IMPORT FONT
       ========================================= */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

    /* =========================================
       VARIABEL WARNA — TEMA PROFESIONAL
       Palet: Putih bersih + Biru Navy + Biru Royal
       Cocok untuk presentasi kementerian
       ========================================= */
    :root {
        --bg-primary:     #F0F7F4;
        --bg-secondary:   #FFFFFF;
        --bg-card:        #FFFFFF;
        --bg-sidebar:     #1B4332;
        --bg-sidebar-sec: #2D6A4F;

        --color-navy:     #1B4332;
        --color-royal:    #2D6A4F;
        --color-accent:   #40916C;
        --color-teal:     #52B788;

        --color-success:  #2D6A4F;
        --color-warning:  #E9A020;
        --color-danger:   #D62839;
        --color-purple:   #7B2D8B;
        --color-blue:     #1565C0;
        --color-magenta:  #C2185B;

        --text-primary:   #1B4332;
        --text-secondary: #2D6A4F;
        --text-muted:     #74A98A;
        --text-white:     #FFFFFF;

        --border-light:   #D8EDE4;
        --border-medium:  #B7D9C8;
        --shadow-sm:      0 1px 4px rgba(27,67,50,0.08);
        --shadow-md:      0 4px 16px rgba(27,67,50,0.12);
        --shadow-lg:      0 8px 32px rgba(27,67,50,0.16);

        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
    }

    /* =========================================
       GLOBAL RESET & BASE
       ========================================= */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #F0F7F4;
        background-image:
            radial-gradient(ellipse at 10% 0%, rgba(64,145,108,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 100%, rgba(82,183,136,0.06) 0%, transparent 50%);
    }

    /* Header transparan agar tidak muncul garis hitam */
    /* Sembunyikan header bawaan Streamlit */
    [data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
    }

    /* Sembunyikan menu burger dan footer */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Tombol toggle sidebar — pastikan selalu muncul */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        z-index: 999 !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: 6px !important;
    }

    [data-testid="collapsedControl"] svg {
        color: var(--color-navy) !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }

    /* =========================================
       SIDEBAR
       ========================================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332 0%, #081C15 100%) !important;
        border-right: 1px solid rgba(82,183,136,0.2);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem !important;
    }

    /* Tombol navigasi sidebar */
    [data-testid="stSidebar"] button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: rgba(255,255,255,0.8) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        margin-bottom: 3px !important;
    }

    [data-testid="stSidebar"] button:hover {
        background: rgba(82,183,136,0.2) !important;
        border-color: rgba(82,183,136,0.4) !important;
        color: #FFFFFF !important;
    }

    /* =========================================
       LOGO SIDEBAR
       ========================================= */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 4px 18px 4px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 18px;
        margin-top: -8px;
    }

    .sidebar-logo-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #40916C, #52B788);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .sidebar-logo-text h3 {
        margin: 0;
        font-size: 13px;
        font-weight: 700;
        color: #FFFFFF;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        line-height: 1.3;
    }

    .sidebar-logo-text p {
        margin: 0;
        font-size: 9px;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }

    .premium-divider {
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 16px 0;
        border: none;
    }

    /* Status bar sidebar */
    .status-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: var(--radius-sm);
        padding: 10px 12px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #2ECC71;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 0 6px #2ECC71;
        animation: pulse 2.5s infinite;
    }

    @keyframes pulse {
        0%   { opacity: 1; }
        50%  { opacity: 0.5; }
        100% { opacity: 1; }
    }

    /* Label navigasi sidebar */
    .nav-label {
        font-size: 9px;
        color: rgba(255,255,255,0.35);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 8px;
        padding: 0 2px;
    }

    /* =========================================
       PAGE HEADER
       ========================================= */
    .page-header {
        display: flex;
        align-items: center;
        gap: 16px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-lg);
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid #40916C;
    }

    .page-header-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #2D6A4F, #52B788);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }

    .page-title {
        font-size: 22px;
        font-weight: 800;
        color: var(--color-navy);
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }

    .page-subtitle {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 3px;
        font-weight: 500;
    }

    /* =========================================
       SECTION HEADER
       ========================================= */
    .section-header {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        margin: 0px 0 10px 0;
    }

    .section-header-accent {
        width: 3px;
        height: 100%;
        min-height: 36px;
        background: linear-gradient(180deg, #40916C, #52B788);
        border-radius: 2px;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .section-title {
        font-size: 13px !important;   /* turun dari 15px */
        font-weight: 700;
        color: var(--color-navy);
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .section-subtitle {
        font-size: 10px !important;   /* turun dari 11px */
        color: var(--text-muted);
        margin-top: 2px;
        font-weight: 400;
    }

    /* =========================================
       KPI CARDS
       ========================================= */
    .kpi-card {
        border: none;
        border-radius: var(--radius-md);
        padding: 16px 18px;
        position: relative;
        box-shadow: var(--shadow-md);
        height: 100%;
        overflow: hidden;
    }

    /* Warna solid per tipe */
    .kpi-card.accent  { background: linear-gradient(135deg, #1D5FAD, #2E86DE); }
    .kpi-card.success { background: linear-gradient(135deg, #0A6B3A, #1A9A5A); }
    .kpi-card.warning { background: linear-gradient(135deg, #B8680A, #D97706); }
    .kpi-card.danger  { background: linear-gradient(135deg, #9B1C1C, #C0392B); }
    .kpi-card.purple  { background: linear-gradient(135deg, #5B21B6, #7C3AED); }
    .kpi-card.white   { background: linear-gradient(135deg, #0F2A4A, #1A3A5C); }

    /* Semua teks jadi putih */
    .kpi-card .kpi-label { color: rgba(255,255,255,0.75) !important; }
    .kpi-card .kpi-value { color: #FFFFFF !important; }
    .kpi-card .kpi-sub   { color: rgba(255,255,255,0.6) !important; }

    /* Hapus ::before gradient bar karena card sudah berwarna */
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #1B4332, #40916C, #52B788);
        border-radius: var(--radius-md) var(--radius-md) 0 0;
    }

    .kpi-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    .kpi-label {
        font-size: 11px;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .kpi-value {
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .kpi-sub {
        font-size: 11px;
        color: var(--text-muted);
        margin-top: 8px;
        font-weight: 400;
    }

    .kpi-trend {
        position: absolute;
        top: 14px;
        right: 14px;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 20px;
    }

    .kpi-trend.up   { background: rgba(26,122,74,0.1);  color: var(--color-success); }
    .kpi-trend.down { background: rgba(192,57,43,0.1);  color: var(--color-danger);  }
    .kpi-trend.neutral { background: rgba(74,96,128,0.1); color: var(--text-secondary); }
    
    /* KPI — 4 kolom penuh rata kiri-kanan */
    div[data-testid="stHorizontalBlock"]:has(.kpi-card) {
        gap: 8px !important;
        }

    div[data-testid="stHorizontalBlock"]:has(.kpi-card) > div {
        flex: 1 1 0 !important;
        min-width: 0 !important;}

    /* Warna nilai KPI */
    .accent  { color: var(--color-accent) !important; }
    .success { color: var(--color-success) !important; }
    .warning { color: var(--color-warning) !important; }
    .danger  { color: var(--color-danger) !important; }
    .purple  { color: var(--color-purple) !important; }
    .white   { color: var(--color-navy) !important; }

    /* =========================================
       STATS CARD — seragam untuk semua halaman
       ========================================= */
    .stats-card {
        background: #FFFFFF;
        border: 1px solid #D8EDE4;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(27,67,50,0.08);
        box-sizing: border-box;
    }
    .stats-card-label {
        font-size: 10px;
        color: #74A98A;
        font-weight: 600;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stats-card-value {
        font-size: 20px;
        font-weight: 800;
        line-height: 1.1;
    }

    /* =========================================
       CHART CONTAINER / VIZ CARD
       ========================================= */
    .viz-card {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-md) !important;
        padding: 16px !important;
        box-shadow: var(--shadow-sm) !important;
        margin-bottom: 0 !important;
    }

    /* =========================================
       INSIGHT & ALERT CARDS
       ========================================= */
    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-left: 4px solid var(--color-accent);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: var(--shadow-sm);
    }

    .insight-card.success { border-left-color: var(--color-success); background: rgba(26,122,74,0.04); }
    .insight-card.warning { border-left-color: var(--color-warning); background: rgba(196,123,0,0.04); }
    .insight-card.danger  { border-left-color: var(--color-danger);  background: rgba(192,57,43,0.04); }
    .insight-card.info    { border-left-color: var(--color-accent);  background: rgba(45,134,222,0.04); }

    .insight-title {
        font-size: 13px;
        font-weight: 700;
        color: var(--color-navy);
        margin-bottom: 5px;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .insight-body {
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.65;
    }

    /* Alert items */
    .alert-item {
        display: flex;
        gap: 12px;
        padding: 12px 14px;
        border-radius: var(--radius-md);
        margin-bottom: 8px;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        box-shadow: var(--shadow-sm);
    }

    .alert-item.opportunity {
        border-color: rgba(26,122,74,0.25);
        background: rgba(26,122,74,0.04);
        border-left: 3px solid var(--color-success);
    }

    .alert-item.critical {
        border-color: rgba(192,57,43,0.25);
        background: rgba(192,57,43,0.04);
        border-left: 3px solid var(--color-danger);
    }

    .alert-item.warning {
        border-color: rgba(196,123,0,0.25);
        background: rgba(196,123,0,0.04);
        border-left: 3px solid var(--color-warning);
    }

    .alert-item.info {
        border-left: 3px solid var(--color-accent);
    }

    .alert-icon { font-size: 16px; padding-top: 1px; }
    .alert-content h5 {
        margin: 0 0 3px 0;
        font-size: 12px;
        font-weight: 700;
        color: var(--color-navy);
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    .alert-content p {
        margin: 0;
        font-size: 11px;
        color: var(--text-secondary);
        line-height: 1.5;
    }

    /* =========================================
       HOTEL LIST ITEMS
       ========================================= */
    .hotel-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 14px;
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        margin-bottom: 8px;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s;
    }

    .hotel-item:hover { box-shadow: var(--shadow-md); }
    .hotel-info { flex-grow: 1; }
    .hotel-name { font-size: 13px; font-weight: 700; color: var(--color-navy); margin-bottom: 3px; }
    .hotel-meta { font-size: 11px; color: var(--text-muted); }

    /* =========================================
       BADGES
       ========================================= */
    .badge {
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }

    .badge-high   { background: rgba(26,122,74,0.12);  color: var(--color-success); border: 1px solid rgba(26,122,74,0.25); }
    .badge-medium { background: rgba(45,134,222,0.12); color: var(--color-accent);  border: 1px solid rgba(45,134,222,0.25); }
    .badge-low    { background: rgba(196,123,0,0.12);  color: var(--color-warning); border: 1px solid rgba(196,123,0,0.25); }
    .badge-avoid  { background: rgba(192,57,43,0.12);  color: var(--color-danger);  border: 1px solid rgba(192,57,43,0.25); }

    /* =========================================
       PROGRESS BARS
       ========================================= */
    .prog-container { margin-bottom: 10px; }
    .prog-label {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 5px;
        font-weight: 500;
    }
    .prog-bar {
        height: 6px;
        background: var(--border-light);
        border-radius: 3px;
        overflow: hidden;
    }
    .prog-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--color-royal), var(--color-accent));
        border-radius: 3px;
    }
    .prog-fill.danger {
        background: linear-gradient(90deg, #C0392B, #E74C3C);
    }

    /* =========================================
       DESTINASI LIST SIDEBAR
       ========================================= */
    .dest-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 10px;
        border-radius: var(--radius-sm);
        font-size: 12px;
        color: rgba(255,255,255,0.8);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .dest-count { font-weight: 700; font-size: 12px; }
    .dest-count.high   { color: #2ECC71; }
    .dest-count.medium { color: #5DADE2; }
    .dest-count.low    { color: #F39C12; }

    /* =========================================
       STRATEGY CARDS
       ========================================= */
    .strategy-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: var(--shadow-sm);
    }

    .strategy-timeline {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 3px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 10px;
    }

    .timeline-short  { background: rgba(26,122,74,0.1);  color: var(--color-success); }
    .timeline-medium { background: rgba(45,134,222,0.1); color: var(--color-royal);   }
    .timeline-long   { background: rgba(103,65,217,0.1); color: var(--color-purple);  }

    .strategy-item {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    .strategy-bullet {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-top: 6px;
        flex-shrink: 0;
    }

    /* =========================================
       ECONOMETRICS CARD
       ========================================= */
    .econ-card {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 16px;
        box-shadow: var(--shadow-sm);
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 0;
        border-bottom: 1px solid var(--border-light);
    }

    .metric-row:last-child { border-bottom: none; }
    .metric-name { font-size: 12px; color: var(--text-secondary); }
    .metric-val  { font-size: 12px; font-weight: 700; color: var(--color-navy); }
    .coef-positive { color: var(--color-success) !important; }
    .coef-negative { color: var(--color-danger)  !important; }

    /* =========================================
       STREAMLIT WIDGET OVERRIDES
       ========================================= */
    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 13px !important;
    }

    /* =========================================
    TAB KPI — PENUH & RATA TENGAH
    ========================================= */

    /* =========================================
       TABS — final clean version
       ========================================= */
    button[data-baseweb="tab"] {
        color: #1B4332 !important;
        background: transparent !important;
        border-bottom: 3px solid transparent !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-radius: 0 !important;
        font-size: clamp(10px, 1.1vw, 12px) !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 8px clamp(8px, 1.5vw, 18px) !important;
        margin-right: 2px !important;
        white-space: nowrap !important;
        transition: all 0.15s !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #1B4332 !important;
        background: rgba(64,145,108,0.08) !important;
        border-bottom: 3px solid #74A98A !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1B4332 !important;
        background: transparent !important;
        border-bottom: 3px solid #40916C !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    button[data-baseweb="tab"] * {
        color: inherit !important;
    }

    div[data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #B7D9C8 !important;
        gap: 0 !important;
        overflow: hidden !important;
        padding: 0 !important;
    }

    /* Sembunyikan scroll arrow */
    div[data-baseweb="tab-list"] > button:not([data-baseweb="tab"]) {
        display: none !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    button[data-baseweb="tab"] {
        color: #1B4332 !important;
        background: transparent !important;
        border-bottom: 3px solid transparent !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-radius: 0 !important;
        font-size: clamp(10px, 1.1vw, 12px) !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        padding: 8px clamp(8px, 1.5vw, 18px) !important;
        margin-right: 2px !important;
        white-space: nowrap !important;
        transition: all 0.15s !important;
        text-align: center !important;           /* ← tambah */
        justify-content: center !important;      /* ← tambah */
        flex: 1 1 0 !important;                  /* ← tambah biar rata penuh */
        min-width: 0 !important;                 /* ← tambah biar tidak overflow */
    }

    div[data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #B7D9C8 !important;
        gap: 0 !important;
        overflow: hidden !important;
        padding: 0 !important;
        display: flex !important;                /* ← tambah */
        width: 100% !important;                  /* ← tambah */
    }

    /* =========================================
       OCEAN STATUS SUMMARY (Executive Page)
       ========================================= */
    .ocean-summary {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 14px;
        margin-top: 12px;
        box-shadow: var(--shadow-sm);
    }

    .ocean-summary-label {
        font-size: 10px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* =========================================
       DIVIDER UTAMA
       ========================================= */
    hr.premium-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
        margin: 14px 0;
    .block-container hr.premium-divider {
        border-top: 1px solid var(--border-light); /* di area konten */
        }
    }
    /* =========================================
       RADIO BUTTON — PETA SPASIAL (MAP LAYERS)
       ========================================= */
    /* Label teks radio button */
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label span {
        color: var(--text-primary) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }

    /* Pilihan aktif */
    [data-testid="stRadio"] label[data-checked="true"] p,
    [data-testid="stRadio"] label[data-checked="true"] span {
        color: var(--color-accent) !important;
        font-weight: 700 !important;
    }

    /* Lingkaran radio — default (tidak dipilih): hanya garis luar */
    [data-testid="stRadio"] [role="radio"] {
        background-color: transparent !important;
        border: 2px solid #74A98A !important;
    }

    /* Lingkaran radio — dipilih: merah dengan dot tengah putih */
    [data-testid="stRadio"] [role="radio"][aria-checked="true"] {
        background-color: #D62839 !important;
        border: 2px solid #D62839 !important;
    }

    /* Dot putih di tengah saat dipilih */
    [data-testid="stRadio"] [role="radio"][aria-checked="true"]::after {
        content: '';
        display: block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: white;
        margin: auto;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }

    [data-testid="stRadio"] [role="radio"] {
        position: relative;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)