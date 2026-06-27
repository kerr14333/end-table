# Parametric End Table — built with FreeCAD 1.1 (Part workbench)
# Run headless from the project root:
#   "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe" scripts\build_end_table.py
# Writes model/end_table.FCStd and model/end_table.stl.
#
# Design: cherry, 3/4" stock.
#   - Top: 20 x 8-1/4 x 3/4", vertical corners filleted at 1-1/8" radius, with a
#     45-deg routed chamfer on the underside edge and an eased top edge.
#   - Two X-frames (visible as an "X" from the long side), each = two tapered
#     boards (2-1/2" wide at top, 1-1/4" at the foot) joined by a HALF-LAP at the
#     crossing (a real boolean cut: each board loses half its thickness there).
#   - One central stretcher ties the two frames together for side-to-side rigidity.
#
# Coordinate system (inches, converted to mm for the document):
#   X = length (20)   Y = width (8.25)   Z = height (24)

import math
from pathlib import Path
import FreeCAD as App
import Part

IN = 25.4  # FreeCAD documents are unitless = mm; build in inches and convert.

# Resolve output paths relative to this script (scripts/ -> project root).
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------- parameters
TOP_LEN   = 20.0
TOP_WID   = 8.25         # fixed width -- do not change
TOP_THK   = 0.75
CORNER_R  = 1.125
TOTAL_H   = 24.0
STOCK     = 0.75          # leg-board thickness (Y direction)
LEG_W_TOP = 2.5           # board width at the top tip
LEG_W_FOOT= 1.25          # board width at the foot
END_EXT   = 3.0           # how far to over-build each board before trimming flat

# Top underside edge bevel, cut with a bearing-guided 45-deg chamfer bit:
#   field stays TOP_THK; the perimeter shows a vertical EDGE_BAND, then a 45-deg
#   chamfer runs up/inward over BEVEL_RUN to the flat field on the bottom.
#   With EDGE_BAND + BEVEL_RUN == TOP_THK and run == rise, the bevel is 45 deg
#   (set the chamfer bit to a 1/2" depth of cut).
EDGE_BAND = 0.25          # visible vertical thickness at the very edge (1/4")
BEVEL_RUN = 0.5           # 45-deg chamfer width = TOP_THK - EDGE_BAND

# Soft "mid-century" eased top edge (a small roundover) to echo the chair.
EASE_R = 0.125            # 1/8" roundover on the top's upper perimeter edge

LEG_TOP_Z = TOTAL_H - TOP_THK     # 23.25 -> legs meet underside of top

# foot / tip X-positions of an X-frame (legs pulled inboard so the top
# overhangs the ends; feet stay splayed past the tips for a wide stance)
FOOT_L, FOOT_R = 3.0, 17.0
TIP_L,  TIP_R  = 4.5, 15.5

# Y-centerlines of the two frames (1.5" overhang each side of the 7" top)
OVERHANG = 1.5
FRAME_A_Y0 = OVERHANG - STOCK / 2.0          # near face of frame A boards
FRAME_B_Y0 = (TOP_WID - OVERHANG) - STOCK / 2.0

# big clip box used to trim boards flat at floor (Z=0) and underside of top
CLIP = Part.makeBox(40 * IN, 12 * IN, LEG_TOP_Z * IN, App.Vector(-6 * IN, -3 * IN, 0))


def tapered_board(foot_x, tip_x):
    """A flat, tapered board (thickness in Y, Y in [0, STOCK]), running on the
    diagonal from foot (foot_x, Z=0) to tip (tip_x, Z=LEG_TOP_Z), over-built past
    both ends then trimmed flat by CLIP so the foot and top seat squarely."""
    dx, dz = (tip_x - foot_x), LEG_TOP_Z
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L            # unit vector along the board length
    nx, nz = -uz, ux                   # perpendicular, in the X-Z plane
    slope = (LEG_W_TOP - LEG_W_FOOT) / L
    # half-widths at the extended ends so the taper hits the exact target
    # widths at the real foot / tip after trimming
    hF = (LEG_W_FOOT - slope * END_EXT) / 2.0
    hT = (LEG_W_TOP  + slope * END_EXT) / 2.0
    fx, fz = foot_x - ux * END_EXT, 0.0 - uz * END_EXT
    tx, tz = tip_x  + ux * END_EXT, LEG_TOP_Z + uz * END_EXT

    def P(px, pz):
        return App.Vector(px * IN, 0.0, pz * IN)

    c1 = P(fx + nx * hF, fz + nz * hF)
    c2 = P(fx - nx * hF, fz - nz * hF)
    c3 = P(tx - nx * hT, tz - nz * hT)
    c4 = P(tx + nx * hT, tz + nz * hT)
    face = Part.Face(Part.makePolygon([c1, c2, c3, c4, c1]))
    solid = face.extrude(App.Vector(0, STOCK * IN, 0))
    return solid.common(CLIP)


