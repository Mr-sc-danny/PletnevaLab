# RMSD and SASA Comparison

## Purpose

Plots RMSD and heme-SASA time series for either a two-way or four-way dataset comparison.

## Input configuration

The `MODES` block defines data-table paths, colors, and labels. Each table is expected to contain frame values and a measurement column.

## Calculation

The script loads each table, converts frame numbers to nanoseconds using 50 frames per ns, and renders aligned RMSD and SASA panels with consistent axes and legends.

## Usage

```bash
python rmsd_sasa_comparison.py --mode 2way
python rmsd_sasa_comparison.py --mode 4way
```

## Output

Writes `rmsd_sasa_2way.png` or `rmsd_sasa_4way.png`.
