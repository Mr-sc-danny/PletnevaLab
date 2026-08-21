Insert CASTp bulb.json spheres as dummy atoms into an existing PDB.
Dummy atoms are inserted immediately before END.
Naming convention:
PBD submitted to Castp: protein.pdb
Bulb JSON: protein.json
Chimera Visualization comand:
size byattribute bfactor :DUM 
If command doesn't work try put size_by_bfactor.py into the same folder and in chimera cmd:
open size_by_bfactor.py
