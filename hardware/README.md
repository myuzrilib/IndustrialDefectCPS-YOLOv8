# CPS-Sort deflection station — printed brackets

Parametric re-derivation of the two 3D-printed brackets at each deflection station.
The original AutoCAD models were lost; these are rebuilt from the author's dimensioned
hand sketch of **26 October 2026**, which supersedes an earlier reconstruction made from
photographs alone.

```
pip install trimesh manifold3d numpy matplotlib
python3 brackets.py --preview     # writes both STLs and preview PNGs
python3 make_drawings.py          # writes brackets_drawing.pdf (3 pages) and PNGs
python3 make_system_figs.py       # writes station_layout.png and wiring.png
```

`station_layout.png` is the plan view of the four station distances; `wiring.png` is the
control-electronics schematic. Both are generated from the same constants the firmware and
host script use, so they cannot drift out of date.

`make_drawings.py` imports `brackets.py`, so the drawings and the meshes cannot drift
apart: change a parameter in one place and both regenerate from it.

## Two parts, not one

An earlier revision of this folder modelled the station as a **single** 250 × 50 × 150 mm
bracket. That was wrong. The sketch shows two separate printed parts, and the 250 mm
dimension is the **height of part B**, not the length of part A's plate.

| | |
|---|---|
| **Part A** — moving arm | Joins the servo to the PVC deflector blade. 200 × 50 mm plate, 13 mm walls, 100 mm leg. Overall 200 × 50 × 113 mm, ~193 cm³. |
| **Part B** — fixed bracket | Joins the servo assembly to the conveyor frame. 250 mm post with a slot down its length for setting the servo height; 60 mm top plate with a window the servo body passes through. Overall 60 × 50 × 263 mm, ~132 cm³. |

Both meshes are watertight.

## Part A — servo to PVC blade

| Parameter | Value | Source |
|---|---|---|
| `a_plate_len` | 200 mm | sketch, top view |
| `a_plate_wid` | 50 mm | sketch, top view |
| `a_plate_th`, `a_leg_th` | 13 mm | sketch, side view |
| `a_leg_h` | 100 mm | sketch, front view (70 + 20 + 10) |
| `a_servo_bolt_x` | 20 mm | sketch, top view — **one** bolt, not two |
| `a_horn_len` × `a_horn_wid` | 20 × 10 mm | markup, 26 Oct — pocket in the underside that seats the rectangular servo horn |
| `a_horn_d` | 3 mm | author — cut to the same depth as the blade seat |
| `a_blade_w` | 20 mm | sketch — the 20 mm band in the 70/20/10 chain |
| `a_rebate_top` | 70 mm | sketch — top of the blade seat below the plate |
| `a_rebate_d` | 3 mm | author, measured on the part |
| `a_servo_bolt_d` | ⌀3.5 | **assumed** M3 clearance |
| `a_blade_bolt_d` | ⌀4.5 | **assumed** — the blade retaining bolt |

The blade root is held in a rebate cut to the blade width, with one bolt through its
centre. The rebate is on the **inner** face of the leg — the side facing the plate and
the servo (`a_rebate_face`, author's markup *"sebelah kiri"*, 26 Oct). An earlier
revision had it on the outer face.

Around the servo bolt, a 20 × 10 × 3 mm pocket is cut into the **underside** of the
plate. The MG995 horn is rectangular, so the pocket keys part A to the horn: the bolt
alone would let the plate spin on the horn screw, and the pocket is what transmits the
torque.

## Part B — servo to conveyor frame

| Parameter | Value | Source |
|---|---|---|
| `b_plate_len` | 60 mm | sketch, top view (15 + 30 + 15) |
| `b_plate_th` | 13 mm | sketch, side view |
| `b_window_len` | 30 mm | sketch, top view |
| `b_post_h` | 250 mm | sketch, front view |
| `b_post_wid` | 40 mm | sketch, front view |
| `b_slot_wid` | 10 mm | sketch, front view (40 = 15 + 10 + 15) |
| `b_plate_wid` | 50 mm | **assumed** — not dimensioned on the sketch |
| `b_post_th` | 13 mm | **assumed** — same wall thickness as everything else |
| `b_window_wid` | 24 mm | **assumed** — MG995 body 19.7 mm plus clearance |
| `b_bolt_d`, `b_bolt_pitch`, `b_bolt_margin` | ⌀3.5, 26 mm, 7.5 mm | **assumed** — four holes, two in each margin |
| `b_slot_end` | 20 mm | **assumed** — where the slot stops at each end |

Eight numbers on part B are assumptions. Four of them matter for fit: the plate depth,
the post thickness, the window depth and the bolt pitch. The rest only affect how the
part looks.

**One of them does not add up.** The MG995 body is 40.7 x 19.7 mm, and the sketch gives
the window as 30 mm in the dimensioned direction only. Thirty millimetres will not pass
the 40.7 mm side, so either the undimensioned direction of the window is around 45 mm —
which would also make the 50 mm plate depth too small — or the servo does not drop
through the plate at all and the window only clears its shaft boss. `brackets.py` prints
a note about this on every build rather than guessing one of the two. It needs a
measurement off the real part.

## What is still open

**The blade kinematics are now settled** — the horn pocket resolved them. Part A is the
moving arm: the servo body is carried by part B, the horn drives part A through the
rectangular pocket, and the PVC blade bolted to part A's leg swings with it as a rigid
body. The blade does **not** flex. An earlier note in this file argued for a flexing
blade; that was wrong, and §2 of the manuscript should describe a swinging arm.

**The blade is complete.** It is not modelled as a mesh — it is cut from flat PVC trim
profile and bent by hand, so what a builder needs is the cut-and-bend drawing on page 3
of `brackets_drawing.pdf`, generated by `page_c()` from the parameters below.

| | |
|---|---|
| `blade_len` | **200 mm** — measured |
| `blade_width` | **20 mm** — from the seat on part A, which was cut to fit it |
| `blade_bend_at` | **130 mm** — the bend runs from 130 mm to the tip |
| `blade_bend_angle` | **15°** |
| `blade_hole_x` | 10 mm — **assumed**, the only number on the blade that is not measured |
| `blade_th` | 2 mm — **assumed**, affects nothing in the drawing |

Derived: the bent section is 70 mm long, its tip stands **18.1 mm** off the straight
run, and the blade's projected length is **197.6 mm**.

The bend radius is not specified. The blade was formed by hand, so a builder should
match the angle, not a radius.

## Before this is deposited as a design file

Print one of each and fit them. Until a printed copy has been bolted to the conveyor
with a servo and a blade in it, this is a plausible reconstruction, not a validated
design, and a paper that presents it as the latter would mislead its readers.

If it cannot be printed and fitted, say so. Wording that is accurate:

> The original CAD models of the two printed brackets were lost. The design files
> deposited here are parametric re-derivations from the authors' dimensioned sketches of
> the physical parts. They have not been re-printed or re-fitted, and builders should
> verify fit before use.

A reviewer may accept that or may not. Either way it is the truth, and it is better
discovered by the authors than by a reader whose print does not fit.
