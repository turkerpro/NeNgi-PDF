
"""
NeNgi PDF - Page Management Utilities
Reordering, rotating, deleting, inserting blank/external pages, merging, and splitting.
"""

from __future__ import annotations
from typing import Any
from typing import List, Optional
import fitz
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

    @staticmethod
    def split_document(doc: PDFDocument, mode: str, value: Any, output_dir: str, prefix: str = 'split') -> bool:
        """Splits PDF into multiple files.
        mode can be: 'page_count' (value=int), 'file_size' (value=MB), 'bookmarks' (value=None)
        """
        import os
        if not doc.is_open:
            return False
        
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            total_pages = doc.page_count
            
            if mode == 'page_count':
                pages_per_file = int(value)
                if pages_per_file <= 0:
                    return False
                    
                file_idx = 1
                for start_page in range(0, total_pages, pages_per_file):
                    end_page = min(start_page + pages_per_file - 1, total_pages - 1)
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc.doc, from_page=start_page, to_page=end_page)
                    out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                    new_doc.save(out_path, garbage=3, deflate=True)
                    new_doc.close()
                    file_idx += 1
                return True
                
            elif mode == 'file_size':
                # Splitting by file size is complex, usually involves binary search or estimating page size.
                # A basic implementation could just split page by page and check size, but that's slow.
                # We'll do a simple estimation here: (doc_size / total_pages)
                max_bytes = float(value) * 1024 * 1024
                
                start_page = 0
                file_idx = 1
                
                while start_page < total_pages:
                    new_doc = fitz.open()
                    current_size = 0
                    added = False
                    for p in range(start_page, total_pages):
                        # Approximate size: save memory doc and check len
                        temp_doc = fitz.open()
                        temp_doc.insert_pdf(doc.doc, from_page=p, to_page=p)
                        bz = temp_doc.tobytes()
                        page_size = len(bz)
                        temp_doc.close()
                        
                        if current_size + page_size > max_bytes and added:
                            break
                        
                        new_doc.insert_pdf(doc.doc, from_page=p, to_page=p)
                        current_size += page_size
                        start_page = p + 1
                        added = True
                    
                    out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                    new_doc.save(out_path, garbage=3, deflate=True)
                    new_doc.close()
                    file_idx += 1
                
                return True
                
            elif mode == 'bookmarks':
                # Split by top-level bookmarks
                toc = doc.doc.get_toc(simple=False)
                if not toc:
                    return False
                
                bookmarks = [t for t in toc if t[0] == 1] # Level 1
                if not bookmarks:
                    return False
                    
                file_idx = 1
                for i, b in enumerate(bookmarks):
                    start_page = b[2] - 1
                    end_page = bookmarks[i+1][2] - 2 if i + 1 < len(bookmarks) else total_pages - 1
                    if start_page > end_page or start_page < 0:
                        continue
                        
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc.doc, from_page=start_page, to_page=end_page)
                    out_path = os.path.join(output_dir, f"{prefix}_{file_idx}.pdf")
                    new_doc.save(out_path, garbage=3, deflate=True)
                    new_doc.close()
                    file_idx += 1
                
                return True
                
            return False
        except Exception as e:
            print(f"Split error: {e}")
            return False

