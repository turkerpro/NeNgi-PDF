"""
NeNgi PDF - Document Tools Side Panel
Collapsible right sidebar providing quick document utilities,
OCR processing, and an interactive command interface.
Completely vector SVG powered with no AI/Copilot branding.
"""

from __future__ import annotations
from typing import List, Tuple
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame
)

from nengi.ui.icons import get_svg_icon
from nengi.ui.styles import get_dark_tokens, get_light_tokens


def _get_tokens(is_dark: bool = True):
    """Returns design tokens for current theme."""
    return get_dark_tokens() if is_dark else get_light_tokens()


class CopilotPanel(QWidget):
    """NextGen right sidebar for document utilities and quick tools."""

    closed = pyqtSignal()
    action_triggered = pyqtSignal(str)
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

        tokens = _get_tokens(True)
        self.is_dark = True
        self._action_buttons: List[Tuple[QPushButton, str]] = []

        # 1. Header: Document Tools title and close button
        header_layout = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setPixmap(get_svg_icon("tools", tokens.colors.text_accent, 20).pixmap(20, 20))
        header_layout.addWidget(lbl_icon)

        self.lbl_title = QLabel("Belge Araçları")
        self.lbl_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {tokens.colors.text_primary};")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()

        self.btn_close = QPushButton()
        self.btn_close.setIcon(get_svg_icon("close", tokens.colors.text_tertiary, 16))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.setFixedSize(26, 26)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(
            f"QPushButton {{ border: none; background: transparent; border-radius: 13px; }}"
            f"QPushButton:hover {{ background-color: {tokens.colors.bg_hover}; }}"
        )
        self.btn_close.clicked.connect(self.closed.emit)
        header_layout.addWidget(self.btn_close)

        layout.addLayout(header_layout)

        # 2. Action Cards - Only: Search, Recent, Contextual Suggestions
        self._add_action_card(layout, "search", "Arama", "search")
        self._add_action_card(layout, "recent", "Son Kullanılanlar", "recent")
        self._add_action_card(layout, "suggest", "Bağlamsal Öneri", "suggest")

        # 3. Message & Activity Area (Scrollable)
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

        # 4. Bottom Interactive Input
        self.input_frame = QFrame()
        tokens = _get_tokens(True)
        self.input_frame.setStyleSheet(
            f"QFrame {{ background-color: {tokens.colors.bg_tertiary}; border: 1px solid {tokens.colors.border_default}; border-radius: 20px; padding: 2px 6px; }}"
        )
        input_lay = QHBoxLayout(self.input_frame)
        input_lay.setContentsMargins(8, 2, 4, 2)

        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Belge içinde arayın veya işlem yapın...")
        self.txt_query.setStyleSheet(f"QLineEdit {{ border: none; background: transparent; color: {tokens.colors.text_primary}; font-size: 12px; }}")
        self.txt_query.returnPressed.connect(self._send_query)
        input_lay.addWidget(self.txt_query)

        btn_send = QPushButton()
        btn_send.setIcon(get_svg_icon("send", tokens.colors.text_inverse, 14))
        btn_send.setIconSize(QSize(14, 14))
        btn_send.setFixedSize(28, 28)
        btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_send.setStyleSheet(
            f"QPushButton {{ border: none; border-radius: 14px; background-color: {tokens.colors.accent_primary}; }}"
            f"QPushButton:hover {{ background-color: {tokens.colors.accent_hover}; }}"
        )
        btn_send.clicked.connect(self._send_query)
        input_lay.addWidget(btn_send)

        layout.addWidget(self.input_frame)

    def _add_action_card(self, layout: QVBoxLayout, icon_name: str, title: str, action_key: str):
        btn = QPushButton(f"  {title}")
        btn.setObjectName("actionCard")
        tokens = _get_tokens(True)
        icon_color = tokens.colors.text_tertiary
        btn.setIcon(get_svg_icon(icon_name, icon_color, 16))
        btn.setIconSize(QSize(16, 16))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"QPushButton#actionCard {{"
            f"  text-align: left; padding: 10px 12px; border: 1px solid {tokens.colors.border_strong};"
            f"  border-radius: {tokens.radius.lg}px; background-color: {tokens.colors.bg_tertiary}; color: {tokens.colors.text_primary}; font-size: 12px; font-weight: 500;"
            f"}}"
            f"QPushButton#actionCard:hover {{"
            f"  background-color: {tokens.colors.bg_hover}; border-color: {tokens.colors.accent_primary}; color: {tokens.colors.text_inverse};"
            f"}}"
        )
        btn.clicked.connect(lambda: self.action_triggered.emit(action_key))
        self._action_buttons.append((btn, icon_name))
        layout.addWidget(btn)

    def update_theme(self, is_dark: bool):
        """Updates icons, borders, and backgrounds dynamically when theme changes."""
        self.is_dark = is_dark
        tokens = _get_tokens(is_dark)
        title_color = tokens.colors.text_primary
        if hasattr(self, "lbl_title"):
            self.lbl_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {title_color};")
        if hasattr(self, "btn_close"):
            self.btn_close.setIcon(get_svg_icon("close", tokens.colors.text_tertiary, 16))

        card_bg = tokens.colors.bg_tertiary
        card_border = tokens.colors.border_strong
        card_text = tokens.colors.text_primary
        card_hover_bg = tokens.colors.bg_hover
        icon_color = tokens.colors.text_tertiary

        for btn, icon_name in self._action_buttons:
            btn.setIcon(get_svg_icon(icon_name, icon_color, 16))
            btn.setStyleSheet(
                f"QPushButton#actionCard {{"
                f"  text-align: left; padding: 10px 12px; border: 1px solid {tokens.colors.border_strong};"
                f"  border-radius: {tokens.radius.lg}px; background-color: {tokens.colors.bg_tertiary}; color: {tokens.colors.text_primary}; font-size: 12px; font-weight: 500;"
                f"}}"
                f"QPushButton#actionCard:hover {{"
                f"  background-color: {tokens.colors.bg_hover}; border-color: {tokens.colors.accent_primary}; color: {tokens.colors.text_inverse};"
                f"}}"
            )
        if hasattr(self, "input_frame"):
            self.input_frame.setStyleSheet(
                f"QFrame {{ background-color: {tokens.colors.bg_tertiary}; border: 1px solid {tokens.colors.border_default}; border-radius: 20px; padding: 2px 6px; }}"
            )
        if hasattr(self, "txt_query"):
            self.txt_query.setStyleSheet(
                f"QLineEdit {{ border: none; background: transparent; color: {tokens.colors.text_primary}; font-size: 12px; }}"
            )

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