"""
NeNgi PDF - Visual Page Organizer Dialog
Manage pages visually: rotate, delete, move up/down, insert blank page,
and merge external PDF pages.
"""

from __future__ import annotations
from typing import Optional, List
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap
from nengi.core.pdf_document import PDFDocument
from nengi.core.page_manager import PageManager


class PageManagerDialog(QDialog):
    """Visual dialog to manage, reorder, rotate, and delete pages."""

    def __init__(self, doc: PDFDocument, parent: Optional[QDialog] = None):
        super().__init__(parent)
        self.doc = doc
        self.setWindowTitle("Sayfaları Yönet ve Düzenle - NeNgi PDF")
        self.resize(750, 520)
        self._init_ui()
        self._refresh_list()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left: Thumbnails Grid
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Belgedeki Sayfalar:"))

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(QSize(130, 170))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(12)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.list_widget)
        main_layout.addLayout(left_layout, stretch=4)

        # Right: Actions Panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        right_panel.addWidget(QLabel("⚙️ Sayfa İşlemleri:"))

        btn_rot_cw = QPushButton("🔄 90° Sağa Döndür")
        btn_rot_cw.clicked.connect(lambda: self._rotate_selected(90))
        right_panel.addWidget(btn_rot_cw)

        btn_rot_ccw = QPushButton("↺ 90° Sola Döndür")
        btn_rot_ccw.clicked.connect(lambda: self._rotate_selected(-90))
        right_panel.addWidget(btn_rot_ccw)

        btn_move_up = QPushButton("▲ Sayfayı Başa / Yukarı Taşı")
        btn_move_up.clicked.connect(self._move_up)
        right_panel.addWidget(btn_move_up)

        btn_move_down = QPushButton("▼ Sayfayı Sona / Aşağı Taşı")
        btn_move_down.clicked.connect(self._move_down)
        right_panel.addWidget(btn_move_down)

        right_panel.addSpacing(15)

        btn_add_blank = QPushButton("➕ Boş Sayfa Ekle")
        btn_add_blank.clicked.connect(self._add_blank)
        right_panel.addWidget(btn_add_blank)

        btn_add_pdf = QPushButton("📑 Başka PDF'ten Sayfa Ekle...")
        btn_add_pdf.clicked.connect(self._insert_external_pdf)
        right_panel.addWidget(btn_add_pdf)

        right_panel.addSpacing(15)

        btn_delete = QPushButton("🗑️ Seçili Sayfaları Sil")
        btn_delete.setObjectName("dangerButton")
        btn_delete.clicked.connect(self._delete_selected)
        right_panel.addWidget(btn_delete)

        right_panel.addStretch()

        btn_done = QPushButton("Kapat ve Uygula")
        btn_done.setObjectName("accentButton")
        btn_done.clicked.connect(self.accept)
        right_panel.addWidget(btn_done)

        main_layout.addLayout(right_panel, stretch=1)

    def _refresh_list(self):
        self.list_widget.clear()
        if not self.doc or not self.doc.is_open:
            return

        for i in range(self.doc.page_count):
            pix = self.doc.render_page_pixmap(i, zoom=0.25)
            item = QListWidgetItem(f"Sayfa {i + 1}")
            item.setIcon(QIcon(pix))
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.list_widget.addItem(item)

    def _get_selected_indices(self) -> List[int]:
        return [item.data(Qt.ItemDataRole.UserRole) for item in self.list_widget.selectedItems()]

    def _rotate_selected(self, angle: int):
        indices = self._get_selected_indices()
        if not indices:
            QMessageBox.information(self, "Bilgi", "Lütfen döndürmek istediğiniz sayfaları seçin.")
            return
        PageManager.rotate_pages(self.doc, indices, angle)
        self._refresh_list()

    def _delete_selected(self):
        indices = self._get_selected_indices()
        if not indices:
            QMessageBox.information(self, "Bilgi", "Lütfen silmek istediğiniz sayfaları seçin.")
            return

        if self.doc.page_count - len(indices) < 1:
            QMessageBox.warning(self, "Uyarı", "Belgedeki tüm sayfaları silemezsiniz. En az 1 sayfa kalmalıdır.")
            return

        reply = QMessageBox.question(
            self, "Onay", f"{len(indices)} sayfa silinecek. Emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            PageManager.delete_pages(self.doc, indices)
            self._refresh_list()

    def _move_up(self):
        indices = self._get_selected_indices()
        if not indices or indices[0] <= 0:
            return
        idx = indices[0]
        PageManager.move_page(self.doc, idx, idx - 1)
        self._refresh_list()
        self.list_widget.setCurrentRow(idx - 1)

    def _move_down(self):
        indices = self._get_selected_indices()
        if not indices or indices[0] >= self.doc.page_count - 1:
            return
        idx = indices[0]
        PageManager.move_page(self.doc, idx, idx + 1)
        self._refresh_list()
        self.list_widget.setCurrentRow(idx + 1)

    def _add_blank(self):
        PageManager.insert_blank_page(self.doc)
        self._refresh_list()

    def _insert_external_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Eklenecek PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
        if file_path:
            self.doc.insert_file(file_path)
            self._refresh_list()
