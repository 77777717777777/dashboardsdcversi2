"""
insights.py — Generator insight & rekomendasi otomatis berbasis data
"""

import pandas as pd
import numpy as np


def generate_insights(df: pd.DataFrame) -> list:
    """Hasilkan list insight berdasarkan data yang difilter."""
    insights = []
    if df.empty:
        return [{"type": "warning", "tag": "⚠️ WARNING", "text": "Tidak ada data untuk dianalisis."}]

    # 1. Dominasi destinasi
    dest_counts = df.groupby("destinasi").size().sort_values(ascending=False)
    top_dest = dest_counts.index[0]
    top_n = dest_counts.iloc[0]
    pct_top = top_n / len(df) * 100
    insights.append({
        "type": "warning",
        "tag": "🏆 SUPPLY DOMINANCE",
        "text": (
            f"<b>{top_dest}</b> mendominasi {pct_top:.1f}% total supply "
            f"({top_n:,} dari {len(df):,} akomodasi). "
            "Konsentrasi ekstrem ini mengindikasikan potensi oversupply di destinasi tersebut."
        ),
    })

    # 2. Harga kosong
    pct_kosong = df["harga"].isna().mean() * 100
    insights.append({
        "type": "warning",
        "tag": "💰 DATA HARGA",
        "text": (
            f"{pct_kosong:.0f}% data harga tidak tersedia. "
            "Mayoritas adalah akomodasi informal lokal yang belum terdigitalisasi — "
            "peluang besar untuk platform digitalisasi harga dinamis."
        ),
    })

    # 3. Red vs Blue Ocean
    status_col = None
    for c in ["status_ocean", "status_pasar"]:
        if c in df.columns:
            status_col = c
            break

    if status_col:
        status_dist = df[status_col].value_counts(normalize=True) * 100
        red_pct = sum(v for k, v in status_dist.items() if "red" in str(k).lower() or "padat" in str(k).lower())
        insights.append({
            "type": "danger" if red_pct > 60 else "info",
            "tag": "🌊 KOMPETISI PASAR",
            "text": (
                f"{red_pct:.0f}% akomodasi berada di zona <b>Red Ocean</b> (pasar jenuh). "
                "Strategi diferensiasi produk dan penargetan niche market sangat direkomendasikan "
                "untuk pemain baru yang ingin masuk."
            ),
        })

    # 4. Destinasi dengan demand area tertinggi tapi supply rendah
    if "total_demand_area" in df.columns and "saingan_radius_1km" in df.columns:
        grp = df.groupby("destinasi").agg(
            avg_demand=("total_demand_area", "mean"),
            avg_saingan=("saingan_radius_1km", "mean"),
            count=("nama_hotel", "count"),
        )
        grp["demand_per_saingan"] = grp["avg_demand"] / (grp["avg_saingan"] + 1)
        if len(grp):
            best = grp["demand_per_saingan"].idxmax()
            ratio = grp.loc[best, "demand_per_saingan"]
            insights.append({
                "type": "success",
                "tag": "🎯 PELUANG TERBAIK",
                "text": (
                    f"<b>{best}</b> memiliki rasio demand-to-competition tertinggi "
                    f"({ratio:.1f} ulasan/saingan). Ini adalah zona <em>Blue Ocean</em> yang paling potensial "
                    "untuk investasi baru."
                ),
            })

    # 5. Korelasi foto vs rating
    if "foto_per_ulasan" in df.columns:
        valid = df[(df["foto_per_ulasan"].notna()) & (df["rating"] > 0) & (df["foto_per_ulasan"] > 0)]
        if len(valid) > 30:
            corr = valid["foto_per_ulasan"].corr(valid["rating"])
            if corr < -0.05:
                insights.append({
                    "type": "info",
                    "tag": "📸 DEFENSIVE MARKETING",
                    "text": (
                        f"Korelasi negatif (r={corr:.2f}) antara rasio foto dan rating. "
                        "Properti dengan rating rendah cenderung mengunggah lebih banyak foto — "
                        "ini adalah sinyal <em>defensive marketing</em> yang menggantikan kualitas dengan kuantitas visual."
                    ),
                })

    return insights


