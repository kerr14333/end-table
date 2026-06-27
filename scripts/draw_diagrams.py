# Dimensioned shop drawings for the cherry X-leg end table.
#   - Side elevation of the X-frame (heights, foot stance, leg/crossing angles)
#   - End elevation (width, frame spacing, stretcher)
#   - Leg detail (taper, end-cut angle, half-lap)
#   - Top plan (length/width, corner radius, cleat placement)
# Writes SVG (embedded in docs/plans.html) + PNG (for quick eyeballing) to
# docs/diagrams/.  Run:  python scripts\draw_diagrams.py
#
# Geometry mirrors the parameter block in build_end_table.py (the single source
# of truth). Keep these values in sync if that block changes.
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)

# ---- parameters (mirror build_end_table.py) -------------------------------
TOP_LEN, TOP_WID, TOP_THK = 20.0, 8.25, 0.75
CORNER_R = 1.125
TOTAL_H = 24.0
STOCK = 0.75
LEG_W_TOP, LEG_W_FOOT = 2.5, 1.25
CLEAT_THK, CLEAT_MARGIN, CLEAT_LEN = 0.75, 0.375, 7.0
LEG_TOP_Z = TOTAL_H - TOP_THK            # 23.25
LEG_TRIM_Z = LEG_TOP_Z - CLEAT_THK       # 22.5
FOOT_L, FOOT_R = 3.0, 17.0
TIP_L, TIP_R = 4.5, 15.5
OVERHANG = 1.0
FRAME_A_Y0 = OVERHANG - STOCK / 2.0      # 0.625
FRAME_B_Y0 = (TOP_WID - OVERHANG) - STOCK / 2.0   # 6.875
A_INNER, B_INNER = FRAME_A_Y0 + STOCK, FRAME_B_Y0  # 1.375, 6.875
SX0, SX1, SZ0, SZ1 = 9.625, 10.375, 11.75, 14.25

# ---- styling --------------------------------------------------------------
INK = "#3a2a1a"      # geometry outline
WOOD = "#d8a673"     # leg / part fill
WOOD2 = "#e7c9a4"    # secondary fill (top, cleats)
DIM = "#1763b8"      # dimension lines / text
CEN = "#b07a3a"      # centerlines
plt.rcParams.update({"font.size": 9, "font.family": "DejaVu Sans"})

ARROW = dict(arrowstyle="<->", color=DIM, lw=0.9, shrinkA=0, shrinkB=0)


def leg_poly(foot_x, tip_x, z0=0.0, z1=LEG_TRIM_Z):
    """Trimmed elevation outline (x,z) of one tapered leg board."""
    dx, dz = tip_x - foot_x, LEG_TOP_Z
    L = math.hypot(dx, dz)
    n = np.array([-dz / L, dx / L])           # perpendicular in X-Z
    foot_c, tip_c = np.array([foot_x, 0.0]), np.array([tip_x, LEG_TOP_Z])
    eP = (foot_c + n * LEG_W_FOOT / 2, tip_c + n * LEG_W_TOP / 2)
    eM = (foot_c - n * LEG_W_FOOT / 2, tip_c - n * LEG_W_TOP / 2)

    def inter(p, q, zc):
        t = (zc - p[1]) / (q[1] - p[1])
        return np.array([p[0] + t * (q[0] - p[0]), zc])

    return [inter(*eP, z0), inter(*eP, z1), inter(*eM, z1), inter(*eM, z0)]


def dim(ax, p1, p2, off, text, side=1, txt_off=0.18, fs=9):
    """Aligned dimension between p1 and p2, offset perpendicular by `off`."""
    p1, p2 = np.array(p1, float), np.array(p2, float)
    d = p2 - p1
    L = np.hypot(*d)
    u = d / L
    n = np.array([-u[1], u[0]]) * side
    a, b = p1 + n * off, p2 + n * off
    ax.annotate("", xy=tuple(a), xytext=tuple(b), arrowprops=ARROW)
    for pt, e in ((p1, a), (p2, b)):
        ax.plot([pt[0], e[0] + n[0] * 0.12 * np.sign(off)],
                [pt[1], e[1] + n[1] * 0.12 * np.sign(off)],
                color=DIM, lw=0.5)
    mid = (a + b) / 2 + n * txt_off
    ang = math.degrees(math.atan2(d[1], d[0]))
    if ang > 90 or ang < -90:
        ang += 180
    ax.text(mid[0], mid[1], text, color=DIM, ha="center", va="center",
            rotation=ang, rotation_mode="anchor", fontsize=fs)


