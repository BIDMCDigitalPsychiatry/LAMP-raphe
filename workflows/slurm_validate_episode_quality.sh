#!/bin/bash
#SBATCH --job-name=raphe_episode_dq
#SBATCH --partition=cpu
#SBATCH --nodelist=node001
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --time=04:00:00
#SBATCH --output=logs/episode_dq_%j.out
#SBATCH --error=logs/episode_dq_%j.err

set -euo pipefail

cd "/shared/Digital Clinic/RAPHE"

/home/akargara/envs/socialmedia/bin/python \
  workflows/validate_episode_quality_cho370.py
