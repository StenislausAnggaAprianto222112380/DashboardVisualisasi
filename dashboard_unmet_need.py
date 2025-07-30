import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import Choropleth, LayerControl, Tooltip
from streamlit_folium import st_folium

# Judul aplikasi
st.set_page_config(layout="wide")
st.title("Dashboard Visualisasi Unmet Need Pelayanan Kesehatan pada Disabilitas")

# Load data Excel dan SHP
excel_path = "DatasetVisualisasi.xlsx"
shapefile_path = "KabJawa.shp"

@st.cache_data
def load_data():
    df = pd.read_excel(excel_path)
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs(epsg=4326)  # pastikan CRS sesuai
    gdf["geometry"] = gdf["geometry"].simplify(0.01)  # opsi 3: sederhanakan geometri
    return df, gdf

df, gdf = load_data()

# Sidebar filter
st.sidebar.header("Filter Data")
kategori_unpk = st.sidebar.multiselect("Kategori Unmet Need:", options=df["cat_unpk"].unique(), default=df["cat_unpk"].unique())
kategori_rse = st.sidebar.multiselect("Kategori Kualitas Estimasi (RSE):", options=df["cat_rse"].unique(), default=df["cat_rse"].unique())

# Filter data
filtered_df = df[df["cat_unpk"].isin(kategori_unpk) & df["cat_rse"].isin(kategori_rse)]

# Gabungkan dengan shapefile
merged = gdf.merge(filtered_df, left_on="IDKAB", right_on="kabkot", how="inner")

# Warna kategori
kategori_colors = {
    "Sangat Tinggi": "#D62246",
    "Tinggi": "#F9893E",
    "Sedang": "#F3D64D",
    "Rendah": "#48C28E"
}

# Hanya ambil warna yang masih digunakan
kategori_ada = filtered_df["cat_unpk"].dropna().unique().tolist()
kategori_colors = {k: v for k, v in kategori_colors.items() if k in kategori_ada}

# Buat peta folium
m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="CartoDB positron")

# Tambahkan layer choropleth
for cat, color in kategori_colors.items():
    cat_data = merged[merged["cat_unpk"] == cat]
    folium.GeoJson(
        cat_data,
        style_function=lambda x, col=color: {
            "fillColor": col,
            "color": "black",
            "weight": 0.3,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["kabkot", "unpkpd"], aliases=["Kabupaten/Kota:", "Unmet Need (%):"]),
        name=cat
    ).add_to(m)

folium.LayerControl().add_to(m)

# Tampilkan peta
st_data = st_folium(m, width=1000, height=600)

# Opsi 2: Legenda tampil langsung di Streamlit (bukan di dalam peta)
st.markdown("""
<style>
.legenda-box {
    background-color: white;
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
    width: fit-content;
    margin-bottom: 1rem;
}
.legenda-color {
    display: inline-block;
    width: 15px;
    height: 15px;
    margin-right: 5px;
    border: 1px solid black;
}
</style>
<div class='legenda-box'>
<b>Legenda:</b><br>
""" +
"<br>".join([f"<span class='legenda-color' style='background-color:{kategori_colors[k]}'></span> {k}" for k in kategori_colors]) +
"""
</div>
""", unsafe_allow_html=True)

# Statistik kabupaten/kota tertinggi dan terendah
top3 = filtered_df.nlargest(3, "unpkpd")
bottom = filtered_df.nsmallest(1, "unpkpd")

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Kabupaten/Kota dengan Unmet Need Tertinggi:")
    for _, row in top3.iterrows():
        st.markdown(f"- {row['kabkot']}: **{row['unpkpd']:.1f}%**")

with col2:
    st.markdown("#### Kabupaten/Kota dengan Unmet Need Terendah:")
    st.markdown(f"- {bottom.iloc[0]['kabkot']}: **{bottom.iloc[0]['unpkpd']:.1f}%**")

# Footer
st.markdown("""<hr/>
<center>
2025 Skripsi TA | D-IV Komputasi Statistik | Politeknik Statistika STIS <br>
Email: 222112380@stis.ac.id
</center>
""", unsafe_allow_html=True)
