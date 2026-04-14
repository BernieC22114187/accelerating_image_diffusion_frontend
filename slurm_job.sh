#!/bin/bash
#SBATCH --job-name=flux-kontext-backend
#SBATCH --partition=gpu            # change to your cluster's GPU partition name
#SBATCH --gres=gpu:a5000:1               # FLUX Kontext dev needs ~24 GB VRAM (A100/H100 recommended)
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=04:00:00            # adjust as needed
#SBATCH --output=logs/backend_%j.out
#SBATCH --error=logs/backend_%j.err

# ── Print the node name so you know where to SSH-tunnel from ─────────────────
echo "Backend running on node: $(hostname)"
echo "Forward port 8000 from your local machine with:"
echo "  ssh -L 8000:$(hostname):8000 <your-cluster-login-node>"
echo ""

# ── Environment ───────────────────────────────────────────────────────────────
source ~/miniconda3/etc/profile.d/conda.sh   # adjust path if needed
conda activate diffusion-acceleration-frontend

cd "$(dirname "$0")"    # run from the repo directory

# ── (Optional) Set HuggingFace cache to a shared scratch dir ─────────────────
# export HF_HOME=/scratch/$USER/hf_cache
# export TRANSFORMERS_CACHE=/scratch/$USER/hf_cache

# ── Start backend ─────────────────────────────────────────────────────────────
python backend.py
