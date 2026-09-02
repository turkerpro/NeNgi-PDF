"""
NeNgi PDF - NextGen Left Navigation Rail
Clean vertical navigation bar featuring app branding, primary views,
vector SVG icons, and bottom-pinned settings.
"""

from __future__ import annotations
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
            lbl_logo.setPixmap(get_svg_icon("logo", "#0078D4", 26).pixmap(26, 26))
        brand_layout.addWidget(lbl_logo)

        lbl_title = QLabel("NeNgi PDF")
        lbl_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #0078D4; letter-spacing: 0.5px;")
        brand_layout.addWidget(lbl_title)
        brand_layout.addStretch()

        layout.addLayout(brand_layout)

        # 2. Primary Navigation Items with SVG Icons
        self._add_nav_item(layout, "home", "home", "Ana Sayfa", is_checked=True)
        self._add_nav_item(layout, "recent", "recent", "Son Dosyalar")
        self._add_nav_item(layout, "documents", "documents", "Belgelerim")
        self._add_nav_item(layout, "diff", "diff", "Karşılaştır (DIFF)")
        self._add_nav_item(layout, "tools", "tools", "Hızlı Araçlar")

        layout.addStretch()

        # Divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setStyleSheet("color: #2D3036; background-color: #2D3036; height: 1px; margin: 8px 0;")
        layout.addWidget(self.divider)

        # 3. Bottom Pinned Settings
        self._add_nav_item(layout, "settings", "settings", "Ayarlar", checkable=False)

    def _add_nav_item(self, layout: QVBoxLayout, key: str, icon_name: str, label: str, is_checked: bool = False, checkable: bool = True):
        self._item_icons[key] = icon_name
        btn = QPushButton(f"  {label}")
        btn.setObjectName("navButton")
        icon_color = "#FFFFFF" if is_checked else ("#9DA3AE" if self.is_dark else "#475569")
        btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
        btn.setIconSize(QSize(18, 18))
        btn.setCheckable(checkable)
        btn.setChecked(is_checked)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            "QPushButton#navButton {"
            "  text-align: left; padding: 8px 14px; border: none; border-radius: 8px;"
            "  font-size: 13px; font-weight: 500; color: #9DA3AE; background-color: transparent;"
            "}"
            "QPushButton#navButton:hover {"
            "  background-color: #24272D; color: #FFFFFF;"
            "}"
            "QPushButton#navButton:checked {"
            "  background-color: #0078D4; color: #FFFFFF; font-weight: 600;"
            "}"
        )
        if checkable:
            self._button_group.addButton(btn)
            btn.toggled.connect(lambda is_on, b=btn, name=icon_name: b.setIcon(get_svg_icon(name, "#FFFFFF" if is_on else ("#9DA3AE" if self.is_dark else "#475569"), 18)))
            if is_checked:
                btn.setIcon(get_svg_icon(icon_name, "#FFFFFF", 18))

        btn.clicked.connect(lambda: self._on_btn_clicked(key))
        self._buttons[key] = btn
        layout.addWidget(btn)

    def update_theme(self, is_dark: bool):
        """Updates SVG icons and styles dynamically for dark or light theme."""
        self.is_dark = is_dark
        text_color = "#9DA3AE" if is_dark else "#475569"
        hover_bg = "#24272D" if is_dark else "#E2E8F0"
        hover_text = "#FFFFFF" if is_dark else "#0F172A"
        div_color = "#2D3036" if is_dark else "#E2E8F0"

        if hasattr(self, "divider"):
            self.divider.setStyleSheet(f"color: {div_color}; background-color: {div_color}; height: 1px; margin: 8px 0;")

        for key, btn in self._buttons.items():
            icon_name = self._item_icons.get(key, "")
            is_checked = btn.isChecked()
            icon_color = "#FFFFFF" if is_checked else ("#9DA3AE" if is_dark else "#475569")
            if icon_name:
                btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
            btn.setStyleSheet(
                f"QPushButton#navButton {{"
                f"  text-align: left; padding: 8px 14px; border: none; border-radius: 8px;"
                f"  font-size: 13px; font-weight: 500; color: {text_color}; background-color: transparent;"
                f"}}"
                f"QPushButton#navButton:hover {{"
                f"  background-color: {hover_bg}; color: {hover_text};"
                f"}}"
                f"QPushButton#navButton:checked {{"
                f"  background-color: #0078D4; color: #FFFFFF; font-weight: 600;"
                f"}}"
            )

    def _on_btn_clicked(self, key: str):
        self.nav_changed.emit(key)

    def set_active_item(self, key: str):
        if key in self._buttons and self._buttons[key].isCheckable():
            self._buttons[key].setChecked(True)
