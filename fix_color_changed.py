import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    content = f.read()

method = """
    def _on_floating_tool_changed(self, tool_name: str):
"""

new_method = """
    def _on_color_changed(self, color: tuple):
        # Pass color to current pdf view if available
        view = self._get_current_view()
        if view and hasattr(view, 'set_current_color'):
            view.set_current_color(color)

    def _on_floating_tool_changed(self, tool_name: str):
"""

content = content.replace(method, new_method)

with open(filepath, 'w') as f:
    f.write(content)