def angle_dim(ax, vtx, pa, pb, r, text, fs=9):
    vtx = np.array(vtx, float)
    a1 = math.degrees(math.atan2(pa[1] - vtx[1], pa[0] - vtx[0]))
    a2 = math.degrees(math.atan2(pb[1] - vtx[1], pb[0] - vtx[0]))
    lo, hi = min(a1, a2), max(a1, a2)
    ax.add_patch(Arc(vtx, 2 * r, 2 * r, theta1=lo, theta2=hi, color=DIM, lw=0.9))
    m = math.radians((lo + hi) / 2)
    ax.text(vtx[0] + (r + 0.55) * math.cos(m), vtx[1] + (r + 0.55) * math.sin(m),
            text, color=DIM, ha="center", va="center", fontsize=fs)


def leader(ax, tip, txt_xy, text, fs=8.5, ha="left"):
    ax.annotate(text, xy=tip, xytext=txt_xy, color=INK, fontsize=fs,
                ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))


def fill_poly(ax, pts, fc=WOOD, ec=INK, lw=1.2, **kw):
    ax.add_patch(plt.Polygon(pts, closed=True, facecolor=fc, edgecolor=ec,
                             lw=lw, **kw))


def rect(ax, x, y, w, h, fc=WOOD2, ec=INK, lw=1.2, **kw):
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                               lw=lw, **kw))


def rounded_rect_path(x, y, w, h, r, k=10):
    """Vertices for a rounded rectangle (corner radius r)."""
    cs = [(x + r, y + r), (x + w - r, y + r),
          (x + w - r, y + h - r), (x + r, y + h - r)]
    starts = [180, 270, 0, 90]
    pts = []
    for (cx, cy), s in zip(cs, starts):
        for t in np.linspace(math.radians(s), math.radians(s + 90), k):
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def finish(fig, ax, name):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.02)
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", pad_inches=0.12)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", pad_inches=0.12, dpi=150)
    plt.close(fig)
    print("wrote", name)


# ============================================================ side elevation
def side_elevation():
    fig, ax = plt.subplots(figsize=(6.4, 6.8))
    a = leg_poly(FOOT_L, TIP_R)    # "/"
    b = leg_poly(FOOT_R, TIP_L)    # "\"
    fill_poly(ax, a)
    fill_poly(ax, b)
    # top slab + cleats
    rect(ax, 0, LEG_TOP_Z, TOP_LEN, TOP_THK)
    aR = np.array(a)[1:3, 0]       # right leg top x-range (Pt, Mt)
    bR = np.array(b)[1:3, 0]       # left leg top x-range
    cR = (min(aR) - CLEAT_MARGIN, max(aR) + CLEAT_MARGIN)
    cL = (min(bR) - CLEAT_MARGIN, max(bR) + CLEAT_MARGIN)
    for c in (cL, cR):
        rect(ax, c[0], LEG_TRIM_Z, c[1] - c[0], CLEAT_THK, fc=WOOD2)
    # stretcher (behind the crossing) shown dashed
    rect(ax, SX0, SZ0, SX1 - SX0, SZ1 - SZ0, fc="none", ec=CEN, lw=1.0, ls="--")

    # crossing point
    zc = LEG_TOP_Z * (FOOT_R - FOOT_L) / ((FOOT_R - FOOT_L) + (TIP_R - TIP_L))
    # solve crossing analytically: centerlines meet at x=10
    zc = LEG_TOP_Z * (FOOT_R - TIP_L) / ((TIP_R - FOOT_L) + (FOOT_R - TIP_L))
    xc = 10.0

    # dimensions
    dim(ax, (0, 0), (0, TOTAL_H), 2.4, '24"', side=-1)
    dim(ax, (0, TOTAL_H), (TOP_LEN, TOTAL_H), 1.4, '20"', side=1)
    dim(ax, (FOOT_L, 0), (FOOT_R, 0), 1.6, '14" foot stance', side=-1)
    dim(ax, (xc, 0), (xc, zc), 0.0, '', side=1)          # ext only
    ax.annotate("", xy=(xc, 0), xytext=(xc, zc), arrowprops=ARROW)
    ax.text(xc + 0.3, zc / 2, '≈13"', color=DIM, ha="left", va="center", rotation=90)
    # top thickness + cleat thickness at right
    leader(ax, (TOP_LEN - 0.3, LEG_TOP_Z + TOP_THK / 2),
           (TOP_LEN + 2.2, TOTAL_H + 0.4), 'top (¾" thick)')
    leader(ax, (cR[0] + 0.2, LEG_TRIM_Z + CLEAT_THK / 2),
           (TOP_LEN + 2.2, LEG_TRIM_Z - 0.4), 'cleat (¾" thick)')
    # leg angle from floor + crossing angle
    fa = np.array(leg_poly(FOOT_L, TIP_R)[0])   # foot corner near (3,0)
    angle_dim(ax, (FOOT_L, 0), (FOOT_L + 2, 0),
              (FOOT_L + 2 * math.sin(math.radians(28.27)),
               2 * math.cos(math.radians(28.27))), 2.2, "61.7°")
    angle_dim(ax, (xc, zc),
              (xc + math.sin(math.radians(28.27)), zc + math.cos(math.radians(28.27))),
              (xc - math.sin(math.radians(28.27)), zc + math.cos(math.radians(28.27))),
              1.6, "≈57°")
    leader(ax, (xc + 0.9, zc + 0.6), (xc + 4.5, zc + 3.2), "half-lap (⅜\" deep)")
    leader(ax, (SX1, (SZ0 + SZ1) / 2), (SX1 + 4.0, (SZ0 + SZ1) / 2 - 2.0),
           "stretcher (behind)")
    ax.text(TOP_LEN / 2, TOTAL_H - TOP_THK / 2, "TOP", color=INK,
            ha="center", va="center", fontsize=8)
    ax.set_title("Side elevation (the X)", color=INK, fontsize=11)
    finish(fig, ax, "elevation_side")


