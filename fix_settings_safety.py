import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    content = f.read()

# Make settings initialization happen much earlier and also add fallback in _create_canvas
old_init_start = """    def __init__(self):
        super().__init__()
        from PyQt6.QtCore import QSettings
        self.settings = QSettings('NeNgi', 'NeNgiPDF')"""

new_init_start = """    def __init__(self):
        super().__init__()
        from PyQt6.QtCore import QSettings
        self.settings = QSettings('NeNgi', 'NeNgiPDF')
        # Keep a reference safe for subcomponents that may access before full init
        self._settings_initialized = True"""

if old_init_start in content:
    content = content.replace(old_init_start, new_init_start)
else:
    print("Could not find old_init_start")

# Make _create_canvas safe for missing settings
old_floating = """        self.floating_toolbar = AnnotationToolbar(is_dark=self.settings.value("theme", "light") == "dark")"""
new_floating = """        _settings = getattr(self, 'settings', None)
        _is_dark = (_settings.value("theme", "light") == "dark") if _settings else False
        self.floating_toolbar = AnnotationToolbar(is_dark=_is_dark)"""

if old_floating in content:
    content = content.replace(old_floating, new_floating)
else:
    print("Could not find old_floating_toolbar")

with open(filepath, 'w') as f:
    f.write(content)
