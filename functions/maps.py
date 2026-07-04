import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np

# ==========================================
# TITIK NOL ORGANIK PARIWISATA
# ==========================================
DEST_COORDS = {
    'Labuan Bajo': {'lat': -8.4945, 'lon': 119.8747},
    'Likupang': {'lat': 1.6825, 'lon': 125.1470},
    'Mandalika': {'lat': -8.8937, 'lon': 116.2827},
    'Borobudur': {'lat': -7.6079, 'lon': 110.2038},
    'Danau Toba': {'lat': 2.6594, 'lon': 98.9346},
    'Bromo Tengger Semeru': {'lat': -7.9425, 'lon': 112.9530},
    'Wakatobi': {'lat': -5.3387, 'lon': 123.5339},
    'Tanjung Kelayang': {'lat': -2.5604, 'lon': 107.6724},
    'Morotai': {'lat': 2.0496, 'lon': 128.2891},
    'Raja Ampat': {'lat': -0.4317, 'lon': 130.8050},
}

# ==========================================
# HELPER: POPUP HTML GENERATOR
# ==========================================
def create_popup_html(row):
    """Membangun tooltip popup hotel — konsisten dengan tema dashboard (hijau navy)"""
    name = row.get('nama_hotel', 'Unknown Hotel')
    tipe = row.get('jenis', 'Akomodasi')
    rating = row.get('rating', 0)
    ulasan = row.get('jumlah_ulasan', 0)
    
    opp = row.get('opportunity_score', 0)
    ocean = row.get('status_ocean', 'Unknown')
    rec = str(row.get('rekomendasi_investasi', 'Perlu Kajian'))
    
    atraksi = row.get('nama_atraksi_terdekat', 'Tidak diketahui')
    jarak_atr = row.get('jarak_ke_atraksi_terdekat_km', 0)
    eco_score = row.get('ecosystem_score', 0)
    
    # Palet warna konsisten dengan dashboard
    rec_color = "#1A7A4A" if "Sangat" in rec else "#1D5FAD" if "Direkomendasikan" in rec else "#B8680A"
    ocean_color = "#C0392B" if "Red" in ocean else "#1D5FAD"
    opp_color = "#1A7A4A" if opp >= 60 else "#B8680A" if opp >= 40 else "#C0392B"
    
    html = f"""
    <div style="font-family:'DM Sans', sans-serif; width: 270px; color: #1B4332;">
        <div style="background: linear-gradient(135deg,#1B4332,#2D6A4F); padding: 14px 16px; border-radius: 10px 10px 0 0; color: white;">
            <h4 style="margin:0 0 3px 0; font-size:14px; font-weight:700; color: #FFFFFF; font-family:'Plus Jakarta Sans',sans-serif;">{name}</h4>
            <div style="font-size:11px; color:rgba(255,255,255,0.75);">{tipe} · ⭐ {rating} ({ulasan:,.0f} ulasan)</div>
        </div>
        <div style="padding: 14px 16px; background: #FFFFFF; border-radius: 0 0 10px 10px; border:1px solid #D8EDE4; border-top:none;">
            <div style="margin-bottom: 10px;">
                <span style="font-size:9px; color:#74A98A; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;">Investment Score</span><br>
                <b style="font-size:20px; color:{opp_color}; font-family:'Plus Jakarta Sans',sans-serif;">{opp:.1f}</b>
                <span style="background:{rec_color}; color:white; padding:2px 8px; border-radius:20px; font-size:9px; font-weight:700; margin-left:6px;">{rec}</span>
            </div>
            <div style="margin-bottom: 10px;">
                <span style="font-size:9px; color:#74A98A; font-weight:600; letter-spacing:0.5px; text-transform:uppercase;">Market Status</span><br>
                <b style="font-size:13px; color:{ocean_color};">{ocean}</b>
            </div>
            <hr style="border:0; border-top:1px solid #D8EDE4; margin: 10px 0;">
            <div style="font-size:11px; color:#2D6A4F; line-height:1.6;">
                <span style="color:#74A98A; font-weight:600;">Atraksi Terdekat:</span><br>
                <b style="color:#1B4332;">{atraksi}</b> ({jarak_atr:.1f} km)<br>
                <span style="color:#74A98A;">Ecosystem Score:</span> <b style="color:#1B4332;">{eco_score:.1f}</b>
            </div>
        </div>
    </div>
    """
    return html

