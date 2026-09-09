import os

filepath = 'nengi/ui/inline_editor.py'
with open(filepath, 'r') as f:
    content = f.read()

old_key_press = """    def keyPressEvent(self, event):
        # Ctrl+Enter or Return (if we want single line enter to commit)
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.commit()
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.cancel()
            return
        super().keyPressEvent(event)"""

new_key_press = """    def keyPressEvent(self, event):
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
        super().keyPressEvent(event)"""

if old_key_press in content:
    content = content.replace(old_key_press, new_key_press)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find keyPressEvent in inline_editor.py")
