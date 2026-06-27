# Render preview images of the end table from the exported STL (mm).
import struct
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

IN = 25.4
ROOT = Path(__file__).resolve().parents[1]
STL = str(ROOT / "model" / "end_table.stl")


def read_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    # binary STL: 80-byte header + uint32 count + 50 bytes/triangle
    if not data[:5].lower().startswith(b"solid") or b"facet" not in data[:512]:
        n = struct.unpack("<I", data[80:84])[0]
        if 84 + n * 50 == len(data):
            tris = np.frombuffer(data[84:], dtype=np.uint8).reshape(n, 50)
            floats = tris[:, 12:48].copy().view("<f4").reshape(n, 3, 3)
            return floats / IN
    # ASCII STL
    verts = [line.split()[1:4] for line in data.decode("ascii", "ignore").splitlines()
             if line.strip().startswith("vertex")]
    arr = np.array(verts, dtype=float).reshape(-1, 3, 3)
    return arr / IN  # mm -> inches


tris = read_stl(STL)
print("triangles:", len(tris))

views = [("iso", 22, -60), ("front", 0, -90), ("end", 0, 0), ("top", 89, -90)]
fig = plt.figure(figsize=(13, 11))
for i, (name, elev, azim) in enumerate(views, 1):
    ax = fig.add_subplot(2, 2, i, projection="3d")
    pc = Poly3DCollection(tris, facecolor="#b5651d", edgecolor="#5c3a16",
                          linewidths=0.15, alpha=1.0)
    ax.add_collection3d(pc)
    pts = tris.reshape(-1, 3)
    mins, maxs = pts.min(0), pts.max(0)
    ctr = (mins + maxs) / 2
    r = (maxs - mins).max() / 2
    ax.set_xlim(ctr[0] - r, ctr[0] + r)
    ax.set_ylim(ctr[1] - r, ctr[1] + r)
    ax.set_zlim(ctr[2] - r, ctr[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title("%s view" % name)
    ax.set_xlabel("X len"); ax.set_ylabel("Y wid"); ax.set_zlabel("Z ht")
fig.tight_layout()
renders = ROOT / "renders"; renders.mkdir(exist_ok=True)
out = str(renders / "end_table_preview.png")
fig.savefig(out, dpi=110)
print("saved", out)
