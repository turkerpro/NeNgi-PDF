"""
NeNgi PDF - Interactive Draggable & Resizable Signature / Stamp Box
Studio style movable and resizable signature element.
Allows the user to freely drag, stretch/shorten, reposition, and commit signatures onto the PDF.
"""

from __future__ import annotations
import os
from typing import Optional, TYPE_CHECKING
import pymupdf as fitz
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)

if TYPE_CHECKING:
    from nengi.ui.pdf_view import PageRenderWidget


class ResizeHandle(QWidget):
    """Bottom-right resize grip handle to stretch/shorten the stamp."""

    def __init__(self, parent: DraggableStampWidget):
        super().__init__(parent)
        self.stamp_widget = parent
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setStyleSheet("background: transparent;")
        self._resizing = False
        self._drag_start = QPoint()
        self._start_size = QSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 120, 212))
        # Draw small bottom-right corner triangle / square handle
        painter.drawRect(6, 6, 9, 9)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(8, 8, 5, 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = True
            self._drag_start = event.globalPosition().toPoint()
            self._start_size = self.stamp_widget.size()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.globalPosition().toPoint() - self._drag_start
            new_w = max(50, self._start_size.width() + delta.x())
            new_h = max(25, self._start_size.height() + delta.y())
            self.stamp_widget.resize(new_w, new_h)
            self.stamp_widget.update_image_display()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class DraggableStampWidget(QWidget):
    """
    Floating movable & resizable stamp/signature widget placed on a PageRenderWidget.
    Supports real-time dragging, resizing, and baking to PDF.
    """

    committed = pyqtSignal()
    discarded = pyqtSignal()

    def __init__(
        self,
        page_widget: PageRenderWidget,
        initial_pos: QPoint,
        image_path: str,
        zoom: float = 1.0,
        initial_width: int = 160,
        initial_height: int = 70,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent or page_widget)
        self.page_widget = page_widget
        self.image_path = image_path
        self.zoom = zoom
        self.raw_pixmap = QPixmap(image_path) if os.path.exists(image_path) else QPixmap()

        self._dragging = False
        self._drag_start_pos = QPoint()

        self.setObjectName("draggableStampBox")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._init_ui()
        self.resize(int(initial_width * zoom), int(initial_height * zoom))
        self.move(initial_pos)
        self.update_image_display()
        self.show()

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 2, 4, 4)
        self.layout.setSpacing(2)

        # Mini Top Action Bar (Clean white floating pill)
        self.action_pill = QFrame(self)
        self.action_pill.setObjectName("actionPill")
        self.action_pill.setStyleSheet(
            "QFrame#actionPill {"
            "  background-color: #FFFFFF;"
            "  border: 1px solid #CBD5E1;"
            "  border-radius: 10px;"
            "  padding: 1px 4px;"
            "}"
            "QFrame#actionPill QLabel {"
            "  background: transparent;"
            "  color: #0078D4;"
            "  font-weight: bold;"
            "  font-size: 10px;"
            "}"
            "QFrame#actionPill QPushButton {"
            "  background: transparent;"
            "  border: none;"
            "  border-radius: 3px;"
            "  font-size: 11px;"
            "}"
            "QFrame#actionPill QPushButton:hover {"
            "  background-color: #E2E8F0;"
            "}"
        )
        bar_layout = QHBoxLayout(self.action_pill)
        bar_layout.setContentsMargins(4, 1, 4, 1)
        bar_layout.setSpacing(4)

        lbl_hint = QLabel("✥ Taşı & Boyutlandır")
        lbl_hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bar_layout.addWidget(lbl_hint)
        bar_layout.addStretch()

        btn_apply = QPushButton("✅")
        btn_apply.setFixedSize(20, 20)
        btn_apply.setToolTip("İmzayı Buraya Sabitle (PDF'e Ekle)")
        btn_apply.setStyleSheet("background-color: #0078D4; color: white; border-radius: 3px; font-size: 10px;")
        btn_apply.clicked.connect(self.commit_to_pdf)
        bar_layout.addWidget(btn_apply)

        btn_delete = QPushButton("🗑️")
        btn_delete.setFixedSize(20, 20)
        btn_delete.setToolTip("İmzayı Kaldır")
        btn_delete.setStyleSheet("background-color: #DC2626; color: white; border-radius: 3px; font-size: 10px;")
        btn_delete.clicked.connect(self.discard)
        bar_layout.addWidget(btn_delete)

        # Allow dragging by clicking on the action pill bar
        self.action_pill.mousePressEvent = self.mousePressEvent
        self.action_pill.mouseMoveEvent = self.mouseMoveEvent
        self.action_pill.mouseReleaseEvent = self.mouseReleaseEvent

        self.layout.addWidget(self.action_pill)

        # Image Display Area (Click-Through to Drag Box)
        self.lbl_image = QLabel(self)
        self.lbl_image.setObjectName("stampContent")
        self.lbl_image.setStyleSheet("background: transparent; border: none;")
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.layout.addWidget(self.lbl_image, stretch=1)

        # Bottom-right resize handle
        self.resize_handle = ResizeHandle(self)
        self.resize_handle.show()

        # Studio Style Transparent Box with Dashed Border
        self.setStyleSheet(
            "QWidget#draggableStampBox {"
            "  background: transparent;"
            "  border: 1.5px dashed #0078D4;"
            "  border-radius: 4px;"
            "}"
            "QWidget#draggableStampBox QLabel#stampContent {"
            "  background: transparent;"
            "  border: none;"
            "}"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position resize handle at bottom right corner
        self.resize_handle.move(self.width() - 16, self.height() - 16)
        self.update_image_display()

    def update_image_display(self):
        """Updates the scaled image according to current widget dimensions."""
        if not self.raw_pixmap or self.raw_pixmap.isNull():
            return
        target_w = max(20, self.lbl_image.width() - 4)
        target_h = max(15, self.lbl_image.height() - 4)
        scaled = self.raw_pixmap.scaled(
            target_w, target_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_image.setPixmap(scaled)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.pos()
            self.raise_()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            parent_rect = self.parentWidget().rect()
            new_x = max(0, min(new_pos.x(), parent_rect.width() - self.width()))
            new_y = max(0, min(new_pos.y(), parent_rect.height() - self.height()))
            self.move(new_x, new_y)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def commit_to_pdf(self):
        """Bakes the signature permanently into the underlying PDF page at current size and position."""
        if not self.image_path or not os.path.exists(self.image_path):
            self.discard()
            return

        # Calculate exact image area in PDF coordinates
        img_pos = self.lbl_image.mapTo(self.page_widget, QPoint(0, 0))
        pdf_x = img_pos.x() / self.zoom
        pdf_y = img_pos.y() / self.zoom
        pdf_w = self.lbl_image.width() / self.zoom
        pdf_h = self.lbl_image.height() / self.zoom

        stamp_rect = fitz.Rect(pdf_x, pdf_y, pdf_x + pdf_w, pdf_y + pdf_h)

        self.page_widget.doc.add_image_stamp(
            self.page_widget.page_idx,
            stamp_rect,
            self.image_path
        )
        self.page_widget.render_cache()
        self.page_widget.update()
        self.page_widget.page_modified.emit()
        self.committed.emit()
        self.close()

    def discard(self):
        """Removes the draggable stamp without baking."""
        self.discarded.emit()
        self.close()
