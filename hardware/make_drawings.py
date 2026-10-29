#!/usr/bin/env python3
"""
Dimensioned drawings for the two CPS-Sort brackets.

    python3 make_drawings.py        # writes brackets_drawing.pdf (2 pages) and PNGs

Imports brackets.py, so the drawings and the STLs cannot drift apart: change a
parameter there and both regenerate from it.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle

import brackets as M

INK = '#1b1d21'
DIM = '#c00000'
GHOST = '#9aa0a6'
SEAT = '#f2d7d5'


def dim_h(ax, x0, x1, y, label, off=0, tick=2.0):
    y = y + off
    ax.annotate('', xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='<->', color=DIM, lw=0.8,
                                shrinkA=0, shrinkB=0))
    for x in (x0, x1):
        ax.plot([x, x], [y - tick, y + tick], color=DIM, lw=0.6)
    ax.text((x0 + x1) / 2, y + 2.5, label, ha='center', va='bottom',
            fontsize=7.5, color=DIM)


def dim_v(ax, y0, y1, x, label, off=0, tick=2.0):
    x = x + off
    ax.annotate('', xy=(x, y0), xytext=(x, y1),
                arrowprops=dict(arrowstyle='<->', color=DIM, lw=0.8,
                                shrinkA=0, shrinkB=0))
    for y in (y0, y1):
        ax.plot([x - tick, x + tick], [y, y], color=DIM, lw=0.6)
    ax.text(x - 2.5, (y0 + y1) / 2, label, ha='right', va='center',
            fontsize=7.5, color=DIM, rotation=90)


def view_label(ax, text):
    ax.text(0.0, 1.0, text, transform=ax.transAxes, ha='left', va='bottom',
            fontsize=9, color=INK)


def finish(ax, xlim, ylim):
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


# ============================================================== PART A
def page_a(fig):
    L, W, T = M.a_plate_len, M.a_plate_wid, M.a_plate_th
    LH, LT = M.a_leg_h, M.a_leg_th

    gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.5, 1.5],
                          left=0.07, right=0.97, top=0.88, bottom=0.11, hspace=0.42)
    ax1, ax2, ax3 = (fig.add_subplot(gs[i]) for i in range(3))

    # ---- TOP VIEW: plate in plan, servo bolt hole, leg footprint
    ax1.add_patch(Rectangle((0, 0), L, W, fill=False, ec=INK, lw=1.3))
    ax1.add_patch(Rectangle((L - LT, 0), LT, W, fill=False, ec=GHOST, lw=0.8, ls='--'))
    sx = M.a_servo_bolt_x
    # horn pocket is in the underside, so it is hidden detail in plan
    ax1.add_patch(Rectangle((sx - M.a_horn_len / 2, W / 2 - M.a_horn_wid / 2),
                            M.a_horn_len, M.a_horn_wid,
                            facecolor=SEAT, ec=INK, lw=1.0, ls=(0, (5, 3))))
    ax1.add_patch(Circle((sx, W / 2), M.a_servo_bolt_d / 2, fill=False, ec=INK, lw=1.0))
    dim_h(ax1, 0, L, W, f'{L:.0f}', off=14)
    dim_v(ax1, 0, W, L, f'{W:.0f}', off=13)
    dim_h(ax1, 0, sx, 0, f'{sx:.0f}', off=-13)
    dim_h(ax1, sx - M.a_horn_len / 2, sx + M.a_horn_len / 2, W,
          f'{M.a_horn_len:.0f}', off=4)
    dim_v(ax1, W / 2 - M.a_horn_wid / 2, W / 2 + M.a_horn_wid / 2, 0,
          f'{M.a_horn_wid:.0f}', off=-13)
    ax1.text(sx + M.a_horn_len / 2 + 8, W / 2,
             f'SERVO HORN POCKET\n{M.a_horn_len:.0f} × {M.a_horn_wid:.0f} × '
             f'{M.a_horn_d:.0f} deep, in the underside.\n'
             f'⌀{M.a_servo_bolt_d:.1f} bolt into the horn screw.',
             ha='left', va='center', fontsize=7, color=INK)
    ax1.text(L - LT - 5, W / 2, 'leg below', ha='right', va='center',
             fontsize=7, color=GHOST)
    view_label(ax1, 'TOP VIEW')
    finish(ax1, (-26, L + 26), (-26, W + 26))

    # ---- SIDE VIEW: plate on edge, leg hanging down, blade seat on the leg
    ax2.add_patch(Rectangle((0, -T), L, T, fill=False, ec=INK, lw=1.3))
    ax2.add_patch(Rectangle((L - LT, -T - LH), LT, LH, fill=False, ec=INK, lw=1.3))

    sz0 = -T - M.a_rebate_top - M.a_blade_w          # bottom of the seat
    sz1 = -T - M.a_rebate_top                        # top of the seat
    rx0 = L - M.a_rebate_d if M.a_rebate_face == 'outer' else L - LT
    ax2.add_patch(Rectangle((rx0, sz0), M.a_rebate_d, M.a_blade_w,
                            facecolor=SEAT, ec=INK, lw=1.0))
    bz = (sz0 + sz1) / 2
    ax2.add_patch(Circle((L - LT / 2, bz), M.a_blade_bolt_d / 2,
                         fill=False, ec=INK, lw=0.9))
    ax2.plot([L - LT - 4, L + 4], [bz, bz], color=INK, lw=0.6, ls=(0, (6, 3, 1, 3)))

    # horn pocket seen on edge, cut up into the underside of the plate
    ax2.add_patch(Rectangle((sx - M.a_horn_len / 2, -T), M.a_horn_len, M.a_horn_d,
                            facecolor=SEAT, ec=INK, lw=1.0))
    ax2.plot([sx, sx], [-T - 5, 2], color=INK, lw=0.6, ls=(0, (6, 3, 1, 3)))
    dim_h(ax2, sx - M.a_horn_len / 2, sx + M.a_horn_len / 2, -T,
          f'{M.a_horn_len:.0f}', off=-14)
    ax2.text(sx + M.a_horn_len / 2 + 10, -T - 9,
             f'horn pocket, {M.a_horn_d:.0f} mm deep', ha='left', va='center',
             fontsize=7, color=INK)
    dim_v(ax2, -T, 0, 0, f'{T:.0f}', off=-13)
    dim_v(ax2, -T, sz1, L - LT, f'{M.a_rebate_top:.0f}', off=-16)
    dim_v(ax2, sz0, sz1, L - LT, f'{M.a_blade_w:.0f}', off=-48)
    dim_v(ax2, -T - LH, sz0, L - LT, f'{LH - M.a_rebate_top - M.a_blade_w:.0f}', off=-16)
    dim_v(ax2, -T - LH, -T, L, f'{LH:.0f}', off=16)
    dim_h(ax2, L - LT, L, -T - LH, f'{LT:.0f}', off=-12)
    ax2.text(L - LT - 62, bz,
             f'PVC BLADE SEAT — {M.a_rebate_d:.0f} mm rebate on the {M.a_rebate_face} face\n'
             f'of the leg, cut to the {M.a_blade_w:.0f} mm blade width,\n'
             f'one ⌀{M.a_blade_bolt_d:.1f} bolt at its centre',
             ha='right', va='center', fontsize=7, color=INK)
    view_label(ax2, 'SIDE VIEW')
    finish(ax2, (-26, L + 26), (-T - LH - 26, 26))

    # ---- FRONT VIEW: the leg seen face-on, blade bolt centred
    ax3.add_patch(Rectangle((0, -T - LH), W, LH, fill=False, ec=INK, lw=1.3))
    ax3.add_patch(Rectangle((0, -T), W, T, fill=False, ec=INK, lw=1.3))
    ax3.add_patch(Circle((W / 2, bz), M.a_blade_bolt_d / 2, fill=False, ec=INK, lw=1.0))
    dim_v(ax3, -T - LH, -T, 0, f'{LH:.0f}', off=-13)
    dim_v(ax3, -T - LH, bz, W, f'{-(-T - LH) + bz:.0f}', off=16)
    dim_h(ax3, 0, W, -T - LH, f'{W:.0f}', off=-12)
    ax3.text(W + 44, bz, 'blade retaining bolt', ha='left', va='center',
             fontsize=7, color=INK)
    view_label(ax3, 'FRONT VIEW  (leg)')
    finish(ax3, (-26, W + 150), (-T - LH - 26, 26))

    fig.suptitle('PART A — moving arm: servo horn to PVC deflector blade',
                 x=0.07, y=0.965, ha='left', fontsize=12, color=INK)
    fig.text(0.07, 0.925, 'All dimensions in millimetres.  Material: PLA.  Quantity: 4.',
             ha='left', fontsize=8, color=INK)
    fig.text(0.07, 0.045,
             'Dimensions from the author\'s dimensioned sketch of 26 October 2026 and his '
             'markup of this drawing the same day, which moved the blade\nseat to the inner '
             'face of the leg and added the pocket that seats the rectangular servo horn. '
             'Not on either, and therefore assumed:\nthe servo bolt diameter '
             f'(⌀{M.a_servo_bolt_d:.1f}, M3 clearance) and the blade bolt diameter '
             f'(⌀{M.a_blade_bolt_d:.1f}). The original AutoCAD model was lost; this is a '
             'parametric\nre-derivation and has not been re-printed or re-fitted.',
             ha='left', fontsize=7, color=DIM)


# ============================================================== PART B
def page_b(fig):
    PL, PW, PT = M.b_plate_len, M.b_plate_wid, M.b_plate_th
    H, PO, SW = M.b_post_h, M.b_post_wid, M.b_slot_wid
    margin = (PL - M.b_window_len) / 2

    gs = fig.add_gridspec(2, 2, height_ratios=[0.95, 3.0], width_ratios=[1.0, 1.25],
                          left=0.07, right=0.97, top=0.88, bottom=0.11,
                          hspace=0.26, wspace=0.18)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    # ---- TOP VIEW: plate, servo window, four bolt holes
    ax1.add_patch(Rectangle((-PL / 2, -PW / 2), PL, PW, fill=False, ec=INK, lw=1.3))
    ax1.add_patch(Rectangle((-M.b_window_len / 2, -M.b_window_wid / 2),
                            M.b_window_len, M.b_window_wid, fill=False, ec=INK, lw=1.2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax1.add_patch(Circle((sx * (M.b_window_len / 2 + M.b_bolt_margin),
                                  sy * M.b_bolt_pitch / 2),
                                 M.b_bolt_d / 2, fill=False, ec=INK, lw=1.0))
    dim_h(ax1, -M.b_window_len / 2, M.b_window_len / 2, M.b_window_wid / 2,
          f'{M.b_window_len:.0f}', off=4)
    dim_h(ax1, M.b_window_len / 2, PL / 2, -PW / 2, f'{margin:.0f}', off=-11)
    dim_h(ax1, -PL / 2, PL / 2, -PW / 2, f'{PL:.0f}', off=-24)
    dim_v(ax1, -PW / 2, PW / 2, PL / 2, f'{PW:.0f}*', off=11)
    ax1.text(0, M.b_window_wid / 2 + 13, 'servo window', ha='center', va='bottom',
             fontsize=7, color=INK)
    view_label(ax1, 'TOP VIEW')
    finish(ax1, (-PL / 2 - 34, PL / 2 + 34), (-PW / 2 - 40, PW / 2 + 30))

    # ---- SIDE VIEW: plate on edge, post hanging down
    y0 = -(PW - M.b_post_th) / 2
    ax2.add_patch(Rectangle((-PW / 2, -PT), PW, PT, fill=False, ec=INK, lw=1.3))
    ax2.add_patch(Rectangle((y0 - M.b_post_th / 2, -PT - H), M.b_post_th, H,
                            fill=False, ec=INK, lw=1.3))
    dim_v(ax2, -PT, 0, -PW / 2, f'{PT:.0f}', off=-13)
    dim_v(ax2, -PT - H, -PT, PW / 2, f'{H:.0f}', off=16)
    dim_h(ax2, y0 - M.b_post_th / 2, y0 + M.b_post_th / 2, -PT - H,
          f'{M.b_post_th:.0f}*', off=-14)
    view_label(ax2, 'SIDE VIEW')
    finish(ax2, (-PW / 2 - 34, PW / 2 + 34), (-PT - H - 34, 30))

    # ---- FRONT VIEW: post face-on with the height-adjustment slot
    slot_h = H - 2 * M.b_slot_end
    ax3.add_patch(Rectangle((-PL / 2, -PT), PL, PT, fill=False, ec=INK, lw=1.3))
    ax3.add_patch(Rectangle((-PO / 2, -PT - H), PO, H, fill=False, ec=INK, lw=1.3))
    sz = -PT - H / 2
    r = SW / 2
    ax3.add_patch(Circle((0, sz - slot_h / 2 + r), r, fill=False, ec=INK, lw=1.0))
    ax3.add_patch(Circle((0, sz + slot_h / 2 - r), r, fill=False, ec=INK, lw=1.0))
    for s in (-1, 1):
        ax3.plot([s * r, s * r], [sz - slot_h / 2 + r, sz + slot_h / 2 - r],
                 color=INK, lw=1.0)
    dim_v(ax3, -PT - H, -PT, -PO / 2, f'{H:.0f}', off=-15)
    dim_h(ax3, -PO / 2, -SW / 2, -PT - H, f'{(PO - SW) / 2:.0f}', off=-16)
    dim_h(ax3, SW / 2, PO / 2, -PT - H, f'{(PO - SW) / 2:.0f}', off=-16)
    dim_h(ax3, -SW / 2, SW / 2, -PT - H, f'{SW:.0f}', off=-34)
    dim_h(ax3, -PO / 2, PO / 2, -PT - H, f'{PO:.0f}', off=-52)
    ax3.text(PO / 2 + 8, sz,
             'slot for setting the servo\nheight above the belt\n'
             'at assembly',
             ha='left', va='center', fontsize=7, color=INK)
    view_label(ax3, 'FRONT VIEW')
    finish(ax3, (-PL / 2 - 34, PL / 2 + 150), (-PT - H - 66, 30))

    fig.suptitle('PART B — fixed bracket: servo to conveyor frame',
                 x=0.07, y=0.965, ha='left', fontsize=12, color=INK)
    fig.text(0.07, 0.925, 'All dimensions in millimetres.  Material: PLA.  Quantity: 4.',
             ha='left', fontsize=8, color=INK)
    fig.text(0.07, 0.045,
             'Dimensions marked * are NOT on the author\'s sketch and are assumed: the plate '
             f'depth ({PW:.0f} mm) and the post thickness ({M.b_post_th:.0f} mm).\n'
             f'Also assumed, and not dimensioned here: the servo window depth '
             f'({M.b_window_wid:.0f} mm, MG995 body plus clearance), the four bolt holes '
             f'(⌀{M.b_bolt_d:.1f} at {M.b_bolt_pitch:.0f} mm\npitch) and where the slot stops '
             f'at each end ({M.b_slot_end:.0f} mm). The original AutoCAD model was lost; this '
             'is a parametric re-derivation.',
             ha='left', fontsize=7, color=DIM)


# ============================================================== BLADE
def page_c(fig):
    import math
    L, W = M.blade_len, M.blade_width
    BA, ANG = M.blade_bend_at, M.blade_bend_angle
    tail = L - BA
    rise = tail * math.sin(math.radians(ANG))
    run = tail * math.cos(math.radians(ANG))

    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0],
                          left=0.07, right=0.97, top=0.86, bottom=0.30, hspace=0.55)
    ax1, ax2 = (fig.add_subplot(gs[i]) for i in range(2))

    # ---- FLAT PATTERN, before bending
    ax1.add_patch(Rectangle((0, 0), L, W, fill=False, ec=INK, lw=1.4))
    ax1.add_patch(Rectangle((0, 0), BA, W, facecolor='#eef1f4', ec='none'))
    ax1.plot([BA, BA], [-4, W + 4], color=DIM, lw=1.0, ls=(0, (7, 3, 1.5, 3)))
    ax1.add_patch(Circle((M.blade_hole_x, W / 2), 2.25, fill=False, ec=INK, lw=1.0))

    dim_h(ax1, 0, L, W, f'{L:.0f}', off=16)
    dim_h(ax1, 0, BA, 0, f'{BA:.0f}', off=-13)
    dim_h(ax1, BA, L, 0, f'{tail:.0f}', off=-13)
    dim_v(ax1, 0, W, L, f'{W:.0f}', off=13)
    dim_h(ax1, 0, M.blade_hole_x, W, f'{M.blade_hole_x:.0f}*', off=4)
    ax1.text(BA + 3, W + 9, 'BEND LINE', ha='left', va='bottom',
             fontsize=7.5, color=DIM)
    ax1.text(BA / 2, W / 2, 'bolts to part A', ha='center', va='center',
             fontsize=7, color=GHOST)
    view_label(ax1, 'FLAT PATTERN  —  cut from PVC trim profile')
    finish(ax1, (-30, L + 30), (-30, W + 34))

    # ---- SIDE PROFILE, after bending
    ax2.plot([0, BA], [0, 0], color=INK, lw=2.2, solid_capstyle='butt')
    ax2.plot([BA, BA + run], [0, -rise], color=INK, lw=2.2, solid_capstyle='butt')
    ax2.plot([BA, L], [0, 0], color=GHOST, lw=0.8, ls=(0, (5, 4)))
    th = [i * math.radians(ANG) / 24 for i in range(25)]
    ax2.plot([BA + 26 * math.cos(t) for t in th],
             [-26 * math.sin(t) for t in th], color=DIM, lw=0.8)
    ax2.text(BA + 32, -8, f'{ANG:.0f}°', ha='left', va='center',
             fontsize=8.5, color=DIM)

    dim_h(ax2, 0, BA, -rise, f'{BA:.0f}', off=-16)
    dim_v(ax2, -rise, 0, BA + run, f'{rise:.1f}', off=15)
    ax2.text(BA + run / 2, -rise - 30,
             f'tip stands {rise:.1f} mm off the straight run', ha='center',
             va='top', fontsize=7, color=INK)
    ax2.text(0, 10, 'root — clamped in the 20 mm seat on part A\'s leg',
             ha='left', va='bottom', fontsize=7, color=INK)
    view_label(ax2, 'SIDE PROFILE  —  after bending')
    finish(ax2, (-30, L + 30), (-rise - 50, 34))

    fig.suptitle('PVC DEFLECTOR BLADE — cut and bend',
                 x=0.07, y=0.945, ha='left', fontsize=12, color=INK)
    fig.text(0.07, 0.905,
             'All dimensions in millimetres.  Material: PVC trim profile.  Quantity: 4.',
             ha='left', fontsize=8, color=INK)
    fig.text(0.07, 0.20,
             'METHOD\n'
             f'  1.  Cut a {L:.0f} × {W:.0f} mm strip from PVC trim profile.\n'
             f'  2.  Drill one ⌀4.5 mm hole on the centre line, {M.blade_hole_x:.0f} mm '
             'from the root end.\n'
             f'  3.  Bend the last {tail:.0f} mm through {ANG:.0f}°, away from the belt. '
             f'The tip then stands {rise:.1f} mm off the straight run.\n'
             f'  4.  Bolt the root into the {M.a_blade_w:.0f} mm seat on part A\'s leg.',
             ha='left', fontsize=8, color=INK, va='top', linespacing=1.6)
    fig.text(0.07, 0.065,
             f'The {L:.0f} mm length, the {W:.0f} mm width, the bend from {BA:.0f} mm to '
             f'the tip and the {ANG:.0f}° angle are the author\'s measurements of the\n'
             f'physical blade. Marked * and therefore assumed: the bolt hole position '
             f'({M.blade_hole_x:.0f} mm from the root). The bend radius is not specified '
             '— it was\nformed by hand, so a builder should match the angle, not a radius.',
             ha='left', fontsize=7, color=DIM)


if __name__ == '__main__':
    with PdfPages('brackets_drawing.pdf') as pdf:
        for n, fn in (('a', page_a), ('b', page_b), ('c', page_c)):
            fig = plt.figure(figsize=(8.27, 11.69))
            fn(fig)
            pdf.savefig(fig, facecolor='white')
            fig.savefig(f'brackets_drawing_{n}.png', dpi=300, facecolor='white')
            plt.close(fig)
            print(f'written brackets_drawing_{n}.png')
    print('written brackets_drawing.pdf')
