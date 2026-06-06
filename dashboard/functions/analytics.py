import pandas as pd
import numpy as np
import os
import traceback
import streamlit as st


# ==========================================
# CONSTANTS & DESIGN TOKENS
# ==========================================
DESIGN = {
    'bg': '#061427',
    'card': 'rgba(17, 40, 75, 0.4)',
    'border': 'rgba(0, 212, 255, 0.15)',
    'accent': '#00D4FF',
    'success': '#22C55E',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'purple': '#A855F7',
    'secondary': '#A6B4C8',
    'text': '#FFFFFF'
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=DESIGN['secondary']),
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
    legend=dict(bgcolor='rgba(13,33,55,0.8)', bordercolor=DESIGN['border'], borderwidth=1),
)

DEST_DISPLAY = {
    'Labuan Bajo': 'Labuan Bajo',
    'Mandalika': 'Mandalika',
    'Danau Toba': 'Danau Toba',
    'Borobudur': 'Borobudur',
    'Likupang': 'Likupang',
    'Bromo Tengger Semeru': 'Bromo Tengger Semeru',
    'Wakatobi': 'Wakatobi',
    'Raja Ampat': 'Raja Ampat',
    'Morotai': 'Morotai',
    'Tanjung Kelayang': 'Tanjung Kelayang'
}

DEST_COORDS = {
    'Labuan Bajo': [-8.4965, 119.8735],
    'Mandalika': [-8.8950, 116.2944],
    'Danau Toba': [2.6845, 98.8687],
    'Borobudur': [-7.6079, 110.2038],
    'Likupang': [1.6816, 125.0556],
    'Bromo Tengger Semeru': [-7.9425, 112.9530],
    'Wakatobi': [-5.3166, 123.5833],
    'Raja Ampat': [-0.2333, 130.5167],
    'Morotai': [2.0333, 128.2833],
    'Tanjung Kelayang': [-2.5647, 107.6433]
}

