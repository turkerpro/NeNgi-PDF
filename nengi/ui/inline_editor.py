from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import fitz

class InlineTextEditor(QTextEdit):
    editing_finished = pyqtSignal(str, dict, fitz.Rect) # text, style, rect
    editing_cancelled = pyqtSignal()

    def __init__(self, text: str, style: dict, pdf_rect: fitz.Rect, zoom: float, parent=None):
        super().__init__(parent)
        self.pdf_rect = pdf_rect
        self.style = style
        self.zoom = zoom
        
        self.setText(text)
        
        # Configure Font
        font = QFont(style.get("family", "Arial"))
        font.setPointSizeF(style.get("size", 11.0) * zoom)
        font.setBold(style.get("is_bold", False))
        font.setItalic(style.get("is_italic", False))
        self.setFont(font)
        
        # Configure Color
        r, g, b = style.get("color_rgb", (0, 0, 0))
        self.setTextColor(QColor(int(r*255), int(g*255), int(b*255)))
        
        # Styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 240);
                border: 2px dashed #0078D4;
                color: #000000;
            }
        """)
        
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Position and size
        sx = pdf_rect.x0 * zoom
        sy = pdf_rect.y0 * zoom
        # Give it a bit more width/height for editing comfortably
        sw = max((pdf_rect.width * zoom) + 100, 200)
        sh = max((pdf_rect.height * zoom) + 50, 50)
        self.setGeometry(int(sx - 5), int(sy - 5), int(sw), int(sh))
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
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
            # Insert 4 spaces instead of 	 because PyMuPDF doesn't render 	 correctly
            self.insertPlainText("    ")
            return
        super().keyPressEvent(event)
        
    def commit(self):
        new_text = self.toPlainText().strip()
        if new_text:
            self.editing_finished.emit(new_text, self.style, self.pdf_rect)
        else:
            self.editing_cancelled.emit()
        self.deleteLater()
        
    def cancel(self):
        self.editing_cancelled.emit()
        self.deleteLater()
