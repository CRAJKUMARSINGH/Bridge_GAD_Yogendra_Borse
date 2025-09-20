import streamlit as st
import os
import sys
from pathlib import Path
import pandas as pd
import base64
from datetime import datetime

# Ensure we can import the package from src/
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bridge_gad.bridge_generator import BridgeGADGenerator
from bridge_gad.output_formats import MultiFormatExporter

st.set_page_config(page_title="BridgeGAD UI", page_icon="🌉", layout="wide")

st.title("🌉 BridgeGAD-00 Interactive UI")
st.write("Upload Excel parameters and generate DXF/PDF/HTML/SVG/PNG outputs using the enhanced generator.")

# State
if "result" not in st.session_state:
    st.session_state.result = None

uploaded = st.file_uploader("Upload Excel file (three columns: Value, Variable, Description)", type=["xlsx","xls"])

col1, col2 = st.columns(2)
with col1:
    fmt_html = st.checkbox("Export HTML (canvas)", value=True)
    fmt_pdf = st.checkbox("Export PDF", value=True)
    fmt_svg = st.checkbox("Export SVG", value=True)
    fmt_png = st.checkbox("Export PNG", value=False)
with col2:
    open_canvas = st.checkbox("Open HTML in browser after export (CLI only)", value=False, help="This option is relevant when running via CLI; in Streamlit we provide a download instead.")

if uploaded is not None:
    st.success(f"File uploaded: {uploaded.name}")

    # Preview
    with st.expander("Preview uploaded file (first 10 rows)"):
        try:
            df_preview = pd.read_excel(uploaded, header=None)
            st.dataframe(df_preview.head(10))
        except Exception as e:
            st.error(f"Could not preview file: {e}")

    if st.button("Generate Outputs", type="primary"):
        with st.spinner("Generating bridge drawing..."):
            temp_dir = ROOT / ".ui_temp"
            out_root = ROOT / "UI_OUTPUTS"
            temp_dir.mkdir(exist_ok=True)
            out_root.mkdir(exist_ok=True)

            temp_in = temp_dir / uploaded.name
            with open(temp_in, "wb") as f:
                f.write(uploaded.getbuffer())

            # Use generator to create DXF first
            gen = BridgeGADGenerator()
            out_base = out_root / Path(uploaded.name).stem
            out_base.parent.mkdir(exist_ok=True, parents=True)
            dxf_out = out_base.with_suffix(".dxf")

            ok = gen.generate_complete_drawing(temp_in, dxf_out)
            if not ok:
                st.error("Failed to generate bridge drawing from the uploaded Excel.")
            else:
                # Multi-format export
                exporter = MultiFormatExporter(gen)
                formats = []
                if fmt_pdf:
                    formats.append("pdf")
                if fmt_html:
                    formats.append("html")
                if fmt_svg:
                    formats.append("svg")
                if fmt_png:
                    formats.append("png")

                generated = {"dxf": dxf_out if dxf_out.exists() else None}
                for fmt in formats:
                    try:
                        path = exporter.export(out_base.with_suffix(f".{fmt}"), fmt)
                        generated[fmt] = path if Path(path).exists() else None
                    except Exception as e:
                        generated[fmt] = None
                        st.warning(f"Failed to export {fmt.upper()}: {e}")

                st.session_state.result = {"base": str(out_base), "files": {k: str(v) if v else None for k, v in generated.items()}}
                st.success("Generation completed.")

# Results display
res = st.session_state.result
if res:
    st.header("Results")
    files = res["files"]
    for fmt in ["dxf", "pdf", "svg", "html", "png"]:
        p = files.get(fmt)
        if p and os.path.exists(p):
            st.write(f"✅ {fmt.upper()} generated: {p}")
            with open(p, "rb") as f:
                data = f.read()
                mime = {
                    "dxf": "application/octet-stream",
                    "pdf": "application/pdf",
                    "svg": "image/svg+xml",
                    "html": "text/html",
                    "png": "image/png",
                }.get(fmt, "application/octet-stream")
                st.download_button(label=f"Download {fmt.upper()}", data=data, file_name=Path(p).name, mime=mime)
        else:
            st.write(f"❌ {fmt.upper()} not available.")
