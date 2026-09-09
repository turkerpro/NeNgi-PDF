import re
import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

pattern = re.compile(r'    def prompt_edit_selected_text\(self\):.*?    def convert_selected_to_draggable', re.DOTALL)

new_edit = """    def prompt_edit_selected_text(self):
        self._ensure_text_extracted()
        
        target_rect = None
        target_text = ""
        style = None
        
        if not self.selected_words and self.hovered_block:
            b = self.hovered_block
            target_rect = fitz.Rect(b[0], b[1], b[2], b[3])
            target_text = b[4]
            style = self.doc.detect_text_style_at_rect(self.page_idx, target_rect)
        elif self.selected_words:
            min_x = min(w[0] for w in self.selected_words)
            min_y = min(w[1] for w in self.selected_words)
            max_x = max(w[2] for w in self.selected_words)
            max_y = max(w[3] for w in self.selected_words)
            target_rect = fitz.Rect(min_x, min_y, max_x, max_y)
            target_text = " ".join([w[4] for w in self.selected_words])
            style = self.doc.detect_text_style_at_rect(self.page_idx, target_rect)
            
        if target_rect and style:
            from nengi.ui.inline_editor import InlineTextEditor
            editor = InlineTextEditor(target_text, style, target_rect, self.zoom, self)
            
            # Hide the block while editing
            self.active_text_widgets.append(editor)
            self.update() # triggers paintEvent to draw white box
            
            def on_commit(new_text, s, r):
                if editor in self.active_text_widgets:
                    self.active_text_widgets.remove(editor)
                self.doc.replace_text_block(
                    self.page_idx, r, new_text,
                    fontname=s.get("fitz_font", "helv"), 
                    fontsize=s.get("size", 11.0), 
                    color=s.get("color_rgb", (0,0,0)),
                    baseline_y=s.get("baseline_y"), 
                    origin_x=s.get("origin_x")
                )
                self.selected_words = []
                self.render_cache()
                self.update()
                
            def on_cancel():
                if editor in self.active_text_widgets:
                    self.active_text_widgets.remove(editor)
                self.update()

            editor.editing_finished.connect(on_commit)
            editor.editing_cancelled.connect(on_cancel)
            
            editor.show()
            editor.setFocus()
            editor.selectAll()

    def convert_selected_to_draggable"""

content = pattern.sub(new_edit, content)

with open(filepath, 'w') as f:
    f.write(content)
