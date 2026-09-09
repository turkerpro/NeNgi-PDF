import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    content = f.read()

old_shortcut = """        # Save
        act_save = QAction(self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_current_file)
        self.addAction(act_save)"""

new_shortcut = """        # Save
        act_save = QAction(self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_current_file)
        self.addAction(act_save)

        # Save As
        act_save_as = QAction(self)
        act_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        act_save_as.triggered.connect(self.save_current_file_as)
        self.addAction(act_save_as)"""

if old_shortcut in content:
    content = content.replace(old_shortcut, new_shortcut)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find old_shortcut")
