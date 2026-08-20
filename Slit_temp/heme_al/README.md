# Heme-Methionine Distance Analysis

## Purpose

This script measures distances from the heme iron to the four heme nitrogens, the axial methionine sulfur, and the proximal histidine nitrogen. It also calculates the five heme-ligand angles defined by the selected atom triplets.

## Input configuration

The `CONFIGS` block selects the trajectory and topology for each supported model:

- `2042`: `2042/2042_all.dcd` with `2042/ionized.pdb`, sulfur residue 78.
- `2042f_new`: `2042f_new/60nsp.dcd` with `2042f_new/ionized.pdb`, sulfur residue 78.
- `pac551`: `pac551/Pa_c551_ox_1.dcd` with `pac551/ionized.pdb`, sulfur residue 61.

The analysis uses `DT_NS = 0.02` ns per frame and summarizes the 20-60 ns interval.

## Calculation

1. Load the selected MDTraj topology.
2. Select FE, NA, NB, NC, ND, SD, and NE2 atoms.
3. Stream the DCD in chunks of 1000 frames to limit memory use.
4. Calculate distances in Angstroms and angles in degrees.
5. Convert frame indices to time and filter the requested time window.
6. Calculate means and standard deviations for every reported measurement.

## Usage

Run one model at a time from this folder or from an environment where the configured paths are valid:

```bash
python heme_methionine_distance_analysis.py --model 2042
python heme_methionine_distance_analysis.py --model 2042f_new
python heme_methionine_distance_analysis.py --model pac551
```

## Output

The script writes `distance_analysis_<model>.txt`. The report contains the number of analyzed frames, mean distance, distance standard deviation, mean angle, and angle standard deviation.

## Dependencies

Requires Python, MDTraj, and NumPy. The trajectory and topology files must exist at the paths defined in `CONFIGS`.
