"""
NeNgi PDF - Floating Island / Pill Toolbar
Modern floating capsule widget positioned at the bottom of the document canvas,
containing quick interaction tools powered by clean vector SVG icons.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFrame, QButtonGroup, 
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor

from nengi.ui.icons import get_svg_icon


class FloatingPillToolbar(QFrame):
    """Floating capsule toolbar positioned above document view."""

    tool_changed = pyqtSignal(str) # "view", "edit_text", "text", "whiteout", "signature", "rotate", "pages", "undo", "redo"

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("floatingPill")
        self.setFixedHeight(48)

        # Soft drop shadow for floating elevation
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)
        layout.setSpacing(6)

        # 1. Primary Canvas Tools (Exclusive toggle)
        self.is_dark = True
        self._buttons: List[Tuple[QPushButton, str]] = []

        self.btn_view = self._add_tool_btn("cursor", "İnceleme / Seçim Modu", "view", checkable=True, checked=True)
        self.btn_draw = self._add_tool_btn("draw", "Serbest Çizim", "draw", checkable=True)
        self.btn_text = self._add_tool_btn("text", "Metin Ekle", "text", checkable=True)
        self.btn_whiteout = self._add_tool_btn("eraser", "Silgi / Beyazlat", "whiteout", checkable=True)
        self.btn_sig = self._add_tool_btn("signature", "İmza Ekle", "signature", checkable=False)

        # Subtle divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.VLine)
        self.divider.setStyleSheet("color: #383C44; background-color: #383C44; width: 1px; margin: 8px 4px;")
        layout.addWidget(self.divider)

        # 2. Action Tools
        self._add_tool_btn("rotate", "Sayfayı Döndür", "rotate", checkable=False)
        self._add_tool_btn("pages", "Sayfaları Yönet", "pages", checkable=False)

    def _add_tool_btn(self, icon_name: str, tooltip: str, tool_id: str, checkable: bool = False, checked: bool = False) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("pillButton")
        btn.setToolTip(tooltip)
        icon_color = "#FFFFFF" if checked else ("#D0D4DC" if self.is_dark else "#334155")
        btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
        btn.setIconSize(QSize(18, 18))
        btn.setCheckable(checkable)
        btn.setChecked(checked)
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton#pillButton {"
            "  border: none; border-radius: 18px;"
            "  background-color: transparent;"
            "}"
            "QPushButton#pillButton:hover {"
            "  background-color: #353942;"
            "}"
            "QPushButton#pillButton:checked {"
            "  background-color: #0078D4;"
            "}"
        )
        if checkable:
            self._btn_group.addButton(btn)
            btn.toggled.connect(lambda is_on, b=btn, name=icon_name: b.setIcon(get_svg_icon(name, "#FFFFFF" if is_on else ("#D0D4DC" if self.is_dark else "#334155"), 18)))
            if checked:
                btn.setIcon(get_svg_icon(icon_name, "#FFFFFF", 18))

        btn.clicked.connect(lambda: self.tool_changed.emit(tool_id))
        self._buttons.append((btn, icon_name))
        self.layout().addWidget(btn)
        return btn

    def update_theme(self, is_dark: bool):
        """Updates icons and button hover backgrounds dynamically when theme toggles."""
        self.is_dark = is_dark
        hover_bg = "#353942" if is_dark else "#E2E8F0"
        div_color = "#383C44" if is_dark else "#CBD5E1"
        if hasattr(self, "divider"):
            self.divider.setStyleSheet(f"color: {div_color}; background-color: {div_color}; width: 1px; margin: 8px 4px;")

        for btn, icon_name in self._buttons:
            is_checked = btn.isChecked()
            icon_color = "#FFFFFF" if is_checked else ("#D0D4DC" if is_dark else "#334155")
            btn.setIcon(get_svg_icon(icon_name, icon_color, 18))
            btn.setStyleSheet(
                f"QPushButton#pillButton {{"
                f"  border: none; border-radius: 18px;"
                f"  background-color: transparent;"
                f"}}"
                f"QPushButton#pillButton:hover {{"
                f"  background-color: {hover_bg};"
                f"}}"
                f"QPushButton#pillButton:checked {{"
                f"  background-color: #0078D4;"
                f"}}"
            )

    def set_active_tool(self, tool_id: str):
        if tool_id == "view":
            self.btn_view.setChecked(True)
        elif tool_id == "text":
            self.btn_text.setChecked(True)
        elif tool_id == "whiteout":
            self.btn_whiteout.setChecked(True)
