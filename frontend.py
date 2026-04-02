import gradio as gr
from gradio_image_annotation import image_annotator
import numpy as np
from PIL import Image


example_annotation = {
    "image": "https://raw.githubusercontent.com/gradio-app/gradio/main/guides/assets/logo.png"
}

def get_boxes_json(annotations):
    return annotations["boxes"]

def on_image_upload(image):
    if image is None:
        return gr.update()
    return {"image": image, "boxes": []}
    

with gr.Blocks() as demo:
    with gr.Walkthrough(selected=0) as walkthrough:
        with gr.Step("Image", id=0):
            image = gr.Image(type="pil")    
            next_btn = gr.Button("Next")
            next_btn.click(lambda: gr.Walkthrough(selected=1), outputs=walkthrough)
        with gr.Step("Draw Bounding Box", id=1):
            annotator = image_annotator(
                # TODO: don't know how to pass in 'image' from previous step into this component, so just hardcoding the example for now
                # Also crashes once you draw bounding box?? does not crash if this is step 1 though, so maybe has to do with the walkthrough component?
                # {"image": image},
                example_annotation,
                label_list=["Area-to-change"],
                label_colors=[(0, 0, 255)],
                boxes_alpha=0.2,
                box_thickness=1,
                box_selected_thickness=2,
                single_box=True,
                interactive=True
            )
            get_bbox_btn = gr.Button("Get bounding boxes")
            json_boxes = gr.JSON()
            get_bbox_btn.click(get_boxes_json, annotator, json_boxes)
            
            next_btn_2 = gr.Button("Next")
            next_btn_2.click(lambda: gr.Walkthrough(selected=2), outputs=walkthrough)
            
            with gr.Accordion("Keyboard Shortcuts"):
                gr.Markdown("""
                - ``C``: Create mode
                - ``D``: Drag mode
                - ``E``: Edit selected box (same as double-click a box)
                - ``Delete``: Remove selected box
                - ``Space``: Reset view (zoom/pan)
                - ``Enter``: Confirm modal dialog
                - ``Escape``: Cancel/close modal dialog
                """)
        with gr.Step("Input edit prompt", id=2):
            prompt = gr.Textbox()
            btn = gr.Button("generate")
            btn.click(lambda: gr.Walkthrough(selected=3), outputs=walkthrough)
        with gr.Step("Result", id=3):
            gr.Image(label="result", interactive=False)
    image.change(fn=on_image_upload, inputs=image, outputs=annotator)

if __name__ == "__main__":
    demo.launch()