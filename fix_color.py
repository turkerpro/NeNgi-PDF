import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "def _on_floating_tool_changed" in line:
        new_lines.append("    def _on_color_changed(self, color: tuple):\n")
        new_lines.append("        view = self._get_current_view()\n")
        new_lines.append("        if view and hasattr(view, 'set_current_color'):\n")
        new_lines.append("            view.set_current_color(color)\n\n")
    new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)
