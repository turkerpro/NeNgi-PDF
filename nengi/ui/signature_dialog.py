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
    QPushButton, QLabel, QFileDialog, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QPixmap
from PIL import Image


def make_image_background_transparent(img_path: str) -> str:
    """Removes white/paper background from signature scan/image and saves as transparent PNG."""
    try:
        img = Image.open(img_path).convert("RGBA")
        pixels = img.load()
        width, height = img.size
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                # If pixel is near-white or light paper background
                if r > 215 and g > 215 and b > 215:
                    pixels[x, y] = (255, 255, 255, 0)
        
        out_path = os.path.join(tempfile.gettempdir(), f"nengi_sig_trans_{os.path.basename(img_path)}.png")
        img.save(out_path, "PNG")
        return out_path
    except Exception as e:
        print(f"Error making background transparent: {e}")
        return img_path


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
        self.setFixedSize(520, 360)
        self.saved_signature_path: Optional[str] = None
        self._raw_uploaded_path: Optional[str] = None
        self._init_ui()

    @property
    def signature_path(self) -> Optional[str]:
        """Provides direct compatibility with caller."""
        return self.saved_signature_path

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # Tab 1: Draw Signature
        tab_draw = QWidget()
        lay_draw = QVBoxLayout(tab_draw)
        lay_draw.addWidget(QLabel("Mouse veya kaleminizle imzanızı çizin:"))
        self.canvas = DrawingCanvas()
        lay_draw.addWidget(self.canvas, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_clear = QPushButton("İmzayı Temizle")
        btn_clear.clicked.connect(self.canvas.clear)
        lay_draw.addWidget(btn_clear, alignment=Qt.AlignmentFlag.AlignRight)
        self.tabs.addTab(tab_draw, "✍️ İmza Çiz")

        # Tab 2: Upload Image
        tab_upload = QWidget()
        lay_upload = QVBoxLayout(tab_upload)
        lay_upload.addWidget(QLabel("Bilgisayarınızdan imza resmi (PNG/JPG) seçin:"))
        
        btn_browse = QPushButton("📁 İmza Resmi Seç...")
        btn_browse.clicked.connect(self._browse_signature_file)
        lay_upload.addWidget(btn_browse)

        self.lbl_preview = QLabel("Önizleme Yok")
        self.lbl_preview.setFixedSize(320, 95)
        self.lbl_preview.setStyleSheet("border: 1px dashed #666; background: #222; text-align: center; color: #888; border-radius: 4px;")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_upload.addWidget(self.lbl_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        self.chk_remove_bg = QCheckBox("Beyaz kağıt arka planını otomatik şeffaflaştır (Önerilen)")
        self.chk_remove_bg.setChecked(True)
        self.chk_remove_bg.stateChanged.connect(self._on_transparency_toggled)
        lay_upload.addWidget(self.chk_remove_bg)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size: 11px;")
        lay_upload.addWidget(self.lbl_status)

        self.tabs.addTab(tab_upload, "🖼️ Resimden Yükle")

        layout.addWidget(self.tabs)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        bottom_layout.addWidget(btn_cancel)

        bottom_layout.addStretch()

        btn_confirm = QPushButton("İmzayı Kullan ve Belgeye Ekle")
        btn_confirm.setObjectName("accentButton")
        btn_confirm.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        btn_confirm.clicked.connect(self._on_confirm)
        bottom_layout.addWidget(btn_confirm)

        layout.addLayout(bottom_layout)

    def _browse_signature_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "İmza Resmi Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path and os.path.exists(file_path):
            self._raw_uploaded_path = file_path
            self._update_preview()

    def _on_transparency_toggled(self):
        if self._raw_uploaded_path:
            self._update_preview()

    def _update_preview(self):
        if not self._raw_uploaded_path or not os.path.exists(self._raw_uploaded_path):
            return

        try:
            target_path = self._raw_uploaded_path
            if self.chk_remove_bg.isChecked():
                target_path = make_image_background_transparent(self._raw_uploaded_path)

            self.saved_signature_path = target_path
            pix = QPixmap(target_path)
            if not pix.isNull():
                scaled_pix = pix.scaled(
                    300, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_preview.setPixmap(scaled_pix)
                self.lbl_status.setText(f"✓ Hazır: {os.path.basename(self._raw_uploaded_path)}")
                self.lbl_status.setStyleSheet("color: #107C41; font-weight: bold; font-size: 11px;")
            else:
                self.lbl_status.setText("Resim yüklenemedi!")
                self.lbl_status.setStyleSheet("color: #D83B01; font-weight: bold; font-size: 11px;")
        except Exception as e:
            print(f"Error updating signature preview: {e}")

    def _on_confirm(self):
        # If active tab is drawing (tab 0)
        if self.tabs.currentIndex() == 0:
            temp_file = os.path.join(tempfile.gettempdir(), "nengi_drawn_signature.png")
            self.canvas.image.save(temp_file, "PNG")
            self.saved_signature_path = temp_file
        else:
            # If upload tab (tab 1)
            if not self.saved_signature_path or not os.path.exists(self.saved_signature_path):
                QMessageBox.warning(self, "Uyarı", "Lütfen önce bir imza resmi seçin.")
                return

        self.accept()
