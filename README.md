# Report figures

Figures for the report *3D Object Tracking Tool for Underwater Gripper Experiments*: Fig. 1, 2, B1 (diagrams) and E1–E3 (data).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dodokim777-boop/figure/blob/main/workflow/05_report_figures.ipynb)

| File | Content |
|---|---|
| `report_figures/make_figures.py` | All figures. Format settings in `CONFIG` at the top; one `fig_*` function per figure |
| `report_figures/figure_data.xlsx` | Data for E1–E3. Sheet `Sources` lists the source files and how each sheet was made |
| `workflow/05_report_figures.ipynb` | Colab notebook: draws and shows the figures, downloads them as a zip |

## View the figures

Open the Colab badge above and run the cells. The figures are shown in the notebook.
Locally: `python report_figures/make_figures.py` (needs numpy, pandas, openpyxl, matplotlib).
Output: `report_figures/output/` with one PDF and PNG per figure and `all_figures.pdf`.

## Edit the figures

- **Format** (font, column width, font size, colors, file types): `CONFIG` in `make_figures.py`.
- **Content** (labels, layout of one figure): its `fig_*` function.
- **Data**: the sheet of `figure_data.xlsx`.

| Report figure | Function | Sheet |
|---|---|---|
| Fig. 1 Tank, cameras, coordinate frames | `fig_1` | — (geometry in the code) |
| Fig. 2 Processing pipeline | `fig_2` | — |
| Fig. B1 Single-camera reconstruction | `fig_B1` | — |
| Fig. E1 18 static points, error vectors | `fig_E1` | `E1` |
| Fig. E2 Output limits of trailing gaps | `fig_E2` | `E2`, `E2_interior` |
| Fig. E3 Representative case (trial 9) | `fig_E3` | `E3` |

## Notes

- Fig. 1: camera positions from the 0920 calibration (C = −Rᵀt); tank plan 80 cm × 80 cm from the trajectory viewer; tank height 75 cm approximate.
- Sheet `E3` was made with the postprocessing code of 30 Sep (Section 5.4 analysis scripts).
- The processing code is in [underwater-gripper-tracking](https://github.com/dodokim777-boop/underwater-gripper-tracking).
