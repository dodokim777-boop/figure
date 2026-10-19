# Report figures

Draws the figures of the report (English version of v6): Fig. 1, 2, B1 (diagrams) and E1–E3 (data).

| File | Content |
|---|---|
| `make_figures.py` | All figures. Format settings in `CONFIG` at the top |
| `figure_data.xlsx` | Data for E1–E3. Sheet `Sources` lists the source files and how each sheet was made |
| `output/` | Created when run: one PDF and PNG per figure, and `all_figures.pdf` with every figure |

## Run

- **Colab**: open `workflow/05_report_figures.ipynb` and run the cells. The figures are shown in the notebook and can be downloaded as a zip.
- **Local**: `python report_figures/make_figures.py`
  - `--only E2 E3` draws only those figures

## Change the format

Edit `CONFIG` in `make_figures.py`: font, column width (cm), font size, colors, output formats, panel titles.
PDF output keeps text as text (TrueType), so labels stay editable in a vector editor.

## Figures and data

| Report figure | Function | Sheet |
|---|---|---|
| Fig. 1 Tank, cameras, coordinate frames | `fig_1` | — (geometry in the code) |
| Fig. 2 Processing pipeline | `fig_2` | — |
| Fig. B1 Single-camera recovery decisions | `fig_B1` | — |
| Fig. E1 18 static points, error vectors | `fig_E1` | `E1` |
| Fig. E2 Output limits of trailing gaps | `fig_E2` | `E2`, `E2_interior` |
| Fig. E3 Representative case (trial 9) | `fig_E3` | `E3` |

## Notes

- Fig. 1: camera positions come from the 0920 calibration (C = −Rᵀt). The tank plan (80 cm × 80 cm) comes from the trajectory viewer; the tank height (75 cm) is approximate.
- Sheet `E3` was made with the postprocessing code of 30 Sep (5.4 analysis scripts). It was not re-run with the current code.
- The data files (videos, raw/final Excel, NPZ) stay on Drive. This folder holds only the summary numbers the figures need.
