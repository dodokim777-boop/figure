"""Report figures (Fig. 1, 2, B1, E1–E3).

Run:     python make_figures.py               # all figures
         python make_figures.py --only E2 E3  # selected figures
Output:  output/<figure>.pdf and .png, plus output/all_figures.pdf

Change the format (font, width, font size, colors, file types) in CONFIG only.
Each figure is one fig_<name> function. Data: figure_data.xlsx (see the Sources sheet).
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.ticker import FuncFormatter, NullFormatter

logging.getLogger('fontTools').setLevel(logging.ERROR)

# ============================== CONFIG ==============================
CONFIG = dict(
    font=None,                 # None: first installed font in FONT_CANDIDATES
    width_single_cm=8.8,       # single-column width
    width_double_cm=18.0,      # double-column width
    font_size=8,               # ticks, legends, text [pt]
    title_size=8.5,            # panel titles [pt]
    line_width=1.0,
    axes_line_width=0.6,
    marker_size=22,            # scatter marker area [pt^2]
    panel_titles=True,         # show (a), (b) panel titles
    formats=('pdf', 'png'),    # 'pdf', 'svg', 'eps' are vector; 'png', 'tif' raster
    dpi=600,
    combined_pdf=True,         # also write output/all_figures.pdf
)
FIG_LIST = ['1', '2', 'B1', 'E1', 'E2', 'E3']

FONT_CANDIDATES = ['Arial', 'Helvetica', 'Liberation Sans', 'DejaVu Sans']

C = dict(
    ref=(0.12, 0.29, 0.49), obs=(0.75, 0.22, 0.17), vec=(0.45, 0.50, 0.52),
    front=(0.12, 0.29, 0.49), top=(0.75, 0.22, 0.17), zone_entry=(0.55, 0.71, 0.86),
    grey=(0.70, 0.72, 0.74), shade=(0.86, 0.90, 0.95), limit=(0.93, 0.49, 0.13),
    zone=(0.93, 0.49, 0.13), water=(0.80, 0.90, 0.97), wall=(0.85, 0.86, 0.88),
    box_fill=(0.93, 0.95, 0.98), box_edge=(0.12, 0.29, 0.49),
    data_fill=(0.95, 0.95, 0.95), data_edge=(0.45, 0.50, 0.52),
    dec_fill=(1.00, 0.97, 0.90), dec_edge=(0.89, 0.51, 0.09),
    stop_fill=(0.99, 0.93, 0.92), stop_edge=(0.75, 0.22, 0.17),
)
# ===================================================================

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / 'figure_data.xlsx'
OUT_DIR = HERE / 'output'
CM = 1 / 2.54


# ------------------------------ common ------------------------------
def setup_style():
    font = CONFIG['font']
    if font is None:
        installed = {f.name for f in font_manager.fontManager.ttflist}
        font = next((f for f in FONT_CANDIDATES if f in installed), 'DejaVu Sans')
    plt.rcParams.update({
        'font.family': font, 'font.size': CONFIG['font_size'],
        'axes.titlesize': CONFIG['title_size'], 'axes.labelsize': CONFIG['font_size'],
        'xtick.labelsize': CONFIG['font_size'], 'ytick.labelsize': CONFIG['font_size'],
        'legend.fontsize': CONFIG['font_size'] - 0.5, 'lines.linewidth': CONFIG['line_width'],
        'axes.linewidth': CONFIG['axes_line_width'], 'xtick.direction': 'out', 'ytick.direction': 'out',
        'axes.unicode_minus': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    })
    return font


def new_fig(width, height_cm):
    w = CONFIG['width_double_cm'] if width == 'double' else CONFIG['width_single_cm']
    return plt.figure(figsize=(w * CM, height_cm * CM))


def style_ax(ax, letter=None, title=None, grid=True):
    for s in ax.spines.values():
        s.set_linewidth(CONFIG['axes_line_width'])
    if grid:
        ax.grid(True, alpha=0.15, linewidth=0.5)
        ax.set_axisbelow(True)
    if letter and CONFIG['panel_titles']:
        ax.set_title(f'({letter}) {title}' if title else f'({letter})')


def save(fig, name, pdf_pages):
    OUT_DIR.mkdir(exist_ok=True)
    for fmt in CONFIG['formats']:
        fig.savefig(OUT_DIR / f'{name}.{fmt}', dpi=CONFIG['dpi'], bbox_inches='tight', pad_inches=0.02)
    if pdf_pages is not None:
        pdf_pages.savefig(fig, bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
    print('saved:', name)


def read_sheet(name):
    return pd.read_excel(DATA_FILE, sheet_name=name)


# ------------------------------ diagram helpers ------------------------------
def canvas(width, height_cm):
    w = CONFIG['width_double_cm'] if width == 'double' else CONFIG['width_single_cm']
    fig = plt.figure(figsize=(w * CM, height_cm * CM))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w); ax.set_ylim(0, height_cm); ax.set_aspect('equal'); ax.axis('off')
    return fig, ax


def fd_lines(ax, cx, cy, header, body, fs=None):
    fs = fs or CONFIG['font_size'] - 0.5
    body = [body] if isinstance(body, str) else list(body)
    lines = ([header] if header else []) + body
    bold = ([True] if header else []) + [False] * len(body)
    lh = 1.3 * fs * 0.0353
    top = cy + (len(lines) - 1) * lh / 2
    for i, (t, b) in enumerate(zip(lines, bold)):
        ax.text(cx, top - i * lh, t, ha='center', va='center', fontsize=fs,
                fontweight='bold' if b else 'normal')


def fd_box(ax, cx, cy, w, h, header, body, kind='process'):
    face, edge = {'data': (C['data_fill'], C['data_edge']), 'stop': (C['stop_fill'], C['stop_edge']),
                  'dashed': ((1, 1, 1), C['data_edge'])}.get(kind, (C['box_fill'], C['box_edge']))
    r = min(w, h) / 2 * 0.9 if kind == 'terminal' else 0.15
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle=f'round,pad=0,rounding_size={r}',
                                fc=face, ec=edge, lw=0.8, ls='--' if kind == 'dashed' else '-'))
    fd_lines(ax, cx, cy, header, body)


def fd_diamond(ax, cx, cy, w, h, body):
    ax.add_patch(Polygon([[cx, cy + h / 2], [cx + w / 2, cy], [cx, cy - h / 2], [cx - w / 2, cy]],
                         fc=C['dec_fill'], ec=C['dec_edge'], lw=0.8))
    fd_lines(ax, cx, cy, '', body)


def fd_arrow(ax, pts, label=None, xy=None, style='-'):
    P = np.asarray(pts, float); col = (0.25, 0.25, 0.25)
    ax.plot(P[:, 0], P[:, 1], style, color=col, lw=0.8)
    d = P[-1] - P[-2]; d = d / np.linalg.norm(d); n = np.array([-d[1], d[0]])
    tip = P[-1]; base = tip - 0.2 * d
    ax.add_patch(Polygon([tip, base + 0.09 * n, base - 0.09 * n], fc=col, ec=col))
    if label:
        ax.text(xy[0], xy[1], label, ha='center', va='center', fontsize=CONFIG['font_size'] - 1,
                color=(0.3, 0.3, 0.3))


# ============================== Fig. 1 ==============================
def fig_1(pdf):
    """Fig. 1. Tank, top and front cameras, reference marker and gripper frame (schematic).

    World coordinates (ID0 marker frame, cm). Camera centers from the 0920 calibration (C = -R'·t).
    Tank plan 80 cm × 80 cm from the trajectory viewer; tank height 75 cm is approximate.
    """
    G = np.array([-26.5, 28.0, 17.1]); zW, yF = 67.0, -11.6
    Ct = np.array([-32.0, 24.9, 108.2]); Cf = np.array([-27.3, -65.1, 42.6])
    tank = np.array([[-66.5, 13.5], [yF, 68.4], [0, 75]])
    zh, zH = 25, 25
    fs = CONFIG['font_size'] - 1
    fig = new_fig('double', 9.0)

    # (a) 3D layout
    ax = fig.add_axes([0.0, 0.0, 0.56, 0.95], projection='3d')
    bx, by, bz = tank
    V = np.array([[x, y, z] for z in bz for y in by for x in bx])
    E = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (1, 3), (4, 6), (5, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in E:
        ax.plot(*zip(V[a], V[b]), color=C['grey'], lw=0.6)
    ax.add_collection3d(Poly3DCollection([[(bx[0], by[0], zW), (bx[1], by[0], zW), (bx[1], by[1], zW), (bx[0], by[1], zW)]],
                                         fc=C['water'] + (0.45,), ec=(0.45, 0.65, 0.85)))
    ax.add_collection3d(Poly3DCollection([[(bx[0], yF, 0), (bx[1], yF, 0), (bx[1], yF, zW), (bx[0], yF, zW)]],
                                         fc=C['wall'] + (0.35,), ec=(0.6, 0.6, 0.6)))
    m = 7.5
    ax.add_collection3d(Poly3DCollection([[(-m, -m, 0), (m, -m, 0), (m, m, 0), (-m, m, 0)]], fc=(0.2, 0.2, 0.2)))
    q = 14
    for d, c, lab in [((q, 0, 0), (0.8, 0.15, 0.15), 'X'), ((0, q, 0), (0.15, 0.55, 0.2), 'Y'), ((0, 0, q), (0.15, 0.3, 0.75), 'Z')]:
        ax.quiver(0, 0, 0, *d, color=c, lw=1.2, arrow_length_ratio=0.25)
        ax.text(*(np.array(d) * 1.2), lab, color=c, fontsize=fs)
    ax.text(10, 8, 0, 'ID0 marker (world origin)', fontsize=fs)
    zx = G[0] + zh * np.array([-1, 1]); zy = G[1] + zh * np.array([-1, 1]); zz = G[2] + np.array([0, zH])
    Vz = np.array([[x, y, z] for z in zz for y in zy for x in zx])
    for a, b in E:
        ax.plot(*zip(Vz[a], Vz[b]), '--', color=C['zone'], lw=0.8)
    ax.plot([G[0]], [G[1]], [G[2]], 'ko', ms=3)
    ax.text(G[0] + 2, G[1], G[2] - 6, 'Gripper center (output origin)', fontsize=fs)
    ax.text(zx[0], zy[1], zz[1] + 3, 'Graspable zone', color=C['zone'], fontsize=fs)

    def cam(Cc, d):
        d = np.asarray(d, float); d /= np.linalg.norm(d); s, f = 7, 9
        u = np.array([1, 0, 0.]) if abs(d[2]) > 0.9 else np.array([0, 0, 1.])
        r = np.cross(d, u); r /= np.linalg.norm(r); u = np.cross(r, d)
        B = Cc + f * d; P = [B + s * (r + u), B + s * (r - u), B + s * (-r - u), B + s * (-r + u)]
        for p in P:
            ax.plot(*zip(Cc, p), color=C['ref'], lw=0.8)
        ax.add_collection3d(Poly3DCollection([P], fc=C['ref'] + (0.25,), ec=C['ref']))
        ax.plot([Cc[0]], [Cc[1]], [Cc[2]], 's', color=C['ref'], ms=4)

    cam(Ct, [0, 0, -1]); cam(Cf, [0, 1, 0])
    ax.text(Ct[0] + 6, Ct[1], Ct[2] + 4, 'Top camera', fontsize=fs)
    ax.text(Cf[0], Cf[1], Cf[2] - 14, 'Front camera', fontsize=fs, ha='center')
    ax.text(bx[0], by[1], zW + 8, f'Water surface Z = {zW:.0f} cm', color=(0.25, 0.45, 0.70), fontsize=fs)
    ax.set_xlim(-70, 20); ax.set_ylim(-70, 70); ax.set_zlim(0, 115)
    ax.set_box_aspect((90, 140, 115)); ax.view_init(elev=18, azim=-58); ax.axis('off')
    if CONFIG['panel_titles']:
        ax.set_title('(a) 3D layout', y=0.98)

    # (b) side section (Y–Z) with example refracted rays
    ax = fig.add_axes([0.62, 0.13, 0.37, 0.76])
    nA, nW = 1.0, 1.333
    ax.fill([yF, tank[1, 1], tank[1, 1], yF], [0, 0, zW, zW], color=C['water'], lw=0)
    ax.plot([yF, tank[1, 1]], [zW, zW], color=(0.45, 0.65, 0.85), lw=1.2)
    ax.plot([yF, yF], [0, tank[2, 1]], color=(0.45, 0.45, 0.45), lw=2.2)
    ax.plot([yF, tank[1, 1]], [0, 0], color=(0.3, 0.3, 0.3), lw=1.0)
    ax.add_patch(Rectangle((G[1] - zh, G[2]), 2 * zh, zH, fill=False, ec=C['zone'], ls='--', lw=0.8))
    ax.plot(G[1], G[2], 'ko', ms=3)
    ax.plot([-7.5, 7.5], [0, 0], color=(0.1, 0.1, 0.1), lw=3)
    T = G[1:]

    def bisect(f, a, b):
        fa = f(a)
        for _ in range(80):
            mid = (a + b) / 2; fm = f(mid)
            if fa * fm <= 0: b = mid
            else: a, fa = mid, fm
        return (a + b) / 2

    ys = bisect(lambda s: nA * (s - Ct[1]) / np.hypot(s - Ct[1], Ct[2] - zW) - nW * (T[0] - s) / np.hypot(T[0] - s, zW - T[1]),
                min(Ct[1], T[0]) - 1e-6, max(Ct[1], T[0]) + 1e-6)
    zs = bisect(lambda s: nA * (s - Cf[2]) / np.hypot(s - Cf[2], yF - Cf[1]) - nW * (T[1] - s) / np.hypot(T[1] - s, T[0] - yF),
                min(Cf[2], T[1]) - 1e-6, max(Cf[2], T[1]) + 1e-6)
    ax.plot([Ct[1], ys, T[0]], [Ct[2], zW, T[1]], color=C['obs'], lw=1)
    ax.plot([Cf[1], yF, T[0]], [Cf[2], zs, T[1]], color=C['obs'], lw=1)
    for Cc in (Ct, Cf):
        ax.plot(Cc[1], Cc[2], 's', color=C['ref'], ms=5)
    ax.text(Ct[1] + 4, Ct[2], 'Top camera', fontsize=fs, va='center')
    ax.text(Cf[1], Cf[2] + 8, 'Front camera', fontsize=fs, ha='center')
    ax.text(tank[1, 1] - 2, zW + 4, 'Air', fontsize=fs, ha='right')
    ax.text(tank[1, 1] - 2, zW - 5, 'Water', fontsize=fs, ha='right')
    ax.text(yF - 2, 5, 'Front interface', fontsize=fs, ha='right')
    ax.text(G[1], G[2] + zH + 3, 'Graspable zone', color=C['zone'], fontsize=fs, ha='center')
    ax.set_aspect('equal'); ax.set_xlim(-75, 75); ax.set_ylim(-5, 118)
    ax.set_xlabel('Y (world) [cm]'); ax.set_ylabel('Z (world) [cm]')
    style_ax(ax, 'b', 'Side section and refracted rays', grid=False)
    save(fig, 'fig_1_setup_schematic', pdf)


# ============================== Fig. 2 ==============================
def fig_2(pdf):
    """Fig. 2. Processing pipeline, steps 1–14 (same numbering as steps ①–⑭ in the code and README)."""
    H = 10.6
    fig, ax = canvas('double', H)
    xA, xB, xC = 3.2, 9.9, 15.5
    w, wC, h, dy = 5.6, 4.6, 1.2, 1.62
    ts = CONFIG['title_size']
    ax.text(xA, H - 0.35, 'Preprocessing (online)', fontsize=ts, fontweight='bold', ha='center')
    ax.text(xB, H - 0.35, 'Postprocessing (offline)', fontsize=ts, fontweight='bold', ha='center')
    ys = [H - 1.25 - i * dy for i in range(6)]

    colA = [('Inputs', ['Top/front videos (frame-aligned)', 'YOLO weights, calibration K·D·R·t'], 'data'),
            ('1. Object detection', ['YOLO, bounding-box center per camera'], 'process'),
            ('2–3. Refraction and triangulation', ['Vector Snell, closest points', 'ray gap ≤ 7 cm'], 'process'),
            ('4. Candidate gating', ['Jump and Mahalanobis gates', '7-of-10 track confirmation'], 'process'),
            ('5. Gripper frame', ['Measured coordinates'], 'process'),
            ('raw_N.xlsx', ['Trajectory · Triangulation · Online_Filter'], 'data')]
    colB = [('6. Outlier removal', ['Hampel test on local linear trend'], 'process'),
            ('7–8. Boundary coordinates, noise', ['Fixed anchors; σa from second differences'], 'process'),
            ('9–10. Single-camera reconstruction', ['Unobserved axis + remaining ray (Fig. B1)'], 'process'),
            ('11. Graspable zone, inferred grasp', ['Final pre-smoothing coordinates, State'], 'process'),
            ('14. Frame-wise velocity', ['Local linear slope, k = 5'], 'process'),
            ('final_N.xlsx', ['Result · Plot_Aux · Debug'], 'data')]
    for col, x in [(colA, xA), (colB, xB)]:
        for k, (hd, bd, kind) in enumerate(col):
            fd_box(ax, x, ys[k], w, h, hd, bd, kind)
            if k:
                fd_arrow(ax, [[x, ys[k - 1] - h / 2], [x, ys[k] + h / 2]])
    xm = (xA + w / 2 + xB - w / 2) / 2
    fd_arrow(ax, [[xA + w / 2, ys[5]], [xm, ys[5]], [xm, ys[0]], [xB - w / 2, ys[0]]])
    # visualization-only branch (dashed)
    yv = ys[3]
    fd_box(ax, xC, yv, wC, h, '12–13. Visualization only', ['Zone display, 3D RTS → Plot_Aux'], 'dashed')
    fd_arrow(ax, [[xB + w / 2, yv], [xC - wC / 2, yv]], style='--')
    fd_arrow(ax, [[xC, yv - h / 2], [xC, ys[5]], [xB + w / 2, ys[5]]], style='--')
    ax.text(xC, ys[5] - 0.95, 'Dashed: does not affect final\ncoordinates or velocity',
            ha='center', va='center', fontsize=CONFIG['font_size'] - 1.5, color=(0.35, 0.35, 0.35))
    save(fig, 'fig_2_pipeline', pdf)


# ============================== Fig. B1 ==============================
def fig_B1(pdf):
    """Fig. B1. Coordinate reconstruction in single-camera intervals (detail of steps 9–10)."""
    H = 12.0
    fig, ax = canvas('double', H)
    x0, w = 9.0, 7.6
    xs = [2.45, 6.75, 11.25, 15.55]; wM, hM = 3.95, 1.3
    dw, dh = 5.0, 1.15
    y_s, y_l, y_d1 = H - 0.6, H - 2.0, H - 3.45
    y_bus, y_m, y_mg = H - 4.3, H - 5.15, H - 6.15
    y_d2, y_r, y_d3, y_t = H - 6.9, H - 8.35, H - 9.8, H - 11.05
    xR = 15.55

    fd_box(ax, x0, y_s, w, 0.95, '', ['Single-camera interval', 'front lost → estimate Z;  top lost → estimate Y'], 'terminal')
    fd_arrow(ax, [[x0, y_s - 0.475], [x0, y_l + 0.65]])
    fd_box(ax, x0, y_l, w, 1.3, 'Link gaps, find boundary coordinates (B.1)',
           ['Same direction, ≤ 60 frames apart', 'search ±30 frames (60 if fewer than 3)'])
    fd_arrow(ax, [[x0, y_l - 0.65], [x0, y_d1 + dh / 2]])
    fd_diamond(ax, x0, y_d1, dw, dh, ['Gap structure?'])
    ax.plot([x0, x0], [y_d1 - dh / 2, y_bus], color=(0.25, 0.25, 0.25), lw=0.8)
    ax.plot([xs[0], xs[-1]], [y_bus, y_bus], color=(0.25, 0.25, 0.25), lw=0.8)
    boxes = [('Linear interpolation (B.2)', ['Single gap,', 'boundaries on both sides'], 'process'),
             ('1D Kalman + RTS (B.3–B.4)', ['Intermittent gaps', 'Theil–Sen start, Huber update'], 'process'),
             ('1D extrapolation (B.3–B.5)', ['Trailing or leading gap', '≤ 150 frames (300 in zone)'], 'process'),
             ('No output', ['No boundary coordinates', '(NO_RAW_ANCHOR)'], 'stop')]
    for x, (hd, bd, kind) in zip(xs, boxes):
        fd_arrow(ax, [[x, y_bus], [x, y_m + hM / 2]])
        fd_box(ax, x, y_m, wM, hM, hd, bd, kind)
    for x in xs[1:3]:
        ax.plot([x, x, x0], [y_m - hM / 2, y_mg, y_mg], color=(0.25, 0.25, 0.25), lw=0.8)
    fd_arrow(ax, [[x0, y_mg], [x0, y_d2 + dh / 2]])
    fd_diamond(ax, x0, y_d2, dw, dh, ['Posterior SD ≤ 6 cm (Z)', 'or ≤ 2 cm (Y)?'])
    fd_arrow(ax, [[x0, y_d2 - dh / 2], [x0, y_r + 0.65]], 'Yes', (x0 + 0.4, y_d2 - dh / 2 - 0.2))
    fd_arrow(ax, [[xs[0], y_m - hM / 2], [xs[0], y_r], [x0 - w / 2, y_r]])
    fd_box(ax, x0, y_r, w, 1.3, 'Ray–plane intersection and offset (B.6)',
           ['Remaining ray × plane of the unobserved axis', 'offset to the boundary coordinates'])
    fd_arrow(ax, [[x0, y_r - 0.65], [x0, y_d3 + dh / 2]])
    fd_diamond(ax, x0, y_d3, dw, dh, ['Valid intersection and', 'front-X check?'])
    fd_arrow(ax, [[x0, y_d3 - dh / 2], [x0, y_t + 0.375]], 'Yes', (x0 + 0.4, y_d3 - dh / 2 - 0.2))
    fd_box(ax, x0, y_t, 5.6, 0.75, '', ['Reconstructed coordinate (RECOVERED)'], 'terminal')
    fd_box(ax, xR, y_d3, wM, 1.3, 'Excluded (LOST)', ['Reason recorded in', 'Hidden_Stop_Reason'], 'stop')
    fd_arrow(ax, [[x0 + dw / 2, y_d2], [xR, y_d2], [xR, y_d3 + 0.65]], 'No', (x0 + dw / 2 + 0.45, y_d2 + 0.22))
    fd_arrow(ax, [[x0 + dw / 2, y_d3], [xR - wM / 2, y_d3]], 'No', (x0 + dw / 2 + 0.45, y_d3 + 0.22))
    save(fig, 'fig_B1_recovery_flow', pdf)


# ============================== Fig. E1 ==============================
def fig_E1(pdf):
    """Fig. E1. Hand-measured positions, point estimates and error vectors (×3) of the 18 static points."""
    T = read_sheet('E1')
    ref = T[['RefX_cm', 'RefY_cm', 'RefZ_cm']].to_numpy(float)
    obs = T[['ObsX_cm', 'ObsY_cm', 'ObsZ_cm']].to_numpy(float)
    k = 3; v = k * (obs - ref); pts = T['Point'].to_numpy(int)
    ms = CONFIG['marker_size']
    fig = new_fig('double', 15)
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1], hspace=0.32, wspace=0.38)

    ax = fig.add_subplot(gs[0, :], projection='3d')
    h1 = ax.scatter(*ref.T, s=ms * 1.4, color=C['ref'], marker='o', depthshade=False)
    ax.quiver(*ref.T, *v.T, color=C['vec'], lw=0.8, arrow_length_ratio=0.25)
    h2 = ax.scatter(*obs.T, s=ms * 1.2, color=C['obs'], marker='^', depthshade=False)
    for p, r in zip(pts, ref):
        ax.text(r[0], r[1], r[2] + 3, f'P{p}', fontsize=CONFIG['font_size'] - 1.5, ha='center')
    rng = np.ptp(np.r_[ref, obs], axis=0)
    ax.set_box_aspect(rng); ax.view_init(elev=22, azim=-60)
    ax.set_xlabel('X [cm]'); ax.set_ylabel('Y [cm]'); ax.set_zlabel('Z [cm]')
    ax.tick_params(labelsize=CONFIG['font_size'] - 1)
    fig.legend([h1, h2], ['Hand-measured position', 'Point estimate'],
               loc='upper right', bbox_to_anchor=(0.98, 0.93), frameon=True)
    if CONFIG['panel_titles']:
        ax.set_title(f'(a) 18 static points in the gripper frame (error vectors ×{k})')

    names = ['X', 'Y', 'Z']; titles = ['XY plane', 'XZ plane', 'YZ plane']
    for i, (a, b) in enumerate([(0, 1), (0, 2), (1, 2)]):
        ax = fig.add_subplot(gs[1, i])
        ax.quiver(ref[:, a], ref[:, b], v[:, a], v[:, b], angles='xy', scale_units='xy', scale=1,
                  color=C['vec'], width=0.006, headwidth=4, headlength=5)
        ax.scatter(ref[:, a], ref[:, b], s=ms, color=C['ref'], marker='o', zorder=3)
        ax.scatter(obs[:, a], obs[:, b], s=ms * 0.9, color=C['obs'], marker='^', zorder=3)
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel(f'{names[a]} [cm]'); ax.set_ylabel(f'{names[b]} [cm]')
        style_ax(ax, 'bcd'[i], titles[i])
        if i == 0:   # scale arrow for a 5 cm error, below all points
            x0 = -5.0; y0 = min(ref[:, b].min(), obs[:, b].min()) - 12
            ax.annotate('', xy=(x0 + 5 * k, y0), xytext=(x0, y0), arrowprops=dict(arrowstyle='->', color=C['vec'], lw=0.8))
            ax.text(x0, y0 + 2.5, f'5 cm error (×{k})', fontsize=CONFIG['font_size'] - 1.5)
            ax.plot([x0], [y0 - 3], alpha=0)
    save(fig, 'fig_E1_static18_layout', pdf)


# ============================== Fig. E2 ==============================
def fig_E2(pdf):
    """Fig. E2. Output limits of trailing gaps: (a) output length, 320-frame gaps; (b) 3D RMSE, 150-frame gaps."""
    T = read_sheet('E2'); I = read_sheet('E2_interior')
    fig = new_fig('double', 7.5)
    gs = fig.add_gridspec(1, 2, wspace=0.25)

    ax = fig.add_subplot(gs[0, 0])
    sel = lambda e, c: T[(T.Exp == e) & (T.Cond == c) & (T.GapLen == 320)].set_index('Trial')['OutFrames']
    series = [sel('TRAILING', 'FRONT'), sel('TRAILING', 'TOP'), sel('TRAILING_ZONE_ENTRY', 'FRONT')]
    trials = sorted(series[0].index)
    cols = [C['front'], C['top'], C['zone_entry']]
    labels = ['Front lost', 'Top lost', 'Front lost, after zone entry']
    x = np.arange(len(trials)); bw = 0.27
    for j, (s, c, lab) in enumerate(zip(series, cols, labels)):
        ax.bar(x + (j - 1) * bw, [s.get(t, np.nan) for t in trials], bw, color=c, label=lab)
    for yv, ls, txt in [(150, '--', 'Standard limit 150'), (300, ':', 'Extended limit 300')]:
        ax.axhline(yv, ls=ls, color=C['limit'], lw=1)
        ax.text(x[-1] + 0.5, yv + 5, txt, ha='right', va='bottom', color=C['limit'], fontsize=CONFIG['font_size'] - 1)
    ax.set_xticks(x, [str(t) for t in trials])
    ax.set_xlabel('Trial')
    ax.set_ylim(0, 340); ax.set_ylabel('Output frames')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=CONFIG['font_size'] - 1, frameon=False)
    style_ax(ax, 'a', 'Output length for a 320-frame gap')

    ax = fig.add_subplot(gs[0, 1])
    groups = [(I[(I.Placement == 'LONGEST') & (I.Cond == 'FRONT') & (I.GapLen == 150)].RMSE3D_cm,
               I[(I.Placement == 'LONGEST') & (I.Cond == 'TOP') & (I.GapLen == 150)].RMSE3D_cm),
              (T[(T.Exp == 'TRAILING') & (T.Cond == 'FRONT') & (T.GapLen == 150)].RMSE3D_cm,
               T[(T.Exp == 'TRAILING') & (T.Cond == 'TOP') & (T.GapLen == 150)].RMSE3D_cm),
              (T[(T.Exp == 'TRAILING_ZONE_ENTRY') & (T.Cond == 'FRONT') & (T.GapLen == 150)].RMSE3D_cm, None)]
    rng = np.random.default_rng(1); off = [-0.17, 0.17]
    for g, pair in enumerate(groups, start=1):
        for c, vals in enumerate(pair):
            if vals is None or len(vals) == 0:
                continue
            xs = g + off[c] + (rng.random(len(vals)) - 0.5) * 0.12
            ax.scatter(xs, vals, s=14, color=[C['front'], C['top']][c], alpha=0.75,
                       label=['Front lost', 'Top lost'][c] if g == 1 else None)
            ax.plot(g + off[c] + np.array([-0.1, 0.1]), [vals.mean()] * 2, 'k-', lw=1.4)
    ax.set_yscale('log'); ax.set_ylim(0.03, 10); ax.set_xlim(0.5, 3.5)
    ax.set_yticks([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, _: f'{val:g}'))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks([1, 2, 3], ['Interior gap', 'Trailing gap',
                              'Trailing gap\n(after zone entry)'])
    ax.set_ylabel('3D RMSE [cm]')
    ax.legend(loc='upper left', fontsize=CONFIG['font_size'] - 1)
    style_ax(ax, 'b', '3D RMSE, 150-frame gap (dots: videos, bars: mean)')
    save(fig, 'fig_E2_trailing_gap', pdf)


# ============================== Fig. E3 ==============================
def fig_E3(pdf):
    """Fig. E3. Representative case of single-camera reconstruction (trial 9, front-camera loss)."""
    D = read_sheet('E3')
    fig = new_fig('double', 11)
    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.22)
    titles = [['Interior gap, 150 frames — unobserved Z',
               'Trailing gap, 320 frames — unobserved Z'],
              ['Interior gap: 3D error',
               'Trailing gap: 3D error']]
    stop = 'Output stops'
    for c, case in enumerate(['interior150', 'trailing320']):
        S = D[D.Case == case]
        gap = S[S.InGap == 1]; out = gap[gap.Zout_cm.notna()]
        ax = fig.add_subplot(gs[0, c])
        h1 = ax.axvspan(gap.Frame.min(), gap.Frame.max(), color=C['shade'], lw=0, zorder=0)
        h2, = ax.plot(S.Frame, S.Zref_cm, 'k-', lw=0.9)
        h3, = ax.plot(S.Frame, S.Zout_cm, '-', color=C['obs'], lw=1.2)
        if c == 1:
            ax.axvline(out.Frame.max(), ls='--', color=C['limit'], lw=1)
            yl = ax.get_ylim()
            ax.text(out.Frame.max() + 4, yl[1] - 0.04 * (yl[1] - yl[0]), stop, color=C['limit'], va='top', fontsize=CONFIG['font_size'] - 1)
        ax.set_xlim(S.Frame.min(), S.Frame.max())
        ax.set_xlabel('Frame'); ax.set_ylabel('Z [cm]')
        ax.legend([h1, h2, h3], ['Gap', 'Original measured trajectory',
                                 'Reconstructed output'], loc='lower left', fontsize=CONFIG['font_size'] - 1)
        style_ax(ax, 'ab'[c], titles[0][c])

        ax = fig.add_subplot(gs[1, c])
        ax.plot(out.GapElapsed, out.Err3D_cm, '-', color=C['obs'], lw=1)
        if c == 1:
            n = int(out.GapElapsed.max())
            ax.axvline(n, ls='--', color=C['limit'], lw=1)
            ax.text(n - 2, out.Err3D_cm.max() * 0.08, f'{stop} at frame {n}',
                    color=C['limit'], ha='right', fontsize=CONFIG['font_size'] - 1)
        ax.set_ylim(bottom=0)
        ax.set_xlabel('Frames since gap start')
        ax.set_ylabel('3D error [cm]')
        style_ax(ax, 'cd'[c], titles[1][c])
    save(fig, 'fig_E3_case_trial9', pdf)


# ============================== run ==============================
FIGURES = {'1': fig_1, '2': fig_2, 'B1': fig_B1, 'E1': fig_E1, 'E2': fig_E2, 'E3': fig_E3}


def main():
    ap = argparse.ArgumentParser(description='Draw the report figures')
    ap.add_argument('--only', nargs='+', help='figures to draw, e.g. E2 E3')
    args = ap.parse_args()
    font = setup_style()
    print('font:', font)
    figs = args.only or FIG_LIST
    OUT_DIR.mkdir(exist_ok=True)
    pdf = PdfPages(OUT_DIR / 'all_figures.pdf') if CONFIG['combined_pdf'] else None
    try:
        for f in figs:
            FIGURES[f](pdf)
    finally:
        if pdf is not None:
            pdf.close()
    print('output:', OUT_DIR)


if __name__ == '__main__':
    main()
