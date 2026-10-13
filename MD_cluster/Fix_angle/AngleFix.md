 
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