# ==========================================
# MAIN MAP RENDERER (TAB 2)
# ==========================================
def render_main_map(df, layer_id='opportunity'):
    center_lat, center_lon = -2.5, 118.0
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles='OpenStreetMap')
    
    if df.empty: return m
    valid_df = df.dropna(subset=['latitude', 'longitude'])

    # Tema Gradien Neon (Cyan -> Green -> Orange -> Red)
    custom_gradient = {
        0.2: 'rgba(0, 212, 255, 0.8)',   # Cyan
        0.5: 'rgba(34, 197, 94, 0.9)',   # Green
        0.8: 'rgba(245, 158, 11, 0.9)',  # Orange
        1.0: 'rgba(239, 68, 68, 1)'      # Red
    }

    if layer_id in ['opportunity', 'supply', 'competition']:
        # Pilih bobot (weight) berdasarkan layer
        if layer_id == 'opportunity':
            weight_col = 'opportunity_score'
            gradient = custom_gradient
        elif layer_id == 'supply':
            weight_col = 'jumlah_ulasan'
            gradient = {0.2: '#00D4FF', 0.6: '#22C55E', 1.0: '#EF4444'}
        else: # competition
            weight_col = 'competition_score'
            gradient = {0.2: '#22C55E', 0.6: '#F59E0B', 1.0: '#EF4444'} # Dibalik, merah = kompetisi tinggi

        # 1. BUAT EFEK GLOWING HEATMAP
        heat_data = [[row['latitude'], row['longitude'], row.get(weight_col, 1)] for _, row in valid_df.iterrows()]
        HeatMap(heat_data, radius=22, blur=18, max_zoom=10, gradient=gradient).add_to(m)

        # 2. TAMBAHKAN TITIK KECIL AGAR BISA DI-KLIK JURI
        for _, row in valid_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=3, # Titik kecil saja
                color='rgba(255,255,255,0.4)',
                weight=1,
                fill=True,
                fill_color='white',
                fill_opacity=0.1,
                popup=folium.Popup(create_popup_html(row), max_width=300)
            ).add_to(m)

    else:
        # Layer berbasis titik (Ocean, Atraksi, Premium)
        for _, row in valid_df.iterrows():
            if layer_id == 'ocean':
                ocean = row.get('status_ocean', '')
                color = '#EF4444' if 'Red' in ocean else '#00D4FF' if 'Blue' in ocean else '#A6B4C8'
            elif layer_id == 'premium':
                color = '#A855F7' if row.get('is_premium', 0) == 1 else '#64748B'
            elif layer_id == 'attraction':
                eco = row.get('ecosystem_score', 0)
                color = '#22C55E' if eco >= 70 else '#00D4FF' if eco >= 40 else '#F43F5E'
            else:
                color = '#00D4FF'

            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                weight=1,
                popup=folium.Popup(create_popup_html(row), max_width=300)
            ).add_to(m)

    return m

# ==========================================
# DESTINATION DEEP DIVE MAP
# ==========================================
def render_destination_map(df, selected_dest):
    if selected_dest in DEST_COORDS:
        center_lat = DEST_COORDS[selected_dest]['lat']
        center_lon = DEST_COORDS[selected_dest]['lon']
    else:
        center_lat = df['latitude'].mean() if not df.empty else -2.5
        center_lon = df['longitude'].mean() if not df.empty else 118.0
        
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='CartoDB Voyager')
    
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>Pusat Wisata: {selected_dest}</b>",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    if df.empty: return m

    # Tampilkan Heatmap Lokal
    heat_data = [[row['latitude'], row['longitude'], row.get('opportunity_score', 50)] for _, row in df.dropna(subset=['latitude', 'longitude']).iterrows()]
    custom_gradient = {0.2: 'rgba(0, 212, 255, 0.8)', 0.5: 'rgba(34, 197, 94, 0.9)', 0.8: 'rgba(245, 158, 11, 0.9)', 1.0: 'rgba(239, 68, 68, 1)'}
    HeatMap(heat_data, radius=20, blur=15, max_zoom=14, gradient=custom_gradient).add_to(m)

    # Marker klik lokal
    for _, row in df.dropna(subset=['latitude', 'longitude']).iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=4,
            color='rgba(255,255,255,0.6)',
            weight=1,
            fill=True,
            fill_color='white',
            fill_opacity=0.2,
            popup=folium.Popup(create_popup_html(row), max_width=300)
        ).add_to(m)

    return m