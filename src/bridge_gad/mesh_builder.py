import numpy as np

def build_bridge_mesh(df, thickness, pier_width):
    verts, faces = [], []
    x = 0.0
    for _, row in df.iterrows():
        L, W = float(row["Length (m)"]), float(row["Width (m)"])
        for dy in [0, W]:
            for dz in [0, thickness]:
                verts.extend([(x, dy, dz), (x + L, dy, dz)])
        # pier
        for dy in [0, W]:
            for dz in [0, -2.0]:
                verts.extend(
                    [
                        (x + L - pier_width / 2, dy, dz),
                        (x + L + pier_width / 2, dy, dz),
                    ]
                )
        x += L + pier_width
    # simple quad faces
    n = len(verts) // 4
    faces = [[i, i + 1, i + 2, i + 3] for i in range(0, n * 4, 4)]
    return np.array(verts), faces
