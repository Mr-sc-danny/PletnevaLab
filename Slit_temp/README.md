# Slit Python Scripts

This folder contains the organized Slit analysis scripts from the PletnevaLab repository.

## Why `__pycache__` folders appear

Python creates `__pycache__` directories automatically when a module is imported or compiled. They contain generated `.pyc` bytecode, not source code, and should not be treated as part of the research scripts. They are excluded from this organized source tree and should remain untracked.

## Organization

Scripts are grouped by analysis logic:

- `contact_maps`: residue contact-frequency and heatmap analysis.
- `epr_angle`: methionine ligand-plane orientation analysis.
- `frame_extraction`: trajectory frame extraction for CAVER input.
- `heme_al`: heme-ligand distance and angle analysis.
- `rmsd_sasa`: RMSD/SASA comparison plotting.
- `WH`: WH distance analyses.
- `caver_pymol`: generated CAVER/PyMOL scripts, preserved unchanged.

Each maintained analysis script uses explicit input-configuration, calculation, and output sections. The folder names `contact_map_neat` and `contact_map_neat_figure_only` were removed because they contained no Python code; their behavior is covered by `contact_maps/contact_map_analysis.py`.

## Repository coverage

The companion `PletnevaLabForBots` repository contains all 15 Python files from the parent `PletenevaLab` repository plus `Echem_process/UVVis_Redox_Workup.ipynb`. Its root is intentionally flat so every code or notebook file has a matching `<filename>_readme.md` documentation file.