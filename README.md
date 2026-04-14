# Accelerated Image Diffusion — Frontend

A Gradio web app that lets you edit specific regions of an image using a text prompt. It talks to a separate backend server that runs [FLUX.1-Kontext-dev](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev), with an option to compare accelerated vs. normal generation side-by-side.

There are two UI modes, each with its own entry point:

| Mode | File | Port | Region Selection |
|---|---|---|---|
| Freeform Brush | `freeform.py` | 7861 | Paint over the target area with a brush |
| Bounding Box | `bounding_box.py` | 7860 | Draw a rectangle around the target area |

## How It Works

### Freeform Brush mode (`freeform.py`)

1. **Upload & paint** — upload an image, then use the red brush to paint over the area you want to edit. Use the eraser or **Clear Strokes** to correct mistakes. The brush size slider automatically adapts to the image dimensions.
2. **Describe the edit** — type a text prompt referencing the painted region (e.g. *"replace the red painted region with a sports car"*).
3. **Generate** — click **Generate** and view the result.

The composite image (background + painted mask layer visible) is sent to the backend. FLUX.1-Kontext-dev sees the red strokes and edits accordingly.

### Bounding Box mode (`bounding_box.py`)

1. **Upload an image** — drop any image into the upload box.
2. **Draw a bounding box** — use the annotator to draw a box around the region you want to edit. Press `C` to create, `D` to drag, `Delete` to remove.
3. **Describe the edit** — type a text prompt.
4. **Generate** — click **Generate** and view the result.

The bounding box coordinates are used to overlay a semi-transparent red rectangle on the image before sending to the backend, giving the model a visual cue for where to edit.

### Generation Modes

| Mode | Behavior |
|---|---|
| ⚡ Accelerated | Runs with `torch.compile` on the transformer |
| 🐢 Normal | Runs without `torch.compile` |
| ⚡🐢 Both | Runs both in a single backend call and displays results side-by-side |

Generation time is displayed below each result image.

### Architecture

```
Browser (Gradio UI)
       │
       │  POST /generate  { image, prompt, accelerate }        (single mode)
       │  POST /generate  { image, prompt, both: true }        (Both mode)
       ▼
  Backend server (localhost:8000)
       │
       ├─ single: { image, generation_time_seconds }
       └─ both:   { accelerated_image, accelerated_time,
                    normal_image, normal_time }
```

**Key files:**

| File | Purpose |
|---|---|
| `freeform.py` | Gradio UI — freeform brush mode (port 7861) |
| `bounding_box.py` | Gradio UI — bounding-box mode (port 7860) |
| `backend.py` | FastAPI server — loads FLUX.1-Kontext-dev, serves `/generate` |
| `helpers.py` | Shared image encoding utils and backend HTTP helpers |
| `slurm_job.sh` | SLURM batch script to run the backend on a GPU node |
| `style.css` | Custom CSS theme |

## Setup

### 1. Install dependencies

**Conda (recommended):**
```bash
conda env create -f environment.yml
conda activate diffusion-acceleration-frontend
```

**pip:**
```bash
pip install -r requirements.txt
```

Then install PyTorch with the correct CUDA version for your machine:
```bash
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu121
```

### 2. Authenticate with Hugging Face

FLUX.1-Kontext-dev is a gated model. Accept the license at [huggingface.co/black-forest-labs/FLUX.1-Kontext-dev](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev), then log in:

```bash
huggingface-cli login
```

## Running on the Cluster (SLURM)

The backend requires a GPU (~24 GB VRAM). Submit it as a SLURM job:

```bash
sbatch slurm_job.sh
```

Check the log to get the GPU node hostname:
```bash
tail -f logs/backend_<JOBID>.out
```

Then forward port 8000 to your local machine:
```bash
ssh -L 8000:<GPU_NODE_HOSTNAME>:8000 <cluster-login-node>
```

## Running the Frontend

Once the backend is reachable at `http://localhost:8000`, launch whichever UI you want:

```bash
# Freeform brush mode
python freeform.py       # → http://localhost:7861

# Bounding box mode
python bounding_box.py   # → http://localhost:7860
```

To point to a different backend address, edit `BACKEND_URL` in `helpers.py`.
