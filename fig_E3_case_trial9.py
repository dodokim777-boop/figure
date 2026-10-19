"""Fig. E3. Representative case of single-camera reconstruction (trial 9, front-camera loss).

Run alone:  python fig_E3_case_trial9.py   ->  output/fig_E3_case_trial9.pdf, .png
"""

from style import CONFIG, C, new_fig, style_ax, save, read_sheet

NAME = 'fig_E3_case_trial9'


def draw():
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
