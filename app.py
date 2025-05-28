import streamlit as st
import pandas as pd
from shapely import wkt
import simplekml
import tempfile

st.set_page_config(page_title="WKT to KML Converter", layout="wide")

st.title("🗺️ Konversi WKT Polygon ke KML")

# Upload file Excel
uploaded_file = st.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Baca isi file
    df = pd.read_excel(uploaded_file)
    st.success("✅ File berhasil dibaca.")
    st.dataframe(df)

    # Pilihan kolom
    st.markdown("### 🔧 Pilih Kolom:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name_col = st.selectbox("📛 Kolom untuk Nama Polygon", options=df.columns)
    with col2:
        desc_col = st.selectbox("📝 Kolom untuk Deskripsi", options=df.columns)
    with col3:
        wkt_col = st.selectbox("📐 Kolom untuk WKT Polygon", options=df.columns)

    # Tombol konversi
    if st.button("🔄 Konversi ke KML"):
        kml = simplekml.Kml()
        error_rows = []

        for idx, row in df.iterrows():
            try:
                polygon_wkt = row[wkt_col]
                polygon_name = str(row[name_col])
                polygon_desc = str(row[desc_col])
                geom = wkt.loads(polygon_wkt)

                if geom.geom_type == "Polygon":
                    coords = [(lon, lat) for lon, lat in geom.exterior.coords]
                    pol = kml.newpolygon(name=polygon_name, outerboundaryis=coords)
                    pol.description = polygon_desc
                    pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.blue)
                    pol.style.linestyle.color = simplekml.Color.blue
                    pol.style.linestyle.width = 2
                else:
                    error_rows.append(idx)
            except Exception as e:
                error_rows.append(idx)

        # Simpan KML ke file sementara
        with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp:
            kml.save(tmp.name)
            tmp.seek(0)
            kml_bytes = tmp.read()

        st.success("🎉 File KML berhasil dibuat!")

        st.download_button(
            label="⬇️ Download KML",
            data=kml_bytes,
            file_name="output_polygon.kml",
            mime="application/vnd.google-earth.kml+xml"
        )

        if error_rows:
            st.warning(f"⚠️ {len(error_rows)} baris gagal dikonversi (bukan Polygon atau error lainnya).")
