"""Fig. E1. Hand-measured positions, point estimates and error vectors (×3) of the 18 static points.

Run alone:  python fig_E1_static_points.py   ->  output/fig_E1_static18_layout.pdf, .png
"""
import numpy as np

from style import CONFIG, C, new_fig, style_ax, save, read_sheet

NAME = 'fig_E1_static18_layout'


def draw():
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
