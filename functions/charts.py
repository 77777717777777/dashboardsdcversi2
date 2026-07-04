import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from .analytics import DESIGN, PLOTLY_LAYOUT

# ==========================================
# HELPER: APPLY PREMIUM LAYOUT
# ==========================================
def apply_layout(fig, title='', height=300, show_legend=True):
    """Menerapkan tema dark navy & cyan neon ke setiap grafik Plotly"""
    layout = PLOTLY_LAYOUT.copy()
    layout['height'] = height
    if title:
        layout['title'] = dict(text=title, font=dict(color=DESIGN['text'], size=14, family='Inter'))
    layout['showlegend'] = show_legend
    
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor='rgba(15,42,74,0.07)', zerolinecolor='rgba(15,42,74,0.1)')
    fig.update_yaxes(gridcolor='rgba(15,42,74,0.07)', zerolinecolor='rgba(15,42,74,0.1)')
    return fig

# ==========================================
# 1. EXECUTIVE & RANKING CHARTS
# ==========================================
def plot_national_heatmap(dest_stats, metric, title):
    """Horizontal Bar Chart yang diwarnai seperti Heatmap"""
    if dest_stats.empty or metric not in dest_stats.columns: return go.Figure()
    
    df = dest_stats.sort_values(metric, ascending=True)
    colorscale = [[0, DESIGN['danger']], [0.5, DESIGN['warning']], [1, DESIGN['success']]] if metric != 'avg_competition' else [[0, DESIGN['success']], [0.5, DESIGN['warning']], [1, DESIGN['danger']]]
    
    fig = go.Figure(go.Bar(
        x=df[metric],
        y=df['dest_display'],
        orientation='h',
        marker=dict(
            color=df[metric],
            colorscale=colorscale,
            line=dict(width=1, color='rgba(0,0,0,0.5)')
        ),
        text=df[metric].round(1),
        textposition='outside',
        cliponaxis=False,
        textfont=dict(color=DESIGN['text'], size=11),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))
    return apply_layout(fig, title=title, height=280, show_legend=False)
    fig.update_xaxes(range=[0, df[metric].max() * 1.2])
    fig.update_layout(margin=dict(l=10, r=70, t=20, b=30))

def plot_opportunity_ranking(dest_stats, column, title, height=320):
    """Horizontal Bar khusus untuk Ranking"""
    if dest_stats.empty or column not in dest_stats.columns: return go.Figure()
    
    df = dest_stats.sort_values(column, ascending=True)
    color = DESIGN['danger'] if 'competition' in column.lower() else DESIGN['accent']
    
    fig = go.Figure(go.Bar(
        x=df[column], y=df['dest_display'], orientation='h',
        marker_color=color, opacity=0.85,
        text=df[column].round(1), textposition='outside',
        cliponaxis=False,
        textfont=dict(color='#4A6080', size=10)
    ))
    return apply_layout(fig, title='', height=height, show_legend=False)
    fig.update_xaxes(range=[0, df[column].max() * 1.2])
    fig.update_layout(margin=dict(l=10, r=60, t=20, b=40))
    
def plot_donut(labels, values, colors=None, height=320):
    if not colors:
        colors = [DESIGN['accent'], DESIGN['success'], DESIGN['danger'],
                  DESIGN['warning'], DESIGN['purple'], '#3B82F6', '#F43F5E', '#10B981']
    
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.60,
        marker=dict(colors=colors, line=dict(color=DESIGN['bg'], width=2)),
        textinfo='percent',
        textfont=dict(color=DESIGN['text'], size=9),
        hoverinfo='label+value+percent',
        textposition='inside',
        automargin=True,
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        margin=dict(l=10, r=10, t=10, b=80),
        legend=dict(
            font=dict(color=DESIGN['secondary'], size=9),
            bgcolor='rgba(0,0,0,0)',
            orientation='v',
            yanchor='top',
            y=-0.05,
            xanchor='center',
            x=0.5,
            itemsizing='constant',
            itemwidth=30
        )
    )
    return fig

