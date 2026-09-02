"""
NeNgi PDF - Format Conversion Utilities
Exports PDF pages as PNG/JPG and converts image collections into PDF.
"""

from __future__ import annotations
import os
from typing import List
from PIL import Image
import pymupdf as fitz
from .pdf_document import PDFDocument


class FormatConverter:
    """Converts between PDF and image formats."""

    @staticmethod
    def export_page_as_image(doc: PDFDocument, page_num: int, output_path: str, dpi: int = 300) -> bool:
        """Exports a single PDF page to an image file (PNG/JPG)."""
        if not doc.is_open:
            return False
        try:
            page = doc.get_page(page_num)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(output_path)
            return True
        except Exception as e:
            print(f"Export page image error: {e}")
            return False

    @staticmethod
    def export_all_pages(doc: PDFDocument, output_dir: str, format_ext: str = "png", dpi: int = 300) -> List[str]:
        """Exports all pages of a PDF to image files in output_dir."""
        results = []
        if not doc.is_open:
            return results

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(doc.file_path or "document"))[0]

        for i in range(doc.page_count):
            filename = f"{base_name}_sayfa_{i + 1:03d}.{format_ext}"
            out_file = os.path.join(output_dir, filename)
            if FormatConverter.export_page_as_image(doc, i, out_file, dpi=dpi):
                results.append(out_file)

        return results

    @staticmethod
    def images_to_pdf(image_paths: List[str], output_pdf_path: str) -> bool:
        """Converts a list of images into a single PDF."""
        if not image_paths:
            return False
        try:
            pdf_doc = fitz.open()
            for img_path in image_paths:
                img = fitz.open(img_path)
                rect = img[0].rect
                pdfbytes = img.convert_to_pdf()
                img.close()
                
                img_pdf = fitz.open("pdf", pdfbytes)
                page = pdf_doc.new_page(width=rect.width, height=rect.height)
                page.show_pdf_page(rect, img_pdf, 0)
                img_pdf.close()

            pdf_doc.save(output_pdf_path, garbage=3, deflate=True)
            pdf_doc.close()
            return True
        except Exception as e:
            print(f"Images to PDF conversion error: {e}")
            return False
