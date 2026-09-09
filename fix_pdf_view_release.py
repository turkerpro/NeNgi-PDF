import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_release = """    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode in ["view", "highlight", "underline", "strikethrough"] and self._is_selecting_text:
                self._is_selecting_text = False
                
                if self.selected_words and self.mode in ["highlight", "underline", "strikethrough"]:"""

new_release = """    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode in ["view", "highlight", "underline", "strikethrough"] and self._is_selecting_text:
                self._is_selecting_text = False
                if self.selected_words:
                    self.selected_blocks = []
                
                if self.selected_words and self.mode in ["highlight", "underline", "strikethrough"]:"""

if old_release in content:
    content = content.replace(old_release, new_release)
    with open(filepath, 'w') as f:
        f.write(content)
