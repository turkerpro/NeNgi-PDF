"""
NeNgi PDF - Thumbnail Sidebar Widget
Displays page previews on the left panel, with direct navigation,
page rotation, deletion, and reordering.
"""

from __future__ import annotations
from typing import Optional, List
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QMenu, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap
from nengi.core.pdf_document import PDFDocument


class ThumbnailBar(QWidget):
    """Left sidebar showing clickable thumbnail previews of all pages."""

    page_selected = pyqtSignal(int)
    pages_modified = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc: Optional[PDFDocument] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("📑 Sayfa Önizlemeleri")
        title.setStyleSheet("font-weight: bold; color: #A0A0A0; padding: 4px;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.setSpacing(6)
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)

    def load_thumbnails(self, doc: PDFDocument):
        """Generates thumbnails for all pages of doc."""
        self.doc = doc
        self.list_widget.clear()

        if not self.doc or not self.doc.is_open:
            return

        for i in range(self.doc.page_count):
            pix = self.doc.render_page_pixmap(i, zoom=0.25)
            item = QListWidgetItem(f"Sayfa {i + 1}")
            item.setIcon(QIcon(pix))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_widget.addItem(item)

        if self.doc.page_count > 0:
            self.list_widget.setCurrentRow(0)

    def select_page(self, page_idx: int):
        """Highlights the active page in the sidebar without re-triggering signal."""
        if 0 <= page_idx < self.list_widget.count():
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentRow(page_idx)
            self.list_widget.blockSignals(False)

    def _on_row_changed(self, row: int):
        if row >= 0:
            self.page_selected.emit(row)

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item or not self.doc:
            return

        page_idx = self.list_widget.row(item)
        menu = QMenu(self)

        act_rot = menu.addAction("🔄 90° Sağa Döndür")
        act_del = menu.addAction("🗑️ Bu Sayfayı Sil")

        action = menu.exec(self.list_widget.mapToGlobal(pos))
        if action == act_rot:
            self.doc.rotate_page(page_idx, 90)
            self.load_thumbnails(self.doc)
            self.pages_modified.emit()
        elif action == act_del:
            if self.doc.page_count > 1:
                self.doc.delete_page(page_idx)
                self.load_thumbnails(self.doc)
                self.pages_modified.emit()
            else:
                QMessageBox.warning(self, "Uyarı", "Son kalan sayfa silinemez.")
