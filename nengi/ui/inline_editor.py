from PyQt6.QtWidgets import QTextEdit, QWidget, QHBoxLayout, QVBoxLayout, QComboBox, QDoubleSpinBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QFontDatabase
import fitz

from nengi.core.pdf_document import _resolve_tr_font


class InlineTextEditor(QWidget):
    editing_finished = pyqtSignal(str, dict, fitz.Rect) # text, style, rect
    editing_cancelled = pyqtSignal()

    def __init__(self, text: str, style: dict, pdf_rect: fitz.Rect, zoom: float, parent=None):
        super().__init__(parent)
        self.pdf_rect = pdf_rect
        self.style = dict(style)
        self.zoom = zoom
        self._committed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Mini format şeridi (canvas overlay, ayrı pencere yok)
        self.toolbar = QWidget(self)
        bar = QHBoxLayout(self.toolbar)
        bar.setContentsMargins(4, 2, 4, 2)
        bar.setSpacing(4)

        self.cb_family = QComboBox(self.toolbar)
        families = sorted(QFontDatabase.families())
        if not families:
            families = ["Arial", "Helvetica"]
        self.cb_family.addItems(families)
        fam = self.style.get("family", "Arial")
        idx = self.cb_family.findText(fam, Qt.MatchFlag.MatchContains)
        if idx >= 0:
            self.cb_family.setCurrentIndex(idx)
        else:
            self.cb_family.setCurrentIndex(0)
            self.style["family"] = self.cb_family.currentText()
        self.cb_family.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.cb_family.currentTextChanged.connect(self._on_family_changed)
        bar.addWidget(self.cb_family, 1)

        self.sp_size = QDoubleSpinBox(self.toolbar)
        self.sp_size.setRange(4.0, 120.0)
        self.sp_size.setSingleStep(0.5)
        self.sp_size.setValue(float(self.style.get("size", 11.0)))
        self.sp_size.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.sp_size.valueChanged.connect(self._on_size_changed)
        bar.addWidget(self.sp_size)

        self.btn_bold = QPushButton("B", self.toolbar)
        self.btn_bold.setCheckable(True)
        self.btn_bold.setChecked(bool(self.style.get("is_bold", False)))
        self.btn_bold.setFixedWidth(28)
        self.btn_bold.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_bold.setStyleSheet("font-weight: bold;")
        self.btn_bold.toggled.connect(self._on_bold_toggled)
        bar.addWidget(self.btn_bold)

        self.btn_italic = QPushButton("I", self.toolbar)
        self.btn_italic.setCheckable(True)
        self.btn_italic.setChecked(bool(self.style.get("is_italic", False)))
        self.btn_italic.setFixedWidth(28)
        self.btn_italic.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_italic.setStyleSheet("font-style: italic;")
        self.btn_italic.toggled.connect(self._on_italic_toggled)
        bar.addWidget(self.btn_italic)

        self.toolbar.setStyleSheet(
            "QWidget { background-color: #24272D; border: 1px solid #353942; border-radius: 4px; }"
            "QComboBox, QDoubleSpinBox, QPushButton { color: #FFFFFF; }"
        )
        layout.addWidget(self.toolbar)

        self.edit = QTextEdit(self)
        self.edit.setText(text)

        # Configure Font
        self._apply_font_to_edit()

        # Configure Color
        r, g, b = self.style.get("color_rgb", (0, 0, 0))
        self.edit.setTextColor(QColor(int(r*255), int(g*255), int(b*255)))

        # Styling
        self.edit.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 240);
                border: 2px dashed #0078D4;
                color: #000000;
            }
        """)

        self.edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.edit.installEventFilter(self)
        layout.addWidget(self.edit, 1)

        # Position and size (+şerit payı)
        sx = pdf_rect.x0 * zoom
        sy = pdf_rect.y0 * zoom
        # Give it a bit more width/height for editing comfortably
        sw = max((pdf_rect.width * zoom) + 100, 200)
        sh = max((pdf_rect.height * zoom) + 50 + 30, 80)
        self.setGeometry(int(sx - 5), int(sy - 5), int(sw), int(sh))

    # ---- format şeridi ----
    def _map_to_fitz(self, fam: str, is_b: bool, is_i: bool) -> str:
        # Standart aileler base14'e, diğerleri core çözümleyiciye düşer
        # (replace_text_block zaten _resolve_tr_font ile tr-sans gömer).
        low = (fam or "").lower()
        if "times" in low:
            return "tibi" if is_b and is_i else ("tibo" if is_b else ("tiit" if is_i else "tiro"))
        if "courier" in low:
            return "cobi" if is_b and is_i else ("cobo" if is_b else ("coit" if is_i else "couri"))
        _resolve_tr_font()
        return "hebi" if is_b and is_i else ("hebo" if is_b else ("heit" if is_i else "helv"))

    def _refresh_fitz_font(self):
        self.style["fitz_font"] = self._map_to_fitz(
            self.style.get("family", "Arial"),
            bool(self.style.get("is_bold", False)),
            bool(self.style.get("is_italic", False)),
        )

    def _apply_font_to_edit(self):
        font = QFont(self.style.get("family", "Arial"))
        font.setPointSizeF(float(self.style.get("size", 11.0)) * self.zoom)
        font.setBold(bool(self.style.get("is_bold", False)))
        font.setItalic(bool(self.style.get("is_italic", False)))
        self.edit.setFont(font)

    def _on_family_changed(self, fam: str):
        self.style["family"] = fam
        self._refresh_fitz_font()
        self._apply_font_to_edit()

    def _on_size_changed(self, val: float):
        self.style["size"] = float(val)
        self._apply_font_to_edit()

    def _on_bold_toggled(self, on: bool):
        self.style["is_bold"] = bool(on)
        self._refresh_fitz_font()
        self._apply_font_to_edit()

    def _on_italic_toggled(self, on: bool):
        self.style["is_italic"] = bool(on)
        self._refresh_fitz_font()
        self._apply_font_to_edit()

    # ---- QTextEdit uyumluluğu ----
    def toPlainText(self) -> str:
        return self.edit.toPlainText()

    def insertPlainText(self, text: str):
        self.edit.insertPlainText(text)

    def setFocus(self):
        self.edit.setFocus()

    def eventFilter(self, obj, event):
        if obj is self.edit and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.commit()
                return True
            elif event.key() == Qt.Key.Key_Escape:
                self.cancel()
                return True
            elif event.key() == Qt.Key.Key_Tab:
                # Insert 4 spaces instead of \t because PyMuPDF doesn't render \t correctly
                self.edit.insertPlainText("    ")
                return True
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        # Şerit içi odak gezintisinde commit etme; odak tüm
        # overlay dışına çıkınca commit et.
        super().focusOutEvent(event)
        from PyQt6.QtWidgets import QApplication
        fw = QApplication.focusWidget()
        if fw is not None and self.isAncestorOf(fw):
            return
        self.commit()

    def keyPressEvent(self, event):
        # Ctrl+Enter to commit
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.commit()
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel()
            return
        elif event.key() == Qt.Key.Key_Tab:
            # Insert 4 spaces instead of \t because PyMuPDF doesn't render \t correctly
            self.insertPlainText("    ")
            return
        super().keyPressEvent(event)

    def commit(self):
        if self._committed:
            return
        self._committed = True
        new_text = self.edit.toPlainText().strip()
        if new_text:
            self.editing_finished.emit(new_text, self.style, self.pdf_rect)
        else:
            self.editing_cancelled.emit()
        self.deleteLater()

    def cancel(self):
        if self._committed:
            return
        self._committed = True
        self.editing_cancelled.emit()
        self.deleteLater()
