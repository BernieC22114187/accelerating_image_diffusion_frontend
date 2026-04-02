# Accelerated Image Diffusion — Frontend

A Gradio web app that lets you edit specific regions of an image using a text prompt. It talks to a separate backend server that runs the diffusion model, with an option to compare accelerated vs. normal generation side-by-side.

## How It Works

The UI walks the user through four steps:

1. **Upload an image** — drop any image into the upload box.
2. **Draw a bounding box** — use the annotator to draw a box around the region you want to edit. Press `C` to create a box, `D` to drag, `Delete` to remove.
3. **Describe the edit** — type a text prompt (e.g. *"replace with a red sports car"*).
4. **Generate** — click **Generate** and view the result.

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
       │  HTTP POST /generate  { image, bbox, prompt, accelerate }
       ▼
  Backend server (localhost:8000)
       │
       └─ Returns { image (base64), generation_time_seconds }
```

The frontend encodes the uploaded image as base64, packages it with the bounding box coordinates and prompt, and POSTs to the backend. The backend returns the edited image as base64 along with how long generation took.

**Key files:**

| File | Purpose |
|---|---|
| `app.py` | Gradio UI layout and event handlers |
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

Make sure the backend server is running at `http://localhost:8000`, then:

```bash
python app.py
```

The app will be available at `http://localhost:7860`.

To point to a different backend, edit the `BACKEND_URL` constant in `helpers.py`.
