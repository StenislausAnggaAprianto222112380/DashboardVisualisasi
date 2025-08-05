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

#GAMBAR KONTEN
st.markdown("""
<div style="display: flex; justify-content: center;">
    <img src="https://raw.githubusercontent.com/StenislausAnggaAprianto222112380/DashboardVisualisasi/refs/heads/main/unpkpd.jpg"
         alt="UNPKPD"
         title="Sumber gambar: Freepik.com"
         style="max-width: 500px; width: 100%; height: auto; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" />
</div>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>Dashboard Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas di Pulau Jawa Tahun 2023</h1>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: justify; max-width: 1000px; margin: auto; font-size:16px;">
    <p>
        <b>Unmet need pelayanan kesehatan</b> menunjukkan persentase penduduk yang seharusnya berobat ketika sakit dan terganggu aktivitasnya 
        tetapi tidak melakukan pengobatan karena disebabkan oleh beberapa hal, seperti kurangnya dana untuk melakukan pengobatan, 
        kurangnya dana untuk transportasi, tidak terdapat sarana transportasi yang memadai, atau waktu tunggu pelayanan kesehatan yang lama. 
        (<i>BPS, 2023</i>).
    </p>
    <p>
        <b>Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas (UNPK PD)</b> adalah hasil disagregasi dari kejadian unmet need pelayanan kesehatan 
        menjadi subpopulasi disabilitas (<i>Bappenas, 2020</i>).
    </p>
</div>
""", unsafe_allow_html=True)


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

st.markdown("## Statistik UNPKPD")

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
        <h1 style="margin-bottom: 0;">{len(kategori_counts)} Kategori</h1>
        <p style="margin-top: 0; line-height:1.2;">{kategori_display}</p>
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
ordered_kategori = ["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
kategori_opsi = ["Semua"] + [k for k in ordered_kategori if k in gdf["cat_unpk"].unique()]

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

# --- CEK DATA HASIL FILTER ---
if filtered_gdf.empty:
    st.warning("Tidak ada kategori yang anda minta!")
else:
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

    # --- LEGEND HTML ---
    legend_html = """
    <div style="
        position: fixed; 
        bottom: 40px; left: 40px; width: 200px; 
        background-color: white;
        border:2px solid grey; 
        z-index:9999; 
        font-size:14px;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b>Legenda Kategori UNPKPD</b><br>
        <i style="background:#b7f7a5;width:18px;height:18px;float:left;margin-right:8px;"></i>Sangat Rendah [2.37%-7.38%]<br>
        <i style="background:#f7f79c;width:18px;height:18px;float:left;margin-right:8px;"></i>Rendah        [7.38%-12.39%]<br>
        <i style="background:#fca15e;width:18px;height:18px;float:left;margin-right:8px;"></i>Sedang        [12.39%-17.39%]<br>
        <i style="background:#f75d59;width:18px;height:18px;float:left;margin-right:8px;"></i>Tinggi        [17.39%-22.40%]<br>
        <i style="background:#8b0000;width:18px;height:18px;float:left;margin-right:8px;"></i>Sangat Tinggi [22.40%-27.41%]
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))


    st.markdown("### Peta Interaktif")
    st_folium(m, width=1200, height=600)

# --- FOOTER ---
st.markdown("""
<hr style="margin-top: 50px; margin-bottom: 10px;">
<div style="text-align: center; font-size: 14px; color: grey;">
    Dikembangkan oleh <b>Stenislaus Angga Aprianto</b> &nbsp; | &nbsp; Politeknik Statistika STIS &nbsp; | &nbsp; 2025
</div>
""", unsafe_allow_html=True)
