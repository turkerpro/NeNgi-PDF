import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_init = """        self.selected_words: List[Tuple[float, float, float, float, str, int, int, int]] = []"""
new_init = """        self.selected_words: List[Tuple[float, float, float, float, str, int, int, int]] = []
        self.selected_blocks: List[Tuple[float, float, float, float, str, int, int]] = []"""
if old_init in content:
    content = content.replace(old_init, new_init)

with open(filepath, 'w') as f:
    f.write(content)
