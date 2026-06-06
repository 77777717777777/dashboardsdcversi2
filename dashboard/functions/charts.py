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
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)')
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
        textfont=dict(color=DESIGN['text'], size=11),
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))
    return apply_layout(fig, title=title, height=280, show_legend=False)

def plot_opportunity_ranking(dest_stats, column, title):
    """Horizontal Bar khusus untuk Ranking"""
    if dest_stats.empty or column not in dest_stats.columns: return go.Figure()
    
    df = dest_stats.sort_values(column, ascending=True)
    color = DESIGN['danger'] if 'competition' in column.lower() else DESIGN['accent']
    
    fig = go.Figure(go.Bar(
        x=df[column], y=df['dest_display'], orientation='h',
        marker_color=color, opacity=0.85,
        text=df[column].round(1), textposition='outside',
        textfont=dict(color=DESIGN['secondary'], size=10)
    ))
    return apply_layout(fig, title='', height=280, show_legend=False)

def plot_donut(labels, values, colors=None):
    """Donut chart premium"""
    if not colors:
        colors = [DESIGN['accent'], DESIGN['success'], DESIGN['danger'], DESIGN['warning'], DESIGN['purple'], '#3B82F6', '#F43F5E', '#10B981']
    
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color=DESIGN['bg'], width=2)),
        textinfo='percent', textfont=dict(color=DESIGN['text'], size=11),
        hoverinfo='label+value+percent'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=20, b=20),
        legend=dict(font=dict(color=DESIGN['secondary'], size=10), bgcolor='rgba(0,0,0,0)')
    )
    return fig

# ==========================================
# 2. QUADRANTS & MATRICES (SCATTER)
# ==========================================
def plot_competition_demand_quadrant(dest_stats):
    """Kuadran Bisnis: X=Competition, Y=Demand"""
    if dest_stats.empty or 'avg_competition' not in dest_stats.columns or 'avg_demand' not in dest_stats.columns:
        return go.Figure()
        
    med_comp = dest_stats['avg_competition'].median()
    med_dem = dest_stats['avg_demand'].median()
    
    fig = go.Figure()
    
    # Tambahkan titik destinasi
    fig.add_trace(go.Scatter(
        x=dest_stats['avg_competition'], y=dest_stats['avg_demand'],
        mode='markers+text',
        marker=dict(
            size=14,
            color=dest_stats['avg_opportunity'] if 'avg_opportunity' in dest_stats.columns else '#00D4FF',
            colorscale='viridis', showscale=False,
            line=dict(color=DESIGN['text'], width=1)
        ),
        text=dest_stats['dest_display'],
        textposition='top center',
        textfont=dict(color=DESIGN['secondary'], size=10),
        hovertemplate='<b>%{text}</b><br>Comp: %{x:.1f}<br>Demand: %{y:.1f}<extra></extra>'
    ))
    
    # Kuadran lines
    fig.add_vline(x=med_comp, line=dict(color='rgba(255,255,255,0.2)', dash='dot', width=1))
    fig.add_hline(y=med_dem, line=dict(color='rgba(255,255,255,0.2)', dash='dot', width=1))
    
    # Labels kuadran
    fig.add_annotation(x=med_comp*0.8, y=med_dem*1.2, text="Golden Opportunity", showarrow=False, font=dict(color=DESIGN['success'], size=10))
    fig.add_annotation(x=med_comp*1.2, y=med_dem*1.2, text="Saturated / Red Ocean", showarrow=False, font=dict(color=DESIGN['danger'], size=10))
    
    fig = apply_layout(fig, height=280, show_legend=False)
    fig.update_xaxes(title="Avg Competition Score")
    fig.update_yaxes(title="Avg Demand Score")
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
def plot_gwr_coefficients(df, coef_col, title):
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
    fig = apply_layout(fig, height=350, show_legend=False)
    fig.update_xaxes(title="Coefficient Value")
    return fig

