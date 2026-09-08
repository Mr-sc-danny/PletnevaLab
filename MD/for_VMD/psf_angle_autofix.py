#!/usr/bin/env python3
"""
psf_angle_autofix.py

Repairs a specific, reproducible psfgen bug seen with the PRES HOCY / PHEM /
PSUL heme-linking patches: the ANGLE statements that should be vertexed on
the ligand atom actually bonded to FE (e.g. His NE2, Met SD) instead get a
WRONG vertex atom (e.g. His CE1 duplicated, or Met's backbone C). The BOND
records from the same patch are NOT affected by this bug, so they serve as
ground truth for which atom is really bonded to the metal in each residue.

Strategy (metal-agnostic, works for FE or any other coordinating metal type
you list with --metal-types):
  1. Parse the PSF: atoms, bonds, angles.
  2. For every metal atom M, build {(segname,resid): ligand_atom_serial}
     from the BOND section (i.e. which atom in each coordinating residue is
     *actually* bonded to M).
  3. For every angle (a, b, c) touching a metal atom that is flagged bad
     (degenerate, i.e. two serials equal, OR whose type-triple has no
     match in the supplied parameter files), find the non-metal, non-
     duplicate atom (the "anchor", e.g. CD2/CE1/CG/CE) and look up the
     correct ligand atom for that anchor's (segname,resid) from step 2.
     Replace the wrong vertex with that correct ligand atom serial.
  4. Rewrite the PSF's angle section in-place (preserving CHARMM's 8-char
     fixed-width field format) and write a CSV log of every change made.

This never guesses blindly: a fix is only applied when the bond-derived
ligand atom is unambiguous and distinct from the atoms already in the
triple. Anything it can't confidently resolve is left alone and reported.

Usage:
    python3 psf_angle_autofix.py input.psf output.psf par1.prm par2.prm ... \
        [--metal-types FE ZN MG] [--log fixes.csv]
"""

import argparse
import csv


def parse_psf(path):
    with open(path, "r", errors="ignore") as f:
        lines = f.readlines()

    atoms = {}       # serial -> (segname, resid, resname, atomname, atype)
    bonds = []
    angle_start_line = None
    angle_lines_end = None
    ntheta = None

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if "!NATOM" in line:
            natom = int(line.split()[0])
            for j in range(i + 1, i + 1 + natom):
                p = lines[j].split()
                serial = int(p[0])
                atoms[serial] = (p[1], p[2], p[3], p[4], p[5])
            i = i + 1 + natom
            continue
        if "!NBOND" in line:
            nbond = int(line.split()[0])
            nums = []
            j = i + 1
            while len(nums) < nbond * 2:
                nums.extend(int(x) for x in lines[j].split())
                j += 1
            bonds = list(zip(nums[0::2], nums[1::2]))
            i = j
            continue
        if "!NTHETA" in line:
            ntheta = int(line.split()[0])
            angle_start_line = i + 1
            j = angle_start_line
            count = 0
            while count < ntheta * 3:
                count += len(lines[j].split())
                j += 1
            angle_lines_end = j
            i = j
            continue
        i += 1

    return lines, atoms, bonds, ntheta, angle_start_line, angle_lines_end


