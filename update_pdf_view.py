import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

# Replace the edit method implementation
old_edit = """    def prompt_edit_selected_text(self):
        self._ensure_text_extracted()
        if not self.selected_words:
            # If no words are highlighted but a block is hovered, edit the whole block
            if self.hovered_block:
                b = self.hovered_block
                block_rect = fitz.Rect(b[0], b[1], b[2], b[3])
                style = self.doc.detect_text_style_at_rect(self.page_idx, block_rect)
                dlg = TextEditorDialog(
                    initial_text=b[4],
                    detected_style=style,
                    title="✏️ Paragrafı Düzenle",
                    parent=self
                )
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                        baseline_y=style.get("baseline_y"), origin_x=style.get("origin_x")
                    )
                    self.render_cache()
                    self.update()
        else:
            # For multiline custom selections, we union the bboxes
            min_x = min(w[0] for w in self.selected_words)
            min_y = min(w[1] for w in self.selected_words)
            max_x = max(w[2] for w in self.selected_words)
            max_y = max(w[3] for w in self.selected_words)
            union_rect = fitz.Rect(min_x, min_y, max_x, max_y)
            style = self.doc.detect_text_style_at_rect(self.page_idx, union_rect)
            
            combined_text = " ".join([w[4] for w in self.selected_words])
            dlg = TextEditorDialog(
                initial_text=combined_text,
                detected_style=style,
                title="✏️ Seçili Metni Düzenle",
                parent=self
            )
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.doc.replace_text_block(
                    self.page_idx, union_rect, dlg.result_text,
                    fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                    baseline_y=style.get("baseline_y"), origin_x=style.get("origin_x")
                )
                self.selected_words = []
                self.render_cache()
                self.update()"""

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
            editor.selectAll()"""

if old_edit in content:
    content = content.replace(old_edit, new_edit)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find old_edit block!")
