#!/usr/bin/env python3
"""
CPS-Sort deflection station — the two printed brackets.

    pip install trimesh manifold3d numpy
    python3 brackets.py                  # writes both STLs
    python3 brackets.py --preview        # also writes preview PNGs

WHAT THIS IS
------------
The original AutoCAD models were lost. These are parametric re-derivations built
from the author's dimensioned hand sketch of 26 October 2026, which supersedes an
earlier reconstruction made from photographs alone.

The station uses TWO separate printed parts, not one. An earlier revision of this
file modelled them as a single bracket, which was wrong: the 250 mm dimension is
the height of part B, not the length of part A's plate.

    PART A   moving arm
             Joins the servo to the PVC deflector blade. A 200 mm plate carries the
             servo near its free end; a 100 mm leg at the other end carries the
             blade root in a rebate cut to the blade width.

    PART B   fixed bracket
             Joins the servo assembly to the conveyor frame. A 250 mm post with a
             slot down its length, so the servo height above the belt can be set;
             a top plate with a window the servo body passes through.

Dimensions marked SKETCH come from the author's drawing. Dimensions marked ASSUMED
are not on the sketch and are the author's to correct; the geometry regenerates from
the parameters, so each correction is a one-line edit.
"""

import argparse
import math

import numpy as np
import trimesh

# ======================================================= PART A  servo <-> PVC blade
a_plate_len = 200.0      # SKETCH, top view
a_plate_wid = 50.0       # SKETCH, top view
a_plate_th = 13.0        # SKETCH, side view

a_leg_h = 100.0          # SKETCH, front view. Measured below the plate underside.
a_leg_th = 13.0          # SKETCH

# servo fixing: ONE bolt through the plate, 20 mm in from the free end, into the centre
# screw of the servo horn. Around it, a shallow rectangular pocket in the UNDERSIDE of
# the plate captures the horn itself — the MG995 horn is rectangular, so the pocket keys
# part A to it and the whole bracket swings with the horn; the author added it precisely
# because the rotating part of the servo is rectangular (author, 26 Oct).
a_servo_bolt_x = 20.0    # SKETCH, top view
a_servo_bolt_d = 3.5     # ASSUMED M3 clearance
a_horn_len = 20.0        # AUTHOR markup, along the plate
a_horn_wid = 10.0        # AUTHOR markup, across the plate
a_horn_d = 3.0           # AUTHOR: cut to the same 3 mm depth as the blade seat.

# PVC blade seat on the leg: a rebate cut to the blade width, bolt through its centre
a_blade_w = 20.0         # SKETCH, side view — the 20 mm band in the 70/20/10 chain
a_rebate_d = 3.0         # author, measured on the part
a_rebate_top = 70.0      # SKETCH: top of the rebate, below the plate underside
a_rebate_face = 'inner'  # SKETCH markup "sebelah kiri": the seat is on the plate side
#                          of the leg. 'outer' puts it on the far face instead.
a_blade_bolt_d = 4.5     # ASSUMED. Blade retaining bolt, centred in the rebate.

# ==================================================== PART B  servo <-> conveyor frame
b_plate_len = 60.0       # SKETCH, top view: 15 + 30 + 15
b_plate_wid = 50.0       # ASSUMED — the sketch does not dimension this direction
b_plate_th = 13.0        # SKETCH, side view

b_window_len = 30.0      # SKETCH, top view — the servo body passes through here
b_window_wid = 24.0      # ASSUMED: MG995 body 19.7 mm plus clearance

b_bolt_d = 3.5           # ASSUMED M3
b_bolt_margin = 7.5      # ASSUMED: holes centred in the 15 mm margin each side
b_bolt_pitch = 26.0      # ASSUMED: spacing of the two holes on each side

b_post_h = 250.0         # SKETCH, front view
b_post_wid = 40.0        # SKETCH, front view
b_post_th = 13.0         # ASSUMED, same wall thickness as everything else
b_slot_wid = 10.0        # SKETCH, front view: 40 = 15 + 10 + 15
b_slot_end = 20.0        # ASSUMED: slot stops this far from each end of the post

fillet_r = 3.0           # gusset at the inside corner

# ============================================== PVC DEFLECTOR BLADE  (not printed)
# A length of PVC trim profile, cut and bent by hand. No mesh: it is made from a flat
# strip, so what a builder needs is a cut-and-bend drawing, produced by make_drawings.py.
blade_len = 200.0        # AUTHOR
blade_width = 20.0       # AUTHOR — a_blade_w, the seat on part A was cut to fit it
blade_bend_at = 130.0    # AUTHOR: the bend runs from 130 mm to the tip
blade_bend_angle = 15.0  # AUTHOR, degrees
blade_hole_x = 10.0      # ASSUMED: bolt hole centre from the root end
blade_th = 2.0           # ASSUMED: wall thickness of the PVC profile
# ================================================================== END PARAMETERS


def box(size, translate):
    m = trimesh.creation.box(extents=size)
    m.apply_translation(translate)
    return m


