import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "def _on_floating_tool_changed" in line:
        new_lines.append("    def _on_property_changed(self, prop: str, value):\n")
        new_lines.append("        view = self._get_current_view()\n")
        new_lines.append("        if view:\n")
        new_lines.append("            if prop == 'width' and hasattr(view, 'current_width'):\n")
        new_lines.append("                view.current_width = value\n")
        new_lines.append("            elif prop == 'opacity' and hasattr(view, 'current_opacity'):\n")
        new_lines.append("                view.current_opacity = value\n\n")
    new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)
