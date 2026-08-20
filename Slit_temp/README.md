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

The current `PletnevaLabForBots` repository contains the 13 Python scripts from this Slit folder. The parent `PletenevaLab` repository also contains `Agilent_UV_Extractor/extract_spectra.py` and `Echem_process/plot_together.py`; those two files are outside this authorized Slit-only change and therefore are not modified here.