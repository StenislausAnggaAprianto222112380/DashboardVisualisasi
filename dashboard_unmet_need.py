import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --- SETUP HALAMAN ---
st.set_page_config(page_title="Unmet Need Disabilitas 2023", layout="wide")

# --- HEADER ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
    }
    .big-title {
        font-size: 36px !important;
        font-weight: 800;
        color: #1B4332;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .subtext {
        font-size: 16px;
        color: #444;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        flex: 1;
        min-width: 230px;
    }
    .card-title {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 0.2rem;
        color: #333;
    }
    .card-value {
        font-size: 32px;
        font-weight: 800;
        color: #111;
        margin-top: 0.3rem;
        line-height: 1.2;
    }
    .card-subtext {
        font-size: 14px;
        color: #666;
        margin-top: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas di Pulau Jawa Tahun 2023</div>", unsafe_allow_html=True)

st.markdown("<p class='subtext'>Unmet need pelayanan kesehatan pada penyandang disabilitas merupakan proporsi penyandang disabilitas yang merasa sakit dalam 1 tahun terakhir namun tidak mendapatkan pelayanan yang dibutuhkan (BPS).</p>", unsafe_allow_html=True)

# --- DATA ---
df = pd.read_excel("DatasetVisualisasi.xlsx")

# --- Statistik ---
rata2_unmet = df['unpkpd'].mean()
kab_tertinggi = df.loc[df['unpkpd'].idxmax()]
kab_terendah = df.loc[df['unpkpd'].idxmin()]

summary = {
    'tinggi': df[df['cat_unpk'] == 'Tinggi'].shape[0],
    'sedang': df[df['cat_unpk'] == 'Sedang'].shape[0],
    'rendah': df[df['cat_unpk'] == 'Rendah'].shape[0],
    'sangat tinggi': df[df['cat_unpk'] == 'Sangat Tinggi'].shape[0],
    'sangat rendah': df[df['cat_unpk'] == 'Sangat Rendah'].shape[0]
}

# --- STATISTIK KARTU ---
st.markdown("""
<div style='display: flex; flex-wrap: wrap; gap: 1.25rem;'>

    <div class='card' style='background-color: #E6F4EA;'>
        <div class='card-title'>Unmet Need</div>
        <div class='card-value'>{:.1f}%</div>
        <div class='card-subtext'>Rata-rata unmet need di Pulau Jawa</div>
    </div>

    <div class='card' style='background-color: #F3F7FA; flex: 2;'>
        <div class='card-title'>Sebaran Wilayah</div>
        <div class='card-value' style='font-size: 18px; font-weight: 600; color: #1B4332;'>
            Sangat Tinggi: {sangat_tinggi} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            Tinggi: {tinggi} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            Sedang: {sedang} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            Rendah: {rendah} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            Sangat Rendah: {sangat_rendah}
        </div>
    </div>

    <div class='card' style='background-color: #FFF4F4;'>
        <div class='card-title'>Kab/Kota Tertinggi</div>
        <div class='card-value'>{kab_max}</div>
        <div class='card-subtext'>{val_max:.1f}%</div>
    </div>

    <div class='card' style='background-color: #F1FFF0;'>
        <div class='card-title'>Kab/Kota Terendah</div>
        <div class='card-value'>{kab_min}</div>
        <div class='card-subtext'>{val_min:.1f}%</div>
    </div>

</div>
""".format(
    rata2_unmet,
    sangat_tinggi=summary['sangat tinggi'],
    tinggi=summary['tinggi'],
    sedang=summary['sedang'],
    rendah=summary['rendah'],
    sangat_rendah=summary['sangat rendah'],
    kab_max=kab_tertinggi['name_kabkot'],
    val_max=kab_tertinggi['unpkpd'],
    kab_min=kab_terendah['name_kabkot'],
    val_min=kab_terendah['unpkpd']
), unsafe_allow_html=True)

# --- PETA INTERAKTIF RINGAN (SATSET) ---
from folium.features import GeoJsonTooltip

# --- PETA ---
gdf = gpd.read_file("KabJawa.geojson")  # ← PASTIKAN FILE INI ADA
gdf["IDKAB"] = gdf["IDKAB"].astype(str)
df["kabkot"] = df["kabkot"].astype(str)
gdf = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# Mapping warna kategori
color_dict = {
    'Sangat Tinggi': '#B91C1C',
    'Tinggi': '#F87171',
    'Sedang': '#FDBA74',
    'Rendah': '#FDE68A',
    'Sangat Rendah': '#B9FBC0'
}

# Tambah kolom warna langsung
gdf["fillColor"] = gdf["cat_unpk"].map(color_dict)

# Buat folium Map
m = folium.Map(location=[-7.5, 111], zoom_start=6, tiles="cartodbpositron")

# Satu layer saja
geojson = folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        'fillColor': feature['properties']['fillColor'],
        'color': 'black',
        'weight': 0.3,
        'fillOpacity': 0.6
    },
    tooltip=GeoJsonTooltip(
        fields=["name_kabkot", "unpkpd"],
        aliases=["Kab/Kota", "Unmet Need (%)"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: white;
            border: 1px solid black;
            border-radius: 3px;
            padding: 5px;
        """,
    ),
    name="Sebaran Unmet Need"
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
