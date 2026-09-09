import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_func = "    def set_tool(self, tool_name: str):"
new_func = """    def set_current_color(self, color: tuple):
        self.current_color = color
        for page in self.pages:
            page.current_color = color

    def set_tool(self, tool_name: str):"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open(filepath, 'w') as f:
        f.write(content)
