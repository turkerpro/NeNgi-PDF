import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_paint = """        # Draw rendered page pixmap
        if self.cached_pixmap:
            painter.drawPixmap(0, 0, self.cached_pixmap)

        # Draw diff or search highlight overlays"""

new_paint = """        # Draw rendered page pixmap
        if self.cached_pixmap:
            painter.drawPixmap(0, 0, self.cached_pixmap)

        # Hide original blocks of DraggableBlockWidgets being dragged
        from PyQt6.QtGui import QColor, QBrush
        from PyQt6.QtCore import QRectF
        for w in self.active_text_widgets:
            if type(w).__name__ == "DraggableBlockWidget":
                sx = w.pdf_rect.x0 * self.zoom
                sy = w.pdf_rect.y0 * self.zoom
                sw = w.pdf_rect.width * self.zoom
                sh = w.pdf_rect.height * self.zoom
                painter.fillRect(QRectF(sx, sy, sw, sh), QBrush(QColor(255, 255, 255)))

        # Draw diff or search highlight overlays"""

if old_paint in content:
    content = content.replace(old_paint, new_paint)
    with open(filepath, 'w') as f:
        f.write(content)
