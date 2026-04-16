#!/bin/bash
#SBATCH --job-name=hf-predownload
#SBATCH --partition=compsci
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --time=02:00:00
#SBATCH --output=/home/users/bc295/accelerating_image_diffusion_frontend/logs/predownload_%j.out
#SBATCH --error=/home/users/bc295/accelerating_image_diffusion_frontend/logs/predownload_%j.err

source ~/miniconda3/etc/profile.d/conda.sh
conda activate diffusion-acceleration-frontend

export HF_HOME=/usr/project/xtmp/bc295/hf_cache
export HF_TOKEN=$(cat ~/.hf_token)

mkdir -p "$HF_HOME"

cd /home/users/bc295/accelerating_image_diffusion_frontend
python predownload_model.py

