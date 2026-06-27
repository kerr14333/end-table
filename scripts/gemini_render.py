# Photorealistic rendering of the end table next to the chair, via Gemini.
#   - Image 1: the real chair photo (the scene to edit).
#   - Image 2: a clean CAD shape-guide render of the table (geometry to honor).
# Requires GEMINI_API_KEY in the environment and `pip install google-genai`.
import io
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from google import genai
from google.genai import types

IN = 25.4
ROOT = Path(__file__).resolve().parents[1]
STL = str(ROOT / "model" / "end_table.stl")
CHAIR = str(ROOT / "reference" / "chair.jpeg")
GUIDE = str(ROOT / "renders" / "table_clean.png")
OUT = str(ROOT / "renders" / "table_with_chair_realistic")

PROMPT = """Insert the custom end table shown in the second image into the real
photograph shown in the first image. This is a photorealistic interior product
visualization.

Placement: stand the table on the hardwood floor close beside the RIGHT side of
the leather armchair, as a side table, nearly touching the chair.

SCALE (use the chair to size it): the armchair is 30 inches tall overall. Make
the end table 24 inches tall -- exactly 80% of the chair's height -- so the
tabletop lands right at the TOP OF THE CHAIR'S ARMREST. Do not make it smaller
than that; its top must clearly reach armrest height.

ORIENTATION (most important): align the table PARALLEL to the armchair. The
table's LONG axis must run the same direction as the chair -- front-to-back,
parallel to the chair's arm and the line of its seat -- so that the long edge
of the tabletop is parallel to the chair's arm and the short end of the table
faces the camera/front of the room. The table should look squarely aligned and
flush with the chair, like a matching companion side table, NOT rotated,
angled, skewed, or turned diagonally relative to the chair. Its feet sit flat
and square to the chair.

Keep everything else in the photo exactly as it is.

The table is solid CHERRY wood. Render it photorealistically with natural wood
grain and a warm satin oil finish. CRITICAL: keep the exact geometry and
proportions from the second image -- two crossed (X-shaped) tapered legs that
are wider at the top and narrower at the feet, joined by a half-lap where they
cross, supporting a thin floating top whose underside edge is chamfered, with
softly rounded corners.

Match the room's lighting: soft daylight coming from the window on the left.
Add a realistic soft contact shadow where the legs meet the floor, and a subtle
reflection on the hardwood. Output one single photorealistic image, same
viewpoint and framing as the original photo."""


def render_guide(elev=12, azim=-72, px=1200):
    """A clean cherry-shaded render of the table on transparent background."""
    data = open(STL, "rb").read().decode("ascii", "ignore").splitlines()
    verts = [ln.split()[1:4] for ln in data if ln.strip().startswith("vertex")]
    tris = np.array(verts, float).reshape(-1, 3, 3) / IN
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    shade = 0.45 + 0.55 * np.clip(n @ L, 0, 1)
    cols = np.clip(shade[:, None] * np.array([0.52, 0.26, 0.16]), 0, 1)
    cols = np.hstack([cols, np.ones((len(cols), 1))])
    fig = plt.figure(figsize=(px / 150, px / 150), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1], projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))
    pts = tris.reshape(-1, 3); mn, mx = pts.min(0), pts.max(0)
    c = (mn + mx) / 2; r = (mx - mn).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    fig.savefig(GUIDE, transparent=True); plt.close(fig)
    img = Image.open(GUIDE).convert("RGBA")
    img = img.crop(img.getbbox()); img.save(GUIDE)
    return img


def main():
    guide = render_guide()
    chair = Image.open(CHAIR).convert("RGB")
    client = genai.Client()

    model = sys.argv[1] if len(sys.argv) > 1 else "gemini-3-pro-image"
    configs = [
        types.GenerateContentConfig(response_modalities=["Image"],
                                    image_config=types.ImageConfig(aspect_ratio="4:3")),
        types.GenerateContentConfig(response_modalities=["Image"]),
        None,
    ]
    last_err = None
    for cfg in configs:
        try:
            resp = client.models.generate_content(
                model=model, contents=[PROMPT, chair, guide], config=cfg)
            saved = 0
            for cand in resp.candidates or []:
                for part in (cand.content.parts if cand.content else []):
                    if getattr(part, "inline_data", None) and part.inline_data.data:
                        out = f"{OUT}.png" if saved == 0 else f"{OUT}_{saved}.png"
                        Image.open(io.BytesIO(part.inline_data.data)).save(out)
                        print("saved", out)
                        saved += 1
                    elif getattr(part, "text", None):
                        print("model text:", part.text[:300])
            if saved:
                return
            last_err = "no image parts returned"
        except Exception as e:
            last_err = repr(e)
            print("config attempt failed:", last_err[:200])
    print("FAILED:", last_err)
    sys.exit(1)


main()
