import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# --- CONFIG PAGE ---
st.set_page_config(layout="wide", page_title="Unmet Need Disabilitas 2023 Jawa", page_icon="📊")

# --- LOAD DATA ---
@st.cache_data

def load_data():
    df = pd.read_excel("DatasetVisualisasi.xlsx")
    gdf = gpd.read_file("KabJawa.shp")
    return df, gdf

df, gdf = load_data()

# --- PERSIAPAN DATA ---
gdf["IDKAB"] = gdf["IDKAB"].astype(int)
df["kabkot"] = df["kabkot"].astype(int)
merged = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# --- JUDUL ---
st.title("📊 Visualisasi Unmet Need Disabilitas 2023 di Pulau Jawa")
st.markdown("""
Dashboard ini menyajikan visualisasi data *Unmet Need Kebutuhan Pelayanan Disabilitas* tahun 2023 untuk wilayah kabupaten/kota di Pulau Jawa.
""")

# --- STATISTIK: KABUPATEN TERTINGGI ---
highest_row = merged.loc[merged['unpkpd'].idxmax()]
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Kabupaten/Kota dengan Unmet Need Tertinggi")
    st.markdown(f"### {highest_row['name_kabkot']}")
    st.markdown(f"**Unmet Need:** {highest_row['unpkpd']:.2f}%")
    st.markdown(f"**RSE:** {highest_row['rse']:.2f}%")
    st.markdown(f"**Kategori:** {highest_row['cat_unpk']}")
with col2:
    st.metric("Unmet Need Tertinggi", f"{highest_row['unpkpd']:.2f}%")

# --- PETA CHOROPLETH ---
st.subheader("Peta Sebaran Unmet Need Disabilitas (2023)")

# Peta dasar
m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="cartodbpositron")

# Warna dinamis berdasarkan kategori
def get_color(category):
    if category == "Sangat Tinggi": return "#D7191C"
    elif category == "Tinggi": return "#FDAE61"
    elif category == "Sedang": return "#FFFFBF"
    elif category == "Rendah": return "#A6D96A"
    else: return "#1A9641"

# Tambahkan poligon dan tooltip
for _, row in merged.iterrows():
    geo = folium.GeoJson(
        row["geometry"].__geo_interface__,
        style_function=lambda x, color=get_color(row['cat_unpk']): {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.Tooltip(
            f"<b>{row['name_kabkot']}</b><br/>"
            f"Unmet Need: {row['unpkpd']:.2f}%<br/>"
            f"RSE: {row['rse']:.2f}%<br/>"
            f"Kategori: {row['cat_unpk']}"
        )
    )
    geo.add_to(m)

# Tampilkan peta
st_folium(m, width=1000, height=600)

# --- FOOTER ---
st.markdown("---")
st.caption("Sumber data: BPS 2023, diolah | Dashboard dibuat dengan ❤️ oleh Sten. 💻")
