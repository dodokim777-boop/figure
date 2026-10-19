"""Shared style and helpers for all report figures.

Change the format of every figure here (CONFIG and colors C).
Each figure is in its own file (fig_*.py) and imports this module.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Polygon

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
)
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


def save(fig, name, pdf_pages=None):
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


FONT = setup_style()
