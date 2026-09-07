"""
NeNgi PDF - Embedded File Attachments Manager
Manages embedded file attachments inside PDF documents (list, extract, add, delete).
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import pymupdf as fitz
from nengi.core.pdf_document import PDFDocument


class AttachmentManager:
    """Manages PDF embedded files (attachments)."""

    @staticmethod
    def get_attachments(doc: PDFDocument) -> List[Dict[str, Any]]:
        """Returns metadata of all embedded files in the PDF."""
        if not doc.is_open or not doc.doc:
            return []

        attachments = []
        for name in doc.doc.embfile_names():
            try:
                info = doc.doc.embfile_info(name)
                data = doc.doc.embfile_get(name)
                size_bytes = len(data) if data else 0
                desc = info.get("desc", "") if isinstance(info, dict) else ""
                attachments.append({
                    "name": name,
                    "size": size_bytes,
                    "desc": desc,
                })
            except Exception:
                attachments.append({
                    "name": name,
                    "size": 0,
                    "desc": "",
                })
        return attachments

    @staticmethod
    def add_attachment(doc: PDFDocument, file_path: str, description: str = "") -> bool:
        """Embeds an external file into the PDF document."""
        if not doc.is_open or not os.path.exists(file_path):
            return False

        doc.save_state_for_undo()
        name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            data = f.read()

        doc.doc.embfile_add(name, data, desc=description or name)
        doc.is_modified = True
        return True

    @staticmethod
    def extract_attachment(doc: PDFDocument, name: str, output_path: str) -> bool:
        """Extracts an embedded file and saves it to disk."""
        if not doc.is_open:
            return False

        try:
            data = doc.doc.embfile_get(name)
            with open(output_path, "wb") as f:
                f.write(data)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_attachment(doc: PDFDocument, name: str) -> bool:
        """Deletes an embedded file from the PDF document."""
        if not doc.is_open:
            return False

        doc.save_state_for_undo()
        try:
            doc.doc.embfile_del(name)
            doc.is_modified = True
            return True
        except Exception:
            return False
