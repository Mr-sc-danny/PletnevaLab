# CAVER Frame Extraction

## Purpose

Extracts frames 1000-3000 from the supported trajectories and writes protein-plus-heme PDB structures for CAVER input.

## Input configuration

The `CONFIGS` block defines DCD, topology, and output paths for `2042` and `2042f_new`. `START_FRAME` and `END_FRAME` define the inclusive extraction range.

## Calculation

The script validates the input files and frame count, selects `protein or resname HEMOX or resname HEM`, streams the trajectory in chunks, and writes one PDB per selected frame.

## Usage

```bash
python caver_frame_extraction.py --model 2042
python caver_frame_extraction.py --model 2042f_new
```

## Output

Creates numbered PDB files in the configured `caver_inputs_<model>_with_heme_1000_3000` directory.
