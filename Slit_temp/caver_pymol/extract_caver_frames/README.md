# CAVER Frame Extraction

## Purpose

Extracts trajectory frames and writes protein-plus-heme PDB structures for downstream CAVER processing.

## Input and calculation

The script uses its configured DCD, topology, frame range, and output directory. It streams frames, selects the molecular subset required by CAVER, and writes numbered PDB files.

## Usage

Run it from the working directory expected by its configured paths and ensure the CAVER/Python dependencies are available.

## Output

Produces one PDB file per selected trajectory frame. These files are consumed by the generated PyMOL/CAVER viewers.
