import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from shapely.geometry import shape

# --- KONFIGURASI DASAR ---
st.set_page_config(page_title="Dashboard Unmet Need Disabilitas", layout="wide")

# --- BACA DATA (CACHED) ---
@st.cache_data
def load_data():
    df = pd.read_excel("DatasetVisualisasi.xlsx")
    gdf = gpd.read_file("KabJawa.shp")
    df["kabkot"] = df["kabkot"].astype(str)
    gdf["IDKAB"] = gdf["IDKAB"].astype(str)
    return df, gdf

df, gdf = load_data()
gdf_merged = gdf.merge(df, left_on="IDKAB", right_on="kabkot")

# --- WARNA KATEGORI ---
kategori_colors = {
    "Sangat Tinggi": "#D62246",
    "Tinggi": "#F9893E",
    "Sedang": "#F3D64D",
    "Rendah": "#48C28E"
}
if "Sangat Tinggi" not in df["cat_unpk"].unique():
    kategori_colors.pop("Sangat Tinggi")

# ================================
#           HEADER UTAMA
# ================================
st.markdown("""
    <h1 style='text-align: center; color: #0F3D28; font-size: 32px;'>
        Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas di Pulau Jawa Tahun 2023
    </h1>
""", unsafe_allow_html=True)

# ================================
#         KARTU STATISTIK
# ================================
col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.4, 1.4])

with col1:
    mean_val = df["unpkpd"].mean()
    st.markdown(f"""
    <div style="background-color:#EDF8F4;padding:20px;border-radius:12px;">
        <h4 style="margin:0;">Unmet Need</h4>
        <h1 style="color:#0F3D28;">{mean_val:.1f}%</h1>
        <p style="font-size:14px;margin:0;">Penyandang disabilitas dengan kebutuhan layanan kesehatan yang tidak terpenuhi</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    tinggi = df[df["cat_unpk"] == "Tinggi"].shape[0]
    sedang = df[df["cat_unpk"] == "Sedang"].shape[0]
    rendah = df[df["cat_unpk"] == "Rendah"].shape[0]
    st.markdown(f"""
    <div style="background-color:#F4F6F8;padding:20px;border-radius:12px;">
        <h4 style="margin:0;">Sebaran Wilayah</h4>
        <p>Tinggi: <b>{tinggi}</b></p>
        <p>Sedang: <b>{sedang}</b></p>
        <p>Rendah: <b>{rendah}</b></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    top3 = df.nlargest(3, "unpkpd")
    st.markdown("""
    <div style="background-color:#FFF3E0;padding:20px;border-radius:12px;">
        <h4 style="margin:0;">Kabupaten/Kota Tertinggi</h4>
    """, unsafe_allow_html=True)
    for _, row in top3.iterrows():
        st.markdown(
            f"<p style='margin:4px 0;'><b>{row['name_kabkot']}</b>: <span style='color:#F9893E;'>{row['unpkpd']:.1f}%</span></p>",
            unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    bottom = df.nsmallest(1, "unpkpd").iloc[0]
    st.markdown(f"""
    <div style="background-color:#E7F6ED;padding:20px;border-radius:12px;">
        <h4 style="margin:0;">Kabupaten/Kota Terendah</h4>
        <h3 style="color:#0F3D28;">{bottom['name_kabkot']}</h3>
        <h2 style="color:#0F3D28;">{bottom['unpkpd']:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

# ================================
#         PETA INTERAKTIF
# ================================
st.markdown("<h2 style='margin-top:40px;'>🗺️ Peta Interaktif</h2>", unsafe_allow_html=True)

# Dropdown Filter
col_kat, col_rse = st.columns([1, 1])
with col_kat:
    kategori_filter = st.selectbox("Pilih Kategori Unmet Need", options=["Semua"] + sorted(df["cat_unpk"].unique()))
with col_rse:
    kualitas_filter = st.selectbox("Pilih Kualitas Estimasi", options=["Semua"] + sorted(df["cat_rse"].unique()))

# Filter Data
gdf_filtered = gdf_merged.copy()
if kategori_filter != "Semua":
    gdf_filtered = gdf_filtered[gdf_filtered["cat_unpk"] == kategori_filter]
if kualitas_filter != "Semua":
    gdf_filtered = gdf_filtered[gdf_filtered["cat_rse"] == kualitas_filter]

# Tooltip
gdf_filtered["tooltip_text"] = (
    "<b>" + gdf_filtered["name_kabkot"] + "</b><br>"
    + "Unmet Need: " + gdf_filtered["unpkpd"].round(1).astype(str) + "%<br>"
    + "Kategori: " + gdf_filtered["cat_unpk"] + "<br>"
    + "Kualitas: " + gdf_filtered["cat_rse"]
)

# Peta Folium
m = folium.Map(location=[-7.5, 110.0], zoom_start=7.2, tiles="cartodbpositron", control_scale=True)

def style_function(feature):
    kategori = feature["properties"].get("cat_unpk", "")
    return {
        "fillColor": kategori_colors.get(kategori, "gray"),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7
    }

folium.GeoJson(
    gdf_filtered,
    tooltip=folium.GeoJsonTooltip(
        fields=["tooltip_text"],
        aliases=[""],
        sticky=True,
        labels=False,
        style=("background-color: white; padding: 5px;")
    ),
    style_function=style_function,
    highlight_function=lambda feature: {
        "weight": 3,
        "color": "blue",
        "fillOpacity": 0.9
    }
).add_to(m)

# Legend
legend_items = "".join(
    f"<span style='background-color:{kategori_colors[k]};'>&nbsp;&nbsp;&nbsp;&nbsp;</span> {k}<br>"
    for k in kategori_colors
)
legend_html = f"""
<div style='position: fixed; bottom: 70px; left: 30px; width: 180px; height: auto;
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
     padding: 10px; border-radius: 8px'>
<b>Legenda:</b><br>
{legend_items}
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=1000, height=600)

# ================================
#             FOOTER
# ================================
st.markdown("""<hr/>
<center>
2025 Skripsi TA | D-IV Komputasi Statistik | Politeknik Statistika STIS <br>
Email: 222112380@stis.ac.id
</center>
""", unsafe_allow_html=True)
