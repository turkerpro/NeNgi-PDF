import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_convert = """    def convert_selected_to_draggable(self):
        self._ensure_text_extracted()
        
        target_rect = None
        if not self.selected_words and self.hovered_block:
            b = self.hovered_block
            target_rect = fitz.Rect(b[0], b[1], b[2], b[3])
        elif self.selected_words:"""

new_convert = """    def convert_selected_to_draggable(self):
        self._ensure_text_extracted()
        
        target_rect = None
        if not self.selected_words and self.selected_blocks:
            min_x = min(b[0] for b in self.selected_blocks)
            min_y = min(b[1] for b in self.selected_blocks)
            max_x = max(b[2] for b in self.selected_blocks)
            max_y = max(b[3] for b in self.selected_blocks)
            target_rect = fitz.Rect(min_x, min_y, max_x, max_y)
        elif not self.selected_words and self.hovered_block:
            b = self.hovered_block
            target_rect = fitz.Rect(b[0], b[1], b[2], b[3])
        elif self.selected_words:"""

if old_convert in content:
    content = content.replace(old_convert, new_convert)

# Make sure _show_context_menu shows the menu if selected_blocks is not empty
old_menu_cond = """        if target_pw and (target_pw.selected_words or target_pw.hovered_block):"""
new_menu_cond = """        if target_pw and (target_pw.selected_words or target_pw.selected_blocks or target_pw.hovered_block):"""

if old_menu_cond in content:
    content = content.replace(old_menu_cond, new_menu_cond)

# Redacting all selected blocks instead of just target_rect if it's multiple blocks
# Wait, redacting target_rect will redact the bounding box (which might redact things BETWEEN blocks).
# Actually, if we use target_rect for clip, it also clips things BETWEEN blocks.
# And redacting target_rect redacts things between blocks.
# If they selected multiple disjoint blocks, grabbing their union rect grabs everything between them!
# This is usually what they want if they drag a group of items.
# Let's keep it as target_rect (union rect).

with open(filepath, 'w') as f:
    f.write(content)
