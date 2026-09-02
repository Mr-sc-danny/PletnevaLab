#!/bin/bash
# declare a name for this job to be sample_job
#SBATCH --job-name 0019_ox_1

# request the default queue for this job
#SBATCH --partition=standard

# request a total of 20 processors for this job (1 nodes and 20 processors per node)
#SBATCH --nodes=1
# number of cores
#SBATCH --ntasks-per-node=20
# Walltime (job duration): default=?
#SBATCH --time=72:00:00


# Email notifications
#SBATCH --mail-type=BEGIN,END,FAIL

# specify your email address
#SBATCH --mail-user=yingze.jing.gr@dartmouth.edu

#change to the directory where you submitted the job


# include the relative path to the name of your MPI program

NUM_NODES=${SLURM_JOB_NUM_NODES-1}
NUM_THREADS=${SLURM_TASKS_PER_NODE-2}
NUM_PROCS=`expr ${NUM_NODES} \* ${NUM_THREADS}`


module load namd/2.13

namd2 +p20 052926_Slit0019_ox_2.conf &> 052926_Slit0019_ox_2.log