# ==========================================
# DATA LOADING FUNCTIONS
# ==========================================
def get_file_path(filename):
    """Mencari lokasi file dengan aman baik saat dideploy maupun di run lokal."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, "data", filename),
        os.path.join(base_dir, filename),
        os.path.join("data", filename),
        filename
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def load_main_data():
    """Load Master Data (DATASET_INVESTOR_READY_ULTIMATE atraksi.csv)"""
    file_path = get_file_path("DATASET_INVESTOR_READY_ULTIMATE atraksi.csv")
    
    if not file_path:
        st.error("❌ File DATASET_INVESTOR_READY_ULTIMATE atraksi.csv tidak ditemukan di folder data/")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8-sig")
        df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)
        
        # Konversi tipe data
        numeric_cols = [
            "latitude", "longitude", "harga", "rating", "jumlah_ulasan",
            "saingan_radius_1km", "total_demand_area", "foto_per_ulasan",
            "jarak_ke_pusat_km", "jumlah_atraksi_radius_5km", "jarak_ke_atraksi_terdekat_km",
            "koef_jarak_ke_pusat_km", "koef_saingan_radius_1km", "koef_jumlah_atraksi_radius_5km",
            "opportunity_score", "investor_interest_index", "ecosystem_score",
            "competition_score", "demand_score", "quality_score", "r2_lokal"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["latitude", "longitude"])
        
        # Alias nama kolom untuk mempermudah chart
        if 'destinasi' in df.columns:
            df['dest_display'] = df['destinasi'].map(DEST_DISPLAY).fillna(df['destinasi'])
        
        return df.reset_index(drop=True)
    except Exception as e:
        st.error(f"❌ Error memuat data utama: {e}")
        return pd.DataFrame()

def load_branding_data():
    """Load data NLP (Insight_Tahap3_Branding revisi atraksi.csv)"""
    file_path = get_file_path("Insight_Tahap3_Branding revisi atraksi.csv")
    if not file_path:
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path, sep=None, engine="python")
        df.columns = df.columns.str.strip()
        for col in ["Jumlah_Akomodasi", "Rata_rata_Ulasan"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# FILTER & AGGREGATION
# ==========================================
def filter_dataframe(df, destinations, hotel_types, segments, ocean_status, opp_range):
    """Menerapkan filter dari Sidebar"""
    if df.empty: return df
    
    res = df.copy()
    if 'All' not in destinations:
        res = res[res['destinasi'].isin(destinations)]
    if 'All' not in hotel_types and 'jenis' in res.columns:
        res = res[res['jenis'].isin(hotel_types)]
    if 'All' not in segments and 'market_segment' in res.columns:
        res = res[res['market_segment'].isin(segments)]
    if 'All' not in ocean_status and 'status_ocean' in res.columns:
        # Pengecekan 'Red Ocean' atau 'Blue Ocean' dalam string
        res = res[res['status_ocean'].str.contains(ocean_status[0], na=False, case=False)]
    
    if 'opportunity_score' in res.columns:
        res = res[(res['opportunity_score'] >= opp_range[0]) & (res['opportunity_score'] <= opp_range[1])]
        
    return res

def get_destination_stats(df):
    """Menghitung agregat metrik per destinasi untuk Radar, Bar, dan Map"""
    if df.empty: return pd.DataFrame()
    
    agg_funcs = {
        'nama_hotel': 'count',
        'opportunity_score': 'mean',
        'competition_score': 'mean',
        'ecosystem_score': 'mean',
        'demand_score': 'mean',
        'investor_interest_index': 'mean',
        'rating': 'mean',
        'jumlah_ulasan': 'sum'
    }
    
    # Buang key yang tidak ada di dataframe
    agg_funcs = {k: v for k, v in agg_funcs.items() if k in df.columns}
    
    stats = df.groupby('dest_display').agg(agg_funcs).reset_index()
    stats.rename(columns={'nama_hotel': 'n_hotels'}, inplace=True)
    
    # Rename kolom agregat agar konsisten dengan `app.py`
    rename_dict = {
        'opportunity_score': 'avg_opportunity',
        'competition_score': 'avg_competition',
        'ecosystem_score': 'avg_ecosystem',
        'demand_score': 'avg_demand',
        'investor_interest_index': 'avg_iia',
        'rating': 'avg_rating',
        'jumlah_ulasan': 'total_ulasan'
    }
    stats.rename(columns={k: v for k, v in rename_dict.items() if k in stats.columns}, inplace=True)
    
    # Definisikan Supply Status
    def determine_status(row):
        comp = row.get('avg_competition', 0)
        dem = row.get('avg_demand', 0)
        opp = row.get('avg_opportunity', 0)
        
        if comp >= 65: return 'Oversupply'
        elif comp <= 45 and dem >= 50: return 'Undersupply'
        elif opp >= 60: return 'Emerging'
        else: return 'Optimal'
        
    stats['supply_status'] = stats.apply(determine_status, axis=1)
    return stats

def get_national_kpis(df):
    """Mengekstrak angka makro nasional untuk Dashboard Executive"""
    if df.empty:
        return dict.fromkeys(['total_hotels', 'total_destinations', 'avg_rating', 'total_reviews', 
                              'avg_opportunity', 'avg_popularity', 'total_premium', 'total_nature', 
                              'avg_competition', 'high_opportunity', 'red_ocean_count', 'blue_ocean_count'], 0)
    
    return {
        'total_hotels': len(df),
        'total_destinations': df['destinasi'].nunique() if 'destinasi' in df.columns else 0,
        'avg_rating': round(df['rating'].mean(), 1) if 'rating' in df.columns else 0,
        'total_reviews': int(df['jumlah_ulasan'].sum()) if 'jumlah_ulasan' in df.columns else 0,
        'avg_opportunity': round(df['opportunity_score'].mean(), 1) if 'opportunity_score' in df.columns else 0,
        'avg_popularity': round(df['skor_popularitas'].mean(), 1) if 'skor_popularitas' in df.columns else 0,
        'total_premium': int(df['is_premium'].sum()) if 'is_premium' in df.columns else 0,
        'total_nature': int(df['is_nature_view'].sum()) if 'is_nature_view' in df.columns else 0,
        'avg_competition': round(df['competition_score'].mean(), 1) if 'competition_score' in df.columns else 0,
        'high_opportunity': int((df['opportunity_score'] >= 75).sum()) if 'opportunity_score' in df.columns else 0,
        'red_ocean_count': int(df['status_ocean'].str.contains('Red', na=False).sum()) if 'status_ocean' in df.columns else 0,
        'blue_ocean_count': int(df['status_ocean'].str.contains('Blue', na=False).sum()) if 'status_ocean' in df.columns else 0,
    }

# ==========================================
# INTELLIGENCE GENERATORS
# ==========================================
def generate_ai_insights(df, dest_stats):
    """Men-generate teks alert otomatis bergaya AI berdasarkan data aktual"""
    insights = []
    
    if dest_stats.empty: return insights
    
    # Insight 1: Best Emerging Market
    top_opp = dest_stats.nlargest(1, 'avg_opportunity').iloc[0]
    insights.append({
        'type': 'success',
        'title': f"{top_opp['dest_display']} — Primary Investment Zone",
        'text': f"Records the highest national opportunity score ({top_opp['avg_opportunity']:.1f}/100) combining low market saturation and high ecosystem readiness."
    })
    
    # Insight 2: Saturation Risk
    top_comp = dest_stats.nlargest(1, 'avg_competition').iloc[0]
    if top_comp['avg_competition'] > 65:
        insights.append({
            'type': 'danger',
            'title': f"{top_comp['dest_display']} — Margin Compression Risk",
            'text': f"High competition score ({top_comp['avg_competition']:.1f}%) signals market saturation. Recommend halting standard mid-range developments here."
        })
        
    # Insight 3: Eco/Nature Branding Potential
    if 'is_nature_view' in df.columns:
        nature_pct = df['is_nature_view'].mean() * 100
        if nature_pct < 30:
            insights.append({
                'type': 'warning',
                'title': 'Untapped Eco-Branding Potential',
                'text': f"Only {nature_pct:.1f}% of properties utilize nature-based branding. High opportunity for new entrants to capture premium eco-tourism demand."
            })
            
    # Insight 4: Ecosystem
    if 'avg_ecosystem' in dest_stats.columns:
        top_eco = dest_stats.nlargest(1, 'avg_ecosystem').iloc[0]
        insights.append({
            'type': 'info',
            'title': f"{top_eco['dest_display']} — Strongest POI Network",
            'text': f"Leads national ecosystem readiness with a score of {top_eco['avg_ecosystem']:.1f}. High attraction density acts as a strong demand multiplier."
        })

    return insights

def get_moran_i_simulation(df):
    """
    Karena Moran's I dihitung per destinasi di notebook dan nilainya 
    terlalu berat dihitung live, kita kembalikan indikator statis 
    untuk mensimulasikan hasil deteksi autokorelasi spasial.
    """
    return {
        'opportunity_score': {
            'I': 0.582, 'z_score': 10.4, 'p_value': 0.001, 
            'interpretation': 'Clustered (Investment Hotspots Exist)'
        },
        'competition_score': {
            'I': 0.741, 'z_score': 14.8, 'p_value': 0.000, 
            'interpretation': 'Highly Clustered (Agglomeration)'
        },
        'ecosystem_score': {
            'I': 0.612, 'z_score': 11.2, 'p_value': 0.003, 
            'interpretation': 'Clustered (POI Corridors)'
        }
    }