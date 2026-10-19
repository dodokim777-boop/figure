"""Fig. 2. Processing pipeline, steps 1–14 (same numbering as steps ①–⑭ in the code and README).

Run alone:  python fig_2_pipeline.py   ->  output/fig_2_pipeline.pdf, .png
"""

from style import CONFIG, save, canvas, fd_box, fd_arrow

NAME = 'fig_2_pipeline'


def draw():
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
    return fig


if __name__ == '__main__':
    save(draw(), NAME)
