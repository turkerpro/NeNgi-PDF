import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_convert = """    def convert_selected_to_draggable(self):
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
                fontname=style["fitz_font"],
                color_rgb=style["color_rgb"],
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
                fontname=style["fitz_font"],
                color_rgb=style["color_rgb"],
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
            self.page_modified.emit()"""

new_convert = """    def _on_block_committed(self, box):
        if box in self.active_text_widgets:
            self.active_text_widgets.remove(box)
        self.render_cache()
        self.update()
        self.page_modified.emit()

    def convert_selected_to_draggable(self):
        self._ensure_text_extracted()
        
        target_rect = None
        if not self.selected_words and self.hovered_block:
            b = self.hovered_block
            target_rect = fitz.Rect(b[0], b[1], b[2], b[3])
        elif self.selected_words:
            min_x0 = min(w[0] for w in self.selected_words)
            min_y0 = min(w[1] for w in self.selected_words)
            max_x1 = max(w[2] for w in self.selected_words)
            max_y1 = max(w[3] for w in self.selected_words)
            target_rect = fitz.Rect(min_x0, min_y0, max_x1, max_y1)

        if not target_rect:
            return

        ui_x = int(target_rect.x0 * self.zoom)
        ui_y = int(target_rect.y0 * self.zoom)
        pos = QPoint(ui_x, ui_y)

        # Take snapshot of the area for the draggable widget
        page = self.doc.get_page(self.page_idx)
        matrix = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=matrix, clip=target_rect)
        
        from PyQt6.QtGui import QImage, QPixmap
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        qpixmap = QPixmap.fromImage(qimg)

        from nengi.ui.draggable_block import DraggableBlockWidget
        box = DraggableBlockWidget(
            page_widget=self,
            initial_pos=pos,
            pixmap=qpixmap,
            pdf_rect=target_rect,
            zoom=self.zoom,
            parent=self
        )
        box.committed.connect(lambda b=box: self._on_block_committed(b))
        box.discarded.connect(lambda b=box: self._on_block_committed(b))
        self.active_text_widgets.append(box)
        box.show()

        self.selected_words = []
        self._is_selecting_text = False
        self.update()"""

if old_convert in content:
    content = content.replace(old_convert, new_convert)
    with open(filepath, 'w') as f:
        f.write(content)
