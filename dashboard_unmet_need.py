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
    "Sangat Rendah": "#b7f7a5",    # Hijau muda
    "Rendah": "#f7f79c",           # Kuning
    "Sedang": "#fca15e",           # Oranye
    "Tinggi": "#f75d59",           # Merah
    "Sangat Tinggi": "#8b0000",    # Merah tua gelap
}

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>UNPK PD Pelayanan Kesehatan Penyandang Disabilitas di Pulau Jawa Tahun 2023</h1>", unsafe_allow_html=True)

# --- STATISTIK ---
# --- Gaya Hover dan Card ---
st.markdown("""
    <style>
    .card:hover {
        transform: scale(1.03);
        box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- HITUNG NILAI UNTUK STATISTIK KARTU ---
jumlah_st = gdf[gdf["cat_unpk"] == "Sangat Tinggi"].shape[0]
jumlah_sr = gdf[gdf["cat_unpk"] == "Sangat Rendah"].shape[0]

kab_tertinggi = gdf.loc[gdf["unpkpd"].idxmax(), "name_kabkot"]
unpk_tertinggi = gdf["unpkpd"].max()

kab_terendah = gdf.loc[gdf["unpkpd"].idxmin(), "name_kabkot"]
unpk_terendah = gdf["unpkpd"].min()


# --- Kolom Statistik ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="card" style="background-color:#e74c3c;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>UNPK PD</h4>
        <h1>22.8%</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="background-color:#c0392b;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Sangat Tinggi</h4>
        <h1>{jumlah_st}</h1>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="background-color:#27ae60;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Sangat Rendah</h4>
        <h1>{jumlah_sr}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="background-color:#2980b9;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Kab. Tertinggi</h4>
        <h1>{kab_tertinggi}<br>{unpk_tertinggi:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="card" style="background-color:#8e44ad;padding:20px;border-radius:10px;text-align:center;color:white">
        <h4>Kab. Terendah</h4>
        <h1>{kab_terendah}<br>{unpk_terendah:.1f}%</h1>
    </div>
    """, unsafe_allow_html=True)
    
# --- PILIHAN FILTRASI ---
col_kat, col_prov = st.columns(2)
kategori_opsi = ["Semua"] + list(gdf["cat_unpk"].dropna().unique())
prov_opsi = ["Semua"] + sorted(gdf["PROVINSI"].dropna().unique())

with col_kat:
    selected_kategori = st.selectbox("Kategori", kategori_opsi)

with col_prov:
    selected_prov = st.selectbox("Provinsi", prov_opsi)

# --- FILTER DATA ---
filtered_gdf = gdf.copy()
if selected_kategori != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["cat_unpk"] == selected_kategori]
if selected_prov != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["PROVINSI"] == selected_prov]

# --- PETA FOLIUM ---
m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="cartodbpositron")

geojson_data = json.loads(filtered_gdf.to_json())

def style_function(feature):
    kategori = feature["properties"]["cat_unpk"]
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