# ============================================================ end elevation
def end_elevation():
    fig, ax = plt.subplots(figsize=(4.6, 6.8))
    rect(ax, 0, LEG_TOP_Z, TOP_WID, TOP_THK)                   # top
    rect(ax, FRAME_A_Y0, 0, STOCK, LEG_TRIM_Z)                 # frame A
    rect(ax, FRAME_B_Y0, 0, STOCK, LEG_TRIM_Z)                 # frame B
    rect(ax, FRAME_A_Y0, LEG_TRIM_Z, FRAME_B_Y0 + STOCK - FRAME_A_Y0,
         CLEAT_THK, fc=WOOD2)                                  # cleat (end-on)
    rect(ax, A_INNER, SZ0, B_INNER - A_INNER, SZ1 - SZ0,
         fc=WOOD2, ls="--")                                    # stretcher
    ax.text((A_INNER + B_INNER) / 2, (SZ0 + SZ1) / 2, "stretcher",
            ha="center", va="center", fontsize=8, color=INK)

    dim(ax, (0, 0), (0, TOTAL_H), 1.8, '24"', side=1)
    dim(ax, (0, TOTAL_H), (TOP_WID, TOTAL_H), 1.2, '8¼"', side=1)
    dim(ax, (FRAME_A_Y0 + STOCK / 2, 0), (FRAME_B_Y0 + STOCK / 2, 0), 1.6,
        '6¼" (centerlines)', side=-1)
    dim(ax, (A_INNER, SZ0), (A_INNER, SZ1), 0.7, '2½"', side=-1, fs=8)
    leader(ax, (FRAME_A_Y0 + STOCK / 2, LEG_TRIM_Z * 0.7),
           (-2.6, LEG_TRIM_Z * 0.7 + 2), 'leg (¾" stock)', ha="right")
    ax.set_title("End elevation", color=INK, fontsize=11, pad=10)
    finish(fig, ax, "elevation_end")


