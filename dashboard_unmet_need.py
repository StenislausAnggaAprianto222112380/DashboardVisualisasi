import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear

# ================== LOAD DATA ==================
@st.cache_data

def load_data():
    df = pd.read_excel("DatasetVisualisasi.xlsx")
    gdf = gpd.read_file("KabJawa.shp")
    return df, gdf

df, gdf = load_data()

# ================== DATA PREP ==================
# Pastikan kolom id join memiliki tipe yang sama
df["kabkot"] = df["kabkot"].astype(str)
gdf["IDKAB"] = gdf["IDKAB"].astype(str)

# Gabungkan data excel ke shapefile berdasarkan kabkot dan IDKAB
gdf = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# ================== SIDEBAR ==================
st.sidebar.title("Dashboard Unmet Need Disabilitas 2023")
st.sidebar.markdown("Pulau Jawa | Sumber: BPS 2023")

# ================== TITLE ==================
st.markdown("""
    <h2 style='text-align: center; color: black;'>Dashboard Unmet Need KB Penyandang Disabilitas</h2>
    <h4 style='text-align: center; color: black;'>Provinsi di Pulau Jawa - 2023</h4>
""", unsafe_allow_html=True)

# ================== METRIC KABKOT TERTINGGI ==================
# Dapatkan kabupaten dengan unmet need tertinggi
max_row = df.loc[df['unpkpd'].idxmax()]
st.markdown("""
<div style='background-color: #F9893E; padding: 15px; border-radius: 10px; color: white;'>
    <h4 style='margin: 0;'>Kabupaten/Kota dengan Unmet Need Tertinggi:</h4>
    <h2 style='margin: 0;'>{}</h2>
    <p style='margin: 0;'>Unmet Need: {:.2f}%</p>
</div>
""".format(max_row['name_kabkot'], max_row['unpkpd']), unsafe_allow_html=True)

st.markdown("---")

# ================== FOLIUM MAP ==================
# Setup color scale
colormap = linear.YlOrRd_09.scale(df.unpkpd.min(), df.unpkpd.max())
colormap.caption = 'Persentase Unmet Need (%)'

# Membuat peta
m = folium.Map(location=[-7.5, 110.5], zoom_start=7, tiles="CartoDB positron")

# Menambahkan layer choropleth
folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        'fillColor': colormap(feature['properties']['unpkpd']) if feature['properties']['unpkpd'] is not None else 'gray',
        'color': 'black',
        'weight': 0.5,
        'dashArray': '5, 5',
        'fillOpacity': 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['name_kabkot', 'unpkpd', 'cat_unpk'],
        aliases=['Kab/Kota', 'Unmet Need (%)', 'Kategori'],
        localize=True
    )
).add_to(m)

colormap.add_to(m)

# Tampilkan peta di streamlit
st_data = st_folium(m, width=700, height=500)

# ================== TABEL ==================
st.markdown("## Tabel Data Unmet Need")
st.dataframe(df[["name_kabkot", "unpkpd", "rse", "cat_unpk", "cat_rse"]].sort_values(by="unpkpd", ascending=False), use_container_width=True)

# ================== CATATAN ==================
st.markdown("""
### Catatan:
- **Unmet Need**: Persentase kebutuhan ber-KB yang tidak terpenuhi.
- **RSE**: Relative Standard Error.
- Kategori RSE digunakan untuk menilai ketepatan estimasi.
- Data ini diambil dari hasil Survei Sosial Ekonomi Nasional (Susenas) tahun 2023.
""")
