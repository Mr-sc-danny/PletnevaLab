#!/usr/bin/env python3
"""
AngleFix.py

Scans and fixes ONLY the specific, reproducible psfgen bug seen with the
CHARMM heme-linking patches (PRES HOCY / PHEM / PSUL in
top_all36_prot_heme_c.str): the ANGLE records meant to be vertexed on the
atom that actually coordinates the heme iron (His NE2, Met SD, Cys SG...)
instead get a wrong vertex atom substituted in (e.g. His CE1 duplicated,
or Met's backbone C).

No CHARMM parameter files are needed. Detection and repair both rely
purely on the PSF's own (correct) BOND section as ground truth for which
atom is genuinely bonded to the metal in each coordinating residue -- if
an angle touching the metal doesn't use that atom where it should, it's
fixed; otherwise the file is left untouched.

Usage:
    python3 AngleFix.py [input.psf] [output.psf] [--metal-types FE] [--log Angle_fix.log]

All arguments are optional. With no arguments at all:
    python3 AngleFix.py
is exactly equivalent to:
    python3 AngleFix.py ionized.psf ionized_fixed.psf --metal-types FE --log Angle_fix.log
"""

import argparse
import csv


def parse_psf(path):
    # newline="" preserves whatever line endings the file already uses
    # (e.g. CRLF from Windows-built PSFs) instead of normalizing them away,
    # so the only lines that differ from the input are the ones we actually
    # fix -- not every line, due to a CRLF/LF mismatch.
    with open(path, "r", newline="", errors="ignore") as f:
        lines = f.readlines()

    atoms = {}  # serial -> (segname, resid, resname, atomname, atype)
    bonds = []
    angle_start = angle_end = None

    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if "!NATOM" in line:
            natom = int(line.split()[0])
            for j in range(i + 1, i + 1 + natom):
                p = lines[j].split()
                atoms[int(p[0])] = (p[1], p[2], p[3], p[4], p[5])
            i += 1 + natom
            continue
        if "!NBOND" in line:
            nbond = int(line.split()[0])
            nums, j = [], i + 1
            while len(nums) < nbond * 2:
                nums.extend(int(x) for x in lines[j].split())
                j += 1
            bonds = list(zip(nums[0::2], nums[1::2]))
            i = j
            continue
        if "!NTHETA" in line:
            ntheta = int(line.split()[0])
            angle_start = i + 1
            j, count = angle_start, 0
            while count < ntheta * 3:
                count += len(lines[j].split())
                j += 1
            angle_end = j
            break
        i += 1

    return lines, atoms, bonds, angle_start, angle_end


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "input_psf", nargs="?", default="ionized.psf",
        help="PSF to check/fix (default: ionized.psf)",
    )
    ap.add_argument(
        "output_psf", nargs="?", default="ionized_fixed.psf",
        help="where to write the corrected PSF (default: ionized_fixed.psf)",
    )
    ap.add_argument(
        "--metal-types", nargs="+", default=["FE"],
        help="atom types to treat as coordinating metals (default: FE)",
    )
    ap.add_argument(
        "--log", default="Angle_fix.log",
        help="change-log path (default: Angle_fix.log)",
    )
    args = ap.parse_args()

    lines, atoms, bonds, astart, aend = parse_psf(args.input_psf)
    metal_types = set(args.metal_types)
    metal_serials = {s for s, a in atoms.items() if a[4] in metal_types}

    if not metal_serials:
        print(f"No atoms of type {sorted(metal_types)} found — nothing to check.")
        return

    # ligand_atom[(segname, resid)] = atom serial genuinely bonded to a metal
    ligand_atom = {}
    for a, b in bonds:
        for x, y in ((a, b), (b, a)):
            if y in metal_serials and x not in metal_serials:
                ligand_atom[(atoms[x][0], atoms[x][1])] = x

    # Flatten angle section, tracking (line_idx, token_idx) per number
    flat, positions = [], []
    for li in range(astart, aend):
        toks = lines[li].split()
        for ti, tok in enumerate(toks):
            flat.append(int(tok))
            positions.append((li, ti))

    fixes = []
    n_triples = len(flat) // 3
    for ti in range(n_triples):
        i0 = ti * 3
        trio = flat[i0:i0 + 3]
        metal_pos = [k for k, s in enumerate(trio) if s in metal_serials]
        if len(metal_pos) != 1:
            continue
        m_idx = metal_pos[0]
        others = [k for k in range(3) if k != m_idx]
        a_idx, b_idx = others
        sA, sB = trio[a_idx], trio[b_idx]

        wrong_idx = correct_atom = anchor = None
        metal_residue = (atoms[trio[m_idx]][0], atoms[trio[m_idx]][1])

        if sA == sB:
            # degenerate: the duplicated atom's residue tells us the fix.
            # Skip if the duplicated atom is in the SAME residue as the metal
            # itself (e.g. the heme's own porphyrin ring) -- that residue can
            # legitimately have several distinct atoms bonded to the metal,
            # so there is no single "the" ligand atom to fall back on there.
            key = (atoms[sA][0], atoms[sA][1])
            if key != metal_residue:
                lig = ligand_atom.get(key)
                if lig is not None and lig != sA:
                    wrong_idx, correct_atom, anchor = b_idx, lig, sA
        else:
            # not degenerate: see if either atom's residue has a distinct
            # true ligand atom that would belong in the OTHER slot instead
            for anchor_idx, wrong_candidate_idx in ((a_idx, b_idx), (b_idx, a_idx)):
                anchor_s = trio[anchor_idx]
                wrong_s = trio[wrong_candidate_idx]
                key = (atoms[anchor_s][0], atoms[anchor_s][1])
                if key == metal_residue:
                    continue
                lig = ligand_atom.get(key)
                if lig is not None and lig not in (anchor_s, trio[m_idx], wrong_s):
                    wrong_idx, correct_atom, anchor = wrong_candidate_idx, lig, anchor_s
                    break

        if wrong_idx is None:
            continue

        old_serial = trio[wrong_idx]
        flat_idx = i0 + wrong_idx
        flat[flat_idx] = correct_atom

        line_idx, tok_idx = positions[flat_idx]
        orig_line = lines[line_idx]
        ending = "\r\n" if orig_line.endswith("\r\n") else "\n"
        toks = orig_line.split()
        toks[tok_idx] = str(correct_atom)
        lines[line_idx] = "".join(t.rjust(8) for t in toks) + ending

        fixes.append({
            "line_number": line_idx + 1,
            "old_serial": old_serial, "old_type": atoms[old_serial][4],
            "new_serial": correct_atom, "new_type": atoms[correct_atom][4],
            "anchor_serial": anchor, "anchor_seg": atoms[anchor][0],
            "anchor_resid": atoms[anchor][1], "anchor_resname": atoms[anchor][2],
            "anchor_atomname": atoms[anchor][3], "metal_serial": trio[m_idx],
        })

    with open(args.output_psf, "w") as f:
        f.writelines(lines)

    with open(args.log, "w", newline="") as f:
        fieldnames = ["line_number", "old_serial", "old_type", "new_serial",
                      "new_type", "anchor_serial", "anchor_seg", "anchor_resid",
                      "anchor_resname", "anchor_atomname", "metal_serial"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in fixes:
            w.writerow(row)

    print(f"Checked angles touching {sorted(metal_types)}. Applied {len(fixes)} fix(es).")
    for r in fixes:
        print(f"  line {r['line_number']}: {r['old_serial']} ({r['old_type']}) -> "
              f"{r['new_serial']} ({r['new_type']})  "
              f"[residue {r['anchor_seg']}:{r['anchor_resid']} {r['anchor_resname']}]")
    print(f"Fixed PSF written to: {args.output_psf}")
    print(f"Log written to: {args.log}")


if __name__ == "__main__":
    main()
