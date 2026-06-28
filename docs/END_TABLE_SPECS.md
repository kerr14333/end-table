# End Table Spec

Material: 3/4" milled cherry. Build modeled in FreeCAD (see `build_end_table.py`).
Style: sleek modern / mid-century, to sit next to the chair in `images/chair.jpeg`
(warm wood, tapered splayed legs, eased edges, natural oil finish).

## Locked dimensions
* Overall: 24" tall.
* Top: 20" long x 8 1/4" wide x 3/4" thick. Width is fixed; length may be adjusted.
  * Corners rounded, 1 1/8" radius.
  * Underside perimeter: 45-deg routed chamfer 9/16" wide, leaving a 3/16" edge (reads thin / floats).
  * Top edge crisped with a 1/32" micro-bevel.
* Legs: two crossed (X) frames, 3/4" stock, tapered 2 1/2" wide at top to 1" at the foot.
  * Leg lean 30 deg from vertical (60 deg crossing angle). Chosen so the leg-end
    cuts (30 deg off square) and the half-lap nibble (90 - 2x30 = 30 deg off
    square) both fall on a positive stop of the miter gauge (POWERTEC 71391:
    every 5 deg to 60, plus 22.5). Tapers are done on a jig, so unconstrained.
  * Joined at each crossing with a half-lap, 3/8" deep.
  * Feet splayed past the tips (~15 7/8" stance) for stability; legs centered under the top.
  * End overhang ~4 1/2", side overhang ~1" (legs set wide for side-to-side stability).
* One central stretcher ties the two frames together at the crossing. It is glued
  and dowelled into each frame's inner face — two 3/8" dowels per end (its end
  grain needs the dowels; glue alone there is weak).
* Two cleats (~7 x 3 5/8 x 3/4) under the ends of the top: sized and centered on
  the angled leg-tip footprint so each leg seats squarely (the trimmed tips land
  slightly inboard of the leg's nominal tip). The two long bottom edges are eased
  with a 1/4" 45-deg bevel so the cleats read lighter (ends left square, where the
  leg tips bear). The leg tips bear on them, they tie the two frames together at
  the top, and the top fastens to them with figure-8 (desktop) fasteners — two per
  cleat, recessed flush into the cleat top, which pivot to allow seasonal wood movement.

## Tools on hand
Tablesaw, router, miter saw, and standard hand tools.
