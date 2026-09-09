import os

filepath = 'nengi/ui/annotation_toolbar.py'
with open(filepath, 'r') as f:
    content = f.read()

new_method = """    def set_active_tool(self, tool_name: str):
        for btn in self.tool_group.buttons():
            if btn.property("tool_name") == tool_name:
                btn.setChecked(True)
                break

    def update_theme(self,"""

content = content.replace("    def update_theme(self,", new_method)

with open(filepath, 'w') as f:
    f.write(content)
