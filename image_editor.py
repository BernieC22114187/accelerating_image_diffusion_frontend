import gradio as gr

def predict(
    value: dict| None
):
    # process value from the ImageEditor component
    return "prediction"

interface = gr.Interface(predict, gr.ImageEditor(), gr.Textbox())
interface.launch()