# ==========================================
# 2. QUADRANTS & MATRICES (SCATTER)
# ==========================================
def plot_competition_demand_quadrant(dest_stats, height=320):
    if dest_stats.empty or 'avg_competition' not in dest_stats.columns or 'avg_demand' not in dest_stats.columns:
        return go.Figure()
        
    med_comp = dest_stats['avg_competition'].median()
    med_dem  = dest_stats['avg_demand'].median()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dest_stats['avg_competition'],
        y=dest_stats['avg_demand'],
        mode='markers',
        marker=dict(
            size=16,
            color=dest_stats['avg_opportunity'] if 'avg_opportunity' in dest_stats.columns else '#00D4FF',
            colorscale='viridis', showscale=False,
            line=dict(color=DESIGN['text'], width=1)
        ),
        text=dest_stats['dest_display'],
        textposition=['top center' if i % 2 == 0 else 'bottom center' for i in range(len(dest_stats))],
        textfont=dict(color=DESIGN['secondary'], size=9),
        hovertemplate='<b>%{text}</b><br>Persaingan: %{x:.1f}<br>Permintaan: %{y:.1f}<extra></extra>'
    ))
    
    fig.add_vline(x=med_comp, line=dict(color='rgba(0,0,0,0.15)', dash='dot', width=1))
    fig.add_hline(y=med_dem,  line=dict(color='rgba(0,0,0,0.15)', dash='dot', width=1))
    
    fig.add_annotation(x=med_comp*0.5, y=dest_stats['avg_demand'].max()*0.95,
                       text="Peluang Utama", showarrow=False,
                       font=dict(color=DESIGN['success'], size=9, family='Inter'))
    fig.add_annotation(x=dest_stats['avg_competition'].max()*0.85, y=dest_stats['avg_demand'].max()*0.95,
                       text="Pasar Jenuh", showarrow=False,
                       font=dict(color=DESIGN['danger'], size=9, family='Inter'))
    
    fig = apply_layout(fig, height=height, show_legend=False)
    fig.update_xaxes(title="Skor Persaingan", title_font=dict(size=10))
    fig.update_yaxes(title="Skor Permintaan", title_font=dict(size=10))
    
    # Tambah padding sumbu agar label tidak terpotong
    x_pad = dest_stats['avg_competition'].max() * 0.15
    y_pad = dest_stats['avg_demand'].max() * 0.15
    fig.update_xaxes(range=[dest_stats['avg_competition'].min() - x_pad,
                             dest_stats['avg_competition'].max() + x_pad])
    fig.update_yaxes(range=[dest_stats['avg_demand'].min() - y_pad,
                             dest_stats['avg_demand'].max() + y_pad])
    return fig

def plot_investment_matrix(dest_stats):
    """Matrix: Competition vs Opportunity"""
    if dest_stats.empty or 'avg_competition' not in dest_stats.columns or 'avg_opportunity' not in dest_stats.columns: return go.Figure()
    
    fig = go.Figure(go.Scatter(
        x=dest_stats['avg_competition'], y=dest_stats['avg_opportunity'],
        mode='markers+text',
        marker=dict(size=16, color=DESIGN['accent'], opacity=0.8, line=dict(color='white', width=1)),
        text=dest_stats['dest_display'], textposition='bottom center', textfont=dict(color=DESIGN['secondary'], size=10)
    ))
    fig.add_vline(x=dest_stats['avg_competition'].median(), line=dict(color='rgba(255,255,255,0.2)', dash='dot'))
    fig.add_hline(y=dest_stats['avg_opportunity'].median(), line=dict(color='rgba(255,255,255,0.2)', dash='dot'))
    
    fig = apply_layout(fig, height=320, show_legend=False)
    fig.update_xaxes(title="Competition Level (Risk)")
    fig.update_yaxes(title="Opportunity Score (Reward)")
    return fig

# ==========================================
# 3. SPATIAL ECONOMETRICS (GWR & MORAN)
# ==========================================
def plot_gwr_coefficients(df, coef_col, title, height=300):
    """Boxplot distribusi GWR untuk membuktikan Spasial Heterogenitas"""
    if df.empty or coef_col not in df.columns: return go.Figure()
    
    valid_df = df.dropna(subset=[coef_col, 'dest_display'])
    # Urutkan berdasarkan median koefisien
    order = valid_df.groupby('dest_display')[coef_col].median().sort_values().index
    
    fig = go.Figure()
    for dest in order:
        sub = valid_df[valid_df['dest_display'] == dest]
        fig.add_trace(go.Box(
            x=sub[coef_col], y=sub['dest_display'], orientation='h',
            name=dest, marker_color=DESIGN['accent'], line_color=DESIGN['accent'],
            boxmean=True, hoverinfo='x+name'
        ))
    
    fig.add_vline(x=0, line=dict(color=DESIGN['danger'], width=2, dash='dash'))
    fig = apply_layout(fig, height=height, show_legend=False)
    fig.update_xaxes(title="Coefficient Value")
    return fig
    fig.update_xaxes(tickfont=dict(color=DESIGN['secondary']))
    fig.update_yaxes(tickfont=dict(color=DESIGN['secondary']))

