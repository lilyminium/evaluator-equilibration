#!/bin/bash
#SBATCH -J save-boxes
#SBATCH -p free
#SBATCH -t 05:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --account dmobley_lab
#SBATCH --export ALL
#SBATCH --mem=16gb
#SBATCH --constraint=fastscratch
#SBATCH --output slurm-%x.%A-%a.out

. ~/.bashrc

# Use the right conda environment
conda activate evaluator-050

export CUDA_VISIBLE_DEVICES=0

python save-equilibrated-boxes-to-storage.py
