import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "def set_mode(self" in line:
        new_lines.append("    def set_current_color(self, color: tuple):\n")
        new_lines.append("        self.current_color = color\n\n")
    new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)
