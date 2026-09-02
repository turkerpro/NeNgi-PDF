"""
NeNgi PDF - Floating Island / Pill Toolbar
Modern floating capsule widget positioned at the bottom of the document canvas,
containing quick interaction tools (Select, Edit, Add Text, Whiteout, Signature, Rotate, Undo).
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFrame, QButtonGroup, 
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor


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
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(4)

        # 1. Primary Canvas Tools (Exclusive toggle)
        self.btn_view = self._add_tool_btn("👆", "Gezin / Seç", "view", checkable=True, checked=True)
        self.btn_edit = self._add_tool_btn("✏️", "Metni / Paragrafı Düzenle", "edit_text", checkable=False)
        self.btn_text = self._add_tool_btn("✍️", "Metin Ekle", "text", checkable=True)
        self.btn_whiteout = self._add_tool_btn("◻️", "Silgi / Beyazlat", "whiteout", checkable=True)
        self.btn_sig = self._add_tool_btn("🖊️", "İmza Ekle", "signature", checkable=False)

        # Subtle divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet("color: #383C44; background-color: #383C44; width: 1px; margin: 6px 2px;")
        layout.addWidget(div)

        # 2. Action Tools
        self._add_tool_btn("🔄", "Döndür", "rotate", checkable=False)
        self._add_tool_btn("📑", "Sayfalar", "pages", checkable=False)
        self._add_tool_btn("↩️", "Geri Al (Ctrl+Z)", "undo", checkable=False)
        self._add_tool_btn("↪️", "Yinele (Ctrl+Y)", "redo", checkable=False)

    def _add_tool_btn(self, icon_str: str, tooltip: str, tool_id: str, checkable: bool = False, checked: bool = False) -> QPushButton:
        btn = QPushButton(icon_str)
        btn.setObjectName("pillButton")
        btn.setToolTip(tooltip)
        btn.setCheckable(checkable)
        btn.setChecked(checked)
        btn.setFixedSize(36, 36)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            "QPushButton#pillButton {"
            "  font-size: 16px; border: none; border-radius: 18px;"
            "  background-color: transparent; color: #E0E0E0;"
            "}"
            "QPushButton#pillButton:hover {"
            "  background-color: #353942; color: #FFFFFF;"
            "}"
            "QPushButton#pillButton:checked {"
            "  background-color: #0078D4; color: #FFFFFF;"
            "}"
        )
        if checkable:
            self._btn_group.addButton(btn)

        btn.clicked.connect(lambda: self.tool_changed.emit(tool_id))
        self.layout().addWidget(btn)
        return btn

    def set_active_tool(self, tool_id: str):
        if tool_id == "view":
            self.btn_view.setChecked(True)
        elif tool_id == "text":
            self.btn_text.setChecked(True)
        elif tool_id == "whiteout":
            self.btn_whiteout.setChecked(True)
