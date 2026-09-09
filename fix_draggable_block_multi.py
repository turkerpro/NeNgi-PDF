import os

filepath = 'nengi/ui/draggable_block.py'
with open(filepath, 'r') as f:
    content = f.read()

old_init = """    def __init__(
        self,
        page_widget: PageRenderWidget,
        initial_pos: QPoint,
        pixmap: QPixmap,
        pdf_rect: fitz.Rect,
        zoom: float = 1.0,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent or page_widget)
        self.page_widget = page_widget
        self.pdf_rect = pdf_rect"""

new_init = """    def __init__(
        self,
        page_widget: PageRenderWidget,
        initial_pos: QPoint,
        pixmap: QPixmap,
        pdf_rect: fitz.Rect,
        source_rects: list = None,
        zoom: float = 1.0,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent or page_widget)
        self.page_widget = page_widget
        self.pdf_rect = pdf_rect
        self.source_rects = source_rects or [pdf_rect]"""

if old_init in content:
    content = content.replace(old_init, new_init)

old_redact = """        # Redact old area
        page = doc.get_page(page_idx)
        page.add_redact_annot(self.pdf_rect, fill=(1,1,1))
        page.apply_redactions()"""

new_redact = """        # Redact old area(s)
        page = doc.get_page(page_idx)
        for r in self.source_rects:
            page.add_redact_annot(r, fill=(1,1,1))
        page.apply_redactions()"""

if old_redact in content:
    content = content.replace(old_redact, new_redact)

with open(filepath, 'w') as f:
    f.write(content)

# Update pdf_view.py to pass source_rects
filepath_view = 'nengi/ui/pdf_view.py'
with open(filepath_view, 'r') as f:
    content_view = f.read()

old_box = """        box = DraggableBlockWidget(
            page_widget=self,
            initial_pos=pos,
            pixmap=qpixmap,
            pdf_rect=target_rect,
            zoom=self.zoom,
            parent=self
        )"""

new_box = """        source_rects = []
        if not self.selected_words and self.selected_blocks:
            source_rects = [fitz.Rect(b[0], b[1], b[2], b[3]) for b in self.selected_blocks]
        else:
            source_rects = [target_rect]

        box = DraggableBlockWidget(
            page_widget=self,
            initial_pos=pos,
            pixmap=qpixmap,
            pdf_rect=target_rect,
            source_rects=source_rects,
            zoom=self.zoom,
            parent=self
        )"""

if old_box in content_view:
    content_view = content_view.replace(old_box, new_box)

# We also need to clear selected_blocks after dropping/converting
old_clear = """        self.selected_words = []
        self._is_selecting_text = False
        self.update()"""

new_clear = """        self.selected_words = []
        self.selected_blocks = []
        self._is_selecting_text = False
        self.update()"""

if old_clear in content_view:
    content_view = content_view.replace(old_clear, new_clear)

with open(filepath_view, 'w') as f:
    f.write(content_view)
