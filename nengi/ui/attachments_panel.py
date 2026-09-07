"""
NeNgi PDF - Embedded Attachments Sidebar Panel
Shows attached files in the PDF with options to view, add, extract, and delete.
"""

from __future__ import annotations
from typing import Optional
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from nengi.core.pdf_document import PDFDocument
from nengi.core.attachments import AttachmentManager
from nengi.ui.icons import get_svg_icon


class AttachmentsPanel(QWidget):
    """Collapsible panel for managing embedded files."""

    attachment_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None, is_dark: bool = True):
        super().__init__(parent)
        self.doc: Optional[PDFDocument] = None
        self.is_dark = is_dark
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Header
        h_head = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_svg_icon("documents", "#D0D4DC", 18).pixmap(18, 18))
        lbl_title = QLabel("📎 Ekli Dosyalar")
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        h_head.addWidget(lbl_icon)
        h_head.addWidget(lbl_title)
        h_head.addStretch()
        layout.addLayout(h_head)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._extract_selected)
        layout.addWidget(self.list_widget)

        # Buttons
        h_btns = QHBoxLayout()
        self.btn_add = QPushButton("➕ Ekle")
        self.btn_add.clicked.connect(self._add_file)
        h_btns.addWidget(self.btn_add)

        self.btn_extract = QPushButton("💾 Çıkart")
        self.btn_extract.clicked.connect(self._extract_selected)
        h_btns.addWidget(self.btn_extract)

        self.btn_del = QPushButton("🗑️ Sil")
        self.btn_del.clicked.connect(self._delete_selected)
        h_btns.addWidget(self.btn_del)

        layout.addLayout(h_btns)

    def load_document(self, doc: PDFDocument):
        self.doc = doc
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        if not self.doc or not self.doc.is_open:
            return

        att_list = AttachmentManager.get_attachments(self.doc)
        for att in att_list:
            name = att["name"]
            size_kb = att["size"] / 1024.0
            size_str = f"{size_kb:.1f} KB" if size_kb >= 1 else f"{att['size']} B"
            item = QListWidgetItem(f"📄 {name} ({size_str})")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)

    def _add_file(self):
        if not self.doc or not self.doc.is_open:
            return

        path, _ = QFileDialog.getOpenFileName(self, "Belgeye Eklenecek Dosyayı Seç", "", "Tüm Dosyalar (*.*)")
        if path:
            if AttachmentManager.add_attachment(self.doc, path):
                self.refresh_list()
                self.attachment_changed.emit()

    def _extract_selected(self):
        item = self.list_widget.currentItem()
        if not item or not self.doc:
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        out_path, _ = QFileDialog.getSaveFileName(self, "Eki Farklı Kaydet", name, "Tüm Dosyalar (*.*)")
        if out_path:
            if AttachmentManager.extract_attachment(self.doc, name, out_path):
                QMessageBox.information(self, "Başarılı", f"Dosya kaydedildi:\n{os.path.basename(out_path)}")

    def _delete_selected(self):
        item = self.list_widget.currentItem()
        if not item or not self.doc:
            return

        name = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Onay", f"'{name}' ekli dosyası belgeden silinsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if AttachmentManager.delete_attachment(self.doc, name):
                self.refresh_list()
                self.attachment_changed.emit()

    def update_theme(self, is_dark: bool):
        self.is_dark = is_dark
        bg = "#17181A" if is_dark else "#FFFFFF"
        text = "#D0D4DC" if is_dark else "#0F172A"
        border = "#26292E" if is_dark else "#E2E8F0"
        self.setStyleSheet(f"""
            QWidget {{ background-color: {bg}; color: {text}; }}
            QListWidget {{
                background-color: {'#202226' if is_dark else '#F8FAFC'};
                border: 1px solid {border};
                border-radius: 4px;
            }}
        """)
