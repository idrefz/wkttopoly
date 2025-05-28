
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
    # Baca file Excel
    df = pd.read_excel(uploaded_file)
    st.success("File berhasil dibaca. Berikut isi datanya:")
    st.dataframe(df)

    # Periksa kolom penting
    if "Polygon dalam Format WKT" not in df.columns:
        st.error("Kolom 'Polygon dalam Format WKT' tidak ditemukan di file Excel.")
    else:
        # Tombol untuk generate KML
        if st.button("🔄 Konversi ke KML"):
            kml = simplekml.Kml()
            error_rows = []

            for idx, row in df.iterrows():
                try:
                    polygon_wkt = row["Polygon dalam Format WKT"]
                    odc_name = str(row["ODC"]) if "ODC" in row else f"Polygon_{idx+1}"
                    geom = wkt.loads(polygon_wkt)

                    if geom.geom_type == "Polygon":
                        coords = [(lon, lat) for lon, lat in geom.exterior.coords]
                        pol = kml.newpolygon(name=odc_name, outerboundaryis=coords)
                        pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.blue)
                        pol.style.linestyle.color = simplekml.Color.blue
                        pol.style.linestyle.width = 2
                    else:
                        error_rows.append(idx)
                except Exception as e:
                    error_rows.append(idx)

            # Simpan ke file sementara, lalu baca isinya sebagai byte
            with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp:
                kml.save(tmp.name)
                tmp.seek(0)
                kml_bytes = tmp.read()

            st.success("File KML berhasil dibuat!")

            # Tombol download
            st.download_button(
                label="⬇️ Download KML",
                data=kml_bytes,
                file_name="output_polygon.kml",
                mime="application/vnd.google-earth.kml+xml"
            )

            if error_rows:
                st.warning(f"{len(error_rows)} baris gagal dikonversi (bukan Polygon atau error lainnya).")
