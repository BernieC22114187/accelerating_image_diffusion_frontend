import gradio as gr
from gradio_image_annotation import image_annotator
from PIL import Image
from pathlib import Path
import requests
import base64
import io

# ── Backend config ──────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"   # change to your backend address


# ── Helpers ─────────────────────────────────────────────────────────────────
def _pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _to_pil(img) -> Image.Image:
    """Accept PIL Image or numpy array."""
    if isinstance(img, Image.Image):
        return img
    return Image.fromarray(img)


# ── Event handlers ───────────────────────────────────────────────────────────
def on_image_upload(img):
    """Pass the uploaded image straight into the annotator."""
    if img is None:
        return gr.update()
    return {"image": img, "boxes": []}


def on_generate(annotator_data, prompt, accelerate):
    if annotator_data is None:
        gr.Warning("Upload an image first.")
        return None

    boxes = annotator_data.get("boxes", [])
    if not boxes:
        gr.Warning("Draw a bounding box around the region you want to edit.")
        return None

    if not prompt.strip():
        gr.Warning("Enter an edit prompt.")
        return None

    image = _to_pil(annotator_data["image"])
    box   = boxes[0]

    payload = {
        "image": _pil_to_b64(image),
        "bbox": {
            "xmin": box["xmin"],
            "ymin": box["ymin"],
            "xmax": box["xmax"],
            "ymax": box["ymax"],
        },
        "prompt": prompt.strip(),
        "accelerate": accelerate == "⚡ Accelerated",
    }

    try:
        resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        result_img = Image.open(io.BytesIO(base64.b64decode(data["image"])))
        elapsed = data.get("generation_time_seconds")
        time_str = f"Generation time: **{elapsed:.2f}s**" if elapsed is not None else ""
        return result_img, time_str
    except requests.exceptions.ConnectionError:
        gr.Warning(f"Cannot reach backend at {BACKEND_URL}. Is the server running?")
        return None, "Generation time: **—**"
    except Exception as exc:
        gr.Warning(f"Error: {exc}")
        return None, "Generation time: **—**"


# ── UI ───────────────────────────────────────────────────────────────────────
PLACEHOLDER_IMG = (
    "https://raw.githubusercontent.com/gradio-app/gradio/main/guides/assets/logo.png"
)

CSS = Path("style.css").read_text()

with gr.Blocks(title="Accelerated Image Diffusion", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(
        """
        # Accelerated Image Diffusion
        Edit specific regions of an image with a text prompt.
        """
    )

    with gr.Row():
        # ── Left column: input ───────────────────────────────────────────────
        with gr.Column(scale=1):
            gr.Markdown("### Step 1 — Upload Image")
            upload = gr.Image(type="pil", label="Upload Image", height=280)

            gr.Markdown(
                "### Step 2 — Draw Bounding Box\n"
                "Press **C** to create a box · **D** to drag · **Delete** to remove."
            )
            annotator = image_annotator(
                value={"image": PLACEHOLDER_IMG, "boxes": []},
                label_list=["Area-to-change"],
                label_colors=[(201, 100, 66)],
                boxes_alpha=0.3,
                box_thickness=2,
                box_selected_thickness=3,
                single_box=True,
                interactive=True,
                height=380,
            )

        # ── Right column: prompt + result ────────────────────────────────────
        with gr.Column(scale=1):
            gr.Markdown("### Step 3 — Describe the Edit")
            prompt = gr.Textbox(
                placeholder="e.g. 'replace with a red sports car', 'add trees in the background'",
                label="Edit Prompt",
                lines=3,
            )
            gr.Markdown("### Generation Mode")
            accelerate_toggle = gr.Radio(
                choices=["⚡ Accelerated", "🐢 Normal"],
                value="⚡ Accelerated",
                label=None,
                show_label=False,
                info="Accelerated uses our optimized pipeline for faster results.",
            )
            generate_btn = gr.Button("Generate", variant="primary", size="lg")

            gr.Markdown("### Step 4 — Result")
            result = gr.Image(label="Generated Image", interactive=False, height=380)
            generation_time = gr.Markdown(value="Generation time: **—**")

    # ── Wiring ───────────────────────────────────────────────────────────────
    upload.change(fn=on_image_upload, inputs=upload, outputs=annotator)
    generate_btn.click(fn=on_generate, inputs=[annotator, prompt, accelerate_toggle], outputs=[result, generation_time])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
