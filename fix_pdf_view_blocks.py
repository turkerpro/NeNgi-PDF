import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

# 1. Add selected_blocks to init
old_init = """        self.selected_words = []
        self.highlights = []"""
new_init = """        self.selected_words = []
        self.selected_blocks = []
        self.highlights = []"""
if old_init in content:
    content = content.replace(old_init, new_init)

# 2. Update paintEvent to draw selected_blocks
old_paint_hover = """        # Draw Studio style hovered paragraph/block bounding box
        if self.mode == "view" and self.hovered_block and not self._is_selecting_text:
            hb = self.hovered_block
            hx = hb[0] * self.zoom
            hy = hb[1] * self.zoom
            hw = (hb[2] - hb[0]) * self.zoom
            hh = (hb[3] - hb[1]) * self.zoom
            pen = QPen(QColor(0, 120, 215, 160), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 120, 215, 15)))
            painter.drawRect(QRectF(hx, hy, hw, hh))"""

new_paint_hover = """        # Draw selected blocks
        if self.mode == "view":
            for sb in self.selected_blocks:
                sx = sb[0] * self.zoom
                sy = sb[1] * self.zoom
                sw = (sb[2] - sb[0]) * self.zoom
                sh = (sb[3] - sb[1]) * self.zoom
                pen = QPen(QColor(0, 120, 215, 200), 1.5, Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.setBrush(QBrush(QColor(0, 120, 215, 25)))
                painter.drawRect(QRectF(sx, sy, sw, sh))

        # Draw Studio style hovered paragraph/block bounding box
        if self.mode == "view" and self.hovered_block and not self._is_selecting_text and self.hovered_block not in self.selected_blocks:
            hb = self.hovered_block
            hx = hb[0] * self.zoom
            hy = hb[1] * self.zoom
            hw = (hb[2] - hb[0]) * self.zoom
            hh = (hb[3] - hb[1]) * self.zoom
            pen = QPen(QColor(0, 120, 215, 160), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 120, 215, 15)))
            painter.drawRect(QRectF(hx, hy, hw, hh))"""
if old_paint_hover in content:
    content = content.replace(old_paint_hover, new_paint_hover)

with open(filepath, 'w') as f:
    f.write(content)
