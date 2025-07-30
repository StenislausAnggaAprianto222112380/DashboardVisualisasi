
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import numpy as np

# --- DATA DUMMY ---
np.random.seed(42)
kabkota_list = [f"Kab/Kota {i+1}" for i in range(119)]
data = pd.DataFrame({
    "Kabupaten/Kota": kabkota_list,
    "Unmet_Need": np.random.uniform(10, 60, size=119)  # persen
})
data["Kategori"] = pd.cut(
    data["Unmet_Need"],
    bins=[0, 20, 30, 40, 100],
    labels=["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
)

# --- LAYOUT DASHBOARD ---
st.set_page_config(page_title="Dashboard Unmet Need Disabilitas", layout="wide")

st.markdown("### Dashboard Unmet Need Pelayanan Kesehatan pada Penyandang Disabilitas")
st.markdown("#### Tingkat Kabupaten/Kota di Pulau Jawa, Tahun 2023")

# --- STATISTIK RINGKAS ---
col1, col2, col3 = st.columns(3)

with col1:
    mean_prov = data["Unmet_Need"].mean()
    st.metric("Rata-rata Unmet Need Provinsi", f"{mean_prov:.1f}%")

with col2:
    st.markdown("**Sebaran Kabupaten/Kota:**")
    for kategori in ["Sangat Tinggi", "Tinggi", "Sedang", "Rendah"]:
        jumlah = data[data["Kategori"] == kategori].shape[0]
        st.write(f"- {kategori}: {jumlah}")

with col3:
    tertinggi = data.nlargest(3, "Unmet_Need")[["Kabupaten/Kota", "Unmet_Need"]]
    terendah = data.nsmallest(1, "Unmet_Need")
    st.markdown("**Kabupaten/Kota Tertinggi:**")
    for i, row in tertinggi.iterrows():
        st.write(f"{row['Kabupaten/Kota']}: {row['Unmet_Need']:.1f}%")
    st.markdown("---")
    st.markdown(f"**Terendah:** {terendah.iloc[0]['Kabupaten/Kota']} ({terendah.iloc[0]['Unmet_Need']:.1f}%)")

# --- PETA INTERAKTIF (DUMMY POSISI) ---
st.markdown("### Peta Interaktif")

# Simulasi koordinat dummy
data["lat"] = np.random.uniform(-7.5, -6.0, size=119)
data["lon"] = np.random.uniform(106, 111, size=119)

# Filter
kategori_filter = st.selectbox("Pilih Kategori", options=["Semua"] + list(data["Kategori"].unique()))
wilayah_filter = st.selectbox("Pilih Kabupaten/Kota", options=["Semua"] + list(data["Kabupaten/Kota"]))

filtered_data = data.copy()
if kategori_filter != "Semua":
    filtered_data = filtered_data[filtered_data["Kategori"] == kategori_filter]
if wilayah_filter != "Semua":
    filtered_data = filtered_data[filtered_data["Kabupaten/Kota"] == wilayah_filter]

# Buat Peta
m = folium.Map(location=[-7.0, 109.0], zoom_start=7)

colors = {
    "Sangat Tinggi": "darkred",
    "Tinggi": "orange",
    "Sedang": "yellow",
    "Rendah": "green"
}

for _, row in filtered_data.iterrows():
    folium.CircleMarker(
        location=(row["lat"], row["lon"]),
        radius=6,
        color=colors[row["Kategori"]],
        fill=True,
        fill_color=colors[row["Kategori"]],
        popup=f"{row['Kabupaten/Kota']}: {row['Unmet_Need']:.1f}%",
    ).add_to(m)

st_data = st_folium(m, width=1000, height=600)

# Footer
st.markdown("""
<hr/>
<center>
2025 Skripsi TA | D-IV Komputasi Statistik | Politeknik Statistika STIS <br>
Email: 222112300@stis.ac.id
</center>
""", unsafe_allow_html=True)
