"""
NeNgi PDF - Embedded File Attachments Manager
Manages embedded file attachments inside PDF documents (list, extract, add, delete).
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import fitz
from nengi.core.pdf_document import PDFDocument
from nengi.core.result import Result


class AttachmentManager:
    """Manages PDF embedded files (attachments)."""

    @staticmethod
    def get_attachments(doc: PDFDocument) -> Result[List[Dict[str, Any]]]:
        """Returns metadata of all embedded files in the PDF."""
        if not doc.is_open or not doc.doc:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")

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
        return Result.ok(attachments)

    @staticmethod
    def add_attachment(doc: PDFDocument, file_path: str, description: str = "") -> Result[bool]:
        """Embeds an external file into the PDF document."""
        if not doc.is_open or not os.path.exists(file_path):
            return Result.fail("Document not open or file not found", "Open a document and provide valid file path", "INVALID_INPUT")

        doc.save_state_for_undo()
        name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            data = f.read()

        doc.doc.embfile_add(name, data, desc=description or name)
        doc.is_modified = True
        return Result.ok(True)

    @staticmethod
    def extract_attachment(doc: PDFDocument, name: str, output_path: str) -> Result[bool]:
        """Extracts an embedded file and saves it to disk."""
        if not doc.is_open:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")

        try:
            data = doc.doc.embfile_get(name)
            with open(output_path, "wb") as f:
                f.write(data)
            return Result.ok(True)
        except Exception as e:
            logger = __import__("logging").getLogger(__name__)
            logger.exception("Extract attachment error")
            return Result.from_exception(e, "Failed to extract attachment", "EXTRACT_FAILED")

    @staticmethod
    def delete_attachment(doc: PDFDocument, name: str) -> Result[bool]:
        """Deletes an embedded file from the PDF document."""
        if not doc.is_open:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")

        doc.save_state_for_undo()
        try:
            doc.doc.embfile_del(name)
            doc.is_modified = True
            return Result.ok(True)
        except Exception as e:
            logger = __import__("logging").getLogger(__name__)
            logger.exception("Extract attachment error")
            return Result.from_exception(e, "Failed to extract attachment", "EXTRACT_FAILED")
