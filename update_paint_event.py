import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_paint = """        for w in self.active_text_widgets:
            if type(w).__name__ == "DraggableBlockWidget":
                for r in getattr(w, "source_rects", [w.pdf_rect]):
                    sx = r.x0 * self.zoom
                    sy = r.y0 * self.zoom
                    sw = r.width * self.zoom
                    sh = r.height * self.zoom
                    painter.fillRect(QRectF(sx, sy, sw, sh), QBrush(QColor(255, 255, 255)))"""

new_paint = """        for w in self.active_text_widgets:
            if type(w).__name__ in ["DraggableBlockWidget", "InlineTextEditor"]:
                for r in getattr(w, "source_rects", [w.pdf_rect]):
                    sx = r.x0 * self.zoom
                    sy = r.y0 * self.zoom
                    sw = r.width * self.zoom
                    sh = r.height * self.zoom
                    painter.fillRect(QRectF(sx, sy, sw, sh), QBrush(QColor(255, 255, 255)))"""

if old_paint in content:
    content = content.replace(old_paint, new_paint)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find old_paint block!")
