"""
NeNgi PDF - Studio Style Text & Paragraph Editor Dialog
Provides font detection badges, family/size/style selectors, color picker,
and multi-line editing for paragraphs or new text insertion.
"""

from __future__ import annotations
from typing import Optional, Tuple, Dict, Any
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QPlainTextEdit, QComboBox, QDoubleSpinBox, QColorDialog, QFrame
)


class TextEditorDialog(QDialog):
    """
    Rich text editor dialog for NeNgi PDF Studio.
    Displays detected original font styles and allows editing or adding text.
    """

    def __init__(
        self, 
        initial_text: str = "", 
        detected_style: Optional[Dict[str, Any]] = None,
        title: str = "✏️ Metni / Paragrafı Düzenle",
        parent: Optional[QDialog] = None
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 360)

        self.detected_style = detected_style or {
            "family": "Arial",
            "size": 11.0,
            "is_bold": False,
            "is_italic": False,
            "color_rgb": (0.0, 0.0, 0.0),
            "raw_font": "Helvetica",
            "fitz_font": "helv"
        }

        # Initialize state with detected style
        self.current_family = self.detected_style.get("family", "Arial")
        self.current_size = float(self.detected_style.get("size", 11.0))
        self.is_bold = bool(self.detected_style.get("is_bold", False))
        self.is_italic = bool(self.detected_style.get("is_italic", False))
        
        cr, cg, cb = self.detected_style.get("color_rgb", (0.0, 0.0, 0.0))
        self.current_color = QColor(int(cr * 255), int(cg * 255), int(cb * 255))
        self.initial_text = initial_text

        # Results
        self.result_text = initial_text
        self.result_fitz_font = "helv"
        self.result_fontsize = self.current_size
        self.result_color_rgb = (0.0, 0.0, 0.0)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 1. Detected Font Badge (Studio style)
        badge_frame = QFrame()
        badge_frame.setStyleSheet("background-color: #24272D; border: 1px solid #353942; border-radius: 6px; padding: 6px 10px;")
        badge_lay = QHBoxLayout(badge_frame)
        badge_lay.setContentsMargins(4, 2, 4, 2)

        raw_f = self.detected_style.get("raw_font", "Standart")
        bold_lbl = "Kalın, " if self.is_bold else ""
        ital_lbl = "İtalik, " if self.is_italic else ""
        badge_text = f"🔍 <b>Algılanan Yazı Tipi:</b> {self.current_family} ({raw_f}) • {bold_lbl}{ital_lbl}{self.current_size:.1f} pt"
        lbl_badge = QLabel(badge_text)
        lbl_badge.setStyleSheet("color: #0078D4; font-size: 11.5px;")
        badge_lay.addWidget(lbl_badge)
        layout.addWidget(badge_frame)

        # 2. Typography Toolstrip (Family, Size, Bold, Italic, Color)
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(6)

        # Font Family Combo
        lbl_f = QLabel("Font:")
        lbl_f.setStyleSheet("font-weight: 500;")
        tools_layout.addWidget(lbl_f)

        self.cb_family = QComboBox()
        self.cb_family.addItems(["Arial", "Calibri", "Times New Roman", "Courier New", "Segoe UI", "Helvetica"])
        # Select matching or fallback
        idx = self.cb_family.findText(self.current_family, Qt.MatchFlag.MatchContains)
        if idx >= 0:
            self.cb_family.setCurrentIndex(idx)
        tools_layout.addWidget(self.cb_family)

        # Font Size SpinBox
        lbl_s = QLabel("Punto:")
        lbl_s.setStyleSheet("font-weight: 500;")
        tools_layout.addWidget(lbl_s)

        self.sp_size = QDoubleSpinBox()
        self.sp_size.setRange(4.0, 120.0)
        self.sp_size.setSingleStep(0.5)
        self.sp_size.setValue(self.current_size)
        tools_layout.addWidget(self.sp_size)

        # Bold Toggle Button
        self.btn_bold = QPushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setChecked(self.is_bold)
        self.btn_bold.setFixedWidth(28)
        self.btn_bold.setStyleSheet("font-weight: bold; font-size: 13px;")
        tools_layout.addWidget(self.btn_bold)

        # Italic Toggle Button
        self.btn_italic = QPushButton("I")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setChecked(self.is_italic)
        self.btn_italic.setFixedWidth(28)
        self.btn_italic.setStyleSheet("font-style: italic; font-size: 13px;")
        tools_layout.addWidget(self.btn_italic)

        # Color Picker Button
        self.btn_color = QPushButton()
        self.btn_color.setFixedWidth(32)
        self._update_color_button()
        self.btn_color.clicked.connect(self._choose_color)
        tools_layout.addWidget(self.btn_color)

        tools_layout.addStretch()
        layout.addLayout(tools_layout)

        # 3. Multi-line Text Editor
        self.txt_editor = QPlainTextEdit()
        self.txt_editor.setPlainText(self.initial_text)
        self.txt_editor.setPlaceholderText("Metni veya paragrafı buraya yazın...")
        self.txt_editor.setStyleSheet(
            "QPlainTextEdit { background-color: #1A1C20; border: 1px solid #33373E; border-radius: 6px; padding: 8px; color: #FFFFFF; font-size: 13px; }"
        )
        layout.addWidget(self.txt_editor)

        # 4. Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_apply = QPushButton("💾 Uygula")
        btn_apply.setObjectName("accentButton")
        btn_apply.setStyleSheet("background-color: #0078D4; color: white; font-weight: bold; padding: 7px 18px;")
        btn_apply.clicked.connect(self._apply_and_accept)
        btn_layout.addWidget(btn_apply)

        layout.addLayout(btn_layout)

    def _update_color_button(self):
        c_name = self.current_color.name()
        self.btn_color.setStyleSheet(
            f"background-color: {c_name}; border: 2px solid #555555; border-radius: 4px;"
        )

    def _choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Metin Rengini Seçin")
        if color.isValid():
            self.current_color = color
            self._update_color_button()

    def _apply_and_accept(self):
        self.result_text = self.txt_editor.toPlainText()
        self.result_fontsize = self.sp_size.value()
        self.result_color_rgb = (
            self.current_color.redF(),
            self.current_color.greenF(),
            self.current_color.blueF()
        )

        fam = self.cb_family.currentText()
        is_b = self.btn_bold.isChecked()
        is_i = self.btn_italic.isChecked()

        # Map to PyMuPDF font name
        if "times" in fam.lower():
            fitz_base = "times"
            fitz_font = "tibi" if is_b and is_i else ("tibo" if is_b else ("tiit" if is_i else "tiro"))
        elif "courier" in fam.lower():
            fitz_base = "couri"
            fitz_font = "cobi" if is_b and is_i else ("cobo" if is_b else ("coit" if is_i else "couri"))
        else:
            fitz_base = "helv"
            fitz_font = "hebi" if is_b and is_i else ("hebo" if is_b else ("heit" if is_i else "helv"))

        self.result_fitz_font = fitz_font
        self.accept()
