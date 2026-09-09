import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

# Add convert_selected_to_draggable
new_method = """    def convert_selected_to_draggable(self):
        self._ensure_text_extracted()
        if not self.selected_words and self.hovered_block:
            b = self.hovered_block
            block_rect = fitz.Rect(b[0], b[1], b[2], b[3])
            style = self.doc.detect_text_style_at_rect(self.page_idx, block_rect)
            
            ui_x = int(b[0] * self.zoom)
            ui_y = int(b[1] * self.zoom)
            pos = QPoint(ui_x, ui_y)
            
            from nengi.ui.draggable_text import DraggableTextWidget
            box = DraggableTextWidget(
                page_widget=self,
                initial_pos=pos,
                text=b[4],
                fontsize=style["size"],
                fontname=style["font"],
                color_rgb=style["color"],
                zoom=self.zoom
            )
            self.active_text_widgets.append(box)
            box.show()
            
            self.doc.save_state_for_undo()
            page = self.doc.get_page(self.page_idx)
            page.add_redact_annot(block_rect, fill=(1,1,1))
            page.apply_redactions()
            self.doc.is_modified = True
            
            self.selected_words = []
            self._is_selecting_text = False
            self.render_cache()
            self.update()
            self.page_modified.emit()
            return
            
        if self.selected_words:
            current_text = " ".join(w[4] for w in self.selected_words)
            min_x0 = min(w[0] for w in self.selected_words)
            min_y0 = min(w[1] for w in self.selected_words)
            max_x1 = max(w[2] for w in self.selected_words)
            max_y1 = max(w[3] for w in self.selected_words)
            union_rect = fitz.Rect(min_x0, min_y0, max_x1, max_y1)
            style = self.doc.detect_text_style_at_rect(self.page_idx, union_rect)

            ui_x = int(min_x0 * self.zoom)
            ui_y = int(min_y0 * self.zoom)
            pos = QPoint(ui_x, ui_y)

            from nengi.ui.draggable_text import DraggableTextWidget
            box = DraggableTextWidget(
                page_widget=self,
                initial_pos=pos,
                text=current_text,
                fontsize=style["size"],
                fontname=style["font"],
                color_rgb=style["color"],
                zoom=self.zoom
            )
            self.active_text_widgets.append(box)
            box.show()
            
            self.doc.save_state_for_undo()
            page = self.doc.get_page(self.page_idx)
            page.add_redact_annot(union_rect, fill=(1,1,1))
            page.apply_redactions()
            self.doc.is_modified = True
            
            self.selected_words = []
            self._is_selecting_text = False
            self.render_cache()
            self.update()
            self.page_modified.emit()

    def _prompt_add_text"""

content = content.replace("    def _prompt_add_text", new_method)

# Fix Context Menu
old_menu = """        # Text selection actions if text is highlighted
        act_copy = None
        act_edit = None
        act_whiteout_sel = None
        if target_pw and target_pw.selected_words:
            act_copy = menu.addAction("📋 Seçili Metni Kopyala (Ctrl+C)")
            act_edit = menu.addAction("✏️ Seçili Metni Düzenle / Değiştir")
            act_whiteout_sel = menu.addAction("◻️ Seçili Metni Sil / Beyazlat")
            menu.addSeparator()"""

new_menu = """        # Text selection actions if text is highlighted or block hovered
        act_copy = None
        act_edit = None
        act_move = None
        act_whiteout_sel = None
        if target_pw and (target_pw.selected_words or target_pw.hovered_block):
            act_copy = menu.addAction("📋 Seçili Metni Kopyala (Ctrl+C)")
            act_edit = menu.addAction("✏️ Seçili Metni Düzenle / Değiştir")
            act_move = menu.addAction("✂️ Seçili Metni Taşı (Serbest Sürükle)")
            act_whiteout_sel = menu.addAction("◻️ Seçili Metni Sil / Beyazlat")
            menu.addSeparator()"""

content = content.replace(old_menu, new_menu)

old_exec = """        elif action == act_edit and target_pw:
            target_pw.prompt_edit_selected_text()"""

new_exec = """        elif action == act_edit and target_pw:
            target_pw.prompt_edit_selected_text()
        elif action == act_move and target_pw:
            target_pw.convert_selected_to_draggable()"""

content = content.replace(old_exec, new_exec)

with open(filepath, 'w') as f:
    f.write(content)
