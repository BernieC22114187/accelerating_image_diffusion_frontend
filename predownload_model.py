import os
import torch
from diffusers import FluxKontextPipeline

MODEL_ID = "black-forest-labs/FLUX.1-Kontext-dev"
print(f"Downloading {MODEL_ID} to {os.environ.get('HF_HOME', '~/.cache/huggingface')} …")
FluxKontextPipeline.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16)
print("Download complete.")
