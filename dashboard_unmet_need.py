import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
import json
from streamlit_folium import st_folium
from branca.colormap import LinearColormap
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
    return df, gdf

df, gdf = load_data()

# --- MERGE DATA ---
gdf["IDKAB"] = gdf["IDKAB"].astype(str)
df["kabkot"] = df["kabkot"].astype(str)
gdf = gdf.merge(df, left_on="IDKAB", right_on="kabkot", how="left")

# --- KATEGORI UNPKPD ---
def kategori_unpkpd(persen):
    if persen <= 10:
        return "Sangat Rendah"
    elif persen <= 20:
        return "Rendah"
    elif persen <= 30:
        return "Sedang"
    elif persen <= 40:
        return "Tinggi"
    else:
        return "Sangat Tinggi"

gdf["kategori"] = gdf["unpkpd"].apply(kategori_unpkpd)

# --- WARNA PETA ---
color_dict = {
    "Sangat Rendah": "#b7e4c7",  # Hijau muda
    "Rendah": "#fef9b0",         # Kuning
    "Sedang": "#fdae61",         # Orange
    "Tinggi": "#f46d43",         # Merah
    "Sangat Tinggi": "#a50026"   # Merah bata
}

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>UNPK PD Pelayanan Kesehatan Penyandang Disabilitas di Pulau Jawa Tahun 2023</h1>", unsafe_allow_html=True)

# --- STATISTIK ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class='card hover-card'>
            <h2>UNPK PD</h2>
            <h1>22.8%</h1>
            <p>Penyandang disabilitas yang kebutuhannya belum terpenuhi</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    kategori_count = gdf["kategori"].value_counts()
    st.markdown(f"""
        <div class='card hover-card'>
            <h2>Sebaran Wilayah</h2>
            <p>Sangat Tinggi: {kategori_count.get('Sangat Tinggi', 0)}</p>
            <p>Tinggi: {kategori_count.get('Tinggi', 0)}</p>
            <p>Sedang: {kategori_count.get('Sedang', 0)}</p>
            <p>Rendah: {kategori_count.get('Rendah', 0)}</p>
            <p>Sangat Rendah: {kategori_count.get('Sangat Rendah', 0)}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    max_row = gdf.loc[gdf["unpkpd"].idxmax()]
    st.markdown(f"""
        <div class='card hover-card'>
            <h2>Kabupaten Tertinggi</h2>
            <h1>{max_row["unpkpd"]:.1f}%</h1>
            <p>{max_row["name_kabkot"]}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    min_row = gdf.loc[gdf["unpkpd"].idxmin()]
    st.markdown(f"""
        <div class='card hover-card'>
            <h2>Kabupaten Terendah</h2>
            <h1>{min_row["unpkpd"]:.1f}%</h1>
            <p>{min_row["name_kabkot"]}</p>
        </div>
    """, unsafe_allow_html=True)

# --- PILIHAN FILTRASI ---
col_kat, col_prov = st.columns(2)
kategori_opsi = ["Semua"] + list(gdf["kategori"].unique())
prov_opsi = ["Semua"] + sorted(gdf["PROVINSI"].unique())

with col_kat:
    selected_kategori = st.selectbox("Kategori", kategori_opsi)

with col_prov:
    selected_prov = st.selectbox("Provinsi", prov_opsi)

# --- FILTER DATA ---
filtered_gdf = gdf.copy()
if selected_kategori != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["kategori"] == selected_kategori]
if selected_prov != "Semua":
    filtered_gdf = filtered_gdf[filtered_gdf["PROVINSI"] == selected_prov]

# --- PETA FOLIUM ---
#import json

# Konversi GeoDataFrame ke GeoJSON sekali saja agar ringan
geojson_data = json.loads(filtered_gdf.to_json())

def style_function(feature):
    kategori = feature["properties"]["kategori"]
    color = color_dict.get(kategori, "#d3d3d3")
    return {
        "fillColor": color,
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    }

def highlight_function(feature):
    return {"weight": 3, "color": "black"}

# Tooltip interaktif
geojson_layer = folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["name_kabkot", "unpkpd", "kategori", "cat_rse"],
        aliases=["Kabupaten/Kota:", "UNPKPD (%):", "Kategori UNPKPD:", "Kategori Data:"],
        sticky=True,
        labels=True
    )
)

geojson_layer.add_to(m)

st.markdown("### Peta Interaktif")
st_folium(m, width=1200, height=600)
