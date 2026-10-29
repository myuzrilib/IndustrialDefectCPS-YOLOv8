#!/usr/bin/env python3
"""
Two figures for the HardwareX article that did not exist as photographs:
  station_layout.png  — plan view of the conveyor with the four station distances
  wiring.png          — connection schematic for the control electronics

    python3 make_system_figs.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch

INK = '#1b1d21'
DIM = '#c00000'
GHOST = '#9aa0a6'
FILL = '#eef1f4'

# ---- from final.py and the manuscript
STATIONS = [('A', 0.50), ('B', 1.00), ('C', 1.50), ('D', 2.00)]
OFFSET = 0.30          # OFFSET_METERS — camera optical centre to the first trigger point
BELT_LEN = 2.30        # conveyor run, m
BELT_V = 0.054         # m/s


def dim_h(ax, x0, x1, y, label, tick=0.035, color=DIM, fs=8):
    ax.annotate('', xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='<->', color=color, lw=0.9,
                                shrinkA=0, shrinkB=0))
    for x in (x0, x1):
        ax.plot([x, x], [y - tick, y + tick], color=color, lw=0.7)
    ax.text((x0 + x1) / 2, y + 0.045, label, ha='center', va='bottom',
            fontsize=fs, color=color)


def station_layout(path):
    fig, ax = plt.subplots(figsize=(8.0, 3.9))

    belt_y0, belt_y1 = 0.0, 0.46
    ax.add_patch(Rectangle((0, belt_y0), BELT_LEN, belt_y1 - belt_y0,
                           facecolor=FILL, ec=INK, lw=1.2))
    # belt direction
    ax.add_patch(FancyArrowPatch((0.10, 0.23), (0.52, 0.23),
                                 arrowstyle='-|>', mutation_scale=14,
                                 color=GHOST, lw=1.4))
    ax.text(0.17, 0.08, f'{BELT_V} m/s', ha='center', va='bottom',
            fontsize=8, color=GHOST)

    # camera chamber at the head
    ax.add_patch(FancyBboxPatch((-0.34, 0.10), 0.34, 0.42,
                                boxstyle='round,pad=0.012',
                                facecolor='white', ec=INK, lw=1.2))
    ax.text(-0.17, 0.31, 'camera\nchamber', ha='center', va='center',
            fontsize=7.5, color=INK)
    ax.plot([0, 0], [-0.30, 0.78], color=INK, lw=0.8, ls=(0, (6, 3, 1, 3)))
    ax.text(0.012, 0.80, 'optical centre — zero of all station distances',
            ha='left', va='bottom', fontsize=7.5, color=INK)

    # trigger point
    ax.plot([OFFSET, OFFSET], [-0.12, 0.60], color=DIM, lw=0.8, ls=(0, (4, 3)))
    ax.text(OFFSET - 0.015, -0.14, 'trigger point', ha='right', va='top',
            fontsize=7.5, color=DIM)

    # stations
    for name, d in STATIONS:
        ax.add_patch(Rectangle((d - 0.035, belt_y1), 0.07, 0.17,
                               facecolor=INK, ec=INK, lw=0))
        ax.plot([d, d], [belt_y1, belt_y1 + 0.17], color=INK, lw=0)
        ax.text(d, belt_y1 + 0.20, name, ha='center', va='bottom',
                fontsize=9, color=INK)
        # blade sweeping across the belt
        ax.add_patch(FancyArrowPatch((d, belt_y1 - 0.02), (d, belt_y0 + 0.04),
                                     arrowstyle='-|>', mutation_scale=10,
                                     color=GHOST, lw=1.0))
        # bin below
        ax.add_patch(Rectangle((d - 0.085, -0.26), 0.17, 0.17,
                               facecolor='white', ec=GHOST, lw=1.0))

    dim_h(ax, 0, OFFSET, 0.64, f'{OFFSET:.2f}')
    for i, (name, d) in enumerate(STATIONS):
        dim_h(ax, 0, d, -0.42 - 0.17 * i, f'{d:.2f}')

    ax.text(BELT_LEN + 0.04, 0.23, 'belt', ha='left', va='center',
            fontsize=7.5, color=GHOST)
    ax.set_title('Station layout — distances in metres from the camera optical centre',
                 loc='left', fontsize=10, color=INK, pad=16)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-0.50, BELT_LEN + 0.26)
    ax.set_ylim(-1.14, 0.98)
    fig.tight_layout()
    fig.savefig(path, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print('written', path)


def box(ax, x, y, w, h, title, sub=None, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.10',
                                facecolor='white', ec=INK, lw=1.2))
    ax.text(x + w / 2, y + h / 2 + (0.18 if sub else 0), title,
            ha='center', va='center', fontsize=8.5, color=INK,
            fontweight='bold' if bold else 'normal')
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.30, sub, ha='center', va='center',
                fontsize=7, color=GHOST)
    return (x, y, w, h)


def link(ax, a, b, label, side='right', dashed=False, color=INK):
    ax1, ay, aw, ah = a
    bx, by, bw, bh = b
    if side == 'right':
        p0 = (ax1 + aw, ay + ah / 2)
        p1 = (bx, by + bh / 2)
    else:
        p0 = (ax1 + aw / 2, ay)
        p1 = (bx + bw / 2, by + bh)
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=11,
                                 color=color, lw=1.1,
                                 linestyle='--' if dashed else '-',
                                 shrinkA=2, shrinkB=2))
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    ax.text(mx, my + (0.16 if side == 'right' else 0),
            label, ha='center', va='bottom', fontsize=7, color=color)


def wiring(path):
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ROW = 3.4          # centre line of the signal chain

    def unit(x, w, title, sub):
        h = 0.95
        y = ROW - h / 2
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.10',
                                    facecolor='white', ec=INK, lw=1.2))
        ax.text(x + w / 2, y + h * 0.63, title, ha='center', va='center',
                fontsize=8.5, color=INK, fontweight='bold')
        ax.text(x + w / 2, y + h * 0.26, sub, ha='center', va='center',
                fontsize=7, color=GHOST)
        return x, x + w

    l0, l1 = unit(0.0, 2.3, 'Inference laptop', 'Acer Swift 1, CPU only')
    e0, e1 = unit(4.0, 1.8, 'ESP32', 'USB-powered')
    p0, p1 = unit(7.6, 2.1, 'PCA9685', '16-channel PWM')

    def wire(xa, xb, label):
        ax.add_patch(FancyArrowPatch((xa, ROW), (xb, ROW), arrowstyle='-|>',
                                     mutation_scale=12, color=INK, lw=1.1,
                                     shrinkA=3, shrinkB=3))
        ax.text((xa + xb) / 2, ROW + 0.16, label, ha='center', va='bottom',
                fontsize=7, color=INK)

    wire(l1, e0, 'USB serial\n115 200 baud')
    wire(e1, p0, 'I\u00b2C\nSDA GPIO 21  ·  SCL GPIO 22')

    # --- servos, fanned out to the right
    for i, (name, d) in enumerate(STATIONS):
        y = 2.30 - 0.60 * i
        ax.add_patch(FancyBboxPatch((10.6, y), 1.8, 0.44,
                                    boxstyle='round,pad=0.06',
                                    facecolor='white', ec=INK, lw=1.0))
        ax.text(11.5, y + 0.22, f'MG995  {name}', ha='center', va='center',
                fontsize=8, color=INK)
        ax.text(12.55, y + 0.22, f'{d:.2f} m', ha='left', va='center',
                fontsize=7, color=GHOST)
        ax.add_patch(FancyArrowPatch((p1, ROW - 0.42), (10.6, y + 0.22),
                                     arrowstyle='-|>', mutation_scale=9,
                                     color=INK, lw=0.9, shrinkA=2, shrinkB=2))
    ax.text(p1 + 0.15, ROW + 0.62, 'channels 0–3,\nin station order',
            ha='left', va='bottom', fontsize=7, color=INK)

    # --- servo supply, below the PWM board
    sy = 0.55
    ax.add_patch(FancyBboxPatch((7.6, sy), 2.1, 0.80, boxstyle='round,pad=0.10',
                                facecolor='white', ec=INK, lw=1.2))
    ax.text(8.65, sy + 0.52, 'Servo supply', ha='center', va='center',
            fontsize=8.5, color=INK, fontweight='bold')
    ax.text(8.65, sy + 0.22, 'sized for 4 × stall', ha='center', va='center',
            fontsize=7, color=GHOST)
    ax.add_patch(FancyArrowPatch((8.65, sy + 0.80), (8.65, ROW - 0.48),
                                 arrowstyle='-|>', mutation_scale=11,
                                 color=INK, lw=1.1, shrinkA=3, shrinkB=3))
    ax.text(8.80, (sy + 0.80 + ROW - 0.48) / 2, 'V+ / GND', ha='left',
            va='center', fontsize=7, color=INK)

    # --- common ground back to the ESP32
    ax.plot([7.6, 4.9, 4.9], [sy + 0.30, sy + 0.30, ROW - 0.48],
            color=DIM, lw=1.0, ls=(0, (5, 3)))
    ax.text(5.05, sy + 0.46, 'grounds tied together', ha='left', va='bottom',
            fontsize=7, color=DIM)

    ax.text(0.0, -0.30,
            'The servos run from a dedicated rail, not from the ESP32 regulator: four MG995 '
            'units under simultaneous stall exceed\nwhat the board can supply. The USB link '
            'carries both microcontroller power and the serial command channel.',
            ha='left', va='top', fontsize=7.5, color=INK)

    ax.set_title('Control electronics', loc='left', fontsize=10, color=INK, pad=14)
    ax.axis('off')
    ax.set_xlim(-0.3, 13.9)
    ax.set_ylim(-0.95, 4.5)
    fig.tight_layout()
    fig.savefig(path, dpi=300, facecolor='white', bbox_inches='tight')
    plt.close(fig)
    print('written', path)


if __name__ == '__main__':
    station_layout('station_layout.png')
    wiring('wiring.png')
