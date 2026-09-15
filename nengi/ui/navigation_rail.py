"""
NeNgi PDF - NextGen Left Navigation Rail
Clean vertical navigation bar featuring app branding, primary views,
vector SVG icons, and bottom-pinned settings.
"""

from __future__ import annotations
from typing import Dict
import os
import sys
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QButtonGroup
)
from PyQt6.QtGui import QPixmap

from nengi.ui.icons import get_svg_icon
from nengi.ui.styles import get_dark_tokens, get_light_tokens


def _get_tokens(is_dark: bool = True):
    """Returns design tokens for current theme."""
    return get_dark_tokens() if is_dark else get_light_tokens()


class NavigationRail(QWidget):
    """Modern left sidebar with brand identity and view navigation."""

    nav_changed = pyqtSignal(str) # "home", "recent", "documents", "diff", "tools", "settings"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setObjectName("navigationRail")
        self._buttons: dict[str, QPushButton] = {}
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        tokens = _get_tokens(True)
        self.is_dark = True
        self._item_icons: Dict[str, str] = {}

        # 1. Brand Logo & Title
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.setContentsMargins(6, 0, 6, 16)

        lbl_logo = QLabel()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "app_icon.png")
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "resources", "app_icon.png")

        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setPixmap(get_svg_icon("logo", tokens.colors.text_accent, 26).pixmap(26, 26))
        brand_layout.addWidget(lbl_logo)

        lbl_title = QLabel("NeNgi PDF")
        lbl_title.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {tokens.colors.text_accent}; letter-spacing: 0.5px;")
        brand_layout.addWidget(lbl_title)
        brand_layout.addStretch()

        layout.addLayout(brand_layout)

        # 2. Primary Navigation Items with SVG Icons
        self._add_nav_item(layout, "home", "home", "Ana Sayfa", is_checked=True)
        self._add_nav_item(layout, "recent", "recent", "Son Dosyalar")
        self._add_nav_item(layout, "documents", "documents", "Belgelerim")
        self._add_nav_item(layout, "bookmarks", "bookmark", "Yer İmleri")
        self._add_nav_item(layout, "diff", "diff", "Karşılaştır (DIFF)")

        layout.addStretch()

        # Divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        tokens = _get_tokens(True)
        self.divider.setStyleSheet(f"color: {tokens.colors.border_subtle}; background-color: {tokens.colors.border_subtle}; height: 1px; margin: 8px 0;")
        layout.addWidget(self.divider)

        # 3. Bottom Pinned Settings
        self._add_nav_item(layout, "settings", "settings", "Ayarlar", checkable=False)

    def _add_nav_item(self, layout: QVBoxLayout, key: str, icon_name: str, label: str, is_checked: bool = False, checkable: bool = True):
        self._item_icons[key] = icon_name
        btn = QPushButton(f"  {label}")
        btn.setObjectName("navButton")
        tokens = _get_tokens(True)
        icon_color = tokens.colors.text_primary if is_checked else tokens.colors.text_tertiary
        btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
        btn.setIconSize(QSize(18, 18))
        btn.setCheckable(checkable)
        btn.setChecked(is_checked)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            f"QPushButton#navButton {{"
            f"  text-align: left; padding: 8px 14px; border: none; border-radius: {tokens.radius.lg}px;"
            f"  font-size: 13px; font-weight: 500; color: {tokens.colors.text_tertiary}; background-color: transparent;"
            f"}}"
            f"QPushButton#navButton:hover {{"
            f"  background-color: {tokens.colors.bg_hover}; color: {tokens.colors.text_primary};"
            f"}}"
            f"QPushButton#navButton:checked {{"
            f"  background-color: {tokens.colors.accent_primary}; color: {tokens.colors.text_inverse}; font-weight: 600;"
            f"}}"
        )
        if checkable:
            self._button_group.addButton(btn)
            btn.toggled.connect(lambda is_on, b=btn, name=icon_name: b.setIcon(get_svg_icon(name, tokens.colors.text_primary if is_on else tokens.colors.text_tertiary, 18)))
            if is_checked:
                btn.setIcon(get_svg_icon(icon_name, tokens.colors.text_primary, 18))

        btn.clicked.connect(lambda: self._on_btn_clicked(key))
        self._buttons[key] = btn
        layout.addWidget(btn)

    def update_theme(self, is_dark: bool):
        """Updates SVG icons and styles dynamically for dark or light theme."""
        self.is_dark = is_dark
        tokens = _get_tokens(is_dark)
        text_color = tokens.colors.text_tertiary
        hover_bg = tokens.colors.bg_hover
        hover_text = tokens.colors.text_primary
        div_color = tokens.colors.border_subtle

        if hasattr(self, "divider"):
            self.divider.setStyleSheet(f"color: {div_color}; background-color: {div_color}; height: 1px; margin: 8px 0;")

        for key, btn in self._buttons.items():
            icon_name = self._item_icons.get(key, "")
            is_checked = btn.isChecked()
            icon_color = tokens.colors.text_primary if is_checked else tokens.colors.text_tertiary
            if icon_name:
                btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
            btn.setStyleSheet(
                f"QPushButton#navButton {{"
                f"  text-align: left; padding: 8px 14px; border: none; border-radius: {tokens.radius.lg}px;"
                f"  font-size: 13px; font-weight: 500; color: {text_color}; background-color: transparent;"
                f"}}"
                f"QPushButton#navButton:hover {{"
                f"  background-color: {hover_bg}; color: {hover_text};"
                f"}}"
                f"QPushButton#navButton:checked {{"
                f"  background-color: {tokens.colors.accent_primary}; color: {tokens.colors.text_inverse}; font-weight: 600;"
                f"}}"
            )

    def _on_btn_clicked(self, key: str):
        self.nav_changed.emit(key)

    def set_active_item(self, key: str):
        if key in self._buttons and self._buttons[key].isCheckable():
            self._buttons[key].setChecked(True)
