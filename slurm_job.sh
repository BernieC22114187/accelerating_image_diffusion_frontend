#!/bin/bash
#SBATCH --job-name=flux-kontext-backend
#SBATCH --partition=compsci-gpu
#SBATCH --gres=gpu:a5000:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=04:00:00
#SBATCH --output=/home/users/bc295/accelerating_image_diffusion_frontend/logs/backend_%j.out
#SBATCH --error=/home/users/bc295/accelerating_image_diffusion_frontend/logs/backend_%j.err

# ── Print the node name so you know where to SSH-tunnel from ─────────────────
echo "Backend running on node: $(hostname)"
echo "Forward port 8000 from your local machine with:"
echo "  ssh -L 8000:$(hostname):8000 <your-cluster-login-node>"
echo ""

# ── Environment ───────────────────────────────────────────────────────────────
source ~/miniconda3/etc/profile.d/conda.sh   # adjust path if needed
conda activate diffusion-acceleration-frontend

cd /home/users/bc295/accelerating_image_diffusion_frontend

# ── (Optional) Set HuggingFace cache to a shared scratch dir ─────────────────
# export HF_HOME=/scratch/$USER/hf_cache
# export TRANSFORMERS_CACHE=/scratch/$USER/hf_cache

# ── Start backend ─────────────────────────────────────────────────────────────
python backend.py
