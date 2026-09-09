import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_press = """            if self.mode in ["view", "highlight", "underline", "strikethrough"]:
                self._ensure_text_extracted()
                self._is_selecting_text = True
                self._drag_start = event.pos()
                self._drag_current = event.pos()
                self.selected_words = []
                self.update()"""

new_press = """            if self.mode in ["view", "highlight", "underline", "strikethrough"]:
                from PyQt6.QtWidgets import QApplication
                modifiers = QApplication.keyboardModifiers()
                self._ensure_text_extracted()
                self._is_selecting_text = True
                self._drag_start = event.pos()
                self._drag_current = event.pos()
                self.selected_words = []
                
                # Handle block selection
                if self.mode == "view":
                    if self.hovered_block:
                        from PyQt6.QtCore import Qt
                        if modifiers & Qt.KeyboardModifier.ControlModifier:
                            if self.hovered_block in self.selected_blocks:
                                self.selected_blocks.remove(self.hovered_block)
                            else:
                                self.selected_blocks.append(self.hovered_block)
                        else:
                            if self.hovered_block not in self.selected_blocks:
                                self.selected_blocks = [self.hovered_block]
                    else:
                        self.selected_blocks = []
                self.update()"""

if old_press in content:
    content = content.replace(old_press, new_press)

with open(filepath, 'w') as f:
    f.write(content)