def half_lapped_pair():
    """Build one X-frame's two boards and cut a half-lap where they cross."""
    leg_a = tapered_board(FOOT_L, TIP_R)   # "/"  foot-left  -> tip-right
    leg_b = tapered_board(FOOT_R, TIP_L)   # "\"  foot-right -> tip-left
    overlap = leg_a.common(leg_b)          # full-thickness block at the crossing
    yc = STOCK / 2.0
    front = Part.makeBox(40 * IN, (STOCK / 2.0) * IN, 40 * IN,
                         App.Vector(-6 * IN, yc * IN, -6 * IN))   # Y in [yc, STOCK]
    back  = Part.makeBox(40 * IN, (STOCK / 2.0) * IN, 40 * IN,
                         App.Vector(-6 * IN, 0.0,      -6 * IN))   # Y in [0, yc]
    leg_a = leg_a.cut(overlap.common(front))   # leg_a keeps its back half at lap
    leg_b = leg_b.cut(overlap.common(back))    # leg_b keeps its front half at lap
    return leg_a, leg_b


def placed(shape, y_off):
    s = shape.copy()
    s.translate(App.Vector(0, y_off * IN, 0))
    return s


# ------------------------------------------------------------------- build it
leg_a, leg_b = half_lapped_pair()
fA_a, fA_b = placed(leg_a, FRAME_A_Y0), placed(leg_b, FRAME_A_Y0)
fB_a, fB_b = placed(leg_a, FRAME_B_Y0), placed(leg_b, FRAME_B_Y0)

# Top: full thickness in the field, rounded vertical corners, with a 45-deg
# chamfer routed on the underside perimeter so the overhanging edge reads thin.
z_top = LEG_TOP_Z + TOP_THK            # 24.0  (top surface)
z_band = z_top - EDGE_BAND             # underside of the vertical edge band
z_bot = LEG_TOP_Z                      # 23.25 flat field where the legs land

slab = Part.makeBox(TOP_LEN * IN, TOP_WID * IN, TOP_THK * IN,
                    App.Vector(0, 0, z_bot * IN))
vert_edges = [e for e in slab.Edges
              if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) < 1e-6
              and abs(e.Vertexes[0].Point.y - e.Vertexes[1].Point.y) < 1e-6
              and abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6]
slab = slab.makeFillet(CORNER_R * IN, vert_edges)

# outer rounded-rect wire (top face) and an inset copy that defines the chamfer
top_face = max(slab.Faces, key=lambda f: f.CenterOfMass.z)
wO = top_face.OuterWire
wI = wO.makeOffset2D(-BEVEL_RUN * IN)
if wI.ShapeType != "Wire":
    wI = wI.Wires[0]

def at_z(wire, z):
    w = wire.copy()
    w.translate(App.Vector(0, 0, (z - z_top) * IN))
    return w

plate = Part.Face(at_z(wO, z_band)).extrude(App.Vector(0, 0, EDGE_BAND * IN))
core = Part.Face(at_z(wI, z_bot)).extrude(App.Vector(0, 0, (z_top - z_bot) * IN))
skirt = Part.makeLoft([at_z(wI, z_bot), at_z(wO, z_band)], True)
top = plate.fuse(core).fuse(skirt).removeSplitter()

# Ease the upper perimeter edge with a small roundover (mid-century soft edge)
top_edges = [e for e in top.Edges
             if abs(e.Vertexes[0].Point.z - z_top * IN) < 1e-3
             and abs(e.Vertexes[1].Point.z - z_top * IN) < 1e-3]
top = top.makeFillet(EASE_R * IN, top_edges)

# Central stretcher: butts against the inner face of each frame at the crossing
A_inner = FRAME_A_Y0 + STOCK     # 1.875
B_inner = FRAME_B_Y0             # 5.125
SX0, SX1 = 9.625, 10.375   # 3/4" stock, centered on the crossing at X=10
SZ0, SZ1 = 11.75, 14.25    # 2.5" tall, centered on the ~Z13 crossing
stretcher = Part.makeBox((SX1 - SX0) * IN, (B_inner - A_inner) * IN, (SZ1 - SZ0) * IN,
                         App.Vector(SX0 * IN, A_inner * IN, SZ0 * IN))

# ------------------------------------------------------------------- document
doc = App.newDocument("EndTable")
parts = [
    ("Top",            top),
    ("Frame1_LegFwd",  fA_a),
    ("Frame1_LegBack", fA_b),
    ("Frame2_LegFwd",  fB_a),
    ("Frame2_LegBack", fB_b),
    ("Stretcher",      stretcher),
]
for name, shp in parts:
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shp
doc.recompute()

out_fcstd = str(MODEL_DIR / "end_table.FCStd")
doc.saveAs(out_fcstd)

# Bonus mesh export for quick viewing / 3D apps
comp = Part.makeCompound([shp for _, shp in parts])
comp.exportStl(str(MODEL_DIR / "end_table.stl"))

# ------------------------------------------------------------------- report
bb = comp.BoundBox
print("Saved:", out_fcstd)
print("Overall (in):  L=%.2f  W=%.2f  H=%.2f" %
      (bb.XLength / IN, bb.YLength / IN, bb.ZLength / IN))
for name, shp in parts:
    print("  %-14s volume = %7.1f in^3" % (name, shp.Volume / (IN ** 3)))