def plot_morans_result(I, z_score, p_value, label):
    """
    Diverging Bullet Chart untuk Moran's I.
    Skala -1 (Tersebar) → 0 (Acak) → +1 (Mengelompok)
    """
    is_sig = p_value < 0.05

    # Interpretasi otomatis
    if I >= 0.5:
        interp_text = "Sangat Mengelompok"
        bar_color   = '#1A7A4A'
    elif I >= 0.2:
        interp_text = "Cukup Mengelompok"
        bar_color   = '#1D5FAD'
    elif I >= 0:
        interp_text = "Pola Lemah"
        bar_color   = '#C47B00'
    elif I >= -0.2:
        interp_text = "Sedikit Tersebar"
        bar_color   = '#C47B00'
    else:
        interp_text = "Tersebar Merata"
        bar_color   = '#C0392B'

    sig_text  = "" if is_sig else "⚠️ Belum Signifikan"
    sig_color = '#1A7A4A' if is_sig else '#C47B00'

    fig = go.Figure()

    # ── Track background abu-abu (-1 sampai +1) ──────────────────
    fig.add_shape(
        type='rect',
        x0=-1, x1=1,
        y0=-0.18, y1=0.18,
        fillcolor='#E8EFF7',
        line=dict(width=0),
        layer='below',
    )

    # ── Zone referensi tengah (zona acak: -0.1 sampai 0.1) ────────
    fig.add_shape(
        type='rect',
        x0=-0.1, x1=0.1,
        y0=-0.18, y1=0.18,
        fillcolor='#D0DCF0',
        line=dict(width=0),
        layer='below',
    )

    # ── Bar nilai Moran's I (dari 0 ke nilai I) ───────────────────
    fig.add_shape(
        type='rect',
        x0=0, x1=I,
        y0=-0.14, y1=0.14,
        fillcolor=bar_color,
        line=dict(width=0),
        layer='above',
    )

    # ── Garis tengah (zero line) ──────────────────────────────────
    fig.add_shape(
        type='line',
        x0=0, x1=0,
        y0=-0.22, y1=0.22,
        line=dict(color='#4A6080', width=2),
    )

    # ── Marker titik nilai I ──────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[I], y=[0],
        mode='markers',
        marker=dict(
            symbol='diamond',
            size=12,
            color='white',
            line=dict(color=bar_color, width=2.5),
        ),
        showlegend=False,
        hovertemplate=f"Moran's I = {I:.3f}<extra></extra>",
    ))

    # ── Annotation nilai I di atas bar ────────────────────────────
    fig.add_annotation(
        x=I, y=0.32,
        text=f"<b>{I:.3f}</b>",
        showarrow=False,
        font=dict(size=13, color=bar_color, family='Plus Jakarta Sans'),
        xanchor='center',
    )

    # ── Label skala ───────────────────────────────────────────────
    for xpos, txt, anchor in [
        (-1.0, '−1<br><span style="font-size:8px">Tersebar</span>',  'left'),
        ( 0.0, '0<br><span style="font-size:8px">Acak</span>',       'center'),
        ( 1.0, '+1<br><span style="font-size:8px">Mengelompok</span>', 'right'),
    ]:
        fig.add_annotation(
            x=xpos, y=-0.38,
            text=txt,
            showarrow=False,
            font=dict(size=9, color='#8A9BB0'),
            xanchor=anchor,
            align=anchor,
        )

    # ── Label interpretasi & signifikansi ─────────────────────────
    fig.add_annotation(
        x=0, y=0.58,
        text=f"<b style='color:#0F2A4A'>{interp_text}</b>"
             f"  <span style='color:{sig_color};font-size:9px'>{sig_text}</span>",
        showarrow=False,
        font=dict(size=10, color='#0F2A4A'),
        xanchor='center',
    )

    # ── Tick marks -1, -0.5, 0, 0.5, +1 ─────────────────────────
    for xt in [-1, -0.5, 0, 0.5, 1]:
        fig.add_shape(
            type='line',
            x0=xt, x1=xt,
            y0=-0.18, y1=-0.23,
            line=dict(color='#8A9BB0', width=1),
        )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=160,
        margin=dict(l=20, r=20, t=40, b=40),
        xaxis=dict(
            range=[-1.15, 1.15],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[-0.6, 0.75],
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            fixedrange=True,
        ),
        font=dict(color='#4A6080', family='DM Sans', size=10),
    )

    return fig

