import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
from io import BytesIO

st.header("🏞️ Konversi KML ke WKT (Polygon)")

kml_file = st.file_uploader("📤 Unggah file KML", type=["kml"])

if kml_file is not None:
    try:
        # Parse KML file
        tree = ET.parse(kml_file)
        root = tree.getroot()

        # Namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Cari semua Placemark
        placemarks = root.findall(".//kml:Placemark", ns)

        # Proses setiap polygon
        polygons_data = []
        for pm in placemarks:
            name = pm.findtext("kml:name", default="", namespaces=ns)
            desc = pm.findtext("kml:description", default="", namespaces=ns)
            coord_elem = pm.find(".//kml:LinearRing/kml:coordinates", ns)

            if coord_elem is not None:
                raw_coords = coord_elem.text.strip()
                coord_pairs = []
                for coord in raw_coords.split():
                    parts = coord.split(",")
                    if len(parts) >= 2:
                        lon, lat = float(parts[0]), float(parts[1])
                        coord_pairs.append((lon, lat))
                if len(coord_pairs) >= 3:
                    # Tutup polygon jika belum tertutup
                    if coord_pairs[0] != coord_pairs[-1]:
                        coord_pairs.append(coord_pairs[0])
                    poly = Polygon(coord_pairs)
                    polygons_data.append({
                        "Nama": name,
                        "Deskripsi": desc,
                        "WKT": poly.wkt
                    })

        # Tampilkan hasil
        if polygons_data:
            df_kml_wkt = pd.DataFrame(polygons_data)
            st.success(f"✅ Ditemukan {len(df_kml_wkt)} Polygon.")
            st.dataframe(df_kml_wkt)

            # Tombol download Excel
            xlsx_buffer = BytesIO()
            df_kml_wkt.to_excel(xlsx_buffer, index=False)
            st.download_button(
                label="⬇️ Download Excel (WKT)",
                data=xlsx_buffer.getvalue(),
                file_name="output_polygon_wkt.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Tidak ditemukan polygon di dalam file KML.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file KML: {str(e)}")
