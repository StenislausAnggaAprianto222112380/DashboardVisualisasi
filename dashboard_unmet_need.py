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
<div style='display: flex; gap: 1rem; flex-wrap: wrap;'>
    <div style='flex:1; background-color: #E7F5EC; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Unmet Need</div>
        <div class='card-value'>{:.1f}%</div>
        <div class='card-subtext'>Rata-rata unmet need di Pulau Jawa</div>
    </div>
    <div style='flex:2; background-color: #F3F7FA; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Sebaran Wilayah</div>
        <div class='card-value'>
            Sangat Tinggi: {sangat_tinggi} | Tinggi: {tinggi} |
            Sedang: {sedang} | Rendah: {rendah} | Sangat Rendah: {sangat_rendah}
        </div>
    </div>
    <div style='flex:1; background-color: #FFF4F4; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Kab/Kota Tertinggi</div>
        <div class='card-value'>{kab_max} <br> {val_max:.1f}%</div>
    </div>
    <div style='flex:1; background-color: #F1FFF0; padding: 1.25rem; border-radius: 10px;'>
        <div class='card-title'>Kab/Kota Terendah</div>
        <div class='card-value'>{kab_min} <br> {val_min:.1f}%</div>
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