def generate_recommendations(df: pd.DataFrame) -> list:
    """Hasilkan rekomendasi strategis berdasarkan data."""
    recs = []

    # 1. Mandalika underrated
    mandalika = df[df["destinasi"] == "Mandalika"]
    labuan_bajo = df[df["destinasi"] == "Labuan Bajo"]

    if len(mandalika) and len(labuan_bajo) and "total_demand_area" in df.columns:
        m_demand = mandalika["total_demand_area"].mean()
        lb_demand = labuan_bajo["total_demand_area"].mean()
        ratio = m_demand / lb_demand if lb_demand > 0 else 1

        recs.append({
            "number": "01",
            "icon": "🏆",
            "title": "Masuk ke Mandalika Sekarang — Sebelum Ramai",
            "text": (
                f"Mandalika memiliki demand area rata-rata {ratio:.1f}x lebih tinggi dari Labuan Bajo, "
                "namun dengan indeks persaingan yang jauh lebih rendah. "
                "Ini adalah zona <b>underrated dengan momentum MotoGP & Sirkuit Mandalika</b>. "
                "First-mover advantage masih tersedia untuk segmen mid-range & eco-resort."
            ),
        })

    # 2. Labuan Bajo — bukan untuk pemain baru
    if len(labuan_bajo):
        avg_saingan_lb = labuan_bajo.get("saingan_radius_1km", pd.Series([0])).mean() if "saingan_radius_1km" in labuan_bajo.columns else 0
        recs.append({
            "number": "02",
            "icon": "⚠️",
            "title": "Labuan Bajo: Red Ocean Ekstrem — Diferensiasi Wajib",
            "text": (
                f"Labuan Bajo memiliki rata-rata {avg_saingan_lb:.0f} kompetitor dalam radius 1 km. "
                "Market sudah sangat jenuh. Jika tetap ingin masuk, fokus pada "
                "<b>hyper-niche</b> seperti luxury liveaboard, eco-glamping, atau akomodasi "
                "indigenous-themed yang tidak memiliki substitusi langsung."
            ),
        })

    # 3. Digitalisasi akomodasi informal
    pct_no_price = df["harga"].isna().mean() * 100 if "harga" in df.columns else 0
    if pct_no_price > 50:
        recs.append({
            "number": "03",
            "icon": "📱",
            "title": "Digitalisasi Akomodasi Informal — Peluang Platform",
            "text": (
                f"{pct_no_price:.0f}% properti belum memiliki data harga terdigitalisasi. "
                "Peluang besar untuk <b>platform agregator lokal</b> yang membantu UKM akomodasi "
                "onboard ke sistem pemesanan online. Potensi revenue dari komisi booking dan "
                "layanan subscription manajemen properti."
            ),
        })

    # 4. Nature-themed branding
    if "is_nature_view" in df.columns:
        nature = df[df["is_nature_view"] == 1]
        standard = df[df["is_nature_view"] == 0]
        if len(nature) and len(standard):
            avg_ulasan_nature = nature["jumlah_ulasan"].mean()
            avg_ulasan_std = standard["jumlah_ulasan"].mean()
            if avg_ulasan_nature > avg_ulasan_std:
                uplift = (avg_ulasan_nature / avg_ulasan_std - 1) * 100
                recs.append({
                    "number": "04",
                    "icon": "🌿",
                    "title": f"Nature Branding Tingkatkan Ulasan {uplift:.0f}%",
                    "text": (
                        f"Properti dengan nama mengandung unsur alam mendapat rata-rata "
                        f"{avg_ulasan_nature:.0f} ulasan vs {avg_ulasan_std:.0f} untuk nama standar. "
                        "Investasi pada <b>branding berbasis landscape lokal</b> (Komodo, Toba, Bromo) "
                        "secara signifikan meningkatkan visibility organik di platform OTA."
                    ),
                })

    # 5. Fokus pada destinasi frontier
    if "total_demand_area" in df.columns and "saingan_radius_1km" in df.columns:
        low_comp_dests = (
            df.groupby("destinasi")
            .agg(avg_saingan=("saingan_radius_1km", "mean"))
            .query("avg_saingan < 10")
            .index.tolist()
        )
        if low_comp_dests:
            recs.append({
                "number": "05",
                "icon": "🗺️",
                "title": f"Frontier Zone: {', '.join(low_comp_dests[:3])}",
                "text": (
                    f"Destinasi {', '.join(low_comp_dests[:3])} memiliki kompetisi sangat rendah "
                    "(<10 saingan per km²). Cocok untuk investor dengan risk appetite tinggi yang "
                    "ingin menjadi <b>market maker</b> sebelum infrastruktur berkembang. "
                    "Potensi capital gain properti sangat besar jika investasi dilakukan sekarang."
                ),
            })

    return recs[:5]
