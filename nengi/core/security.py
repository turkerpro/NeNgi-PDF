"""
NeNgi PDF - PDF Security & Encryption Handler
Supports password protection (AES-256) and removing protection.
"""

from __future__ import annotations
from typing import Optional
import fitz
from .pdf_document import PDFDocument


class SecurityManager:
    """Handles password protection and decryption."""

    @staticmethod
    def encrypt_document(doc: PDFDocument, password: str, output_path: Optional[str] = None,
                         owner_pw: Optional[str] = None, permissions: Optional[int] = None) -> bool:
        """Protects PDF with AES-256 password (user/owner separation + permission flags).

        :param doc: open PDFDocument.
        :param password: user password (required to open the document).
        :param output_path: target file; defaults to in-place overwrite of doc.file_path.
        :param owner_pw: owner password (full rights); defaults to ``password``.
        :param permissions: PDF permission bitmask (e.g. fitz.PDF_PERM_PRINT | ...);
            defaults to PRINT | COPY | ANNOTATE.
        """
        if not getattr(doc, "is_open", False) or doc.doc is None:
            return False
        save_path = output_path or getattr(doc, "file_path", None)
        if not save_path:
            return False
        user_pw = password
        resolved_owner_pw = owner_pw if owner_pw is not None else password
        if permissions is None:
            permissions = (getattr(fitz, "PDF_PERM_PRINT", 4)
                           | getattr(fitz, "PDF_PERM_COPY", 16)
                           | getattr(fitz, "PDF_PERM_ANNOTATE", 32))
        encryption = getattr(fitz, "PDF_ENCRYPT_AES_256", 4)
        try:
            import os as _os
            encrypt_kw = {
                "encryption": encryption,
                "owner_pw": resolved_owner_pw,
                "user_pw": user_pw,
                "permissions": permissions,
            }
            if save_path == getattr(doc, "file_path", None):
                temp_path = save_path + ".nengi_temp"
                doc.doc.save(temp_path, garbage=3, deflate=True, **encrypt_kw)
                doc.doc.close()
                _os.replace(temp_path, save_path)
                doc.open(save_path, password=user_pw)
            else:
                doc.doc.save(save_path, garbage=3, deflate=True, **encrypt_kw)
                doc.file_path = save_path
            doc.is_modified = False
            return True
        except Exception as e:
            print(f"Error encrypting PDF: {e}")
            return False

    @staticmethod
    def remove_password(doc: PDFDocument, output_path: str) -> bool:
        """Removes encryption from an authenticated PDF and saves a decrypted copy."""
        if not doc.is_open or not doc.is_authenticated:
            return False
        try:
            # Saving without encryption parameters strips the password
            doc.doc.save(output_path, encryption=getattr(fitz, "PDF_ENCRYPT_NONE", 0), garbage=3, deflate=True)
            return True
        except Exception as e:
            print(f"Error removing password: {e}")
            return False
