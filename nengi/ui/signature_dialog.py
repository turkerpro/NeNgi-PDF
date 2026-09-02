"""
NeNgi PDF - Digital Signature Creation & Placement Dialog
Allows users to either draw their signature on a smooth canvas or
upload a signature image file (PNG/JPG) with background transparency.
"""

from __future__ import annotations
import os
import tempfile
from typing import Optional
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QPushButton, QLabel, QFileDialog, QMessageBox, QSlider
)
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PIL import Image


class DrawingCanvas(QWidget):
    """Canvas for drawing signature with smooth mouse/stylus strokes."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(450, 180)
        self.setStyleSheet("background-color: #FFFFFF; border: 2px dashed #0078D4; border-radius: 8px;")
        self.image = QImage(self.size(), QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.transparent)
        self._last_point: Optional[QPoint] = None
        self.pen_width = 3

    def clear(self):
        self.image.fill(Qt.GlobalColor.transparent)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._last_point = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self._last_point:
            painter = QPainter(self.image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(QColor(10, 30, 80), self.pen_width, Qt.PenStyle.SolidLine, 
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self._last_point, event.pos())
            self._last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self._last_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)


class SignatureDialog(QDialog):
    """Dialog to draw or upload signature and prepare it for stamping."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("İmza Ekle - NeNgi PDF")
        self.setFixedSize(500, 320)
        self.saved_signature_path: Optional[str] = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Tab 1: Draw Signature
        tab_draw = QWidget()
        lay_draw = QVBoxLayout(tab_draw)
        lay_draw.addWidget(QLabel("Mouse veya kaleminizle imzanızı çizin:"))
        self.canvas = DrawingCanvas()
        lay_draw.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_clear = QPushButton("İmzayı Temizle")
        btn_clear.clicked.connect(self.canvas.clear)
        lay_draw.addWidget(btn_clear, alignment=Qt.AlignmentFlag.AlignRight)
        tabs.addTab(tab_draw, "✍️ İmza Çiz")

        # Tab 2: Upload Image
        tab_upload = QWidget()
        lay_upload = QVBoxLayout(tab_upload)
        lay_upload.addWidget(QLabel("Bilgisayarınızdan imza resmi (PNG/JPG) seçin:"))
        
        btn_browse = QPushButton("📁 İmza Resmi Seç...")
        btn_browse.clicked.connect(self._browse_signature_file)
        lay_upload.addWidget(btn_browse)

        self.lbl_preview = QLabel("Önizleme Yok")
        self.lbl_preview.setFixedSize(300, 100)
        self.lbl_preview.setStyleSheet("border: 1px solid #444; background: #222; text-align: center;")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_upload.addWidget(self.lbl_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        tabs.addTab(tab_upload, "🖼️ Resimden Yükle")

        layout.addWidget(tabs)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_cancel)

        btn_confirm = QPushButton("İmzayı Kullan ve Belgeye Ekle")
        btn_confirm.setObjectName("accentButton")
        btn_confirm.clicked.connect(self._on_confirm)
        bottom_layout.addWidget(btn_confirm)

        layout.addLayout(bottom_layout)

    def _browse_signature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "İmza Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_path:
            self.saved_signature_path = file_path
            pix = QPixmap(file_path).scaled(280, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_preview.setPixmap(pix)

    def _on_confirm(self):
        # If drawn signature
        if not self.saved_signature_path:
            temp_file = os.path.join(tempfile.gettempdir(), "nengi_drawn_signature.png")
            self.canvas.image.save(temp_file, "PNG")
            self.saved_signature_path = temp_file

        self.accept()
