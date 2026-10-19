# Report figures

Figures for the report *3D Object Tracking Tool for Underwater Gripper Experiments*. One Python file per figure.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dodokim777-boop/figure/blob/main/report_figures.ipynb)

| File | Figure | Data sheet |
|---|---|---|
| `fig_1_setup.py` | Fig. 1 Tank, cameras, coordinate frames | — (geometry in the code) |
| `fig_2_pipeline.py` | Fig. 2 Processing pipeline | — |
| `fig_B1_reconstruction.py` | Fig. B1 Single-camera reconstruction | — |
| `fig_E1_static_points.py` | Fig. E1 18 static points, error vectors | `E1` |
| `fig_E2_trailing_gaps.py` | Fig. E2 Output limits of trailing gaps | `E2`, `E2_interior` |
| `fig_E3_case_trial9.py` | Fig. E3 Representative case (trial 9) | `E3` |
| `style.py` | Shared format (`CONFIG`, colors `C`) and helpers | |
| `make_all.py` | Draws all figures into `output/all_figures.pdf` | |
| `figure_data.xlsx` | Data; sheet `Sources` lists the source files | |

## Draw

- One figure: `python fig_E2_trailing_gaps.py` → `output/fig_E2_trailing_gap.pdf`, `.png`
- All figures: `python make_all.py` (or `python make_all.py E2 E3`)
- Colab: open the badge above and run the cells.

Requires numpy, pandas, openpyxl, matplotlib.

## Edit

- Content of one figure (labels, sizes, layout): its `fig_*.py` file, function `draw()`.
- Format of all figures (font, column width, font size, colors, file types): `style.py`.
- Data: the sheet of `figure_data.xlsx`.

## Notes

- Fig. 1: camera positions from the 0920 calibration (C = −Rᵀt); tank plan 80 cm × 80 cm from the trajectory viewer; tank height 75 cm approximate.
- Sheet `E3` was made with the postprocessing code of 30 Sep (Section 5.4 analysis scripts).
- The processing code is in [underwater-gripper-tracking](https://github.com/dodokim777-boop/underwater-gripper-tracking).
