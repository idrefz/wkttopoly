import streamlit as st
import pandas as pd
from shapely import wkt
from shapely.geometry import Polygon
import simplekml
import tempfile
from fastkml import kml
from io import BytesIO

st.set_page_config(page_title="WKT ↔ KML Converter", layout="wide")

st.title("🗺️ Konversi WKT ⇄ KML")

mode = st.radio("Pilih Mode Konversi", ["WKT ke KML", "KML ke WKT"])

# ================================
# MODE 1: WKT to KML
# ================================
if mode == "WKT ke KML":
    uploaded_file = st.file_uploader("Unggah file Excel (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File berhasil dibaca.")
        st.dataframe(df)

        st.markdown("### 🔧 Pilih Kolom:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name_col = st.selectbox("📛 Kolom Nama Polygon", options=df.columns)
        with col2:
            desc_col = st.selectbox("📝 Kolom Deskripsi", options=df.columns)
        with col3:
            wkt_col = st.selectbox("📐 Kolom WKT Polygon", options=df.columns)

        if st.button("🔄 Konversi ke KML"):
            kml_obj = simplekml.Kml()
            error_rows = []

            for idx, row in df.iterrows():
                try:
                    geom = wkt.loads(row[wkt_col])
                    if geom.geom_type == "Polygon":
                        coords = [(x, y) for x, y in geom.exterior.coords]
                        pol = kml_obj.newpolygon(name=str(row[name_col]), outerboundaryis=coords)
                        pol.description = str(row[desc_col])
                        pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.blue)
                        pol.style.linestyle.color = simplekml.Color.blue
                        pol.style.linestyle.width = 2
                    else:
                        error_rows.append(idx)
                except:
                    error_rows.append(idx)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp:
                kml_obj.save(tmp.name)
                tmp.seek(0)
                kml_bytes = tmp.read()

            st.success("🎉 File KML berhasil dibuat!")

            st.download_button("⬇️ Download KML", data=kml_bytes, file_name="output_polygon.kml",
                               mime="application/vnd.google-earth.kml+xml")

            if error_rows:
                st.warning(f"⚠️ {len(error_rows)} baris gagal dikonversi.")

# ================================
# MODE 2: KML to WKT
# ================================
elif mode == "KML ke WKT":
    kml_file = st.file_uploader("Unggah file KML", type=["kml"])

    if kml_file is not None:
        try:
            kml_content = kml_file.read()
            k = kml.KML()
            k.from_string(kml_content)
            wkt_data = []

            for feature in list(k.features()):
                for placemark in list(feature.features()):
                    if hasattr(placemark, 'geometry') and isinstance(placemark.geometry, Polygon):
                        name = placemark.name
                        desc = placemark.description or ""
                        wkt_text = placemark.geometry.wkt
                        wkt_data.append({"Nama": name, "Deskripsi": desc, "WKT": wkt_text})

            if wkt_data:
                df_wkt = pd.DataFrame(wkt_data)
                st.success("✅ Data berhasil diekstrak dari KML.")
                st.dataframe(df_wkt)

                xlsx_buffer = BytesIO()
                df_wkt.to_excel(xlsx_buffer, index=False)
                st.download_button("⬇️ Download Excel (WKT)", data=xlsx_buffer.getvalue(),
                                   file_name="output_wkt.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.warning("⚠️ Tidak ditemukan data Polygon dalam file KML.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file KML: {str(e)}")
