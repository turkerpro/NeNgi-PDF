"""
NeNgi PDF - Document Tools Side Panel
Collapsible right sidebar providing quick document utilities,
OCR processing, and an interactive command interface.
Completely vector SVG powered with no AI/Copilot branding.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QScrollArea, QFrame
)

from nengi.ui.icons import get_svg_icon


class CopilotPanel(QWidget):
    """NextGen right sidebar for document utilities and quick tools."""

    closed = pyqtSignal()
    action_triggered = pyqtSignal(str) # "summarize", "ocr", "diff", "merge", "protect"
    query_submitted = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setObjectName("copilotPanel")

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(12)

        # 1. Header: Document Tools title and close button
        header_layout = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_svg_icon("tools", "#0078D4", 20).pixmap(20, 20))
        header_layout.addWidget(lbl_icon)

        lbl_title = QLabel("Belge Araçları")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()

        btn_close = QPushButton()
        btn_close.setIcon(get_svg_icon("close", "#8C929C", 16))
        btn_close.setIconSize(QSize(16, 16))
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(
            "QPushButton { border: none; background: transparent; border-radius: 13px; }"
            "QPushButton:hover { background-color: #2D3036; }"
        )
        btn_close.clicked.connect(self.closed.emit)
        header_layout.addWidget(btn_close)

        layout.addLayout(header_layout)

        # 2. Suggested Section Header
        lbl_suggested = QLabel("HIZLI İŞLEMLER")
        lbl_suggested.setStyleSheet("font-size: 10.5px; font-weight: 600; color: #6E7681; letter-spacing: 0.8px;")
        layout.addWidget(lbl_suggested)

        # 3. Action Cards with SVG Icons
        self._add_action_card(layout, "documents", "Sayfadaki Metinleri Kopyala", "summarize")
        self._add_action_card(layout, "search", "Taranmış Metinleri Tanı (OCR)", "ocr")
        self._add_action_card(layout, "diff", "Açık Sekmelerle Karşılaştır (DIFF)", "diff")
        self._add_action_card(layout, "pages", "Birden Çok Dosyayı Birleştir", "merge")
        self._add_action_card(layout, "settings", "Belgeyi Parola ile Şifrele", "protect")

        # 4. Message & Activity Area (Scrollable)
        self.msg_area = QScrollArea()
        self.msg_area.setWidgetResizable(True)
        self.msg_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        msg_container = QWidget()
        self.msg_layout = QVBoxLayout(msg_container)
        self.msg_layout.setContentsMargins(0, 0, 0, 0)
        self.msg_layout.setSpacing(8)
        self.msg_layout.addStretch()

        self.msg_area.setWidget(msg_container)
        layout.addWidget(self.msg_area, 1)

        # 5. Bottom Interactive Input
        input_frame = QFrame()
        input_frame.setStyleSheet(
            "QFrame { background-color: #24272D; border: 1px solid #353942; border-radius: 20px; padding: 2px 6px; }"
        )
        input_lay = QHBoxLayout(input_frame)
        input_lay.setContentsMargins(8, 2, 4, 2)

        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Belge içinde arayın veya işlem yapın...")
        self.txt_query.setStyleSheet("QLineEdit { border: none; background: transparent; color: #FFFFFF; font-size: 12px; }")
        self.txt_query.returnPressed.connect(self._send_query)
        input_lay.addWidget(self.txt_query)

        btn_send = QPushButton()
        btn_send.setIcon(get_svg_icon("send", "#FFFFFF", 14))
        btn_send.setIconSize(QSize(14, 14))
        btn_send.setFixedSize(28, 28)
        btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send.setStyleSheet(
            "QPushButton { border: none; border-radius: 14px; background-color: #0078D4; }"
            "QPushButton:hover { background-color: #1084D9; }"
        )
        btn_send.clicked.connect(self._send_query)
        input_lay.addWidget(btn_send)

        layout.addWidget(input_frame)

    def _add_action_card(self, layout: QVBoxLayout, icon_name: str, title: str, action_key: str):
        btn = QPushButton(f"  {title}")
        btn.setObjectName("actionCard")
        btn.setIcon(get_svg_icon(icon_name, "#A0A5B0", 16))
        btn.setIconSize(QSize(16, 16))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton#actionCard {"
            "  text-align: left; padding: 10px 12px; border: 1px solid #2B2E33;"
            "  border-radius: 8px; background-color: #1E2023; color: #D0D4DC; font-size: 12px; font-weight: 500;"
            "}"
            "QPushButton#actionCard:hover {"
            "  background-color: #26292E; border-color: #0078D4; color: #FFFFFF;"
            "}"
        )
        btn.clicked.connect(lambda: self.action_triggered.emit(action_key))
        layout.addWidget(btn)

    def add_message(self, text: str, is_user: bool = False):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        if is_user:
            lbl.setStyleSheet(
                "background-color: #0078D4; color: #FFFFFF; border-radius: 12px; padding: 8px 12px; font-size: 12px;"
            )
            self.msg_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            lbl.setStyleSheet(
                "background-color: #1E2023; color: #E0E0E0; border: 1px solid #2B2E33; border-radius: 12px; padding: 8px 12px; font-size: 12px;"
            )
            self.msg_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)

    def _send_query(self):
        query = self.txt_query.text().strip()
        if query:
            self.add_message(query, is_user=True)
            self.txt_query.clear()
            self.query_submitted.emit(query)
