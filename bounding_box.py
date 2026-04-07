import gradio as gr
from gradio_image_annotation import image_annotator
from pathlib import Path
import requests

from helpers import BACKEND_URL, _pil_to_b64, _to_pil, _call_backend


# ── Event handlers ───────────────────────────────────────────────────────────
def on_image_upload(img):
    """Pass the uploaded image straight into the annotator."""
    if img is None:
        return gr.update()
    return {"image": img, "boxes": []}


def on_mode_change(mode):
    both = mode == "⚡🐢 Both"
    normal = mode == "🐢 Normal"
    label = "Normal Result" if normal else "Accelerated Result"
    time_placeholder = "Normal: **—** s" if normal else "Accelerated: **—** s"
    return (
        gr.update(label=label),
        gr.update(value=time_placeholder),
        gr.update(visible=both),
    )


def on_generate(annotator_data, prompt, mode):
    no_result = (None, "Accelerated: **—** s", None, "Normal: **—** s", gr.update(visible=False))

    if annotator_data is None:
        gr.Warning("Upload an image first.")
        return no_result

    boxes = annotator_data.get("boxes", [])
    if not boxes:
        gr.Warning("Draw a bounding box around the region you want to edit.")
        return no_result

    if not prompt.strip():
        gr.Warning("Enter an edit prompt.")
        return no_result

    image = _to_pil(annotator_data["image"])
    box   = boxes[0]

    base_payload = {
        "image": _pil_to_b64(image),
        "bbox": {
            "xmin": box["xmin"],
            "ymin": box["ymin"],
            "xmax": box["xmax"],
            "ymax": box["ymax"],
        },
        "prompt": prompt.strip(),
    }

    try:
        if mode == "⚡🐢 Both":
            accel_img, accel_time = _call_backend({**base_payload, "accelerate": True})
            normal_img, normal_time = _call_backend({**base_payload, "accelerate": False})
            return (
                accel_img,
                f"Accelerated: {accel_time}",
                normal_img,
                f"Normal: {normal_time}",
                gr.update(visible=True),
            )
        else:
            accelerate = mode == "⚡ Accelerated"
            img, time_str = _call_backend({**base_payload, "accelerate": accelerate})
            label = "Accelerated" if accelerate else "Normal"
            return img, f"{label}: {time_str}", None, "Normal: **—** s", gr.update(visible=False)

    except requests.exceptions.ConnectionError:
        gr.Warning(f"Cannot reach backend at {BACKEND_URL}. Is the server running?")
        return no_result
    except Exception as exc:
        gr.Warning(f"Error: {exc}")
        return no_result


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
                choices=["⚡ Accelerated", "🐢 Normal", "⚡🐢 Both"],
                value="⚡ Accelerated",
                label=None,
                show_label=False,
                info="'Both' runs accelerated then normal so you can compare generation times.",
            )
            generate_btn = gr.Button("Generate", variant="primary", size="lg")

            gr.Markdown("### Step 4 — Result")
            with gr.Row():
                with gr.Column(scale=1):
                    result = gr.Image(label="Accelerated Result", interactive=False, height=320)
                    generation_time_accelerated = gr.Markdown(value="Accelerated: **—** s")
                with gr.Column(scale=1, visible=False) as col_normal:
                    result_normal = gr.Image(label="Normal Result", interactive=False, height=320)
                    generation_time_normal = gr.Markdown(value="Normal: **—** s")

    # ── Wiring ───────────────────────────────────────────────────────────────
    upload.change(fn=on_image_upload, inputs=upload, outputs=annotator)
    accelerate_toggle.change(
        fn=on_mode_change,
        inputs=accelerate_toggle,
        outputs=[result, generation_time_accelerated, col_normal],
    )
    generate_btn.click(
        fn=on_generate,
        inputs=[annotator, prompt, accelerate_toggle],
        outputs=[result, generation_time_accelerated, result_normal, generation_time_normal, col_normal],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
