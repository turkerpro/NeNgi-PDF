"""
NeNgi PDF - Interactive AcroForm Handler
Reads form fields (text boxes, checkboxes, dropdowns) and allows filling/updating.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import pymupdf as fitz
from .pdf_document import PDFDocument


class FormHandler:
    """Interacts with interactive AcroForm fields in a PDF."""

    @staticmethod
    def get_all_fields(doc: PDFDocument) -> List[Dict[str, Any]]:
        """Returns metadata and current values of all form fields in the document."""
        if not doc.is_open:
            return []

        fields = []
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                fields.append({
                    "page": page_idx,
                    "name": widget.field_name,
                    "type": widget.field_type_string,
                    "value": widget.field_value,
                    "rect": widget.rect,
                    "widget": widget
                })
        return fields

    @staticmethod
    def set_field_value(doc: PDFDocument, field_name: str, value: Any) -> bool:
        """Sets the value of a specific named form field across all pages."""
        if not doc.is_open:
            return False

        updated = False
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                if widget.field_name == field_name:
                    widget.field_value = str(value)
                    widget.update()
                    updated = True

        if updated:
            doc.is_modified = True
        return updated
