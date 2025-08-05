import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import shape
import json

st.set_page_config(layout="wide")
st.title("Dashboard Visualisasi UNPK Penyandang Disabilitas 2023 - Pulau Jawa")

# --- BACA DATA ---
@st.cache_data

def load_data():
    df = pd.read_excel("DatasetVisualisasi.xlsx")
    gdf = gpd.read_file("KabJawa.shp")
    return df, gdf

df, gdf = load_data()

# --- GABUNGKAN DATAFRAME ---
merged_gdf = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# --- BUAT WARNA KATEGORI ---
color_dict = {
    "Sangat Rendah": "#b7f7a5",
    "Rendah": "#f7f79c",
    "Sedang": "#fca15e",
    "Tinggi": "#f75d59",
    "Sangat Tinggi": "#8b0000",
}

# --- BUAT FUNGSI UNTUK PETA ---
geojson_data = json.loads(merged_gdf.to_json())

def style_function(feature):
    kategori = feature["properties"].get("cat_unpk")
    color = color_dict.get(kategori, "#d3d3d3")
    return {
        "fillColor": color,
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    }

def highlight_function(feature):
    return {"weight": 3, "color": "black"}

# --- KOMPONEN STATISTIK KARTU ---
kab_tertinggi = df.loc[df['unpkpd'].idxmax()]
kab_terendah = df.loc[df['unpkpd'].idxmin()]
rata2_unpk = df['unpkpd'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Kabupaten Tertinggi</div>
        <div class="card-value">{}</div>
    </div>
    """.format(kab_tertinggi['name_kabkot']), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Kabupaten Terendah</div>
        <div class="card-value">{}</div>
    </div>
    """.format(kab_terendah['name_kabkot']), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <div class="card-title">Rata-rata UNPKPD</div>
        <div class="card-value">{:.2f}%</div>
    </div>
    """.format(rata2_unpk), unsafe_allow_html=True)

# --- TAMPILKAN PETA ---
with st.container():
    st.subheader("Peta Sebaran UNPKPD")

    m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="cartodbpositron")

    tooltip = folium.GeoJsonTooltip(
        fields=["name_kabkot", "unpkpd", "cat_unpk", "cat_rse"],
        aliases=["Kabupaten/Kota:", "UNPKPD (%):", "Kategori UNPKPD:", "Kategori Data:"],
        sticky=True,
        labels=True
    )

    geojson_layer = folium.GeoJson(
        geojson_data,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    )

    geojson_layer.add_to(m)
    st_folium(m, width=1200, height=600)

# --- CSS UNTUK EFEK TIMBUL KARTU ---
st.markdown("""
<style>
.card {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.card:hover {
    transform: scale(1.05);
    box-shadow: 4px 4px 12px rgba(0,0,0,0.2);
}
.card-title {
    font-size: 20px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}
.card-value {
    font-size: 28px;
    color: #007BFF;
}
</style>
""", unsafe_allow_html=True)
