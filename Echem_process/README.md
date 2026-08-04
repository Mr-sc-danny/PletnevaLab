# UV-Vis Redox Titration Workup

Python replacement for the original MATLAB workflow (`asc_to_xlsx_Voltage.m`,
`data_analyse.m`, `Echem_plot_together.m`): turn raw `.asc` spectra into a fitted
midpoint potential, for both an oxidative and a reductive sweep, and plot the two
together.

Two pieces, run in this order:

1. **`UVVis_Redox_Workup.ipynb`** — run once per sweep direction (oxidative, then
   reductive). Converts spectra → fraction vs. potential → curve fit.
2. **`plot_together.py`** — run once, after both sweeps are done, to plot them together.

## Requirements

```
pip install numpy pandas matplotlib openpyxl ipywidgets lmfit
```

If you're on a fresh kernel/environment and hit an import error, install whichever
package is missing and restart the kernel.

## 1. Run the notebook — once per sweep

Open `UVVis_Redox_Workup.ipynb`. Everything you can change lives in the single
**"ALL PARAMETERS"** cell near the top — nothing else in the notebook needs editing.

| Parameter | What it does |
|---|---|
| `DATA_DIR` | Folder containing the `.asc` files for this sweep |
| `Electrode_Voltage` | Offset (mV) added to each filename's voltage |
| `isosbestic1`, `isosbestic2`, `Apex` | Starting positions for the wavelength-picker sliders (Part 1) |
| `num_potentials` | `1` for a single midpoint potential, `2` for two overlapping ones |
| `Ema_guess`, `n1_guess`, (`Emb_guess`, `n2_guess` if `num_potentials = 2`) | Initial guesses for the curve fit |
| `sweep_label` | `"oxi"` or `"red"` — names this run's output file |

**Steps:**

1. Set `DATA_DIR` to the folder with this sweep's `.asc` files (named only by their
   voltage, e.g. `-200.asc`, `0.asc`, `150.asc` — other characters in the filename break
   the sort/tagging).
2. Set `sweep_label` to `"oxi"` or `"red"`, matching which sweep this run is.
3. **Run All.**
4. In Part 1, drag the three sliders (`isosbestic1`, `isosbestic2`, `Apex`) until the
   dashed guide lines land on the actual isosbestic crossing points and peak in the
   spectra plots. Then run the "lock in" cell right below the sliders.
5. Re-run from Part 2 onward (or just **Run All** again) so the locked-in wavelengths
   flow through to the fit.
6. Check the fit report and the fitted-curve plot at the end of Part 3. If the fit looks
   off, adjust `num_potentials` and/or the initial guesses, then **Run All** again.

**Output:** `<sweep_label>.xlsx` (e.g. `oxi.xlsx`), containing everything needed later:
- `equation` — the fitted equation as a readable string
- `parameters` — fitted values with 95% CI, e.g. `259.8 ± 1.647`
- `parameters_numeric` — the same values as plain numbers, for `plot_together.py`
- `fit_data` — the Potential/Fraction data the fit was run on

Also written along the way: `Full_data.xlsx` (Part 1) and `PotentialFraction.xlsx`
(Part 2) — intermediate files, not needed for step 2 below.

7. **Repeat steps 1-6** for the other sweep direction (flip `sweep_label` to the other
   value, point `DATA_DIR` at that sweep's `.asc` files).

## 2. Plot both sweeps together

Copy `oxi.xlsx` and `red.xlsx` into the same folder as `plot_together.py`, then run:

```
python plot_together.py
```

It reads both files, reconstructs each fitted curve (automatically using whichever
equation that file used — one potential or two, independently for each sweep), and
reproduces the combined plot from `Echem_plot_together.m`: both fitted curves, both
sets of raw data points, bold axis labels, "Oxidative"/"Reductive" legend.

**Output:**
- `oxi_red_together.png` — the combined plot
- `midpoint_potentials.xlsx` — a small summary table:

  | | Ema | Emb |
  |---|---|---|
  | oxi | 259.8 ± 1.647 | |
  | red | 258.1 ± 1.2 | 0.0 ± 1.0 |

  (the `Emb` column only appears if at least one sweep used `num_potentials = 2`)

If you need a different filename or display range, edit the parameters block at the
top of `plot_together.py`:

```python
oxi_filename = "oxi.xlsx"
red_filename = "red.xlsx"
voltage_range = (-400, 700)     # range the fitted curves are drawn over
VoltageDisplay = (-250, 600)    # x-axis display window
```

## Troubleshooting

- **`ModuleNotFoundError`** — install the missing package (see Requirements) and
  restart the kernel.
- **`ValueError: could not convert string to float`** while reading `.asc`/`.csv`
  files in Part 1 — check for a non-numeric filename in `DATA_DIR` (the notebook
  already ignores its own output files like `oxi.xlsx`, but any other stray file with
  a non-numeric name will trigger this).
- **`PermissionError`** on saving an `.xlsx` — the file is open elsewhere (e.g. in
  Excel). Both the notebook and `plot_together.py` handle this by saving to a
  `..._new.xlsx` fallback automatically; close the original file and re-run to
  overwrite it directly.
- **Wavelength not found** (`ValueError: Wavelength ... not found in first column`) —
  `isosbestic1`/`isosbestic2`/`Apex` must land on wavelength points that actually exist
  in your spectra. Use the sliders in Part 1 to pick from the real wavelength grid.