def cyl(d, h, translate, axis='z'):
    m = trimesh.creation.cylinder(radius=d / 2.0, height=h, sections=48)
    if axis == 'x':
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == 'y':
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    m.apply_translation(translate)
    return m


def vslot_y(w, h, depth, centre):
    """Rounded slot through a wall whose thickness runs along Y, elongated along Z."""
    x, y, z = centre
    rise = h - w
    a = cyl(w, depth, [x, y, z - rise / 2], axis='y')
    b = cyl(w, depth, [x, y, z + rise / 2], axis='y')
    return a.union(b).union(box([w, depth, rise], [x, y, z]))


def hslot_z(d, travel, depth, centre):
    """Rounded slot bored along Z, elongated along X — an adjustment slot through a
    horizontal plate. `travel` is the distance between the two end centres."""
    x, y, z = centre
    a = cyl(d, depth, [x - travel / 2, y, z])
    b = cyl(d, depth, [x + travel / 2, y, z])
    return a.union(b).union(box([travel, d, depth], [x, y, z]))


def gusset(x, z_top, size, width, sign):
    """Right-triangular prism stiffening an inside corner, extruded across the width."""
    s = size
    tri = np.array([[0, 0], [s * sign, 0], [0, -s]], dtype=float)
    poly = trimesh.creation.extrude_triangulation(
        vertices=tri, faces=np.array([[0, 1, 2]]), height=width)
    poly.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    poly.apply_translation([x, width / 2, z_top])
    return poly


def fuse(parts):
    body = parts[0]
    for q in parts[1:]:
        body = body.union(q)
    return body


def check_layout():
    """Fail loudly if the parameters put two features on top of each other."""
    issues = []

    # --- part A
    if a_servo_bolt_x + a_horn_len / 2 > a_plate_len - a_leg_th:
        issues.append('part A: horn pocket runs into the leg')
    if a_servo_bolt_x - a_horn_len / 2 < 0:
        issues.append('part A: horn pocket runs off the free end of the plate')
    if a_horn_wid >= a_plate_wid:
        issues.append('part A: horn pocket is wider than the plate')
    if a_horn_d >= a_plate_th:
        issues.append('part A: horn pocket is deeper than the plate is thick')
    if a_servo_bolt_d >= min(a_horn_len, a_horn_wid):
        issues.append('part A: servo bolt is wider than the horn pocket around it')
    if a_rebate_d >= a_leg_th / 2:
        issues.append(f'part A: {a_rebate_d} mm rebate is more than half the '
                      f'{a_leg_th} mm leg wall')
    if a_rebate_top + a_blade_w > a_leg_h:
        issues.append('part A: blade rebate runs off the bottom of the leg')
    if a_blade_bolt_d >= a_blade_w:
        issues.append('part A: blade bolt is wider than the rebate it sits in')
    if a_rebate_face not in ('outer', 'inner'):
        issues.append(f'part A: a_rebate_face = {a_rebate_face!r} is not a known option')

    # --- part B
    # The MG995 body is 40.7 x 19.7 mm. The sketch dimensions the window at 30 mm in one
    # direction only, and 30 mm will not pass the 40.7 mm side. Either the undimensioned
    # direction of the window is ~45 mm, or the servo does not drop through the plate at
    # all and the window only clears its shaft boss. This is flagged, not fixed: it needs
    # a measurement, not a guess.
    if max(b_window_len, b_window_wid) < 40.7:
        print('NOTE  part B: the servo window is %.0f x %.0f mm, and neither side will '
              'pass\n      the 40.7 mm MG995 body. Measure the window on the real part.'
              % (b_window_len, b_window_wid))
    if b_window_len >= b_plate_len:
        issues.append('part B: servo window is wider than the plate')
    if b_window_wid >= b_plate_wid:
        issues.append('part B: servo window is deeper than the plate')
    margin = (b_plate_len - b_window_len) / 2
    if b_bolt_margin + b_bolt_d / 2 > margin:
        issues.append(f'part B: bolt holes fall outside the {margin:.1f} mm margin '
                      'beside the window')
    if b_bolt_pitch + b_bolt_d > b_plate_wid:
        issues.append('part B: bolt pitch does not fit across the plate')
    if b_slot_wid >= b_post_wid:
        issues.append('part B: height slot is wider than the post')
    if 2 * b_slot_end >= b_post_h:
        issues.append('part B: height slot has no length left')
    if b_post_wid > b_plate_len:
        issues.append('part B: post is wider than the plate it carries')

    if issues:
        raise SystemExit('LAYOUT CONFLICT:\n  - ' + '\n  - '.join(issues))


