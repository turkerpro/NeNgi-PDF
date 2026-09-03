"""
NeNgi PDF - Multi-File Merge Wizard Dialog
Merges multiple PDF and image files into a single consolidated PDF document.
"""

from __future__ import annotations
import os
from typing import List, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QFrame
)
import pymupdf as fitz
from nengi.core.converter import FormatConverter


class MergeFilesDialog(QDialog):
    """Modern dialog allowing user to reorder and merge multiple files into one PDF."""

    def __init__(self, initial_files: Optional[List[str]] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("📑 NeNgi PDF - Dosyaları Birleştir")
        self.resize(600, 450)
        self.files: List[str] = [os.path.abspath(f) for f in (initial_files or []) if os.path.exists(f)]
        self.output_pdf_path: Optional[str] = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Header banner
        lbl_info = QLabel("Birleştirmek istediğiniz dosyaların sırasını aşağıdan düzenleyin:")
        lbl_info.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")
        layout.addWidget(lbl_info)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { background-color: #1E1E1E; border: 1px solid #3A3A3A; border-radius: 4px; padding: 4px; }"
            "QListWidget::item { padding: 6px 10px; border-bottom: 1px solid #2A2A2A; color: #E0E0E0; }"
            "QListWidget::item:selected { background-color: #0078D4; color: #FFFFFF; }"
        )
        self._refresh_list()
        layout.addWidget(self.list_widget)

        # Reordering and management buttons
        btn_layout = QHBoxLayout()
        
        btn_add = QPushButton("➕ Dosya Ekle")
        btn_add.clicked.connect(self._add_files)
        btn_layout.addWidget(btn_add)

        btn_remove = QPushButton("➖ Seçileni Kaldır")
        btn_remove.clicked.connect(self._remove_selected)
        btn_layout.addWidget(btn_remove)

        btn_up = QPushButton("⬆️ Yukarı Taşı")
        btn_up.clicked.connect(self._move_up)
        btn_layout.addWidget(btn_up)

        btn_down = QPushButton("⬇️ Aşağı Taşı")
        btn_down.clicked.connect(self._move_down)
        btn_layout.addWidget(btn_down)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Bottom action buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_cancel)

        btn_merge = QPushButton("🚀 Tek PDF Olarak Birleştir")
        btn_merge.setObjectName("accentButton")
        btn_merge.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 8px 16px;")
        btn_merge.clicked.connect(self._perform_merge)
        bottom_layout.addWidget(btn_merge)

        layout.addLayout(bottom_layout)

    def _refresh_list(self):
        self.list_widget.clear()
        for idx, f in enumerate(self.files):
            basename = os.path.basename(f)
            ext = os.path.splitext(f)[1].upper()
            size_kb = os.path.getsize(f) / 1024 if os.path.exists(f) else 0
            item_text = f"{idx + 1}.  {basename}  ({ext}, {size_kb:.1f} KB)"
            item = QListWidgetItem(item_text)
            self.list_widget.addItem(item)

    def _add_files(self):
        try:
            selected, _ = QFileDialog.getOpenFileNames(
                self, "Birleştirilecek Dosyaları Seç", "", 
                "Desteklenen Dosyalar (*.pdf *.png *.jpg *.jpeg *.bmp *.tiff);;PDF Dosyaları (*.pdf);;Resim Dosyaları (*.png *.jpg *.jpeg)"
            )
            if selected:
                for f in selected:
                    if f and os.path.exists(f) and f not in self.files:
                        self.files.append(os.path.abspath(f))
                self._refresh_list()
        except Exception as e:
            print(f"Error adding files: {e}")

    def _remove_selected(self):
        current_row = self.list_widget.currentRow()
        if 0 <= current_row < len(self.files):
            del self.files[current_row]
            self._refresh_list()

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.files[row - 1], self.files[row] = self.files[row], self.files[row - 1]
            self._refresh_list()
            self.list_widget.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.files) - 1:
            self.files[row + 1], self.files[row] = self.files[row], self.files[row + 1]
            self._refresh_list()
            self.list_widget.setCurrentRow(row + 1)

    def _perform_merge(self):
        if not self.files:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir dosya ekleyin.")
            return

        try:
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Birleştirilen PDF'i Kaydet", "Birlesik_Belge.pdf", "PDF Dosyaları (*.pdf)"
            )
            if not save_path:
                return

            merged_doc = fitz.open()
            failed_files = []

            for file_path in self.files:
                if not os.path.exists(file_path):
                    failed_files.append(f"{os.path.basename(file_path)} (Dosya bulunamadı)")
                    continue

                try:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext == ".pdf":
                        src = fitz.open(file_path)
                        if src.is_encrypted and not src.authenticate(""):
                            failed_files.append(f"{os.path.basename(file_path)} (Parola korumalı)")
                            src.close()
                            continue
                        merged_doc.insert_pdf(src)
                        src.close()
                    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
                        img = fitz.open(file_path)
                        pdf_bytes = img.convert_to_pdf()
                        img_pdf = fitz.open("pdf", pdf_bytes)
                        merged_doc.insert_pdf(img_pdf)
                        img.close()
                        img_pdf.close()
                    else:
                        failed_files.append(f"{os.path.basename(file_path)} (Desteklenmeyen biçim)")
                except Exception as ex:
                    failed_files.append(f"{os.path.basename(file_path)} ({ex})")

            if merged_doc.page_count == 0:
                merged_doc.close()
                QMessageBox.critical(self, "Hata", "Hiçbir dosya birleştirilemedi.\n\nHatalar:\n" + "\n".join(failed_files))
                return

            merged_doc.save(save_path)
            merged_doc.close()
            self.output_pdf_path = save_path

            msg = f"Dosyalar başarıyla birleştirildi:\n{save_path}"
            if failed_files:
                msg += f"\n\nAtlanan dosyalar:\n" + "\n".join(failed_files)
            QMessageBox.information(self, "Başarılı", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosyalar birleştirilirken beklenmedik bir hata oluştu:\n{e}")
