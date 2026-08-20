# Contact Map Analysis

## Purpose

Computes residue-residue contact frequencies and mean pairwise distances from an MD trajectory, then creates full and focused heatmaps.

## Input configuration

The `DATASETS` block defines the DCD path, PSF path, frame slice, contact cutoff, and residue labels for datasets `1353` and `2042`.

## Calculation

The script loads the selected trajectory, computes all residue-pair distances, converts each distance into a contact indicator using the configured nanometer cutoff, averages the indicators over frames, and optionally extracts the focused residue window.

## Usage

```bash
python contact_map_analysis.py --dataset 2042 --mode both
python contact_map_analysis.py --dataset 1353 --mode compute
python contact_map_analysis.py --dataset 2042 --mode focus --map-file contact_map_2042.dat
```

## Output

The script writes `contact_map_<dataset>.dat`, `contact_distance_<dataset>.dat`, `contact_map_<dataset>.png`, and `contact_map_focus_<dataset>.png`.