def build_a():
    """Part A — servo to PVC blade. Plate top face at z = 0, leg at the far end."""
    leg_x = a_plate_len - a_leg_th / 2
    parts = [
        box([a_plate_len, a_plate_wid, a_plate_th],
            [a_plate_len / 2, 0, -a_plate_th / 2]),
        box([a_leg_th, a_plate_wid, a_leg_h],
            [leg_x, 0, -a_plate_th - a_leg_h / 2]),
        gusset(a_plate_len - a_leg_th, -a_plate_th, fillet_r * 2, a_plate_wid, -1),
    ]
    body = fuse(parts)

    bz = -a_plate_th - a_rebate_top - a_blade_w / 2
    over = 10.0
    if a_rebate_face == 'outer':
        cx = a_plate_len + over / 2 - a_rebate_d / 2
    else:
        cx = a_plate_len - a_leg_th - over / 2 + a_rebate_d / 2

    cuts = [
        # rectangular pocket in the underside, seating the servo horn
        box([a_horn_len, a_horn_wid, a_horn_d + over],
            [a_servo_bolt_x, 0, -a_plate_th + (a_horn_d + over) / 2 - over]),
        # one bolt down through the plate into the horn's centre screw
        cyl(a_servo_bolt_d, a_plate_th * 3, [a_servo_bolt_x, 0, -a_plate_th / 2]),
        # blade seat: rebate to the blade width, across the full leg width
        box([a_rebate_d + over, a_plate_wid + over, a_blade_w], [cx, 0, bz]),
        # the bolt through the centre of the seat
        cyl(a_blade_bolt_d, a_leg_th * 4, [leg_x, 0, bz], axis='x'),
    ]
    m = body.difference(fuse(cuts))
    m.merge_vertices()
    m.fix_normals()
    return m


def build_b():
    """Part B — servo assembly to conveyor frame. Plate top face at z = 0."""
    parts = [
        box([b_plate_len, b_plate_wid, b_plate_th],
            [0, 0, -b_plate_th / 2]),
        box([b_post_wid, b_post_th, b_post_h],
            [0, -(b_plate_wid - b_post_th) / 2, -b_plate_th - b_post_h / 2]),
        gusset(-b_post_wid / 2, -b_plate_th, fillet_r * 2, b_post_th, +1),
    ]
    # gusset() centres its extrusion on y = 0; shift it onto the post wall
    parts[2].apply_translation([0, -(b_plate_wid - b_post_th) / 2, 0])
    body = fuse(parts)

    cuts = [
        # window the servo body passes through
        box([b_window_len, b_window_wid, b_plate_th * 3], [0, 0, -b_plate_th / 2]),
    ]
    # four bolt holes, two in each margin beside the window
    for sx in (-1, 1):
        for sy in (-1, 1):
            cuts.append(cyl(b_bolt_d, b_plate_th * 3,
                            [sx * (b_window_len / 2 + b_bolt_margin),
                             sy * b_bolt_pitch / 2, -b_plate_th / 2]))
    # height-adjustment slot down the post
    slot_h = b_post_h - 2 * b_slot_end
    cuts.append(vslot_y(b_slot_wid, slot_h, b_post_th * 4,
                        [0, -(b_plate_wid - b_post_th) / 2,
                         -b_plate_th - b_post_h / 2]))

    m = body.difference(fuse(cuts))
    m.merge_vertices()
    m.fix_normals()
    return m


def preview(mesh, stem):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    for name, elev, azim in (('iso', 24, -62), ('side', 4, -90)):
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection='3d')
        tris = mesh.vertices[mesh.faces]
        n = mesh.face_normals
        v = np.array([math.cos(math.radians(elev)) * math.cos(math.radians(azim)),
                      math.cos(math.radians(elev)) * math.sin(math.radians(azim)),
                      math.sin(math.radians(elev))])
        # light from over the viewer's shoulder; no facet edges, or the triangulation
        # of every flat face shows up as spurious diagonals
        key = v / np.linalg.norm(v)
        lit = 0.38 + 0.62 * np.clip(n @ key, 0, 1) ** 0.8
        lit = np.clip(lit + 0.18 * np.clip(-n @ key, 0, 1), 0, 1)
        cols = np.stack([lit * 0.80, lit * 0.82, lit * 0.86, np.ones_like(lit)], axis=1)
        ax.add_collection3d(Poly3DCollection(
            tris, facecolors=cols, edgecolor='none', linewidths=0, alpha=1.0,
            shade=False))
        b = mesh.bounds
        ctr = b.mean(axis=0)
        r = (b[1] - b[0]).max() / 2 * 1.05
        ax.set_xlim(ctr[0] - r, ctr[0] + r)
        ax.set_ylim(ctr[1] - r, ctr[1] + r)
        ax.set_zlim(ctr[2] - r, ctr[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        fig.tight_layout()
        out = f'{stem}_{name}.png'
        fig.savefig(out, dpi=130, facecolor='white')
        plt.close(fig)
        print('preview:', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true')
    args = ap.parse_args()

    check_layout()
    for name, fn in (('part_a_servo_pvc', build_a), ('part_b_conveyor_post', build_b)):
        m = fn()
        m.export(f'{name}.stl')
        bb = m.bounds[1] - m.bounds[0]
        print(f'{name}.stl')
        print(f'  bounding box : {bb[0]:.1f} x {bb[1]:.1f} x {bb[2]:.1f} mm')
        print(f'  volume       : {m.volume/1000:.1f} cm3  '
              f'(~{m.volume/1000*1.24:.0f} g in PLA at 100% infill)')
        print(f'  watertight   : {m.is_watertight}')
        if args.preview:
            preview(m, name)
