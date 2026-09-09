import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_loop = "        for page in self.pages:\n            page.current_color = color"
new_loop = "        for page in self.page_widgets:\n            if hasattr(page, 'set_current_color'):\n                page.set_current_color(color)\n            else:\n                page.current_color = color"

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    with open(filepath, 'w') as f:
        f.write(content)
