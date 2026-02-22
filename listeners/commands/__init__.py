from slack_bolt import App
from .hf import hf_callback


def register(app: App):
    app.command("/hf")(hf_callback)
