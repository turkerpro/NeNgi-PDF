import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

content = "from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal, QSize, QEvent\n" + content

with open(filepath, 'w') as f:
    f.write(content)
