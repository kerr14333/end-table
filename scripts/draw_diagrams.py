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
from fractions import Fraction
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
LEG_W_TOP, LEG_W_FOOT = 2.5, 1.0
BEVEL_RUN = 0.5625                       # underside chamfer width (9/16")
CLEAT_THK, CLEAT_MARGIN, CLEAT_LEN = 0.75, 0.375, 7.0
CLEAT_BEVEL = 0.25                       # 45-deg chamfer on long bottom edges
LEG_TOP_Z = TOTAL_H - TOP_THK            # 23.25
LEG_TRIM_Z = LEG_TOP_Z - CLEAT_THK       # 22.5
TIP_L, TIP_R = 4.5, 15.5
LEAN_DEG = 30.0                          # leg lean from vertical (a miter-gauge stop)
_dx = math.tan(math.radians(LEAN_DEG)) * LEG_TOP_Z
FOOT_L, FOOT_R = TIP_R - _dx, TIP_L + _dx
OVERHANG = 1.0
FRAME_A_Y0 = OVERHANG - STOCK / 2.0      # 0.625
FRAME_B_Y0 = (TOP_WID - OVERHANG) - STOCK / 2.0   # 6.875
A_INNER, B_INNER = FRAME_A_Y0 + STOCK, FRAME_B_Y0  # 1.375, 6.875
SX0, SX1 = 9.625, 10.375
CROSS_Z = (10.0 - FOOT_L) / (TIP_R - FOOT_L) * LEG_TOP_Z   # leg crossing height
SZ0, SZ1 = CROSS_Z - 0.75, CROSS_Z + 0.75                  # 1.5" tall, on crossing

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