# ==========================================
# 4. MULTI-METRIC & COMPARISON
# ==========================================
def plot_multi_radar(dest_stats, metrics):
    if dest_stats.empty or len(metrics) < 3: return go.Figure()
    
    top_2 = dest_stats.nlargest(2, 'avg_opportunity')
    bot_2 = dest_stats.nsmallest(2, 'avg_opportunity')
    compare_df = pd.concat([top_2, bot_2])
    
    # Terjemahan label metrik
    label_id = {
        'avg_opportunity': 'Peluang',
        'avg_competition': 'Persaingan',
        'avg_ecosystem':   'Ekosistem',
        'avg_demand':      'Permintaan',
        'avg_iia':         'Indeks Investor',
    }
    
    colors = [DESIGN['success'], DESIGN['accent'], DESIGN['warning'], DESIGN['danger']]
    fig = go.Figure()
    
    for i, (_, row) in enumerate(compare_df.iterrows()):
        vals = [row[m] for m in metrics]
        vals.append(vals[0])
        lbls = [label_id.get(m, m.replace('avg_','').title()) for m in metrics]
        lbls.append(lbls[0])
        
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=lbls, fill='toself',
            name=row['dest_display'],
            line_color=colors[i % len(colors)],
            fillcolor=f'rgba(0,0,0,0.05)'
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor='rgba(0,0,0,0.1)',
                tickfont=dict(color='#4A6080', size=9)
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.1)',
                tickfont=dict(color='#0F2A4A', size=11, family='Inter')
            )
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#0F2A4A', family='Inter'),
        margin=dict(l=50, r=50, t=40, b=60),
        height=340,
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.2,
            xanchor='center', x=0.5,
            font=dict(size=10, color='#0F2A4A')
        )
    )
    return fig

def plot_grouped_bar(df, x_col, y_cols, labels, colors, height=300):
    """Bar chart berkelompok untuk komparasi multi-metrik"""
    fig = go.Figure()
    for y_col, label, color in zip(y_cols, labels, colors):
        fig.add_trace(go.Bar(
            x=df[x_col], y=df[y_col], name=label, marker_color=color, opacity=0.9
        ))
    
    fig.update_layout(barmode='group')
    return apply_layout(fig, height=height, show_legend=True)

def plot_branding_bars(branding_df, dest_filter=None):
    if branding_df.empty: return go.Figure()
    
    df = branding_df.copy()
    if dest_filter and dest_filter != 'All':
        df = df[df['destinasi'] == dest_filter]
        
    grp = df.groupby(['Segmen', 'Tema_Nama']).agg(
        Median_Popularitas=('Median_Popularitas', 'mean'),
        Median_Ulasan=('Median_Ulasan', 'mean'),
    ).reset_index()
    
    fig = go.Figure()
    colors = {'Mengandung Unsur Alam': DESIGN['success'], 'Nama Standar': DESIGN['accent']}
    
    for tema in ['Nama Standar', 'Mengandung Unsur Alam']:
        sub = grp[grp['Tema_Nama'] == tema]
        fig.add_trace(go.Bar(
            name='Nature Branding' if 'Alam' in tema else 'Standard Naming',
            x=sub['Segmen'].apply(lambda x: x.split('(')[0].strip()),
            y=sub['Median_Popularitas'],
            marker_color=colors.get(tema, DESIGN['secondary']),
            text=sub['Median_Ulasan'].round(0).astype(int),
            textposition='outside', textfont=dict(color='#4A6080', size=11)
        ))
        
    fig.update_layout(barmode='group')
    fig = apply_layout(fig, height=280)
    fig.update_yaxes(title='Median Skor Popularitas')
    return fig

