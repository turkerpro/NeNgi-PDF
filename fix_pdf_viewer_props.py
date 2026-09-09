import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

new_method = """    def set_current_property(self, prop: str, value):
        if prop == 'width':
            for page in self.page_widgets:
                page.current_width = value
        elif prop == 'opacity':
            for page in self.page_widgets:
                page.current_opacity = value

    def set_tool(self"""

content = content.replace("    def set_tool(self", new_method)

with open(filepath, 'w') as f:
    f.write(content)

filepath_main = 'nengi/ui/main_window.py'
with open(filepath_main, 'r') as f:
    content_main = f.read()

old_prop = """    def _on_property_changed(self, prop: str, value):
        view = self.get_current_viewer()
        if view:
            if prop == 'width' and hasattr(view, 'current_width'):
                view.current_width = value
            elif prop == 'opacity' and hasattr(view, 'current_opacity'):
                view.current_opacity = value"""

new_prop = """    def _on_property_changed(self, prop: str, value):
        view = self.get_current_viewer()
        if view and hasattr(view, 'set_current_property'):
            view.set_current_property(prop, value)"""

if old_prop in content_main:
    content_main = content_main.replace(old_prop, new_prop)
    with open(filepath_main, 'w') as f:
        f.write(content_main)
