# WH Distance Analysis

## Purpose

Measures heme-pocket distances along trajectories. The canonical runner supports direct pairwise distance mode and a minimum-heavy-atom distance mode.

## Input configuration

The `CONFIGS` block defines DCD/PDB paths and MDTraj atom-selection queries for models `2042` and `2042f`.

## Calculation

The script selects atoms, streams trajectory chunks, computes distances in Angstroms, filters 20-60 ns with a full-trajectory fallback, and calculates mean, standard deviation, minimum, and maximum.

## Usage

```bash
python wh_distance_analysis.py --model 2042
python wh_distance_analysis.py --model 2042f
```

## Output

Writes `WH_<model>.txt` and `distance_vs_time_<model>.png`. The two `dist_meas` scripts remain separate because they perform multi-dataset analyses.
