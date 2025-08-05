import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import json
from streamlit_folium import st_folium
from shapely.geometry import shape

# --- STYLING & PAGE SETUP ---
st.set_page_config("Dashboard UNPK PD Disabilitas 2023", layout="wide")
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_excel("DatasetVisualisasi.xlsx")
    gdf = gpd.read_file("KabJawa.shp")
    df["kabkot"] = df["kabkot"].astype(str)
    gdf["IDKAB"] = gdf["IDKAB"].astype(str)
    merged = gdf.merge(df, left_on="IDKAB", right_on="kabkot", how="left")
    return merged

gdf = load_data()

# --- WARNA PETA BERDASARKAN KATEGORI (dari cat_unpk) ---
color_dict = {
    "Sangat Rendah": "#b7f7a5",
    "Rendah": "#f7f79c",
    "Sedang": "#fca15e",
    "Tinggi": "#f75d59",
    "Sangat Tinggi": "#8b0000",
}

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>UNPK PD Pelayanan Kesehatan Penyandang Disabilitas di Pulau Jawa Tahun 2023</h1>", unsafe_allow_html=True)

# --- STATISTIK ---
st.markdown("""
    <style>
    .card:hover {
        transform: scale(1.03);
        box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    }
    .card h4, .card h1, .card p {
        color: white !important;
    }
    .card h4 {
        font-size: 18px;
        font-weight: bold;
        margin: 5px 0;
    }
    .card h1 {
        font-size: 22px;
        font-weight: bold;
        margin: 5px 0;
    }
    .card p {
        font-size: 18px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- HITUNG NILAI UNTUK STATISTIK KARTU ---
jumlah_kategori = gdf["cat_unpk"].nunique()
kategori_counts = gdf["cat_unpk"].value_counts().reindex(["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]).dropna().astype(int).to_dict()
kategori_display = "<br>".join([f"{k}: {v}" for k, v in kategori_counts.items()])

kab_tertinggi = gdf.loc[gdf["unpkpd"].idxmax()]
kab_terendah = gdf.loc[gdf["unpkpd"].idxmin()]

# --- 4 KOLOM KARTU SAJA ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="card" style="background-color:#c0392b;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>UNPK PD Nasional</h4>
        <h1>13.85%</h1>
        <p>Angka Nasional UNPK PD sebesar 13.85%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="background-color:#d35400;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Sebaran Wilayah</h4>
        <h1>{len(kategori_counts)} Kategori</h1>
        <p style='line-height:1.5'>{kategori_display}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="background-color:#16a085;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Kabupaten Tertinggi</h4>
        <h1>{kab_tertinggi['unpkpd']:.2f}%</h1>
        <p>{kab_tertinggi['name_kabkot']}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="background-color:#2980b9;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Kabupaten Terendah</h4>
        <h1>{kab_terendah['unpkpd']:.2f}%</h1>
        <p>{kab_terendah['name_kabkot']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- PILIHAN FILTRASI ---
col_kat, col_prov = st.columns(2)
kategori_opsi = ["Semua"] + list(gdf["cat_unpk"].dropna().unique())
prov_opsi = ["Semua"] + sorted(gdf["cat_rse"].dropna().unique())

with col_kat:
    selected_kategori = st.selectbox("Kategori UNPK", kategori_opsi)

with col_prov:
    selected_prov = st.selectbox("Kualitas Hasil Estimasi", prov_opsi)

# --- FILTER DATA ---
filtered_gdf = gdf.copy()
if selected_kategori != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["cat_unpk"] == selected_kategori]
if selected_prov != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["cat_rse"] == selected_prov]

# --- PETA FOLIUM ---
m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="cartodbpositron")

geojson_data = json.loads(filtered_gdf.to_json())

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

geojson_layer = folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["name_kabkot", "unpkpd", "cat_unpk", "cat_rse"],
        aliases=["Kabupaten/Kota:", "UNPKPD (%):", "Kategori UNPKPD:", "Kategori Data:"],
        sticky=True,
        labels=True
    )
)

geojson_layer.add_to(m)

st.markdown("### Peta Interaktif")
st_folium(m, width=1200, height=600)
