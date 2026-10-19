"""Draw every report figure and collect them in output/all_figures.pdf.

Run:  python make_all.py              # all figures
      python make_all.py E2 E3        # selected figures (keys below)
"""
import sys
from matplotlib.backends.backend_pdf import PdfPages

from style import OUT_DIR, save
import fig_1_setup, fig_2_pipeline, fig_B1_reconstruction
import fig_E1_static_points, fig_E2_trailing_gaps, fig_E3_case_trial9

FIGURES = {'1': fig_1_setup, '2': fig_2_pipeline, 'B1': fig_B1_reconstruction,
           'E1': fig_E1_static_points, 'E2': fig_E2_trailing_gaps, 'E3': fig_E3_case_trial9}

if __name__ == '__main__':
    keys = sys.argv[1:] or list(FIGURES)
    OUT_DIR.mkdir(exist_ok=True)
    with PdfPages(OUT_DIR / 'all_figures.pdf') as pdf:
        for k in keys:
            save(FIGURES[k].draw(), FIGURES[k].NAME, pdf)
    print('output:', OUT_DIR)
