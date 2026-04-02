import gradio as gr
from pathlib import Path
import requests
from PIL import Image

from helpers import BACKEND_URL, _pil_to_b64, _to_pil, _call_backend


# ── Event handlers ────────────────────────────────────────────────────────────
def on_clear_strokes(editor_data):
    if editor_data is None:
        return gr.update()
    bg = editor_data.get("background")
    return {"background": bg, "layers": [], "composite": bg}


def on_brush_size_change(size):
    return gr.update(brush=gr.Brush(colors=["rgba(255, 0, 0, 0.5)"], default_size=size))


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


def on_generate(editor_data, prompt, mode):
    no_result = (None, "Accelerated: **—** s", None, "Normal: **—** s", gr.update(visible=False))

    if editor_data is None or editor_data.get("background") is None:
        gr.Warning("Upload an image first.")
        return no_result

    if not prompt.strip():
        gr.Warning("Enter an edit prompt.")
        return no_result

    composite = editor_data.get("composite")
    if composite is None:
        gr.Warning("Paint over the region you want to edit using the brush.")
        return no_result

    image = composite if isinstance(composite, Image.Image) else _to_pil(composite)

    base_payload = {
        "image": _pil_to_b64(image),
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
        label = "Accelerated" if mode == "⚡ Accelerated" else "Normal"
        return image, f"{label}: **—** s", None, "Normal: **—** s", gr.update(visible=False)
    except Exception as exc:
        gr.Warning(f"Error: {exc}")
        return no_result


# ── UI ────────────────────────────────────────────────────────────────────────
CSS = Path("style.css").read_text()

with gr.Blocks(title="Accelerated Image Diffusion", theme=gr.themes.Soft(), css=CSS) as demo:
    gr.Markdown(
        """
        # Accelerated Image Diffusion
        Edit specific regions of an image with a text prompt.
        """
    )

    with gr.Row():
        # ── Left column: input ────────────────────────────────────────────────
        with gr.Column(scale=1):
            gr.Markdown(
                "### Step 1 — Upload & Paint Region\n"
                "Upload an image, then use the **brush** to paint over the area you want to edit. "
                "Use the **eraser** to correct mistakes."
            )
            brush_size = gr.Slider(
                minimum=5, maximum=80, value=24, step=1, label="Brush Size"
            )
            editor = gr.ImageEditor(
                label="Paint Region",
                type="pil",
                brush=gr.Brush(colors=["rgba(255, 0, 0, 0.5)"], default_size=24),
                eraser=gr.Eraser(default_size=24),
                interactive=True,
                height=380,
            )
            clear_btn = gr.Button("Clear Strokes", variant="secondary", size="sm")

        # ── Right column: prompt + result ─────────────────────────────────────
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

    # ── Wiring ────────────────────────────────────────────────────────────────
    brush_size.change(fn=on_brush_size_change, inputs=brush_size, outputs=editor)
    clear_btn.click(fn=on_clear_strokes, inputs=editor, outputs=editor)
    accelerate_toggle.change(
        fn=on_mode_change,
        inputs=accelerate_toggle,
        outputs=[result, generation_time_accelerated, col_normal],
    )
    generate_btn.click(
        fn=on_generate,
        inputs=[editor, prompt, accelerate_toggle],
        outputs=[result, generation_time_accelerated, result_normal, generation_time_normal, col_normal],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
