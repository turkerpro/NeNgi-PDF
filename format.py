import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace("from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal, QSize, QEvent\n", "")

# insert it after typing imports
target = "from typing import Optional, Tuple, List, Callable\n"
content = content.replace(target, target + "from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal, QSize, QEvent\n")

with open(filepath, 'w') as f:
    f.write(content)
