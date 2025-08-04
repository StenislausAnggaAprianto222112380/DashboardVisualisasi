import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Unmet Need Disabilitas 2023", layout="wide")

# --- HEADER ---
st.markdown("""
    <style>
    .big-title {
        font-size:36px !important;
        font-weight: 700;
        color: #1B4332;
        margin-bottom: 0;
    }
    .subtext {
        font-size: 15px;
        color: #333;
        margin-top: 0;
    }
    .card-title {
        font-weight: 600;
        font-size: 18px;
    }
    .card-subtext {
        font-size: 14px;
        color: #777;
    }
    .card-value {
        font-size: 28px;
        font-weight: 700;
        margin: 5px 0 0 0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<p class='big-title'>Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas di Pulau Jawa Tahun 2023</p>", unsafe_allow_html=True)

st.markdown("<p class='subtext'>Unmet need pelayanan kesehatan pada penyandang disabilitas merupakan proporsi penyandang disabilitas yang merasa sakit dalam 1 tahun terakhir namun tidak mendapatkan pelayanan yang dibutuhkan (BPS).</p>", unsafe_allow_html=True)

# --- DATA ---
df = pd.read_excel("DatasetVisualisasi.xlsx")

# Statistik ringkas
rata2_unmet = df['unpkpd'].mean()
prov_tertinggi = df.loc[df['unpkpd'].idxmax()]
prov_terendah = df.loc[df['unpkpd'].idxmin()]

summary = {
    'tinggi': df[df['cat_unpk'] == 'Sangat Tinggi'].shape[0],
    'sedang': df[df['cat_unpk'] == 'Sedang'].shape[0],
    'rendah': df[df['cat_unpk'] == 'Rendah'].shape[0]
}

# --- STATISTIK KARTU ---
st.markdown("""
<div style='display: flex; gap: 1rem;'>
    <div style='flex:1; background-color: #E7F5EC; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Unmet Need</div>
        <div class='card-value'>{:.1f}%</div>
        <div class='card-subtext'>Rata-rata unmet need di Pulau Jawa</div>
    </div>
    <div style='flex:1; background-color: #F3F7FA; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Sebaran Wilayah</div>
        <div class='card-value'>Tinggi: {tinggi} | Sedang: {sedang} | Rendah: {rendah}</div>
    </div>
    <div style='flex:1; background-color: #FFF4F4; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Kab/Kota Tertinggi</div>
        <div class='card-value'>{} <br> {:.1f}%</div>
    </div>
    <div style='flex:1; background-color: #F1FFF0; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Kab/Kota Terendah</div>
        <div class='card-value'>{} <br> {:.1f}%</div>
    </div>
</div>
""".format(
    rata2_unmet,
    summary['tinggi'], summary['sedang'], summary['rendah'],
    prov_tertinggi['name_kabkot'], prov_tertinggi['unpkpd'],
    prov_terendah['name_kabkot'], prov_terendah['unpkpd']
), unsafe_allow_html=True)

# --- PETA ---
gdf = gpd.read_file("KabJawa.geojson")
gdf = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

color_dict = {
    'Sangat Tinggi': '#B71C1C',
    'Tinggi': '#F44336',
    'Sedang': '#FFEB3B',
    'Rendah': '#81C784',
    'Sangat Rendah': '#388E3C'
}

m = folium.Map(location=[-7.5, 111], zoom_start=6, tiles="cartodbpositron")

for _, row in gdf.iterrows():
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, color=color_dict[row['cat_unpk']]: {
            'fillColor': color,
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.6
        },
        tooltip=folium.Tooltip(f"{row['name_kabkot']}: {row['unpkpd']}%")
    ).add_to(m)

st.markdown("## Peta Interaktif")
st_folium(m, width=1200, height=500)

# --- CATATAN KAKI ---
st.markdown("""
---
<p style='font-size:13px; color:#999;'>
Dashboard ini dikembangkan menggunakan Streamlit sebagai bagian dari visualisasi data Unmet Need pelayanan kesehatan pada penyandang disabilitas di Pulau Jawa tahun 2023.<br>
Sumber data: Badan Pusat Statistik (BPS).
</p>
""", unsafe_allow_html=True)
