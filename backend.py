"""
FastAPI backend that serves FLUX.1-Kontext-dev for image editing.

Endpoints
---------
POST /generate
    Body  : GenerateRequest (JSON)
    Returns: {"image": <base64-png>, "generation_time_seconds": float}

Acceleration modes
------------------
  accelerate=False  →  standard inference (NUM_STEPS_NORMAL steps)
  accelerate=True   →  torch.compile on the transformer (NUM_STEPS_ACCEL steps)

The compiled transformer is warm-up-compiled on the first /generate call;
subsequent accelerated calls benefit from the cached kernels.
"""

import base64
import io
import time
import os
from contextlib import asynccontextmanager

import torch
from diffusers import FluxKontextPipeline
from fastapi import FastAPI
from PIL import Image
from pydantic import BaseModel

# ── Config ────────────────────────────────────────────────────────────────────

MODEL_ID = "black-forest-labs/FLUX.1-Kontext-dev"
DTYPE = torch.bfloat16
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

NUM_STEPS_NORMAL = 28
NUM_STEPS_ACCEL  = 28   # same step count; speedup comes from torch.compile
GUIDANCE_SCALE   = 2.5

# ── Global state ──────────────────────────────────────────────────────────────

pipe: FluxKontextPipeline = None
original_transformer  = None   # kept so we can always swap back to uncompiled
compiled_transformer  = None   # lazy-compiled on first accelerated call


# ── Lifespan: load model once at startup ─────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipe, original_transformer
    print(f"Loading {MODEL_ID} on {DEVICE} ({DTYPE}) …")
    pipe = FluxKontextPipeline.from_pretrained(MODEL_ID, torch_dtype=DTYPE)
    pipe.to(DEVICE)
    pipe.set_progress_bar_config(disable=True)
    original_transformer = pipe.transformer
    print("Model ready.")
    yield
    # cleanup (nothing to do for this model)


app = FastAPI(lifespan=lifespan)


# ── Request / response schemas ────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    image: str             # base64-encoded PNG/JPEG (composite with painted region)
    prompt: str
    accelerate: bool = False
    both: bool = False     # run accelerated then normal, return both results


# ── Helpers ───────────────────────────────────────────────────────────────────

def _b64_to_pil(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")


def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _ensure_compiled():
    """Lazily compile the transformer with torch.compile (first call is slow)."""
    global compiled_transformer
    if compiled_transformer is None:
        print("Compiling transformer with torch.compile (one-time, ~1-2 min) …")
        compiled_transformer = torch.compile(
            original_transformer,
            mode="reduce-overhead",
            fullgraph=True,
        )
        print("Compilation done.")


def _run_inference(image: Image.Image, prompt: str, num_steps: int):
    t0 = time.perf_counter()
    with torch.inference_mode():
        result = pipe(
            image=image,
            prompt=prompt,
            num_inference_steps=num_steps,
            guidance_scale=GUIDANCE_SCALE,
        ).images[0]
    return result, round(time.perf_counter() - t0, 2)


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/generate")
def generate(req: GenerateRequest):
    image = _b64_to_pil(req.image)

    if req.both:
        # Run accelerated first, then normal; return both results
        _ensure_compiled()
        pipe.transformer = compiled_transformer
        accel_img, accel_time = _run_inference(image, req.prompt, NUM_STEPS_ACCEL)

        pipe.transformer = original_transformer
        normal_img, normal_time = _run_inference(image, req.prompt, NUM_STEPS_NORMAL)

        return {
            "accelerated_image": _pil_to_b64(accel_img),
            "accelerated_time":  accel_time,
            "normal_image":      _pil_to_b64(normal_img),
            "normal_time":       normal_time,
        }

    if req.accelerate:
        _ensure_compiled()
        pipe.transformer = compiled_transformer
    else:
        pipe.transformer = original_transformer

    result, elapsed = _run_inference(image, req.prompt, NUM_STEPS_ACCEL if req.accelerate else NUM_STEPS_NORMAL)
    return {"image": _pil_to_b64(result), "generation_time_seconds": elapsed}


# ── Dev entry-point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("BACKEND_PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)