# ==========================================
# 5. COMPETITION PAGE — ENHANCED CHARTS
# ==========================================

def plot_competition_ranking(dest_stats, height=320):
    """
    Horizontal bar dengan gradient warna merah-kuning-hijau
    berdasarkan intensitas persaingan.
    """
    if dest_stats.empty or 'avg_competition' not in dest_stats.columns:
        return go.Figure()

    df = dest_stats.sort_values('avg_competition', ascending=True).copy()

    # Warna gradient per bar: merah (tinggi) → hijau (rendah)
    norm = (df['avg_competition'] - df['avg_competition'].min()) / (
        df['avg_competition'].max() - df['avg_competition'].min() + 1e-9
    )
    colors = [
        f"rgb({int(192*n + 26*(1-n))}, {int(57*n + 122*(1-n))}, {int(43*n + 74*(1-n))})"
        for n in norm
    ]

    fig = go.Figure(go.Bar(
        x=df['avg_competition'],
        y=df['dest_display'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=df['avg_competition'].round(1).astype(str) + '%',
        textposition='outside',
        textfont=dict(color='#4A6080', size=10, family='DM Sans'),
        hovertemplate='<b>%{y}</b><br>Tingkat Persaingan: %{x:.1f}%<extra></extra>',
        cliponaxis=False,
    ))

    fig = apply_layout(fig, height=height, show_legend=False)
    fig.update_xaxes(
        title='Skor Persaingan (%)',
        title_font=dict(size=10, color='#4A6080'),
        range=[0, df['avg_competition'].max() * 1.18],
    )
    fig.update_yaxes(title='')
    fig.update_layout(margin=dict(l=10, r=60, t=3, b=20))
    return fig


def plot_investment_matrix_enhanced(dest_stats, height=320):
    """
    Scatter plot Risiko vs Peluang dengan:
    - ukuran marker = jumlah hotel
    - warna = skor peluang
    - garis kuadran + label kuadran
    - anotasi nama destinasi
    """
    if dest_stats.empty:
        return go.Figure()

    required = ['avg_competition', 'avg_opportunity']
    if not all(c in dest_stats.columns for c in required):
        return go.Figure()

    df = dest_stats.copy()
    med_comp = df['avg_competition'].median()
    med_opp  = df['avg_opportunity'].median()

    # Ukuran marker proporsional ke jumlah hotel
    size_col = df['n_hotels'] if 'n_hotels' in df.columns else pd.Series([20]*len(df))
    size_norm = ((size_col - size_col.min()) / (size_col.max() - size_col.min() + 1) * 28 + 12)

    fig = go.Figure()

    # Shading kuadran
    x_max = df['avg_competition'].max() * 1.15
    y_max = df['avg_opportunity'].max() * 1.15

    quadrant_shades = [
        # (x0, y0, x1, y1, warna, label, posisi label)
        (0,       med_opp, med_comp, y_max,  'rgba(26,122,74,0.06)',  'Prioritas Utama',   med_comp*0.5,        y_max*0.94),
        (med_comp,med_opp, x_max,   y_max,  'rgba(196,123,0,0.05)',  'High Risk/High Return', x_max*0.78,      y_max*0.94),
        (0,       0,       med_comp, med_opp,'rgba(74,96,128,0.05)', 'Pasar Stagnan',      med_comp*0.5,        y_max*0.06),
        (med_comp,0,       x_max,   med_opp,'rgba(192,57,43,0.06)',  'Hindari',            x_max*0.78,          y_max*0.06),
    ]

    for x0, y0, x1, y1, fill, label, lx, ly in quadrant_shades:
        fig.add_shape(type='rect', x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=fill, line=dict(width=0), layer='below')
        fig.add_annotation(x=lx, y=ly, text=label, showarrow=False,
                           font=dict(size=9, color='#8A9BB0', family='DM Sans'),
                           xanchor='center')

    # Garis median
    fig.add_vline(x=med_comp, line=dict(color='#B0C8E0', dash='dot', width=1))
    fig.add_hline(y=med_opp,  line=dict(color='#B0C8E0', dash='dot', width=1))

    # Scatter utama
    fig.add_trace(go.Scatter(
        x=df['avg_competition'],
        y=df['avg_opportunity'],
        mode='markers+text',
        marker=dict(
            size=size_norm,
            color=df['avg_opportunity'],
            colorscale=[
                [0.0, '#C0392B'],
                [0.5, '#C47B00'],
                [1.0, '#1A7A4A'],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text='Skor Peluang', font=dict(size=9, color='#4A6080')),
                tickfont=dict(size=8, color='#4A6080'),
                thickness=10,
                len=0.7,
            ),
            line=dict(color='white', width=1.5),
            opacity=0.9,
        ),
        text=df['dest_display'],
        textposition='top center',
        textfont=dict(color='#0F2A4A', size=9, family='DM Sans'),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Persaingan: %{x:.1f}%<br>'
            'Peluang: %{y:.1f}<br>'
            '<extra></extra>'
        ),
        cliponaxis=False,
    ))

    fig = apply_layout(fig, height=height, show_legend=False)
    fig.update_xaxes(
        title='Tingkat Persaingan (Risiko)',
        title_font=dict(size=10, color='#4A6080'),
        range=[0, x_max],
    )
    fig.update_yaxes(
        title='Skor Peluang (Imbal Hasil)',
        title_font=dict(size=10, color='#4A6080'),
        range=[0, y_max],
    )
    fig.update_layout(margin=dict(l=10, r=80, t=20, b=40))
    return fig


