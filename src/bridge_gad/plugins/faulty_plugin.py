from bridge_gad.plugins import PluginBase
from tkinter import messagebox

class FaultyPlugin(PluginBase):
    name = "Faulty Test Plugin"
    version = "1.0.0"
    author = "Er. Rajkumar Singh Chauhan"
    description = "A test plugin that intentionally crashes to test sandbox protection."

    def run(self, parent=None):
        # This will cause an intentional crash
        raise Exception("This is an intentional crash for testing sandbox protection!")