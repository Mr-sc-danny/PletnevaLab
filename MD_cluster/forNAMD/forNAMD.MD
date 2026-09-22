You probably need ionized.pdb and psf here.
Modify the all the conf.
First minimize with sbatch run.sh
Then actual run with sbatch run1.sh
if the claster can't run run.sh, enter this command:
sed -i 's/\r$//' run.sh