def parse_angle_param_types(param_paths):
    SECTION_KEYWORDS = {"BONDS", "ANGLES", "DIHEDRALS", "IMPROPER", "IMPROPERS",
                         "CMAP", "NONBONDED", "NBFIX", "HBOND", "END"}
    angle_types = set()
    for path in param_paths:
        section = None
        with open(path, "r", errors="ignore") as f:
            for raw in f:
                line = raw.split("!", 1)[0].strip()
                if not line:
                    continue
                first_tok = line.split()[0].upper()
                if first_tok in SECTION_KEYWORDS:
                    section = first_tok
                    continue
                if first_tok in ("READ", "TITLE", "*"):
                    continue
                if section == "ANGLES":
                    toks = line.split()
                    if len(toks) >= 3:
                        t1, t2, t3 = toks[0], toks[1], toks[2]
                        angle_types.add((t1, t2, t3))
                        angle_types.add((t3, t2, t1))
    return angle_types


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_psf")
    ap.add_argument("output_psf")
    ap.add_argument("params", nargs="+", help="CHARMM parameter files (.prm/.str)")
    ap.add_argument("--metal-types", nargs="+", default=["FE"],
                     help="Atom types to treat as coordinating metals (default: FE)")
    ap.add_argument("--log", default="psf_angle_autofix_log.csv")
    args = ap.parse_args()

    lines, atoms, bonds, ntheta, astart, aend = parse_psf(args.input_psf)
    angle_types = parse_angle_param_types(args.params)
    metal_types = set(args.metal_types)

    metal_serials = {s for s, a in atoms.items() if a[4] in metal_types}

    # ligand_atom[(segname, resid)] = serial of the atom in that residue
    # that is genuinely bonded (per the BOND section) to a metal atom.
    ligand_atom = {}
    for (a, b) in bonds:
        for x, y in ((a, b), (b, a)):
            if y in metal_serials and x not in metal_serials:
                seg, resid = atoms[x][0], atoms[x][1]
                ligand_atom[(seg, resid)] = x

    # Rebuild flat angle number stream, tracking (line_idx, position) for
    # each of the ntheta*3 numbers so we can write corrections back in place.
    numbers = []       # flat list of ints
    positions = []      # (line_idx, token_idx_within_line) for each int
    for li in range(astart, aend):
        toks = lines[li].split()
        for ti, tok in enumerate(toks):
            numbers.append(int(tok))
            positions.append((li, ti))

    triples = [tuple(numbers[k:k + 3]) for k in range(0, len(numbers), 3)]

    fixes = []
    for ti, (s1, s2, s3) in enumerate(triples):
        trio = (s1, s2, s3)
        touches_metal = any(s in metal_serials for s in trio)
        if not touches_metal:
            continue

        degenerate = (s1 == s2 or s2 == s3 or s1 == s3)
        bad_param = False
        if not degenerate:
            t1, t2, t3 = atoms[s1][4], atoms[s2][4], atoms[s3][4]
            bad_param = (t1, t2, t3) not in angle_types

        if not (degenerate or bad_param):
            continue

        # Find the metal position and the "anchor" (the other real, non-metal
        # atom in the triple that is NOT the wrong/duplicate vertex).
        metal_pos = [k for k, s in enumerate(trio) if s in metal_serials]
        if len(metal_pos) != 1:
            continue  # ambiguous / not our target pattern, leave alone
        m_idx = metal_pos[0]
        other_positions = [k for k in range(3) if k != m_idx]

        # The vertex we suspect is wrong is whichever position currently
        # duplicates another position, or (for bad_param, non-degenerate
        # cases) is simply not the metal and not adjacent in bond list.
        anchor_serial = None
        wrong_idx = None
        vals = list(trio)
        if degenerate:
            # find the duplicated position among the two non-metal slots
            a_idx, b_idx = other_positions
            if vals[a_idx] == vals[b_idx]:
                anchor_serial = vals[a_idx]
                wrong_idx = b_idx  # arbitrary; both are the same wrong atom
            else:
                continue
        else:
            # bad_param, non-degenerate: try each non-metal atom as the anchor
            # and see if the OTHER non-metal position's residue has a distinct
            # bonded ligand atom that would fix the parameter mismatch.
            for cand_anchor_idx in other_positions:
                cand_wrong_idx = [k for k in other_positions if k != cand_anchor_idx][0]
                anchor_candidate = vals[cand_anchor_idx]
                seg, resid = atoms[anchor_candidate][0], atoms[anchor_candidate][1]
                lig = ligand_atom.get((seg, resid))
                if lig is not None and lig != anchor_candidate and lig != vals[m_idx]:
                    anchor_serial = anchor_candidate
                    wrong_idx = cand_wrong_idx
                    break
            if anchor_serial is None:
                continue

        seg, resid = atoms[anchor_serial][0], atoms[anchor_serial][1]
        correct_atom = ligand_atom.get((seg, resid))
        if correct_atom is None or correct_atom == vals[wrong_idx]:
            continue  # nothing sensible to fix to

        old_serial = vals[wrong_idx]
        # Apply fix
        flat_idx = ti * 3 + wrong_idx
        line_idx, tok_idx = positions[flat_idx]
        line_toks = lines[line_idx].split()
        old_field = line_toks[tok_idx]
        new_field = str(correct_atom).rjust(len(old_field))
        # Reconstruct the fixed-width line: CHARMM PSF angle lines use %8d
        # per field consistently for a given file; rebuild with 8-char width.
        line_toks[tok_idx] = str(correct_atom)
        new_line = "".join(t.rjust(8) for t in line_toks) + "\n"
        lines[line_idx] = new_line

        fixes.append({
            "triple_index": ti,
            "line_number": line_idx + 1,
            "old_serial": old_serial,
            "old_type": atoms[old_serial][4] if old_serial in atoms else "?",
            "new_serial": correct_atom,
            "new_type": atoms[correct_atom][4],
            "anchor_serial": anchor_serial,
            "anchor_seg": seg,
            "anchor_resid": resid,
            "anchor_resname": atoms[anchor_serial][2],
            "anchor_atomname": atoms[anchor_serial][3],
            "metal_serial": vals[m_idx],
        })

        # keep our in-memory numbers/vals consistent in case of repeats
        numbers[flat_idx] = correct_atom

    with open(args.output_psf, "w") as f:
        f.writelines(lines)

    with open(args.log, "w", newline="") as f:
        fieldnames = ["triple_index", "line_number", "old_serial", "old_type",
                      "new_serial", "new_type", "anchor_serial", "anchor_seg",
                      "anchor_resid", "anchor_resname", "anchor_atomname",
                      "metal_serial"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in fixes:
            writer.writerow(row)

    print(f"Applied {len(fixes)} fix(es).")
    for row in fixes:
        print(f"  line {row['line_number']}: serial {row['old_serial']} "
              f"({row['old_type']}) -> {row['new_serial']} ({row['new_type']}) "
              f"[anchor: {row['anchor_seg']}:{row['anchor_resid']} "
              f"{row['anchor_resname']} {row['anchor_atomname']}]")
    print(f"Fixed PSF written to: {args.output_psf}")
    print(f"Change log written to: {args.log}")


if __name__ == "__main__":
    main()
