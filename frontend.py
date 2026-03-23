import gradio as gr
from gradio_image_annotation import image_annotator
import numpy as np


example_annotation = {
    "image": "https://gradio-builds.s3.amazonaws.com/demo-files/base.png"
}

def get_boxes_json(annotations):
    return annotations["boxes"]


with gr.Blocks() as demo:
    with gr.Tab("Object annotation", id="tab_object_annotation"):
        annotator = image_annotator(
            example_annotation,
            label_list=["Area-to-change"],
            label_colors=[(0, 0, 255)],
            boxes_alpha=0.2,
            box_thickness=1,
            box_selected_thickness=2,
            single_box=True,
            interactive=True,
            sources=["upload"]
        )
        
        button_get = gr.Button("Get bounding boxes")
        json_boxes = gr.JSON()
        button_get.click(get_boxes_json, annotator, json_boxes)
        
        with gr.Row():
            inp = gr.Textbox(placeholder="Input prompt to change selected area")
            btn = gr.Button("Run Edit")
        

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
     

if __name__ == "__main__":
    demo.launch()