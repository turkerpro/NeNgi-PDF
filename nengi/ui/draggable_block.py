from __future__ import annotations
import fitz
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QMouseEvent, QPixmap, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nengi.ui.pdf_view import PageRenderWidget

class DraggableBlockWidget(QWidget):
    committed = pyqtSignal()
    discarded = pyqtSignal()

    def __init__(
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
        self.pdf_rect = pdf_rect
        self.zoom = zoom
        self._drag_start_pos = QPoint()

        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            DraggableBlockWidget {
                border: 2px dashed #0078D4;
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.85)
        self.setGraphicsEffect(op)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.lbl_img = QLabel()
        self.lbl_img.setPixmap(pixmap)
        layout.addWidget(self.lbl_img)

        # Controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_ok = QPushButton("✔")
        self.btn_ok.setFixedSize(24, 24)
        self.btn_ok.setStyleSheet("background: #0078D4; color: white; border-radius: 4px;")
        self.btn_ok.clicked.connect(self.commit)

        self.btn_cancel = QPushButton("✖")
        self.btn_cancel.setFixedSize(24, 24)
        self.btn_cancel.setStyleSheet("background: #D13438; color: white; border-radius: 4px;")
        self.btn_cancel.clicked.connect(self.discard)

        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.btn_ok)
        ctrl_layout.addWidget(self.btn_cancel)
        layout.addLayout(ctrl_layout)

        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.move(initial_pos)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._drag_start_pos.isNull() and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.pos() - self._drag_start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = QPoint()

    def commit(self):
        ui_pos = self.pos()
        pdf_x = ui_pos.x() / self.zoom
        pdf_y = ui_pos.y() / self.zoom
        
        new_rect = fitz.Rect(pdf_x, pdf_y, pdf_x + self.pdf_rect.width, pdf_y + self.pdf_rect.height)

        doc = self.page_widget.doc
        page_idx = self.page_widget.page_idx

        # Use temporary doc to preserve exact rendering
        import fitz as pymupdf
        tmp_doc = pymupdf.open()
        tmp_doc.insert_pdf(doc.doc, from_page=page_idx, to_page=page_idx)

        # Save undo state
        doc.save_state_for_undo()

        # Redact old area
        page = doc.get_page(page_idx)
        page.add_redact_annot(self.pdf_rect, fill=(1,1,1))
        page.apply_redactions()

        # Draw to new area
        page.show_pdf_page(new_rect, tmp_doc, 0, clip=self.pdf_rect)

        doc.is_modified = True
        self.committed.emit()
        self.deleteLater()

    def discard(self):
        self.discarded.emit()
        self.deleteLater()
