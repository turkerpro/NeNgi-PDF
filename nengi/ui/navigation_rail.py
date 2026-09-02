"""
NeNgi PDF - NextGen Left Navigation Rail
Clean vertical navigation bar featuring app branding, primary views,
vector SVG icons, and bottom-pinned settings.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QButtonGroup
)

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

        # 1. Brand Logo & Title
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        brand_layout.setContentsMargins(6, 0, 6, 16)

        lbl_logo = QLabel()
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
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #2D3036; background-color: #2D3036; height: 1px; margin: 8px 0;")
        layout.addWidget(divider)

        # 3. Bottom Pinned Settings
        self._add_nav_item(layout, "settings", "settings", "Ayarlar", checkable=False)

    def _add_nav_item(self, layout: QVBoxLayout, key: str, icon_name: str, label: str, is_checked: bool = False, checkable: bool = True):
        btn = QPushButton(f"  {label}")
        btn.setObjectName("navButton")
        btn.setIcon(get_svg_icon(icon_name, "#9DA3AE", 18))
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
            btn.toggled.connect(lambda is_on, b=btn, name=icon_name: b.setIcon(get_svg_icon(name, "#FFFFFF" if is_on else "#9DA3AE", 18)))
            if is_checked:
                btn.setIcon(get_svg_icon(icon_name, "#FFFFFF", 18))

        btn.clicked.connect(lambda: self._on_btn_clicked(key))
        self._buttons[key] = btn
        layout.addWidget(btn)

    def _on_btn_clicked(self, key: str):
        self.nav_changed.emit(key)

    def set_active_item(self, key: str):
        if key in self._buttons and self._buttons[key].isCheckable():
            self._buttons[key].setChecked(True)
