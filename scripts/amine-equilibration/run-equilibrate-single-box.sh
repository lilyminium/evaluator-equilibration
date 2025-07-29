#!/bin/bash
#SBATCH -J equilibrate
#SBATCH --array=377-377
#SBATCH -p free-gpu
#SBATCH -t 08:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account dmobley_lab_gpu
#SBATCH --export ALL
#SBATCH --mem=16gb
#SBATCH --constraint=fastscratch
#SBATCH --output slurm-%x.%A-%a.out
#SBATCH --gres=gpu:1

. ~/.bashrc

# Use the right conda environment
conda activate evaluator-050

export CUDA_VISIBLE_DEVICES=0

python equilibrate-single-box.py        \
    -i  $SLURM_ARRAY_TASK_ID            \
    -wd working_directory/equilibration \
    -bd working_directory/boxes         \
    -ff openff-2.1.0.offxml             \
    -maxiter 2000

