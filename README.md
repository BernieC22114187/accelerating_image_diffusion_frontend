# Accelerated Image Diffusion — Frontend

A Gradio web app that lets you edit specific regions of an image using a text prompt. It talks to a separate backend server that runs the diffusion model, with an option to compare accelerated vs. normal generation side-by-side.

There are two UI modes, each with its own entry point:

| Mode | File | Port | Region Selection |
|---|---|---|---|
| Bounding Box | `bounding_box.py` | 7860 | Draw a rectangle around the target area |
| Freeform Brush | `freeform.py` | 7861 | Paint over the target area with a brush |

## How It Works

### Bounding Box mode (`bounding_box.py`)

1. **Upload an image** — drop any image into the upload box.
2. **Draw a bounding box** — use the annotator to draw a box around the region you want to edit. Press `C` to create a box, `D` to drag, `Delete` to remove.
3. **Describe the edit** — type a text prompt (e.g. *"replace with a red sports car"*).
4. **Generate** — click **Generate** and view the result.

The bounding box coordinates (`xmin`, `ymin`, `xmax`, `ymax`) are sent to the backend along with the image and prompt.

### Freeform Brush mode (`freeform.py`)

1. **Upload & paint** — upload an image, then use the red brush to paint over the area you want to edit. Use the eraser to correct mistakes. The brush size slider automatically adapts its range and default to the image dimensions; you can also adjust it manually.
2. **Describe the edit** — type a text prompt.
3. **Generate** — click **Generate** and view the result.

The composite image (background with the painted mask layer) is sent to the backend. No bounding box coordinates are included.

### Generation Modes

| Mode | Behavior |
|---|---|
| ⚡ Accelerated | Runs the diffusion model with acceleration enabled |
| 🐢 Normal | Runs without acceleration |
| ⚡🐢 Both | Runs both back-to-back and displays results side-by-side for comparison |

Generation time is displayed below each result image.

### Architecture

```
Browser (Gradio UI)
       │
       │  HTTP POST /generate  { image, [bbox,] prompt, accelerate }
       ▼
  Backend server (localhost:8000)
       │
       └─ Returns { image (base64), generation_time_seconds }
```

**Key files:**

| File | Purpose |
|---|---|
| `bounding_box.py` | Gradio UI for bounding-box region selection (port 7860) |
| `freeform.py` | Gradio UI for freeform brush region selection (port 7861) |
| `helpers.py` | Image encoding utilities and backend HTTP call |
| `style.css` | Custom CSS theme |

## Setup

### Option 1 — Conda (recommended)

```bash
conda env create -f environment.yml
conda activate diffusion-acceleration-frontend
```

### Option 2 — pip

```bash
pip install -r requirements.txt
```

## Running

Make sure the backend server is running at `http://localhost:8000`, then launch whichever UI you want:

```bash
# Bounding box mode
python bounding_box.py   # → http://localhost:7860

# Freeform brush mode
python freeform.py       # → http://localhost:7861
```

To point to a different backend, edit the `BACKEND_URL` constant in `helpers.py`.
