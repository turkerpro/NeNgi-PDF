import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

method = """
    def set_mode(self, mode: str):
"""

new_method = """
    def set_current_color(self, color: tuple):
        self.current_color = color

    def set_mode(self, mode: str):
"""

content = content.replace(method, new_method)

with open(filepath, 'w') as f:
    f.write(content)
