"""
NeNgi PDF - PDF Security & Encryption Handler
Supports password protection (AES-256) and removing protection.
"""

from __future__ import annotations
from typing import Optional
import pymupdf as fitz
from .pdf_document import PDFDocument


class SecurityManager:
    """Handles password protection and decryption."""

    @staticmethod
    def encrypt_document(doc: PDFDocument, password: str, output_path: Optional[str] = None) -> bool:
        """Protects PDF with AES-256 password."""
        return doc.save(target_path=output_path, password=password)

    @staticmethod
    def remove_password(doc: PDFDocument, output_path: str) -> bool:
        """Removes encryption from an authenticated PDF and saves a decrypted copy."""
        if not doc.is_open or not doc.is_authenticated:
            return False
        try:
            # Saving without encryption parameters strips the password
            doc.doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE, garbage=3, deflate=True)
            return True
        except Exception as e:
            print(f"Error removing password: {e}")
            return False