def plot_gwr_bar(df, height=320):
    """
    Horizontal bar koefisien kompetitor per destinasi.
    Warna dibedakan berdasarkan jenis model (GWR vs OLS/Spatial Lag)
    supaya tidak menyiratkan semua destinasi diestimasi secara spasial lokal.
    """
    if 'koef_saingan_radius_1km' not in df.columns:
        return go.Figure()

    coef_d = (
        df.groupby('dest_display')
        .agg(
            Koefisien=('koef_saingan_radius_1km', 'mean'),
            model=('model_dipakai', 'first'),
        )
        .reset_index()
        .sort_values('Koefisien')
    )

    # Warna: hijau/merah tua = GWR asli (lokal), hijau/merah muda = OLS/Spatial Lag (global)
    def get_color(row):
        is_local = 'GWR' in str(row['model'])
        if row['Koefisien'] >= 0:
            return '#1A7A4A' if is_local else '#86C9A5'   # hijau tua vs hijau muda
        else:
            return '#C0392B' if is_local else '#E8A0A0'   # merah tua vs merah muda

    colors = coef_d.apply(get_color, axis=1)

    fig = go.Figure(go.Bar(
        x=coef_d['Koefisien'],
        y=coef_d['dest_display'],
        orientation='h',
        marker=dict(color=colors, opacity=0.9, line=dict(width=0)),
        text=[f"{v:.3f}" for v in coef_d['Koefisien']],
        textposition='outside',
        textfont=dict(color='#4A6080', size=10, family='DM Sans'),
        customdata=coef_d['model'],
        hovertemplate='<b>%{y}</b><br>Koefisien: %{x:.4f}<br>Model: %{customdata}<extra></extra>',
        cliponaxis=False,
    ))

    fig.add_vline(x=0, line=dict(color='#B0C8E0', width=1.5, dash='solid'))

    x_range = coef_d['Koefisien'].abs().max()
    fig.add_annotation(
        x=x_range * 0.6, y=len(coef_d) - 0.3,
        text='Aglomerasi Positif', showarrow=False,
        font=dict(size=8, color='#1A7A4A', family='DM Sans'),
    )
    fig.add_annotation(
        x=-x_range * 0.6, y=len(coef_d) - 0.3,
        text='Kompetisi Destruktif', showarrow=False,
        font=dict(size=8, color='#C0392B', family='DM Sans'),
    )

    fig = apply_layout(fig, height=height, show_legend=False)
    fig.update_xaxes(
        title='Nilai Koefisien',
        title_font=dict(size=10, color='#4A6080'),
        range=[-x_range * 1.3, x_range * 1.3],
    )
    fig.update_yaxes(title='')
    fig.update_layout(margin=dict(l=10, r=70, t=20, b=40))
    return fig

# Dummy stubs if needed by other components
def plot_bubble(*args, **kwargs): return go.Figure()
def plot_heatmap_matrix(*args, **kwargs): return go.Figure()