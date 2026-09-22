batch_save.tcl will extract hemes (any residue name start with HEM) into seperated pdbs from frames 1000-3000
And construct the pdb in a way that PhorphyStruct can read.
Change the frames number as you wish under the batch_save.tcl code.
set start_frame 1000
set end_frame   3000
