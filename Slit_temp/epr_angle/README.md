# EPR Methionine Ligand Orientation

## Purpose

Measures the axial methionine ligand-plane orientation relative to the heme plane and reports its angles against the NA-NC and NB-ND heme axes.

## Input configuration

The `MODELS` block maps each model to its PDB path, heme residue, methionine residue, and histidine residue.

## Calculation

The script parses PDB coordinates, fits a plane through the heme nitrogens, projects the CG-S and CE-S vectors into that plane, calculates the ligand-plane trace, and measures reference-axis angles.

## Usage

```bash
python methionine_ligand_orientation.py --model 1ayg
python methionine_ligand_orientation.py --model 2042_60
python methionine_ligand_orientation.py --model c551_60
```

## Output

Writes `epr_orientation_<model>.txt` with the plane normal, projected vectors, Fe-S distance, His-Fe distance, and both orientation angles.
