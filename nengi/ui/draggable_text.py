"""
NeNgi PDF - Interactive Draggable Text Box
Studio style movable text element that allows the user to freely
drag, reposition, resize, edit, and commit newly added text on the PDF canvas.
"""

from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING
import fitz
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QColor, QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame
)

from nengi.ui.styles import get_dark_tokens, get_light_tokens

if TYPE_CHECKING:
    from nengi.ui.pdf_view import PageRenderWidget


def _get_tokens(is_dark: bool = True):
    """Returns design tokens for current theme."""
    return get_dark_tokens() if is_dark else get_light_tokens()


class DraggableTextWidget(QWidget):
    """
    Floating movable text box widget placed on a PageRenderWidget.
    Supports real-time dragging, in-place editing, and baking to PDF.
    """

    committed = pyqtSignal()
    discarded = pyqtSignal()

    def __init__(
        self,
        page_widget: PageRenderWidget,
        initial_pos: QPoint,
        text: str,
        fontsize: float = 12.0,
        fontname: str = "helv",
        color_rgb: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        zoom: float = 1.0,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent or page_widget)
        self.page_widget = page_widget
        self.text = text
        self.fontsize = fontsize
        self.fontname = fontname
        self.color_rgb = color_rgb
        self.zoom = zoom

        self._dragging = False
        self._drag_start_pos = QPoint()

        self.setObjectName("draggableTextBox")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self._init_ui()
        self.move(initial_pos)
        self.adjustSize()
        self.show()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 4)
        layout.setSpacing(3)

        # Get tokens for current theme (assume dark for now, could be enhanced)
        tokens = _get_tokens(True)

        # Mini Top Action Bar Pill
        self.action_pill = QFrame(self)
        self.action_pill.setObjectName("actionPill")
        self.action_pill.setStyleSheet(
            f"QFrame#actionPill {{"
            f"  background-color: {tokens.colors.bg_tertiary};"
            f"  border: 1px solid {tokens.colors.border_default};"
            f"  border-radius: {tokens.radius.xl}px;"
            f"  padding: 1px 4px;"
            f"}}"
            f"QFrame#actionPill QLabel {{"
            f"  background: transparent;"
            f"  color: {tokens.colors.text_accent};"
            f"  font-weight: bold;"
            f"  font-size: 10px;"
            f"}}"
            f"QFrame#actionPill QPushButton {{"
            f"  background: transparent;"
            f"  border: none;"
            f"  border-radius: {tokens.radius.xs}px;"
            f"  font-size: 11px;"
            f"}}"
            f"QFrame#actionPill QPushButton:hover {{"
            f"  background-color: {tokens.colors.bg_hover};"
            f"}}"
        )
        bar_layout = QHBoxLayout(self.action_pill)
        bar_layout.setContentsMargins(4, 1, 4, 1)
        bar_layout.setSpacing(4)

        lbl_hint = QLabel("Taşı")
        lbl_hint.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        bar_layout.addWidget(lbl_hint)
        bar_layout.addStretch()

        btn_edit = QPushButton("Düzenle")
        btn_edit.setFixedSize(20, 20)
        btn_edit.setToolTip("Metni veya Fontu Düzenle (Çift Tıklama)")
        btn_edit.clicked.connect(self._edit_text)
        bar_layout.addWidget(btn_edit)

        btn_apply = QPushButton("Uygula")
        btn_apply.setFixedSize(20, 20)
        btn_apply.setToolTip("Metni Buraya Sabitle (PDF'e Yerleştir)")
        btn_apply.setStyleSheet(f"background-color: {tokens.colors.accent_primary}; color: white; border-radius: {tokens.radius.xs}px; font-size: 10px;")
        btn_apply.clicked.connect(self.commit_to_pdf)
        bar_layout.addWidget(btn_apply)

        btn_delete = QPushButton("Sil")
        btn_delete.setFixedSize(20, 20)
        btn_delete.setToolTip("Metin Kutusunu Kaldır")
        btn_delete.setStyleSheet(f"background-color: {tokens.colors.error_bg}; color: {tokens.colors.error_text}; border-radius: {tokens.radius.xs}px; font-size: 10px;")
        btn_delete.clicked.connect(self.discard)
        bar_layout.addWidget(btn_delete)

        # Allow dragging by clicking on the action pill bar
        self.action_pill.mousePressEvent = self.mousePressEvent
        self.action_pill.mouseMoveEvent = self.mouseMoveEvent
        self.action_pill.mouseReleaseEvent = self.mouseReleaseEvent

        layout.addWidget(self.action_pill)

        # Text Label Display (Fully Transparent Background & Click-Through to Drag Box)
        self.lbl_content = QLabel(self.text)
        self.lbl_content.setObjectName("textContent")
        self.lbl_content.setWordWrap(True)
        self.lbl_content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._update_text_style()
        layout.addWidget(self.lbl_content)

        # Studio Style Transparent Bounding Box
        self.setStyleSheet(
            f"QWidget#draggableTextBox {{"
            f"  background: transparent;"
            f"  border: 1.5px dashed {tokens.colors.accent_primary};"
            f"  border-radius: {tokens.radius.md}px;"
            f"}}"
            f"QWidget#draggableTextBox QLabel#textContent {{"
            f"  background: transparent;"
            f"  border: none;"
            f"}}"
        )

    def _update_text_style(self):
        screen_size = max(8, int(self.fontsize * self.zoom))
        r, g, b = [int(c * 255) for c in self.color_rgb]
        self.lbl_content.setStyleSheet(
            f"font-size: {screen_size}pt; color: rgb({r}, {g}, {b}); font-family: 'Segoe UI', Arial, sans-serif; background: transparent; border: none; padding: 2px;"
        )

    def update_zoom(self, new_zoom: float):
        self.zoom = new_zoom
        self._update_text_style()
        self.adjustSize()

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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._edit_text()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def _edit_text(self):
        if getattr(self, "_inline_editing", False):
            return
        self._inline_editing = True
        style = {
            "family": "Arial",
            "size": self.fontsize,
            "is_bold": False,
            "is_italic": False,
            "color_rgb": self.color_rgb,
            "raw_font": "Helvetica",
            "fitz_font": self.fontname,
        }
        # Overlay aynı kutuda: mevcut konumdan pdf_rect türet
        try:
            ui_pos = self.pos()
            pw = self.page_widget
            zoom = self.zoom
            w_pdf = max(self.width() / zoom if zoom else 120, 120)
            h_pdf = max(self.height() / zoom if zoom else 24, 24)
            pdf_rect = fitz.Rect(
                ui_pos.x() / zoom, ui_pos.y() / zoom,
                ui_pos.x() / zoom + w_pdf, ui_pos.y() / zoom + h_pdf,
            )
        except Exception:
            pdf_rect = fitz.Rect(0, 0, 120, 24)
        from nengi.ui.inline_editor import InlineTextEditor
        editor = InlineTextEditor(self.text, style, pdf_rect, self.zoom, self.page_widget)
        try:
            self.page_widget.active_text_widgets.append(editor)
        except Exception:
            pass

        def on_commit(new_text, s, r):
            try:
                if editor in self.page_widget.active_text_widgets:
                    self.page_widget.active_text_widgets.remove(editor)
            except Exception:
                pass
            self.text = new_text
            self.fontsize = s.get("size", self.fontsize)
            self.fontname = s.get("fitz_font", self.fontname)
            self.color_rgb = s.get("color_rgb", self.color_rgb)
            self.lbl_content.setText(self.text)
            self._update_text_style()
            self.adjustSize()
            self._inline_editing = False

        def on_cancel():
            try:
                if editor in self.page_widget.active_text_widgets:
                    self.page_widget.active_text_widgets.remove(editor)
            except Exception:
                pass
            self._inline_editing = False

        editor.editing_finished.connect(on_commit)
        editor.editing_cancelled.connect(on_cancel)
        editor.show()
        editor.setFocus()

    def commit_to_pdf(self):
        """Bakes the text permanently into the underlying PDF page at current position."""
        if not self.text.strip():
            self.discard()
            return

        # Calculate exact text baseline point in PDF coordinates
        label_pos = self.lbl_content.mapTo(self.page_widget, QPoint(0, 0))
        pdf_x = label_pos.x() / self.zoom
        # In PDF coordinates, baseline is near bottom of text font
        pdf_y = (label_pos.y() / self.zoom) + (self.fontsize * 0.9)

        insert_pt = fitz.Point(pdf_x, pdf_y)
        self.page_widget.doc.insert_new_text(
            self.page_widget.page_idx,
            insert_pt,
            self.text,
            fontname=self.fontname,
            fontsize=self.fontsize,
            color=self.color_rgb
        )
        self.page_widget.render_cache()
        self.page_widget.update()
        self.page_widget.page_modified.emit()
        self.committed.emit()
        self.close()

    def discard(self):
        """Removes the draggable box without baking."""
        self.discarded.emit()
        self.close()
