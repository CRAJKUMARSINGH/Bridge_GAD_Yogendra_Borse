import streamlit as st
import pandas as pd
from pathlib import Path
import pygltflib as pygltf
from .mesh_builder import build_bridge_mesh

def run_living_gad(excel_path: Path):
    st.set_page_config(page_title="Living Bridge GAD", layout="wide")
    st.title("🌉  Living Bridge GAD")

    df = pd.read_excel(excel_path)

    with st.sidebar:
        thickness = st.slider("Slab thickness (m)", 0.2, 1.5, 0.5, 0.05)
        pier_width = st.slider("Pier width (m)", 0.5, 3.0, 1.0, 0.1)

    vertices, faces = build_bridge_mesh(df, thickness, pier_width)
    st.write("### 3-D preview (rotate with mouse)")
    st.write(pygltf.quickview(vertices, faces))

    if st.button("Export glTF"):
        out = Path("bridge.gltf")
        pygltf.save(out, vertices, faces)
        with open(out, "rb") as f:
            st.download_button("Download glTF", f.read(), "bridge.gltf")
