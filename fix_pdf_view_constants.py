import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

# Fallbacks for constants
replacements = {
    'fitz.PDF_WIDGET_TYPE_TEXT': 'getattr(fitz, "PDF_WIDGET_TYPE_TEXT", getattr(fitz, "WIDGET_TYPE_TEXT", 0))',
    'fitz.PDF_WIDGET_TYPE_CHECKBOX': 'getattr(fitz, "PDF_WIDGET_TYPE_CHECKBOX", getattr(fitz, "WIDGET_TYPE_CHECKBOX", 1))',
    'fitz.PDF_WIDGET_TYPE_RADIOBUTTON': 'getattr(fitz, "PDF_WIDGET_TYPE_RADIOBUTTON", getattr(fitz, "WIDGET_TYPE_RADIOBUTTON", 2))',
    'fitz.PDF_WIDGET_TYPE_COMBOBOX': 'getattr(fitz, "PDF_WIDGET_TYPE_COMBOBOX", getattr(fitz, "WIDGET_TYPE_COMBOBOX", 3))',
    'fitz.PDF_WIDGET_TYPE_LISTBOX': 'getattr(fitz, "PDF_WIDGET_TYPE_LISTBOX", getattr(fitz, "WIDGET_TYPE_LISTBOX", 4))',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(filepath, 'w') as f:
    f.write(content)

