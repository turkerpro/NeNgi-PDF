"""
NeNgi PDF - Format Conversion Utilities
Exports PDF pages as PNG/JPG and converts image collections into PDF.
"""

from __future__ import annotations
import os
from typing import List
from PIL import Image
import fitz
from .pdf_document import PDFDocument
from nengi.core.result import Result


class FormatConverter:
    """Converts between PDF and image formats."""

    @staticmethod
    def export_page_as_image(doc: PDFDocument, page_num: int, output_path: str, dpi: int = 300) -> Result[bool]:
        """Exports a single PDF page to an image file (PNG/JPG)."""
        if not doc.is_open:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        try:
            page = doc.get_page(page_num)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            pix.save(output_path)
            return Result.ok(True)
        except IndexError as e:
            return Result.fail(str(e), "Page index out of range", "INVALID_PAGE")
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Export page image error")
            return Result.from_exception(e, "Failed to export page as image", "EXPORT_IMAGE_FAILED")

    @staticmethod
    def export_all_pages(doc: PDFDocument, output_dir: str, format_ext: str = "png", dpi: int = 300) -> Result[List[str]]:
        """Exports all pages of a PDF to image files in output_dir."""
        if not doc.is_open:
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(doc.file_path or "document"))[0]
        results = []

        for i in range(doc.page_count):
            filename = f"{base_name}_sayfa_{i + 1:03d}.{format_ext}"
            out_file = os.path.join(output_dir, filename)
            result = FormatConverter.export_page_as_image(doc, i, out_file, dpi=dpi)
            if result:
                results.append(out_file)

        return Result.ok(results)

    @staticmethod
    def images_to_pdf(image_paths: List[str], output_pdf_path: str) -> Result[bool]:
        """Converts a list of images into a single PDF."""
        if not image_paths:
            return Result.fail("No images provided", "Provide at least one image path", "NO_IMAGES")
        pdf_doc = None
        try:
            pdf_doc = fitz.open()
            for img_path in image_paths:
                img = fitz.open(img_path)
                try:
                    rect = img[0].rect
                    pdfbytes = img.convert_to_pdf()
                finally:
                    img.close()

                img_pdf = fitz.open("pdf", pdfbytes)
                try:
                    page = pdf_doc.new_page(width=rect.width, height=rect.height)
                    page.show_pdf_page(rect, img_pdf, 0)
                finally:
                    img_pdf.close()

            pdf_doc.save(output_pdf_path, garbage=3, deflate=True)
            return Result.ok(True)
        except FileNotFoundError as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Image file not found")
            return Result.from_exception(e, "One or more image files not found", "FILE_NOT_FOUND")
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Images to PDF conversion error")
            return Result.from_exception(e, "Failed to convert images to PDF", "CONVERT_FAILED")
        finally:
            if pdf_doc is not None:
                pdf_doc.close()