def plot_morans_result(i_val, z_score, p_val, title):
    """Gauge Chart ala Panel Intelijen untuk Moran's I"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=i_val,
        title={'text': title, 'font': {'size': 12, 'color': DESIGN['secondary']}},
        delta={'reference': 0, 'increasing': {'color': DESIGN['success']}, 'decreasing': {'color': DESIGN['danger']}},
        gauge={
            'axis': {'range': [-1, 1], 'tickcolor': DESIGN['secondary']},
            'bar': {'color': DESIGN['accent']},
            'steps': [
                {'range': [-1, -0.3], 'color': 'rgba(239,68,68,0.2)'},
                {'range': [-0.3, 0.3], 'color': 'rgba(255,255,255,0.05)'},
                {'range': [0.3, 1], 'color': 'rgba(34,197,94,0.2)'}
            ],
            'threshold': {'line': {'color': "white", 'width': 2}, 'thickness': 0.75, 'value': i_val}
        }
    ))
    fig.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font=dict(color=DESIGN['text']))
    return fig

# ==========================================
# 4. MULTI-METRIC & COMPARISON
# ==========================================
def plot_multi_radar(dest_stats, metrics):
    """Radar chart membandingkan Top 2 vs Bottom 2 Destinasi"""
    if dest_stats.empty or len(metrics) < 3: return go.Figure()
    
    # Ambil 2 terbaik dan 2 terbawah berdasarkan opportunity
    top_2 = dest_stats.nlargest(2, 'avg_opportunity')
    bot_2 = dest_stats.nsmallest(2, 'avg_opportunity')
    compare_df = pd.concat([top_2, bot_2])
    
    colors = [DESIGN['success'], DESIGN['accent'], DESIGN['warning'], DESIGN['danger']]
    fig = go.Figure()
    
    for i, (_, row) in enumerate(compare_df.iterrows()):
        vals = [row[m] for m in metrics]
        vals.append(vals[0]) # Tutup garis polygon
        lbls = [m.replace('avg_', '').title() for m in metrics]
        lbls.append(lbls[0])
        
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=lbls, fill='toself', name=row['dest_display'],
            line_color=colors[i % len(colors)], fillcolor=colors[i % len(colors)].replace(')', ', 0.2)').replace('rgb', 'rgba') if '#' not in colors[i] else 'rgba(0,212,255,0.1)'
        ))
        
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color=DESIGN['secondary'], size=10))
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=DESIGN['text'], family='Inter'),
        margin=dict(l=40, r=40, t=30, b=30), height=320,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=10))
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
    """Grouped Bar Khusus untuk NLP Tahap 3"""
    if branding_df.empty: return go.Figure()
    
    df = branding_df.copy()
    if dest_filter and dest_filter != 'All':
        df = df[df['destinasi'] == dest_filter]
        
    grp = df.groupby(['Segmen', 'Tema_Nama'])['Rata_rata_Ulasan'].mean().reset_index()
    
    fig = go.Figure()
    colors = {'Mengandung Unsur Alam': DESIGN['success'], 'Nama Standar': DESIGN['accent']}
    
    for tema in ['Nama Standar', 'Mengandung Unsur Alam']: # Urutkan agar standar di kiri
        sub = grp[grp['Tema_Nama'] == tema]
        fig.add_trace(go.Bar(
            name='Nature Branding' if 'Alam' in tema else 'Standard Naming',
            x=sub['Segmen'].apply(lambda x: x.split('(')[0].strip()),
            y=sub['Rata_rata_Ulasan'],
            marker_color=colors.get(tema, DESIGN['secondary']),
            text=sub['Rata_rata_Ulasan'].round(0).astype(int),
            textposition='outside', textfont=dict(color=DESIGN['text'], size=11)
        ))
        
    fig.update_layout(barmode='group')
    return apply_layout(fig, height=280)

# Dummy stubs if needed by other components
def plot_bubble(*args, **kwargs): return go.Figure()
def plot_heatmap_matrix(*args, **kwargs): return go.Figure()