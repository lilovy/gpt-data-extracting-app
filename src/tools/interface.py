import gradio as gr
# from src.tools import timer
from .timer import timer


def hello(input):
    if input:
        return f"Hi {input}"

@timer
def get_data_from_interface(data):
    resp = requests.post(
        "http://127.0.0.1:7860/run/predict", 
        json={
            "data": [
                data,
                ]
            },
        ).json()
    data = resp["data"]
    return data

def make_interface(func):

    inputs = gr.inputs.Textbox(lines=7, label="Chat with AI")
    outputs = gr.outputs.Textbox(label="Reply")

    gr.Interface(fn=func, inputs=inputs, 
                outputs=outputs, title="AI Chatbot",
                description="Ask anything you want",
                ).launch(share=True)
