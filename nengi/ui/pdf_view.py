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
    QMenu, QInputDialog, QMessageBox, QFileDialog, QGraphicsDropShadowEffect, QDialog
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QMouseEvent, 
    QWheelEvent, QPaintEvent, QCursor, QFont, QAction
)
import pymupdf as fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.image_roundtrip import ImageRoundtripHandler
from nengi.ui.text_editor_dialog import TextEditorDialog


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

        # Text words & Acrobat Pro style paragraph blocks
        self.words: List[Tuple[float, float, float, float, str, int, int, int]] = []
        self.blocks: List[Tuple[float, float, float, float, str, int, int]] = []
        self.selected_words: List[Tuple[float, float, float, float, str, int, int, int]] = []
        self.hovered_block: Optional[Tuple[float, float, float, float, str, int, int]] = None
        self.active_text_widgets: List = []

        # Selection state for text / whiteout / drag
        self._is_selecting_text = False
        self._dragging = False
        self._drag_start = QPoint()
        self._drag_current = QPoint()

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cached_pixmap: Optional[QPixmap] = None
        self._text_extracted = False

        # Set widget geometry immediately from page rect
        try:
            p_rect = self.doc.get_page(self.page_idx).rect
            self.setFixedSize(int(p_rect.width * self.zoom), int(p_rect.height * self.zoom))
        except Exception:
            pass

        # Render first page immediately; subsequent pages render on-demand in paintEvent
        if self.page_idx == 0:
            self.render_cache()

    def _ensure_text_extracted(self):
        """Extracts text words and blocks on-demand only when user interacts with text."""
        if not self._text_extracted and self.doc and self.doc.is_open:
            self.words = self.doc.get_page_text_words(self.page_idx)
            self.blocks = self.doc.get_page_blocks(self.page_idx)
            self._text_extracted = True

    def set_zoom(self, zoom: float):
        if abs(self.zoom - zoom) > 0.01:
            self.zoom = zoom
            self.cached_pixmap = None
            self._text_extracted = False
            try:
                p_rect = self.doc.get_page(self.page_idx).rect
                self.setFixedSize(int(p_rect.width * self.zoom), int(p_rect.height * self.zoom))
            except Exception:
                self.render_cache()

            for tw in list(self.active_text_widgets):
                tw.update_zoom(zoom)

            self.updateGeometry()
            self.update()

    def render_cache(self):
        """Pre-renders page pixmap at current zoom without blocking on heavy text parsing."""
        if not self.doc or not self.doc.is_open or self.page_idx >= self.doc.page_count:
            return
        self.cached_pixmap = self.doc.render_page_pixmap(self.page_idx, self.zoom)
        self._text_extracted = False
        if self.cached_pixmap and self.size() != self.cached_pixmap.size():
            self.setFixedSize(self.cached_pixmap.size())

    def set_highlights(self, highlights: List[Tuple[fitz.Rect, QColor]]):
        """Highlights for diff or search."""
        self.highlights = highlights
        self.update()

    def paintEvent(self, event: QPaintEvent):
        # On-Demand Virtualized Rendering
        if self.cached_pixmap is None:
            self.render_cache()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rendered page pixmap
        if self.cached_pixmap:
            painter.drawPixmap(0, 0, self.cached_pixmap)

        # Draw diff or search highlight overlays
        for rect, color in self.highlights:
            screen_x = rect.x0 * self.zoom
            screen_y = rect.y0 * self.zoom
            screen_w = (rect.x1 - rect.x0) * self.zoom
            screen_h = (rect.y1 - rect.y0) * self.zoom
            
            painter.fillRect(
                QRectF(screen_x, screen_y, screen_w, screen_h),
                QBrush(color)
            )
            border_pen = QPen(color.darker(130), 1.5)
            painter.setPen(border_pen)
            painter.drawRect(QRectF(screen_x, screen_y, screen_w, screen_h))

        # Draw selected text highlights (Blue Fluent Selection)
        if self.selected_words:
            sel_brush = QBrush(QColor(0, 120, 215, 80))
            sel_pen = QPen(QColor(0, 120, 215, 180), 1)
            painter.setBrush(sel_brush)
            painter.setPen(sel_pen)
            for w in self.selected_words:
                sx = w[0] * self.zoom
                sy = w[1] * self.zoom
                sw = (w[2] - w[0]) * self.zoom
                sh = (w[3] - w[1]) * self.zoom
                painter.drawRect(QRectF(sx, sy, sw, sh))

        # Draw Acrobat Pro style hovered paragraph/block bounding box
        if self.mode == "view" and self.hovered_block and not self._is_selecting_text:
            hb = self.hovered_block
            hx = hb[0] * self.zoom
            hy = hb[1] * self.zoom
            hw = (hb[2] - hb[0]) * self.zoom
            hh = (hb[3] - hb[1]) * self.zoom
            pen = QPen(QColor(0, 120, 215, 160), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 120, 215, 15)))
            painter.drawRect(QRectF(hx, hy, hw, hh))

        # Draw drag selection box
        if self.mode == "view" and self._is_selecting_text:
            pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 120, 215, 30)))
            painter.drawRect(QRect(self._drag_start, self._drag_current).normalized())

        # Draw active whiteout rectangle preview while dragging
        if self.mode == "whiteout" and self._dragging:
            pen = QPen(QColor(0, 120, 212), 1.5, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            rect = QRect(self._drag_start, self._drag_current).normalized()
            painter.drawRect(rect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "view":
                self._ensure_text_extracted()
                self._is_selecting_text = True
                self._drag_start = event.pos()
                self._drag_current = event.pos()
                self.selected_words = []
                self.update()
            elif self.mode == "whiteout":
                self._dragging = True
                self._drag_start = event.pos()
                self._drag_current = event.pos()
                self.update()
            elif self.mode == "text":
                self._prompt_add_text(event.pos())
            elif self.mode == "stamp" and self.stamp_image_path:
                self._apply_stamp(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mode == "view":
            self._ensure_text_extracted()
            if self._is_selecting_text:
                self._drag_current = event.pos()
                sel_rect = QRect(self._drag_start, self._drag_current).normalized()
                pdf_sel = fitz.Rect(
                    sel_rect.left() / self.zoom,
                    sel_rect.top() / self.zoom,
                    sel_rect.right() / self.zoom,
                    sel_rect.bottom() / self.zoom
                )
                self.selected_words = [
                    w for w in self.words 
                    if fitz.Rect(w[0], w[1], w[2], w[3]).intersects(pdf_sel)
                ]
                self.update()
            else:
                pdf_x = event.pos().x() / self.zoom
                pdf_y = event.pos().y() / self.zoom
                is_over = any(w[0] <= pdf_x <= w[2] and w[1] <= pdf_y <= w[3] for w in self.words)
                self.setCursor(Qt.CursorShape.IBeamCursor if is_over else Qt.CursorShape.ArrowCursor)

                # Track hovered paragraph block
                prev_b = self.hovered_block
                self.hovered_block = None
                for b in self.blocks:
                    if b[0] <= pdf_x <= b[2] and b[1] <= pdf_y <= b[3]:
                        self.hovered_block = b
                        break
                if self.hovered_block != prev_b:
                    self.update()

        elif self._dragging and self.mode == "whiteout":
            self._drag_current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "view" and self._is_selecting_text:
                self._is_selecting_text = False
                self.update()
            elif self._dragging and self.mode == "whiteout":
                self._dragging = False
                rect = QRect(self._drag_start, event.pos()).normalized()
                if rect.width() > 4 and rect.height() > 4:
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

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.mode == "view" and event.button() == Qt.MouseButton.LeftButton:
            self._ensure_text_extracted()
            pdf_x = event.pos().x() / self.zoom
            pdf_y = event.pos().y() / self.zoom

            # Prioritize paragraph block editing (Acrobat Pro style)
            target_block = None
            for b in self.blocks:
                if b[0] <= pdf_x <= b[2] and b[1] <= pdf_y <= b[3]:
                    target_block = b
                    break

            if target_block:
                block_rect = fitz.Rect(target_block[0], target_block[1], target_block[2], target_block[3])
                style = self.doc.detect_text_style_at_rect(self.page_idx, block_rect)
                dlg = TextEditorDialog(
                    initial_text=target_block[4],
                    detected_style=style,
                    title="✏️ Paragrafı Düzenle (Acrobat Pro)",
                    parent=self
                )
                if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_text != target_block[4]:
                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb
                    )
                    self.render_cache()
                    self.update()
                    self.page_modified.emit()
                return

            # Fallback to single word
            for w in self.words:
                if w[0] <= pdf_x <= w[2] and w[1] <= pdf_y <= w[3]:
                    self.selected_words = [w]
                    self.update()
                    self.prompt_edit_selected_text()
                    break

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_C and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_selected_text()
        else:
            super().keyPressEvent(event)

    def copy_selected_text(self):
        if self.selected_words:
            from PyQt6.QtWidgets import QApplication
            text = " ".join(w[4] for w in self.selected_words)
            QApplication.clipboard().setText(text)

    def prompt_edit_selected_text(self):
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
                    title="✏️ Paragrafı Düzenle (Acrobat Pro)",
                    parent=self
                )
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb
                    )
                    self.render_cache()
                    self.update()
                    self.page_modified.emit()
            return
        
        current_text = " ".join(w[4] for w in self.selected_words)
        min_x0 = min(w[0] for w in self.selected_words)
        min_y0 = min(w[1] for w in self.selected_words)
        max_x1 = max(w[2] for w in self.selected_words)
        max_y1 = max(w[3] for w in self.selected_words)
        union_rect = fitz.Rect(min_x0, min_y0, max_x1, max_y1)

        style = self.doc.detect_text_style_at_rect(self.page_idx, union_rect)
        dlg = TextEditorDialog(
            initial_text=current_text,
            detected_style=style,
            title="✏️ Seçili Metni Düzenle (Acrobat Pro)",
            parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.doc.edit_text_at_rect(
                self.page_idx, union_rect, dlg.result_text,
                fontsize=dlg.result_fontsize, fontname=dlg.result_fitz_font, color=dlg.result_color_rgb
            )
            self.selected_words = []
            self.render_cache()
            self.update()
            self.page_modified.emit()

    def whiteout_selected_text(self):
        if not self.selected_words:
            return
        min_x0 = min(w[0] for w in self.selected_words)
        min_y0 = min(w[1] for w in self.selected_words)
        max_x1 = max(w[2] for w in self.selected_words)
        max_y1 = max(w[3] for w in self.selected_words)
        union_rect = fitz.Rect(min_x0, min_y0, max_x1, max_y1)
        self.doc.whiteout_area(self.page_idx, union_rect)
        self.selected_words = []
        self.render_cache()
        self.update()
        self.page_modified.emit()

    def _prompt_add_text(self, pos: QPoint):
        pdf_x = pos.x() / self.zoom
        pdf_y = pos.y() / self.zoom

        # Detect nearby style for smart font inheritance
        nearby_rect = fitz.Rect(pdf_x - 60, pdf_y - 30, pdf_x + 60, pdf_y + 30)
        style = self.doc.detect_text_style_at_rect(self.page_idx, nearby_rect)

        dlg = TextEditorDialog(
            initial_text="",
            detected_style=style,
            title="✍️ Metin Ekle (Acrobat Pro)",
            parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_text.strip():
            from nengi.ui.draggable_text import DraggableTextWidget
            box = DraggableTextWidget(
                page_widget=self,
                initial_pos=pos,
                text=dlg.result_text,
                fontsize=dlg.result_fontsize,
                fontname=dlg.result_fitz_font,
                color_rgb=dlg.result_color_rgb,
                zoom=self.zoom,
                parent=self
            )
            self.active_text_widgets.append(box)
            box.committed.connect(lambda b=box: self.active_text_widgets.remove(b) if b in self.active_text_widgets else None)
            box.discarded.connect(lambda b=box: self.active_text_widgets.remove(b) if b in self.active_text_widgets else None)

    def commit_all_pending_text(self):
        """Commits all floating text boxes permanently onto the PDF page."""
        for box in list(self.active_text_widgets):
            box.commit_to_pdf()

    def _apply_stamp(self, pos: QPoint):
        if not self.stamp_image_path or not os.path.exists(self.stamp_image_path):
            return
        
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

    def __init__(self, doc: Optional[PDFDocument] = None, parent: Optional[QWidget] = None):
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

        if doc:
            self.load_document(doc)

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

    def set_tool(self, tool_name: str):
        """Sets current active tool ('view', 'text', 'whiteout')."""
        self.set_tool_mode(tool_name)

    def set_stamp_image(self, image_path: str):
        """Switches to stamp mode with signature/stamp image."""
        self.set_tool_mode("stamp", stamp_path=image_path)

    def commit_pending_edits(self):
        """Bakes any uncommitted draggable text boxes before saving."""
        for pw in self.page_widgets:
            pw.commit_all_pending_text()

    def scroll_to_page(self, page_idx: int):
        """Scrolls view to specific page."""
        if 0 <= page_idx < len(self.page_widgets):
            target_widget = self.page_widgets[page_idx]
            self.ensureWidgetVisible(target_widget, 0, 50)
            self.current_page_idx = page_idx
            self.page_changed.emit(page_idx + 1, len(self.page_widgets))

    def go_to_page(self, page_idx: int):
        """Navigates to specific page."""
        self.scroll_to_page(page_idx)

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
        target_pw: Optional[PageRenderWidget] = None
        container_pos = self.container.mapFrom(self, pos)
        for pw in self.page_widgets:
            if pw.geometry().contains(container_pos):
                target_page_idx = pw.page_idx
                target_pw = pw
                break

        # Text selection actions if text is highlighted
        act_copy = None
        act_edit = None
        act_whiteout_sel = None
        if target_pw and target_pw.selected_words:
            act_copy = menu.addAction("📋 Seçili Metni Kopyala (Ctrl+C)")
            act_edit = menu.addAction("✏️ Seçili Metni Düzenle / Değiştir")
            act_whiteout_sel = menu.addAction("◻️ Seçili Metni Sil / Beyazlat")
            menu.addSeparator()

        act_ocr = menu.addAction("🔍 Sayfadaki Metinleri Tanı (OCR / Kelimeler)")
        menu.addSeparator()

        act_paint = menu.addAction(f"🖌️ Bu Sayfayı Harici Resim Editöründe (Paint vb.) Aç ve Temizle")
        act_rotate = menu.addAction("🔄 Sayfayı 90° Sağa Döndür")
        act_delete = menu.addAction("🗑️ Bu Sayfayı Sil")
        menu.addSeparator()
        act_export_img = menu.addAction("🖼️ Bu Sayfayı Resim Olarak Dışa Aktar (PNG)")

        action = menu.exec(self.mapToGlobal(pos))
        if action == act_copy and target_pw:
            target_pw.copy_selected_text()
            self.status_message.emit("Metin panoya kopyalandı.")
        elif action == act_edit and target_pw:
            target_pw.prompt_edit_selected_text()
        elif action == act_whiteout_sel and target_pw:
            target_pw.whiteout_selected_text()
        elif action == act_ocr:
            self.run_ocr(target_page_idx)
        elif action == act_paint:
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

    def run_ocr(self, page_idx: int):
        """Runs OCR on page or checks for existing digital text."""
        if not self.doc or not self.doc.is_open:
            return
        words = self.doc.get_page_text_words(page_idx)
        if words:
            QMessageBox.information(
                self, "Metin Bilgisi", 
                f"Bu sayfada zaten {len(words)} adet dijital kelime mevcut!\n\n"
                "• Metinleri fareyle seçip kopyalayabilirsiniz (Ctrl+C).\n"
                "• Herhangi bir kelimeye çift tıklayarak doğrudan düzenleyebilirsiniz.\n"
                "• Sağ tıklayıp 'Seçili Metni Düzenle' veya 'Sil' diyebilirsiniz."
            )
            return

        self.status_message.emit("Sayfa taranıyor (OCR)...")
        items = self.doc.ocr_page(page_idx)
        if items:
            self.refresh_page(page_idx)
            self.document_modified.emit()
            QMessageBox.information(
                self, "OCR Tamamlandı", 
                f"Sayfada {len(items)} satır metin başarıyla tanındı ve aranabilir/seçilebilir hale getirildi!\n\n"
                "Artık metinleri fareyle seçip düzenleyebilirsiniz."
            )
        else:
            QMessageBox.information(
                self, "Bilgi", 
                "Sayfada ek metin tanınamadı veya metin zaten mevcut."
            )

    def undo(self):
        """Reverts the last document action (Ctrl+Z)."""
        if self.doc and self.doc.undo():
            self.refresh_all_pages()
            self.document_modified.emit()
            self.status_message.emit("İşlem geri alındı.")

    def redo(self):
        """Redoes the last reverted action (Ctrl+Y)."""
        if self.doc and self.doc.redo():
            self.refresh_all_pages()
            self.document_modified.emit()
            self.status_message.emit("İşlem yinelendi.")

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
