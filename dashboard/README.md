# 🗺️ Supply Heatmap — Accommodation Investment Dashboard

Dashboard analisis spasial supply akomodasi untuk 10 Destinasi Super Prioritas Pariwisata Indonesia.
Berbasis model **GWR (Geographically Weighted Regression)** + **DBSCAN Clustering**.

---

## 📁 Struktur Folder

```
dashboard/
├── app.py                        ← Entry point utama Streamlit
├── requirements.txt
├── data/
│   └── Dataset_DSP_FINAL_DASHBOARD.csv   ← ⬅️ TARUH FILE DATA DI SINI
└── functions/
    ├── __init__.py
    ├── analytics.py              ← Semua fungsi chart & komputasi
    ├── maps.py                   ← Fungsi peta Folium
    └── insights.py               ← Generator insight & rekomendasi otomatis
```

---

## 🚀 Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Taruh data
Salin file `Dataset_DSP_FINAL_DASHBOARD.csv` ke folder `data/`:
```
dashboard/data/Dataset_DSP_FINAL_DASHBOARD.csv
```

### 3. Jalankan dashboard
```bash
streamlit run app.py
```

---

## 📊 Kolom Dataset yang Digunakan

| Kolom | Keterangan |
|-------|-----------|
| `destinasi` | Nama destinasi (10 DSP) |
| `nama_hotel` | Nama properti |
| `jenis` | Kategori akomodasi |
| `latitude`, `longitude` | Koordinat |
| `harga` | Harga per malam (Rp) — 68% kosong (informal) |
| `rating` | Skor Google Maps (0–5) |
| `jumlah_ulasan` | Jumlah review |
| `jumlah_foto` | Total foto yang diunggah |
| `saingan_radius_1km` | Jumlah kompetitor dalam 1km |
| `total_demand_area` | Total ulasan dalam area 1km |
| `indeks_investasi` | Skor investasi hasil pipeline ML |
| `skor_popularitas` | Skor popularitas relatif |
| `foto_per_ulasan` | Rasio foto dibanding ulasan |
| `klaster_dbscan` | Label klaster DBSCAN |
| `status_ocean` | Klasifikasi Red/Blue Ocean |
| `koef_jarak_ke_pusat_km` | Koefisien GWR: jarak ke pusat |
| `koef_saingan_radius_1km` | Koefisien GWR: persaingan |
| `koef_foto_per_ulasan` | Koefisien GWR: pemasaran foto |
| `r2_lokal` | R² lokal model GWR per properti |
| `model_dipakai` | GWR (Lokal) atau OLS (Global) |

---

## 📑 Tab Dashboard

1. **Executive Summary** — KPI utama + ranking destinasi + disclaimer data harga
2. **Spatial Heatmap** — Peta Folium nasional (Heatmap + Cluster + Individual, warna = status pasar)
3. **Market Behavior** — Analisis defensive marketing (foto vs rating) + GWR insights
4. **Competition Analysis** — Kuadran spasial: saingan vs demand, warna status pasar
5. **Investment Opportunity** — Top 15 berdasarkan `indeks_investasi` + Mandalika vs Labuan Bajo
6. **Insights & Rekomendasi** — Otomatis dari data aktif

---

## ⚠️ Troubleshooting

**Layar blank/hitam tanpa error?**
- Cek terminal untuk error Python
- Pastikan file CSV ada di `data/Dataset_DSP_FINAL_DASHBOARD.csv`
- Coba jalankan: `python -c "import pandas as pd; df = pd.read_csv('data/Dataset_DSP_FINAL_DASHBOARD.csv', sep=None, engine='python'); print(df.shape)"`

**Error "Kolom wajib tidak ditemukan"?**
- Dashboard akan menampilkan pesan error beserta kolom yang tersedia
- Periksa apakah nama kolom sesuai (case-sensitive)

**Peta tidak muncul?**
- Install ulang: `pip install folium streamlit-folium --upgrade`
