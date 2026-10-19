"""Fig. 1. Tank, top and front cameras, reference marker and gripper frame (schematic).

Run alone:  python fig_1_setup.py   ->  output/fig_1_setup_schematic.pdf, .png
"""
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from style import CONFIG, C, new_fig, style_ax, save

NAME = 'fig_1_setup_schematic'


def draw():
    G = np.array([-26.5, 28.0, 17.1]); zW, yF = 67.0, -11.6
    Ct = np.array([-32.0, 24.9, 108.2]); Cf = np.array([-27.3, -65.1, 42.6])
    tank = np.array([[-66.5, 13.5], [yF, 68.4], [0, 66]])
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