def cleat_profile(a0, a1, zb, bv=CLEAT_BEVEL):
    """Cleat cross-section with the two bottom corners chamfered (across `a`)."""
    zt = zb + CLEAT_THK
    return [(a0, zt), (a0, zb + bv), (a0 + bv, zb),
            (a1 - bv, zb), (a1, zb + bv), (a1, zt)]


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
        fill_poly(ax, cleat_profile(c[0], c[1], LEG_TRIM_Z), fc=WOOD2)
    # stretcher (behind the crossing) shown dashed
    rect(ax, SX0, SZ0, SX1 - SX0, SZ1 - SZ0, fc="none", ec=CEN, lw=1.0, ls="--")

    # crossing point: the two leg centerlines meet at x=10
    xc = 10.0
    zc = (xc - FOOT_L) / (TIP_R - FOOT_L) * LEG_TOP_Z

    # dimensions
    dim(ax, (0, 0), (0, TOTAL_H), 2.4, '24"', side=-1)
    dim(ax, (0, TOTAL_H), (TOP_LEN, TOTAL_H), 1.4, '20"', side=1)
    dim(ax, (FOOT_L, 0), (FOOT_R, 0), 1.6, f'≈{FOOT_R - FOOT_L:.1f}" foot stance', side=-1)
    dim(ax, (xc, 0), (xc, zc), 0.0, '', side=1)          # ext only
    ax.annotate("", xy=(xc, 0), xytext=(xc, zc), arrowprops=ARROW)
    ax.text(xc + 0.3, zc / 2, f'≈{zc:.1f}"', color=DIM, ha="left", va="center", rotation=90)
    # top thickness + cleat thickness at right
    leader(ax, (TOP_LEN - 0.3, LEG_TOP_Z + TOP_THK / 2),
           (TOP_LEN + 2.2, TOTAL_H + 0.4), 'top (¾" thick)')
    leader(ax, (cR[0] + 0.2, LEG_TRIM_Z + CLEAT_THK / 2),
           (TOP_LEN + 2.2, LEG_TRIM_Z - 0.4),
           'cleat — ¾" thick,\nbottom edges beveled 45°')
    # angles (all driven by LEAN_DEG): leg 60deg up from the floor at one foot,
    # the same lean read as 30deg off vertical at the other foot (that's the angle
    # the saw is set to), and the 60deg crossing of the X.
    lean = math.radians(LEAN_DEG)
    angle_dim(ax, (FOOT_L, 0), (FOOT_L + 2, 0),
              (FOOT_L + 2 * math.sin(lean), 2 * math.cos(lean)), 2.2,
              f"{90 - LEAN_DEG:.0f}° (floor)")
    ax.plot([FOOT_R, FOOT_R], [0, 2.5], color=DIM, lw=0.7, ls=":")   # plumb ref
    angle_dim(ax, (FOOT_R, 0), (FOOT_R, 2.0),
              (FOOT_R - 2 * math.sin(lean), 2 * math.cos(lean)), 2.2,
              f"{LEAN_DEG:.0f}° (vert.)")
    angle_dim(ax, (xc, zc),
              (xc + math.sin(lean), zc + math.cos(lean)),
              (xc - math.sin(lean), zc + math.cos(lean)),
              1.6, f"{2 * LEAN_DEG:.0f}° (X)")
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
    # Cleat seen end-on. Its bevel is on the long edges (which run toward/away
    # from us here), so in this view it reads as a plain rectangle with SQUARE
    # ends -- the legs sit flush on it. (The bevel shows in the side elevation.)
    rect(ax, FRAME_A_Y0, LEG_TRIM_Z, FRAME_B_Y0 + STOCK - FRAME_A_Y0,
         CLEAT_THK, fc=WOOD2)
    rect(ax, A_INNER, SZ0, B_INNER - A_INNER, SZ1 - SZ0,
         fc=WOOD2, ls="--")                                    # stretcher
    ax.text((A_INNER + B_INNER) / 2, (SZ0 + SZ1) / 2, "stretcher",
            ha="center", va="center", fontsize=8, color=INK)
    # hidden dowels: 2 per end, run across the butt joint into each leg
    for yb, ye in [(A_INNER - 0.5, A_INNER + 0.75), (B_INNER - 0.75, B_INNER + 0.5)]:
        for z in (CROSS_Z - 0.3125, CROSS_Z + 0.3125):
            ax.plot([yb, ye], [z, z], color="#6b4a25", lw=1.2, ls=(0, (3, 2)))
    leader(ax, (A_INNER + 0.4, CROSS_Z + 0.3125), ((A_INNER + B_INNER) / 2, 17.5),
           '3/8" dowels\n(2 per end)', ha="center")

    dim(ax, (0, 0), (0, TOTAL_H), 1.8, '24"', side=1)
    dim(ax, (0, TOTAL_H), (TOP_WID, TOTAL_H), 1.2, '8¼"', side=1)
    dim(ax, (FRAME_A_Y0 + STOCK / 2, 0), (FRAME_B_Y0 + STOCK / 2, 0), 1.6,
        '6¼" (centerlines)', side=-1)
    dim(ax, (A_INNER, SZ0), (A_INNER, SZ1), 0.7, '1½"', side=-1, fs=8)
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
    # face view -- this is the rectangular BLANK with square ends. The real end
    # cuts are 30 deg off square: the dashed lines are the actual cuts and the
    # hatched triangles drop off as WASTE. The finished leg is a tapered
    # parallelogram whose two long points (top & foot) come out roughly 60 deg.
    fill_poly(ax, [(0, -hF), (0, hF), (Lcut, hT), (Lcut, -hT)])
    end_off_T = 2 * hT * math.tan(math.radians(LEAN_DEG))   # run across the top width
    end_off_F = 2 * hF * math.tan(math.radians(LEAN_DEG))   # run across the foot width
    for w in ([(Lcut, hT), (Lcut, -hT), (Lcut - end_off_T, -hT)],
              [(0, hF), (end_off_F, hF), (0, -hF)]):
        ax.add_patch(plt.Polygon(w, closed=True, facecolor="#d9cdbd",
                                 edgecolor=INK, lw=0.6, hatch="xxx", zorder=2.5))
    ax.text(Lcut - end_off_T / 3.0, -hT / 3.5, "waste", fontsize=6.5,
            color="#5b4d3f", ha="center", va="center", zorder=3)

    # Half-lap band = the footprint of the MATING leg where it crosses this one.
    # Computed from the REAL geometry: where the mating leg's two (tapered, so non-
    # parallel) edges cross THIS leg's two edges. Because the lap is both skewed
    # (60 deg crossing) AND on a tapered board, all four crossings sit at different
    # distances from the foot -- so the band leans and its two walls aren't parallel.
    zc = (10 - FOOT_L) / (TIP_R - FOOT_L) * LEG_TOP_Z   # crossing height
    dlap = math.hypot(10 - FOOT_L, zc)         # centerline distance foot->crossing
    theta = 2 * LEAN_DEG                        # crossing angle between centerlines

    def _leg_edges(foot_x, tip_x):
        """The two long-edge lines (foot point + unit dir) of a leg, in elevation."""
        Cf = np.array([foot_x, 0.0]); Ct = np.array([tip_x, LEG_TOP_Z])
        u = (Ct - Cf); u = u / np.hypot(*u); nrm = np.array([-u[1], u[0]])
        out = []
        for sgn in (+1, -1):
            pf = Cf + sgn * nrm * hF; pt = Ct + sgn * nrm * hT
            d = pt - pf; foot = pf + (0.0 - pf[1]) / d[1] * d   # trim to the floor
            out.append((foot, d / np.hypot(*d)))
        return out

    def _xpt(p, dp, q, dq):
        M = np.array([[dp[0], -dq[0]], [dp[1], -dq[1]]])
        a, _ = np.linalg.solve(M, q - p); return p + a * dp

    _A, _B = _leg_edges(FOOT_L, TIP_R), _leg_edges(FOOT_R, TIP_L)
    lap_d = []     # for each of THIS leg's edges: sorted [near, far] foot distances
    for af, ad in _A:
        lap_d.append(sorted(float(np.hypot(*(_xpt(af, ad, bf, bd) - af)))
                            for bf, bd in _B))
    lap_d.sort(key=lambda pr: -pr[0])          # larger -> the diagram's TOP edge
    (top_near, top_far), (bot_near, bot_far) = lap_d

    # place those distances along THIS leg's drawn edges (foot corners from the cuts)
    FT, TT = np.array([0.0, hF]), np.array([Lcut, hT])                  # top edge
    FB, TB = np.array([end_off_F, -hF]), np.array([Lcut - end_off_T, -hT])  # bottom
    uT = (TT - FT) / np.hypot(*(TT - FT))
    uB = (TB - FB) / np.hypot(*(TB - FB))
    pT1, pT2 = FT + uT * top_near, FT + uT * top_far
    pB1, pB2 = FB + uB * bot_near, FB + uB * bot_far
    band = [tuple(pT1), tuple(pT2), tuple(pB2), tuple(pB1)]
    fill_poly(ax, band, fc="#b9895c", ec=INK, lw=0.8, hatch="///", alpha=0.9)
    ax.plot([pT1[0], pB1[0]], [pT1[1], pB1[1]], color=INK, lw=0.9)   # shoulder wall 1
    ax.plot([pT2[0], pB2[0]], [pT2[1], pB2[1]], color=INK, lw=0.9)   # shoulder wall 2

    # dashed lines = the actual finished end cuts. You SET the saw / miter gauge to
    # 30 deg off square (the arc, measured against the square blank end). The sharp
    # finished corner that results (~58-62 deg, off 60 by the taper) is a CHECK
    # angle -- you don't lay it out, it falls out of the 30 deg cut.
    ax.plot([Lcut, Lcut - end_off_T], [hT, -hT], color=DIM, lw=1.1, ls="--")
    ax.plot([end_off_F, 0], [hF, -hF], color=DIM, lw=1.1, ls="--")

    def _corner(v, p, q):
        a, b = np.array(p) - np.array(v), np.array(q) - np.array(v)
        return math.degrees(math.acos(np.clip(a @ b / (np.hypot(*a) * np.hypot(*b)), -1, 1)))
    tr_top = _corner((Lcut, hT), (0, hF), (Lcut - end_off_T, -hT))
    tr_foot = _corner((0, -hF), (Lcut, -hT), (end_off_F, hF))

    # The SET angle (30 deg off square) is the same parallel cut at both ends, so
    # show the arc once (at the foot). The sharp finished point at each end is a
    # CHECK angle -- called out with leaders, not laid out.
    angle_dim(ax, (0, -hF), (0, hF), (end_off_F, hF), 0.7, "30° off sq.")
    leader(ax, (0.18, -hF + 0.16), (-1.6, -hF - 1.2),
           f"finished\n≈{tr_foot:.0f}°", ha="center")
    leader(ax, (Lcut - 0.6, hT - 0.45), (Lcut - 3.4, hT + 2.0),
           f"finished point ≈{tr_top:.0f}°", ha="center")

    # Foot-to-lap distances, measured ALONG each edge from that edge's foot corner.
    # These differ on the two edges (skew + taper), so mark each edge to its own
    # pair -- the ~30deg miter setting only roughs the walls; scribe to these lines.
    def _frac(x):
        f = Fraction(round(x * 16), 16); w = int(f); r = f - w
        return f'{w}"' if r == 0 else f'{w} {r.numerator}/{r.denominator}"'

    dim(ax, tuple(FT), tuple(pT1), 0.55, _frac(top_near), side=1, fs=7.5)   # top edge
    dim(ax, tuple(FT), tuple(pT2), 1.55, _frac(top_far), side=1, fs=7.5)
    dim(ax, tuple(FB), tuple(pB1), 0.55, _frac(bot_near), side=-1, fs=7.5)  # bottom edge
    dim(ax, tuple(FB), tuple(pB2), 1.55, _frac(bot_far), side=-1, fs=7.5)
    ax.text(float((pT1[0] + pB2[0]) / 2), 0.0, "half-lap", fontsize=7,
            color="#3a2a1a", ha="center", va="center", rotation=58, zorder=4)

    taper_deg = math.degrees(math.atan((LEG_W_TOP - LEG_W_FOOT) / Lcut))
    ax.text(Lcut * 0.40, -hT - 2.7,
            f'taper ≈ {taper_deg:.1f}°  (2½" to 1" over ≈26")',
            color=DIM, ha="center", va="center", fontsize=8)
    ax.text(Lcut * 0.5, -hT - 3.25,
            'solid = blank (square ends)  ·  dashed = real 30° cut (both ends)  ·  hatched = waste',
            fontsize=7, color="#5b4d3f", ha="center", va="center")
    ax.text(Lcut * 0.5, -hT - 3.85,
            'half-lap lines differ on each edge (60° skew + taper) — scribe to them, '
            "don't dial the angle", fontsize=7, color="#5b4d3f", ha="center", va="center")

    dim(ax, (0, hF), (Lcut, hT), 2.75, f'≈{Lcut:.0f}" point-to-point', side=1)
    dim(ax, (0, -hF), (0, hF), 0.9, '1"', side=-1, fs=8)
    dim(ax, (Lcut, -hT), (Lcut, hT), 1.5, '2½"', side=-1, fs=8)

    # edge (thickness) view below
    yb = -hT - 5.7
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
    ax.add_patch(plt.Polygon(rounded_rect_path(BEVEL_RUN, BEVEL_RUN,
                                               TOP_LEN - 2 * BEVEL_RUN,
                                               TOP_WID - 2 * BEVEL_RUN,
                                               max(CORNER_R - BEVEL_RUN, 0.1)),
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
    leader(ax, (BEVEL_RUN, TOP_WID * 0.5), (-3.0, TOP_WID * 0.5 - 1.6),
           'underside 45°\nchamfer (9/16")', ha="right")
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
