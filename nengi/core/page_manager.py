
"""
NeNgi PDF - Page Management Utilities
Reordering, rotating, deleting, inserting blank/external pages, merging, and splitting.
"""

from __future__ import annotations
from typing import Any
from typing import List, Optional
import fitz
from .pdf_document import PDFDocument
from nengi.core.result import Result


class PageManager:
    """Helper class for structural PDF page operations."""

    @staticmethod
    def rotate_pages(doc: PDFDocument, page_indices: List[int], angle_delta: int = 90) -> Result[None]:
        """Rotates specified pages by angle_delta degrees."""
        for idx in page_indices:
            result = doc.rotate_page(idx, angle_delta)
            if not result:
                return Result.fail(result.error, result.hint, result.error_code)
        return Result.ok(None)

    @staticmethod
    def delete_pages(doc: PDFDocument, page_indices: List[int]) -> Result[bool]:
        """Deletes specified pages (sorted in reverse order to keep indices stable)."""
        if doc.page_count - len(page_indices) < 1:
            return Result.fail("Cannot delete all pages", "At least one page must remain", "CANNOT_DELETE_ALL")

        sorted_indices = sorted(page_indices, reverse=True)
        for idx in sorted_indices:
            result = doc.delete_page(idx)
            if not result:
                return Result.fail(result.error, result.hint, result.error_code)
        return Result.ok(True)

    @staticmethod
    def move_page(doc: PDFDocument, from_idx: int, to_idx: int) -> Result[bool]:
        """Moves a single page."""
        return doc.move_page(from_idx, to_idx)

    @staticmethod
    def insert_blank_page(doc: PDFDocument, at_index: int = -1, width: float = 595.0, height: float = 842.0) -> Result[int]:
        """Inserts a new blank A4 page."""
        return doc.insert_blank_page(at_index, width, height)

    @staticmethod
    def merge_pdf_files(file_paths: List[str], output_path: str) -> Result[bool]:
        """Merges multiple PDF files into one output PDF."""
        merged_doc = None
        try:
            merged_doc = fitz.open()
            for path in file_paths:
                sub_doc = fitz.open(path)
                try:
                    merged_doc.insert_pdf(sub_doc)
                finally:
                    sub_doc.close()
            merged_doc.save(output_path, garbage=3, deflate=True)
            return Result.ok(True)
        except fitz.FileDataError as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("FileDataError merging PDFs")
            return Result.from_exception(e, "One or more source PDFs may be corrupted", "FILE_DATA_ERROR")
        except FileNotFoundError as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("File not found")
            return Result.from_exception(e, "One or more source files not found", "FILE_NOT_FOUND")
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Merge error")
            return Result.from_exception(e, "Failed to merge PDFs", "MERGE_FAILED")
        finally:
            if merged_doc is not None:
                merged_doc.close()

    @staticmethod
    def extract_pages(doc: PDFDocument, page_indices: List[int], output_path: str) -> Result[bool]:
        """Extracts specified pages to a new standalone PDF."""
        if not doc.is_open or not page_indices:
            return Result.fail("Document not open or no pages specified", "Open a document and select pages", "INVALID_INPUT")
        new_doc = None
        try:
            new_doc = fitz.open()
            for idx in page_indices:
                new_doc.insert_pdf(doc.doc, from_page=idx, to_page=idx)
            new_doc.save(output_path, garbage=3, deflate=True)
            return Result.ok(True)
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Extract error")
            return Result.from_exception(e, "Failed to extract pages", "EXTRACT_FAILED")
        finally:
            if new_doc is not None:
                new_doc.close()

    @staticmethod
    def split_document(doc: PDFDocument, mode: str, value: Any, output_dir: str, prefix: str = 'split') -> Result[bool]:
        """Splits PDF into multiple files.
        mode can be: 'page_count' (value=int), 'file_size' (value=MB), 'bookmarks' (value=None)
        """
        import os
        if not doc.is_open:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            total_pages = doc.page_count
            
            if mode == 'page_count':
                pages_per_file = int(value)
                if pages_per_file <= 0:
                    return Result.fail("Invalid page count", "Pages per file must be positive", "INVALID_VALUE")
                    
                file_idx = 1
                for start_page in range(0, total_pages, pages_per_file):
                    end_page = min(start_page + pages_per_file - 1, total_pages - 1)
                    new_doc = fitz.open()
                    try:
                        new_doc.insert_pdf(doc.doc, from_page=start_page, to_page=end_page)
                        out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                        new_doc.save(out_path, garbage=3, deflate=True)
                    finally:
                        new_doc.close()
                    file_idx += 1
                return Result.ok(True)
                
            elif mode == 'file_size':
                max_bytes = float(value) * 1024 * 1024
                
                start_page = 0
                file_idx = 1
                
                while start_page < total_pages:
                    new_doc = fitz.open()
                    try:
                        current_size = 0
                        added = False
                        for p in range(start_page, total_pages):
                            temp_doc = fitz.open()
                            try:
                                temp_doc.insert_pdf(doc.doc, from_page=p, to_page=p)
                                bz = temp_doc.tobytes()
                            finally:
                                temp_doc.close()
                            page_size = len(bz)

                            if current_size + page_size > max_bytes and added:
                                break

                            new_doc.insert_pdf(doc.doc, from_page=p, to_page=p)
                            current_size += page_size
                            start_page = p + 1
                            added = True

                        out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                        new_doc.save(out_path, garbage=3, deflate=True)
                    finally:
                        new_doc.close()
                    file_idx += 1
                
                return Result.ok(True)
                
            elif mode == 'bookmarks':
                toc = doc.doc.get_toc(simple=False)
                if not toc:
                    return Result.fail("No bookmarks found", "Document has no top-level bookmarks", "NO_BOOKMARKS")
                
                bookmarks = [t for t in toc if t[0] == 1] # Level 1
                if not bookmarks:
                    return Result.fail("No top-level bookmarks", "Document has no level-1 bookmarks", "NO_BOOKMARKS")
                    
                file_idx = 1
                for i, b in enumerate(bookmarks):
                    start_page = b[2] - 1
                    end_page = bookmarks[i+1][2] - 2 if i + 1 < len(bookmarks) else total_pages - 1
                    if start_page > end_page or start_page < 0:
                        continue

                    new_doc = fitz.open()
                    try:
                        new_doc.insert_pdf(doc.doc, from_page=start_page, to_page=end_page)
                        out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                        new_doc.save(out_path, garbage=3, deflate=True)
                    finally:
                        new_doc.close()
                    file_idx += 1
                
                return Result.ok(True)
                
            return Result.fail("Invalid split mode", "Use 'page_count', 'file_size', or 'bookmarks'", "INVALID_MODE")
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Split error")
            return Result.from_exception(e, "Failed to split document", "SPLIT_FAILED")

