import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --- KONFIGURASI DASHBOARD ---
st.set_page_config(page_title="Dashboard Unmet Need Disabilitas", layout="wide")

st.markdown("## 📊 **Dashboard Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas**")
st.markdown("### Tingkat Kabupaten/Kota di Pulau Jawa Tahun 2023")

# --- LOAD DATA ---
df = pd.read_excel("DatasetVisualisasi.xlsx")
gdf = gpd.read_file("KabJawa.shp")

# Pastikan kolom join bertipe sama
df["kabkot"] = df["kabkot"].astype(str)
gdf["IDKAB"] = gdf["IDKAB"].astype(str)

# Gabungkan data .shp dan .xlsx
gdf_merged = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# --- WARNA KATEGORI UNPKPD ---
kategori_colors = {
    "Sangat Tinggi": "#D62246",
    "Tinggi": "#F9893E",
    "Sedang": "#F3D64D",
    "Rendah": "#48C28E"
}

# Jika kategori hanya "Rendah", "Sedang", "Tinggi" → sesuaikan
if not "Sangat Tinggi" in df["cat_unpk"].unique():
    kategori_colors = {
        "Tinggi": "#F9893E",
        "Sedang": "#F3D64D",
        "Rendah": "#48C28E"
    }

# --- STATISTIK RINGKAS ---
col1, col2, col3 = st.columns([1.2, 1.5, 2])

with col1:
    mean_val = df["unpkpd"].mean()
    st.markdown("#### Rata-rata Unmet Need Provinsi")
    st.markdown(f"<h2 style='color:#D62246'>{mean_val:.1f}%</h2>", unsafe_allow_html=True)

with col2:
    st.markdown("#### Sebaran Kabupaten/Kota:")
    for kategori in kategori_colors.keys():
        jumlah = df[df["cat_unpk"] == kategori].shape[0]
        st.markdown(f"<span style='color:{kategori_colors[kategori]}'>●</span> {kategori}: {jumlah}", unsafe_allow_html=True)

with col3:
    top3 = df.nlargest(3, "unpkpd")
    bottom = df.nsmallest(1, "unpkpd")
    st.markdown("#### Kabupaten/Kota Tertinggi:")
    for _, row in top3.iterrows():
        st.markdown(f"- {row['kabkot']}: **{row['unpkpd']:.1f}%**")
    st.markdown("#### Kabupaten/Kota Terendah:")
    st.markdown(f"- {bottom.iloc[0]['kabkot']}: **{bottom.iloc[0]['unpkpd']:.1f}%**")

# --- PETA INTERAKTIF ---
st.markdown("## 🗺️ Peta Interaktif")

# Filter interaktif
kategori_filter = st.selectbox("Pilih Kategori Unmet Need", options=["Semua"] + sorted(df["cat_unpk"].unique()))
kualitas_filter = st.selectbox("Pilih Kualitas Estimasi", options=["Semua"] + sorted(df["cat_rse"].unique()))

# Filter data
gdf_filtered = gdf_merged.copy()
if kategori_filter != "Semua":
    gdf_filtered = gdf_filtered[gdf_filtered["cat_unpk"] == kategori_filter]
if kualitas_filter != "Semua":
    gdf_filtered = gdf_filtered[gdf_filtered["cat_rse"] == kualitas_filter]

# Peta dasar
m = folium.Map(location=[-7.5, 110.0], zoom_start=7.2, tiles="cartodbpositron")

# Tambahkan poligon
for _, row in gdf_filtered.iterrows():
    color = kategori_colors.get(row["cat_unpk"], "gray")
    tooltip = f"""
    <b>{row['KABKOT']}</b><br>
    Unmet Need: {row['unpkpd']:.1f}%<br>
    Kategori: {row['cat_unpk']}<br>
    Kualitas: {row['cat_rse']}
    """
    folium.GeoJson(
        row["geometry"],
        style_function=lambda feature, clr=color: {
            "fillColor": clr,
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7
        },
        tooltip=tooltip
    ).add_to(m)

# Legend Manual
legend_html = """
<div style='position: fixed; bottom: 70px; left: 30px; width: 180px; height: auto;
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
     padding: 10px; border-radius: 8px'>
<b>Legenda:</b><br>
<span style='background-color:#D62246;color:white'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Sangat Tinggi<br>
<span style='background-color:#F9893E;'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Tinggi<br>
<span style='background-color:#F3D64D;'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Sedang<br>
<span style='background-color:#48C28E;'>&nbsp;&nbsp;&nbsp;&nbsp;</span> Rendah<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Tampilkan peta
st_data = st_folium(m, width=1000, height=600)

# --- FOOTER ---
st.markdown("""<hr/>
<center>
2025 Skripsi TA | D-IV Komputasi Statistik | Politeknik Statistika STIS <br>
Email: 222112380@stis.ac.id
</center>
""", unsafe_allow_html=True)
