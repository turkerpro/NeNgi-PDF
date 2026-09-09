import os
import re

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    content = f.read()

# 1. Add "Farklı Kaydet" button to UI
old_btn_save = """        self.btn_save.setToolTip("Değişiklikleri Kaydet (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_current_file)
        h_layout.addWidget(self.btn_save)"""

new_btn_save = """        self.btn_save.setToolTip("Değişiklikleri Kaydet (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_current_file)
        h_layout.addWidget(self.btn_save)

        self.btn_save_as = QPushButton("  Farklı Kaydet")
        self.btn_save_as.setIcon(get_svg_icon("save", "#D0D4DC", 16))
        self.btn_save_as.setIconSize(QSize(16, 16))
        self.btn_save_as.setToolTip("Farklı Kaydet (Ctrl+Shift+S)")
        self.btn_save_as.clicked.connect(self.save_current_file_as)
        h_layout.addWidget(self.btn_save_as)"""

if old_btn_save in content:
    content = content.replace(old_btn_save, new_btn_save)
else:
    print("Could not find old_btn_save")

# 2. Update save_current_file logic
old_save_logic = """    def save_current_file(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.commit_pending_edits()
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
        if not doc.file_path:
            self.save_current_file_as()
            return
        if doc.save():
            self.show_status_message(f"Kaydedildi: {os.path.basename(doc.file_path)}")
        else:
            self.save_current_file_as()"""

new_save_logic = """    def save_current_file(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.commit_pending_edits()
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
            
        # Eğer dosya geçici bir klasördeyse (Outlook eklentisi, Temp vs.) doğrudan farklı kaydet'e yönlendir
        is_temp = False
        if doc.file_path:
            fp_lower = doc.file_path.lower()
            temp_indicators = ["\\appdata\\local\\temp\\", "\\inetcache\\", "/tmp/", "/var/tmp/", "\\temp\\"]
            if any(ind in fp_lower for ind in temp_indicators):
                is_temp = True
                
        if not doc.file_path or is_temp:
            self.save_current_file_as()
            return
            
        if doc.save():
            self.show_status_message(f"Kaydedildi: {os.path.basename(doc.file_path)}")
        else:
            self.save_current_file_as()"""

if old_save_logic in content:
    content = content.replace(old_save_logic, new_save_logic)
else:
    print("Could not find old_save_logic")

# 3. Add shortcut Ctrl+Shift+S
old_shortcuts = """        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_current_file)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_current_document)"""

new_shortcuts = """        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_file)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_current_file)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self.save_current_file_as)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_current_document)"""

if old_shortcuts in content:
    content = content.replace(old_shortcuts, new_shortcuts)
else:
    print("Could not find old_shortcuts")

with open(filepath, 'w') as f:
    f.write(content)
