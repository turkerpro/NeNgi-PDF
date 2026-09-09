import os

filepath = 'nengi/ui/draggable_block.py'
with open(filepath, 'r') as f:
    content = f.read()

old_style = """        self.setStyleSheet(\"\"\"
            DraggableBlockWidget {
                border: 2px dashed #0078D4;
                background-color: rgba(255, 255, 255, 100);
            }
        \"\"\")"""

new_style = """        self.setStyleSheet(\"\"\"
            DraggableBlockWidget {
                border: 2px dashed #0078D4;
                background-color: rgba(255, 255, 255, 150);
            }
        \"\"\")
        
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.85)
        self.setGraphicsEffect(op)"""

if old_style in content:
    content = content.replace(old_style, new_style)
    with open(filepath, 'w') as f:
        f.write(content)
