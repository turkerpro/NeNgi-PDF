"""
NeNgi PDF - Floating Island / Pill Toolbar
Modern floating capsule widget positioned at the bottom of the document canvas,
containing quick interaction tools powered by clean vector SVG icons.
"""

from __future__ import annotations
from typing import List, Tuple
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QFrame, QButtonGroup,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QColor

from nengi.ui.icons import get_svg_icon
from nengi.ui.styles import get_dark_tokens, get_light_tokens


def _get_tokens(is_dark: bool = True):
    """Returns design tokens for current theme."""
    return get_dark_tokens() if is_dark else get_light_tokens()


class FloatingPillToolbar(QFrame):
    """Floating capsule toolbar positioned above document view - SINGLE AUTHORITATIVE TOOLBAR."""

    tool_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("floatingPill")
        self.setFixedHeight(48)

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

        self.is_dark = True
        self._buttons: List[Tuple[QPushButton, str]] = []

        self.btn_view = self._add_tool_btn("cursor", "İnceleme / Seçim Modu", "view", checkable=True, checked=True)
        self.btn_draw = self._add_tool_btn("draw", "Serbest Çizim", "draw", checkable=True)
        self.btn_text = self._add_tool_btn("text", "Metin Ekle", "text", checkable=True)
        self.btn_whiteout = self._add_tool_btn("eraser", "Silgi / Beyazlat", "whiteout", checkable=True)
        self.btn_sig = self._add_tool_btn("signature", "İmza Ekle", "signature", checkable=False)

        self.divider1 = QFrame()
        self.divider1.setFrameShape(QFrame.Shape.VLine)
        tokens_div = _get_tokens(True)
        self.divider1.setStyleSheet(f"color: {tokens_div.colors.border_default}; background-color: {tokens_div.colors.border_default}; width: 1px; margin: 8px 4px;")
        layout.addWidget(self.divider1)

        self.btn_edit_text = self._add_tool_btn("edit", "Seçili Metni Düzenle", "edit_text", checkable=False)
        self.btn_rotate = self._add_tool_btn("rotate", "Sayfayı Döndür", "rotate", checkable=False)
        self.btn_pages = self._add_tool_btn("pages", "Sayfaları Yönet", "pages", checkable=False)

        self.divider2 = QFrame()
        self.divider2.setFrameShape(QFrame.Shape.VLine)
        tokens_div2 = _get_tokens(True)
        self.divider2.setStyleSheet(f"color: {tokens_div2.colors.border_default}; background-color: {tokens_div2.colors.border_default}; width: 1px; margin: 8px 4px;")
        layout.addWidget(self.divider2)

        self.btn_undo = self._add_tool_btn("undo", "Geri Al (Ctrl+Z)", "undo", checkable=False)
        self.btn_redo = self._add_tool_btn("redo", "Yinele (Ctrl+Y)", "redo", checkable=False)
        self.btn_more = self._add_tool_btn("more", "Genişletilmiş Araçlar", "more", checkable=False)

    def _add_tool_btn(self, icon_name: str, tooltip: str, tool_id: str, checkable: bool = False, checked: bool = False) -> QPushButton:
        btn = QPushButton()
        btn.setObjectName("pillButton")
        btn.setToolTip(tooltip)
        tokens = _get_tokens(True)
        icon_color = tokens.colors.text_inverse if checked else tokens.colors.text_tertiary
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
            f"QPushButton#pillButton:hover {{"
            f"  background-color: {tokens.colors.bg_hover};"
            f"}}"
            f"QPushButton#pillButton:checked {{"
            f"  background-color: {tokens.colors.accent_primary};"
            f"}}"
        )
        if checkable:
            self._btn_group.addButton(btn)
            btn.toggled.connect(lambda is_on, b=btn, name=icon_name: b.setIcon(get_svg_icon(name, tokens.colors.text_inverse if is_on else tokens.colors.text_tertiary, 18)))
            if checked:
                btn.setIcon(get_svg_icon(icon_name, tokens.colors.text_inverse, 18))

        btn.clicked.connect(lambda: self.tool_changed.emit(tool_id))
        self._buttons.append((btn, icon_name))
        self.layout().addWidget(btn)
        return btn

    def update_theme(self, is_dark: bool):
        """Updates icons and button hover backgrounds dynamically when theme toggles."""
        self.is_dark = is_dark
        tokens = _get_tokens(is_dark)
        hover_bg = tokens.colors.bg_hover
        div_color = tokens.colors.border_default
        if hasattr(self, "divider1"):
            self.divider1.setStyleSheet(f"color: {div_color}; background-color: {div_color}; width: 1px; margin: 8px 4px;")
        if hasattr(self, "divider2"):
            self.divider2.setStyleSheet(f"color: {div_color}; background-color: {div_color}; width: 1px; margin: 8px 4px;")

        for btn, icon_name in self._buttons:
            is_checked = btn.isChecked()
            icon_color = tokens.colors.text_inverse if is_checked else tokens.colors.text_tertiary
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
                f"  background-color: {tokens.colors.accent_primary};"
                f"}}"
            )

    def set_active_tool(self, tool_id: str):
        if tool_id == "view":
            self.btn_view.setChecked(True)
        elif tool_id == "text":
            self.btn_text.setChecked(True)
        elif tool_id == "whiteout":
            self.btn_whiteout.setChecked(True)
        elif tool_id == "draw":
            self.btn_draw.setChecked(True)