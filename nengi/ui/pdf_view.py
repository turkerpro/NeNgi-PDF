"""
NeNgi PDF - Interactive Single & Multi-Page PDF Viewer Widget
Supports high-DPI rendering, zooming, panning, whiteout/eraser, text placement,
stamp placement, and right-click context menu for external image editing roundtrip.
"""

from __future__ import annotations
import os
from typing import Optional, Tuple, List, Callable
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, 
    QMenu, QInputDialog, QMessageBox, QFileDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QMouseEvent, 
    QWheelEvent, QPaintEvent, QCursor, QFont, QAction
)
import pymupdf as fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.image_roundtrip import ImageRoundtripHandler


class PageRenderWidget(QWidget):
    """Renders a single PDF page and handles interactive canvas tools."""

    whiteout_applied = pyqtSignal(int, fitz.Rect)     # (page_idx, rect)
    text_applied = pyqtSignal(int, tuple, str, float) # (page_idx, (x, y), text, size)
    stamp_applied = pyqtSignal(int, fitz.Rect, str)   # (page_idx, rect, image_path)
    page_modified = pyqtSignal()

    def __init__(self, doc: PDFDocument, page_idx: int, zoom: float = 1.2, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc = doc
        self.page_idx = page_idx
        self.zoom = zoom
        self.mode = "view"  # "view", "whiteout", "text", "stamp"
        
        self.stamp_image_path: Optional[str] = None
        self.highlights: List[Tuple[fitz.Rect, QColor]] = []

        # Selection state for whiteout / drag
        self._dragging = False
        self._drag_start = QPoint()
        self._drag_current = QPoint()

        self.setMouseTracking(True)
        self.cached_pixmap: Optional[QPixmap] = None
        self.render_cache()

    def set_zoom(self, zoom: float):
        if abs(self.zoom - zoom) > 0.01:
            self.zoom = zoom
            self.render_cache()
            self.updateGeometry()
            self.update()

    def render_cache(self):
        """Pre-renders page pixmap at current zoom."""
        if not self.doc or not self.doc.is_open or self.page_idx >= self.doc.page_count:
            return
        self.cached_pixmap = self.doc.render_page_pixmap(self.page_idx, self.zoom)
        if self.cached_pixmap:
            self.setFixedSize(self.cached_pixmap.size())

    def set_highlights(self, highlights: List[Tuple[fitz.Rect, QColor]]):
        """Highlights for diff or search."""
        self.highlights = highlights
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rendered page pixmap
        if self.cached_pixmap:
            painter.drawPixmap(0, 0, self.cached_pixmap)

        # Draw diff or search highlight overlays
        for rect, color in self.highlights:
            # Transform PDF coordinates to screen pixels
            screen_x = rect.x0 * self.zoom
            screen_y = rect.y0 * self.zoom
            screen_w = (rect.x1 - rect.x0) * self.zoom
            screen_h = (rect.y1 - rect.y0) * self.zoom
            
            painter.fillRect(
                QRectF(screen_x, screen_y, screen_w, screen_h),
                QBrush(color)
            )
            # Outline border
            border_pen = QPen(color.darker(130), 1.5)
            painter.setPen(border_pen)
            painter.drawRect(QRectF(screen_x, screen_y, screen_w, screen_h))

        # Draw active whiteout rectangle preview while dragging
        if self.mode == "whiteout" and self._dragging:
            pen = QPen(QColor(0, 120, 212), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            rect = QRect(self._drag_start, self._drag_current).normalized()
            painter.drawRect(rect)

        # Draw stamp preview
        if self.mode == "stamp" and not self._dragging:
            # Draw cursor preview for stamp
            pass

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "whiteout":
                self._dragging = True
                self._drag_start = event.pos()
                self._drag_current = event.pos()
                self.update()
            elif self.mode == "text":
                self._prompt_add_text(event.pos())
            elif self.mode == "stamp" and self.stamp_image_path:
                self._apply_stamp(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and self.mode == "whiteout":
            self._drag_current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self._dragging and self.mode == "whiteout":
            self._dragging = False
            rect = QRect(self._drag_start, event.pos()).normalized()
            if rect.width() > 4 and rect.height() > 4:
                # Convert screen coordinates to PDF points
                pdf_rect = fitz.Rect(
                    rect.left() / self.zoom,
                    rect.top() / self.zoom,
                    rect.right() / self.zoom,
                    rect.bottom() / self.zoom
                )
                self.doc.whiteout_area(self.page_idx, pdf_rect)
                self.render_cache()
                self.update()
                self.page_modified.emit()
            self.update()

    def _prompt_add_text(self, pos: QPoint):
        text, ok = QInputDialog.getText(self, "Metin Ekle", "Sayfaya eklenecek metni girin:")
        if ok and text:
            pdf_x = pos.x() / self.zoom
            pdf_y = pos.y() / self.zoom
            self.doc.add_text(self.page_idx, (pdf_x, pdf_y), text, fontsize=12.0)
            self.render_cache()
            self.update()
            self.page_modified.emit()

    def _apply_stamp(self, pos: QPoint):
        if not self.stamp_image_path or not os.path.exists(self.stamp_image_path):
            return
        
        # Stamp default size: 150 x 60 pt
        w = 140.0
        h = 55.0
        pdf_x = (pos.x() / self.zoom) - (w / 2)
        pdf_y = (pos.y() / self.zoom) - (h / 2)
        stamp_rect = fitz.Rect(pdf_x, pdf_y, pdf_x + w, pdf_y + h)
        
        self.doc.add_image_stamp(self.page_idx, stamp_rect, self.stamp_image_path)
        self.render_cache()
        self.update()
        self.page_modified.emit()


class PDFViewer(QScrollArea):
    """High-level scrollable PDF viewer hosting page render widgets."""

    page_changed = pyqtSignal(int, int)  # (current_page, total_pages)
    document_modified = pyqtSignal()
    status_message = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc: Optional[PDFDocument] = None
        self.current_page_idx = 0
        self.zoom = 1.2
        self.current_mode = "view"
        self.stamp_image_path: Optional[str] = None
        
        self.roundtrip_handler = ImageRoundtripHandler(self)
        self.roundtrip_handler.image_updated.connect(self._on_external_image_updated)
        self.roundtrip_handler.status_message.connect(self.status_message)

        # Setup scroll container
        self.container = QWidget()
        self.layout_pages = QVBoxLayout(self.container)
        self.layout_pages.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_pages.setSpacing(16)
        self.layout_pages.setContentsMargins(20, 20, 20, 20)
        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.page_widgets: List[PageRenderWidget] = []
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def load_document(self, doc: PDFDocument):
        """Loads a PDFDocument into the viewer."""
        self.doc = doc
        self.current_page_idx = 0
        self.clear_pages()

        if not self.doc or not self.doc.is_open:
            return

        for i in range(self.doc.page_count):
            pw = PageRenderWidget(self.doc, i, self.zoom, self.container)
            pw.mode = self.current_mode
            pw.stamp_image_path = self.stamp_image_path
            pw.page_modified.connect(self.document_modified)
            
            # Subtle card shadow for modern look
            shadow = QGraphicsDropShadowEffect(pw)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 4)
            pw.setGraphicsEffect(shadow)

            self.layout_pages.addWidget(pw)
            self.page_widgets.append(pw)

        self.page_changed.emit(1, self.doc.page_count)
        self.status_message.emit(f"Belge yüklendi: {self.doc.page_count} sayfa")

    def clear_pages(self):
        """Removes all page widgets from view."""
        for pw in self.page_widgets:
            self.layout_pages.removeWidget(pw)
            pw.deleteLater()
        self.page_widgets.clear()

    def set_zoom(self, zoom: float):
        """Clamps and updates zoom level."""
        zoom = max(0.25, min(4.0, zoom))
        self.zoom = zoom
        for pw in self.page_widgets:
            pw.set_zoom(zoom)
        self.status_message.emit(f"Yakınlaştırma: %{int(zoom * 100)}")

    def zoom_in(self):
        self.set_zoom(self.zoom + 0.15)

    def zoom_out(self):
        self.set_zoom(self.zoom - 0.15)

    def reset_zoom(self):
        self.set_zoom(1.0)

    def set_tool_mode(self, mode: str, stamp_path: Optional[str] = None):
        """Switches active tool: 'view', 'whiteout', 'text', 'stamp'."""
        self.current_mode = mode
        self.stamp_image_path = stamp_path
        
        cursor_map = {
            "view": Qt.CursorShape.ArrowCursor,
            "whiteout": Qt.CursorShape.CrossCursor,
            "text": Qt.CursorShape.IBeamCursor,
            "stamp": Qt.CursorShape.PointingHandCursor
        }
        cursor = cursor_map.get(mode, Qt.CursorShape.ArrowCursor)
        self.setCursor(cursor)

        for pw in self.page_widgets:
            pw.mode = mode
            pw.stamp_image_path = stamp_path

    def scroll_to_page(self, page_idx: int):
        """Scrolls view to specific page."""
        if 0 <= page_idx < len(self.page_widgets):
            target_widget = self.page_widgets[page_idx]
            self.ensureWidgetVisible(target_widget, 0, 50)
            self.current_page_idx = page_idx
            self.page_changed.emit(page_idx + 1, len(self.page_widgets))

    def refresh_page(self, page_idx: int):
        """Forces re-render of a specific page widget."""
        if 0 <= page_idx < len(self.page_widgets):
            self.page_widgets[page_idx].render_cache()
            self.page_widgets[page_idx].update()

    def refresh_all_pages(self):
        """Refreshes all pages (e.g. after deletion or rotation)."""
        if self.doc:
            self.load_document(self.doc)

    def _on_external_image_updated(self, page_num: int, xref: int):
        """Callback when external editor (Paint) saves image."""
        self.refresh_page(page_num)
        self.document_modified.emit()

    def _show_context_menu(self, pos: QPoint):
        """Shows right-click context menu on page."""
        if not self.doc or not self.doc.is_open:
            return

        menu = QMenu(self)
        
        # Determine which page was clicked
        target_page_idx = self.current_page_idx
        for pw in self.page_widgets:
            if pw.geometry().contains(self.container.mapFrom(self, pos)):
                target_page_idx = pw.page_idx
                break

        act_paint = menu.addAction(f"🖌️ Bu Sayfayı Harici Resim Editöründe (Paint vb.) Aç ve Temizle")
        act_rotate = menu.addAction("🔄 Sayfayı 90° Sağa Döndür")
        act_delete = menu.addAction("🗑️ Bu Sayfayı Sil")
        menu.addSeparator()
        act_export_img = menu.addAction("🖼️ Bu Sayfayı Resim Olarak Dışa Aktar (PNG)")

        action = menu.exec(self.mapToGlobal(pos))
        if action == act_paint:
            self.roundtrip_handler.edit_scanned_page(self.doc, target_page_idx)
        elif action == act_rotate:
            self.doc.rotate_page(target_page_idx, 90)
            self.refresh_page(target_page_idx)
            self.document_modified.emit()
        elif action == act_delete:
            if self.doc.page_count > 1:
                self.doc.delete_page(target_page_idx)
                self.refresh_all_pages()
                self.document_modified.emit()
            else:
                QMessageBox.warning(self, "Uyarı", "Belgedeki tek sayfa silinemez.")
        elif action == act_export_img:
            file_path, _ = QFileDialog.getSaveFileName(self, "Sayfayı Kaydet", "", "PNG Resmi (*.png);;JPEG Resmi (*.jpg)")
            if file_path:
                from nengi.core.converter import FormatConverter
                FormatConverter.export_page_as_image(self.doc, target_page_idx, file_path)
                QMessageBox.information(self, "Başarılı", "Sayfa resim olarak kaydedildi.")

    def wheelEvent(self, event: QWheelEvent):
        """Handles Ctrl + Wheel zooming."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
