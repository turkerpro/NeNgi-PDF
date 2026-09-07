"""
NeNgi PDF - OCR Suspect Correction Dialog ("Find First Suspect")
Presents zoomed page crops of recognized text words alongside editable inputs
so users can sequentially validate and correct OCR errors.
"""

from __future__ import annotations
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QWidget
)
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import Qt

import pymupdf as fitz
from nengi.core.pdf_document import PDFDocument


class OCRCorrectionDialog(QDialog):
    """Steps through OCR recognized words, showing cropped page image and editable text."""

    def __init__(self, doc: PDFDocument, current_page: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🔍 OCR Hata Düzeltme & Şüpheli Kelime İnceleme - NeNgi PDF")
        self.resize(520, 360)
        self.doc = doc
        self.current_page = current_page
        self.words: List[Tuple[float, float, float, float, str, int, int, int]] = []
        self.current_word_idx = 0
        self._init_ui()
        self._load_page_words()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel("OCR ile tanınan kelimeler taranıyor...")
        self.lbl_info.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        layout.addWidget(self.lbl_info)

        # Zoomed Crop Image Preview
        self.lbl_crop = QLabel("Görsel Yükleniyor...")
        self.lbl_crop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_crop.setStyleSheet("background-color: #202226; border: 1px solid #383C44; border-radius: 6px; min-height: 120px;")
        layout.addWidget(self.lbl_crop)

        # Word Text Input
        h_text = QHBoxLayout()
        h_text.addWidget(QLabel("Düzeltilmiş Kelime:"))
        self.txt_word = QLineEdit()
        self.txt_word.setFont(QFont("Segoe UI", 12))
        h_text.addWidget(self.txt_word)
        layout.addLayout(h_text)

        # Navigation Buttons
        btn_nav = QHBoxLayout()

        self.btn_prev = QPushButton("◀ Önceki Kelime")
        self.btn_prev.clicked.connect(self._prev_word)
        btn_nav.addWidget(self.btn_prev)

        self.btn_accept = QPushButton("✅ Kabul Et & İlerle")
        self.btn_accept.setObjectName("accentButton")
        self.btn_accept.clicked.connect(self._accept_and_next)
        btn_nav.addWidget(self.btn_accept)

        self.btn_next = QPushButton("Sonraki Kelime ▶")
        self.btn_next.clicked.connect(self._next_word)
        btn_nav.addWidget(self.btn_next)

        layout.addLayout(btn_nav)

        # Bottom
        btn_bot = QHBoxLayout()
        btn_bot.addStretch()

        btn_finish = QPushButton("Tamamla & Kapat")
        btn_finish.clicked.connect(self.accept)
        btn_bot.addWidget(btn_finish)

        layout.addLayout(btn_bot)

    def _load_page_words(self):
        if not self.doc or not self.doc.is_open:
            return

        self.words = self.doc.get_page_text_words(self.current_page)
        if not self.words:
            self.lbl_info.setText("Bu sayfada incelenecek metin kelimesi bulunamadı.")
            self.txt_word.setEnabled(False)
            self.btn_accept.setEnabled(False)
            return

        self.current_word_idx = 0
        self._display_current_word()

    def _display_current_word(self):
        if not (0 <= self.current_word_idx < len(self.words)):
            return

        w = self.words[self.current_word_idx]
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]

        self.lbl_info.setText(f"Sayfa {self.current_page+1} - Kelime {self.current_word_idx+1} / {len(self.words)}")
        self.txt_word.setText(text)
        self.txt_word.selectAll()
        self.txt_word.setFocus()

        # Render zoomed crop around word
        try:
            page = self.doc.get_page(self.current_page)
            # Add margin around rect
            margin = 15
            crop_rect = fitz.Rect(max(0, x0 - margin), max(0, y0 - margin), x1 + margin, y1 + margin)
            pix = page.get_pixmap(clip=crop_rect, dpi=200)

            img_fmt = QImage.Format.Format_RGB888 if pix.n < 4 else QImage.Format.Format_RGBA8888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, img_fmt)
            self.lbl_crop.setPixmap(QPixmap.fromImage(qimg).scaled(
                320, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        except Exception:
            self.lbl_crop.setText("(Kırpma önizlemesi oluşturulamadı)")

    def _accept_and_next(self):
        new_text = self.txt_word.text().strip()
        if not new_text:
            return

        w = self.words[self.current_word_idx]
        x0, y0, x1, y1, old_text = w[0], w[1], w[2], w[3], w[4]

        if new_text != old_text:
            # Replace text in document
            rect = fitz.Rect(x0, y0, x1, y1)
            self.doc.edit_text_at_rect(self.current_page, rect, new_text)

        self._next_word()

    def _next_word(self):
        if self.current_word_idx < len(self.words) - 1:
            self.current_word_idx += 1
            self._display_current_word()
        else:
            QMessageBox.information(self, "Tamamlandı", "Sayfadaki tüm kelimeler incelendi.")

    def _prev_word(self):
        if self.current_word_idx > 0:
            self.current_word_idx -= 1
            self._display_current_word()
