"""Fig. E2. Output limits of trailing gaps: (a) output length, 320-frame gaps; (b) 3D RMSE, 150-frame gaps.

Run alone:  python fig_E2_trailing_gaps.py   ->  output/fig_E2_trailing_gap.pdf, .png
"""
import numpy as np
from matplotlib.ticker import FuncFormatter, NullFormatter

from style import CONFIG, C, new_fig, style_ax, save, read_sheet

NAME = 'fig_E2_trailing_gap'


def draw():
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
