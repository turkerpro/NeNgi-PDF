"""
NeNgi PDF - Page Management Utilities
Reordering, rotating, deleting, inserting blank/external pages, merging, and splitting.
"""

from __future__ import annotations
from typing import List, Optional
import pymupdf as fitz
from .pdf_document import PDFDocument


class PageManager:
    """Helper class for structural PDF page operations."""

    @staticmethod
    def rotate_pages(doc: PDFDocument, page_indices: List[int], angle_delta: int = 90) -> None:
        """Rotates specified pages by angle_delta degrees."""
        for idx in page_indices:
            doc.rotate_page(idx, angle_delta)

    @staticmethod
    def delete_pages(doc: PDFDocument, page_indices: List[int]) -> bool:
        """Deletes specified pages (sorted in reverse order to keep indices stable)."""
        if doc.page_count - len(page_indices) < 1:
            return False  # Cannot delete all pages

        sorted_indices = sorted(page_indices, reverse=True)
        for idx in sorted_indices:
            doc.delete_page(idx)
        return True

    @staticmethod
    def move_page(doc: PDFDocument, from_idx: int, to_idx: int) -> bool:
        """Moves a single page."""
        return doc.move_page(from_idx, to_idx)

    @staticmethod
    def insert_blank_page(doc: PDFDocument, at_index: int = -1, width: float = 595.0, height: float = 842.0) -> int:
        """Inserts a new blank A4 page."""
        return doc.insert_blank_page(at_index, width, height)

    @staticmethod
    def merge_pdf_files(file_paths: List[str], output_path: str) -> bool:
        """Merges multiple PDF files into one output PDF."""
        try:
            merged_doc = fitz.open()
            for path in file_paths:
                sub_doc = fitz.open(path)
                merged_doc.insert_pdf(sub_doc)
                sub_doc.close()
            merged_doc.save(output_path, garbage=3, deflate=True)
            merged_doc.close()
            return True
        except Exception as e:
            print(f"Merge error: {e}")
            return False

    @staticmethod
    def extract_pages(doc: PDFDocument, page_indices: List[int], output_path: str) -> bool:
        """Extracts specified pages to a new standalone PDF."""
        if not doc.is_open or not page_indices:
            return False
        try:
            new_doc = fitz.open()
            for idx in page_indices:
                new_doc.insert_pdf(doc.doc, from_page=idx, to_page=idx)
            new_doc.save(output_path, garbage=3, deflate=True)
            new_doc.close()
            return True
        except Exception as e:
            print(f"Extract error: {e}")
            return False
