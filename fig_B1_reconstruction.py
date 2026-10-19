"""Fig. B1. Coordinate reconstruction in single-camera intervals (detail of steps 9–10).

Run alone:  python fig_B1_reconstruction.py   ->  output/fig_B1_recovery_flow.pdf, .png
"""

from style import save, canvas, fd_box, fd_diamond, fd_arrow

NAME = 'fig_B1_recovery_flow'


def draw():
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