# ============================================================ leg detail
def leg_detail():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    L = math.hypot(TIP_R - FOOT_L, LEG_TOP_Z)
    Lcut = L * (LEG_TRIM_Z / LEG_TOP_Z)        # point-to-point trimmed length
    hF, hT = LEG_W_FOOT / 2, LEG_W_TOP / 2
    # face view (taper layout, square ends)
    fill_poly(ax, [(0, -hF), (0, hF), (Lcut, hT), (Lcut, -hT)])
    # half-lap band, centered ~14.75" from foot, skewed at the crossing angle
    dlap = math.hypot(10 - FOOT_L, 13.02)      # ~14.75 along centerline
    theta = 2 * math.degrees(math.atan((TIP_R - FOOT_L) / 2 / LEG_TOP_Z))  # ~56.5
    h = hF + (hT - hF) * dlap / Lcut           # half width at lap
    axw = (LEG_W_TOP * 0.78) / math.sin(math.radians(theta)) / 2  # half axial span
    sk = h / math.tan(math.radians(theta))     # skew shift per half-height
    band = [(dlap - axw - sk, -h), (dlap + axw - sk, -h),
            (dlap + axw + sk, h), (dlap - axw + sk, h)]
    fill_poly(ax, band, fc="#b9895c", ec=INK, lw=0.8, hatch="///", alpha=0.9)
    # end-cut angle indicator at the top end
    ax.plot([Lcut, Lcut - 2 * math.tan(math.radians(28.27))], [hT, -hT],
            color=DIM, lw=1.0, ls="--")
    angle_dim(ax, (Lcut, -hT), (Lcut, hT),
              (Lcut - 2 * math.tan(math.radians(28.27)), hT), 1.2, "28°")

    dim(ax, (0, hF), (Lcut, hT), 1.7, '≈25½" point-to-point', side=1)
    dim(ax, (0, -hF), (0, hF), 0.9, '1¼"', side=-1, fs=8)
    dim(ax, (Lcut, -hT), (Lcut, hT), 1.5, '2½"', side=1, fs=8)
    dim(ax, (0, hF), (dlap, h), 0.5, '≈14¾" to lap', side=1, fs=8)

    # edge (thickness) view below
    yb = -hT - 2.6
    rect(ax, 0, yb, Lcut, STOCK, fc=WOOD)
    rect(ax, dlap - 0.9, yb + STOCK / 2, 1.8, STOCK / 2, fc="#b9895c", hatch="///")
    dim(ax, (Lcut, yb), (Lcut, yb + STOCK), 0.7, '¾"', side=1, fs=8)
    dim(ax, (dlap + 0.9, yb + STOCK / 2), (dlap + 0.9, yb + STOCK), 0.5,
        '⅜"', side=1, fs=7.5)
    ax.text(0, yb + STOCK + 0.4, "edge view (thickness)", fontsize=7.5, color=INK)
    leader(ax, (dlap, yb + STOCK), (dlap + 3.5, yb - 1.2),
           'half-lap ⅜" deep —\nscribe from the mating leg')
    ax.set_title("Leg detail — taper, end angle & half-lap", color=INK,
                 fontsize=11, pad=12)
    finish(fig, ax, "leg_detail")


# ============================================================ top plan
def top_plan():
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.add_patch(plt.Polygon(rounded_rect_path(0, 0, TOP_LEN, TOP_WID, CORNER_R),
                             closed=True, facecolor=WOOD2, edgecolor=INK, lw=1.4))
    # underside chamfer inner line (0.5" in)
    ax.add_patch(plt.Polygon(rounded_rect_path(0.5, 0.5, TOP_LEN - 1, TOP_WID - 1,
                                               max(CORNER_R - 0.5, 0.1)),
                             closed=True, facecolor="none", edgecolor=CEN,
                             lw=0.8, ls=(0, (4, 3))))
    # cleats + leg-tip footprints
    a = np.array(leg_poly(FOOT_L, TIP_R))[1:3, 0]
    b = np.array(leg_poly(FOOT_R, TIP_L))[1:3, 0]
    cy0 = (TOP_WID - CLEAT_LEN) / 2
    cR = (min(a) - CLEAT_MARGIN, max(a) + CLEAT_MARGIN)
    cL = (min(b) - CLEAT_MARGIN, max(b) + CLEAT_MARGIN)
    for c in (cL, cR):
        rect(ax, c[0], cy0, c[1] - c[0], CLEAT_LEN, fc="none", ec=DIM, lw=1.2)
    for y0 in (FRAME_A_Y0, FRAME_B_Y0):
        for xr in ((min(b), max(b)), (min(a), max(a))):
            rect(ax, xr[0], y0, xr[1] - xr[0], STOCK, fc=WOOD, ec=INK, lw=0.8)
    for yc in (FRAME_A_Y0 + STOCK / 2, FRAME_B_Y0 + STOCK / 2):
        ax.plot([-1, TOP_LEN + 1], [yc, yc], color=CEN, lw=0.7, ls=(0, (6, 4)))

    dim(ax, (0, 0), (TOP_LEN, 0), 1.3, '20"', side=-1)
    dim(ax, (0, 0), (0, TOP_WID), 1.3, '8¼"', side=-1)
    dim(ax, (cL[0], cy0 + CLEAT_LEN), (cL[1], cy0 + CLEAT_LEN), 0.9,
        '≈3⅝"', side=1, fs=8)
    dim(ax, (TOP_LEN, cy0), (TOP_LEN, cy0 + CLEAT_LEN), 1.1, '7"', side=1, fs=8)
    leader(ax, (CORNER_R * 0.3, TOP_WID - CORNER_R * 0.3),
           (-2.6, TOP_WID + 1.2), 'R 1⅛"', ha="right")
    ax.text(cL[0] + (cL[1] - cL[0]) / 2, cy0 + CLEAT_LEN / 2, "cleat",
            color=DIM, ha="center", va="center", fontsize=8)
    ax.set_title("Top — plan view", color=INK, fontsize=11)
    finish(fig, ax, "top_plan")


if __name__ == "__main__":
    side_elevation()
    end_elevation()
    leg_detail()
    top_plan()
    print("diagrams written to", OUT)
