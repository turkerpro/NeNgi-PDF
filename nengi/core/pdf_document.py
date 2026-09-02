"""
NeNgi PDF - Core PDF Document Management
Handles reading, rendering, saving, editing, image extraction/replacement,
and annotations using PyMuPDF (fitz).
"""

from __future__ import annotations
import os
import io
from typing import List, Tuple, Dict, Any, Optional
import pymupdf as fitz
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap


class PDFDocument:
    """Wrapper around PyMuPDF Document providing high-level PDF manipulation."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self.doc: Optional[fitz.Document] = None
        self.is_modified: bool = False
        self.is_encrypted: bool = False
        self.is_authenticated: bool = False
        
        if file_path:
            self.open(file_path)

    def open(self, file_path: str, password: Optional[str] = None) -> bool:
        """Opens a PDF file, checking for encryption."""
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.is_modified = False
        self.is_encrypted = self.doc.is_encrypted

        if self.is_encrypted:
            if password:
                self.is_authenticated = self.doc.authenticate(password) > 0
            else:
                self.is_authenticated = False
        else:
            self.is_authenticated = True

        return self.is_authenticated

    def authenticate(self, password: str) -> bool:
        """Attempts to authenticate an encrypted document."""
        if not self.doc or not self.is_encrypted:
            return True
        success = self.doc.authenticate(password) > 0
        self.is_authenticated = success
        return success

    @property
    def is_open(self) -> bool:
        return self.doc is not None and not self.doc.is_closed

    @property
    def page_count(self) -> int:
        return len(self.doc) if self.is_open else 0

    def get_page(self, page_number: int) -> fitz.Page:
        """Returns a PyMuPDF Page object (0-indexed)."""
        if not self.is_open or page_number < 0 or page_number >= self.page_count:
            raise IndexError(f"Page index {page_number} out of range (total: {self.page_count})")
        return self.doc[page_number]

    def render_page_qimage(self, page_number: int, zoom: float = 1.0) -> QImage:
        """Renders a page at the specified zoom level into a PyQt6 QImage."""
        page = self.get_page(page_number)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # FormatRGB888 is compatible with pix.samples
        qimg = QImage(
            pix.samples,
            pix.width,
            pix.height,
            pix.stride,
            QImage.Format.Format_RGB888
        )
        return qimg.copy()

    def render_page_pixmap(self, page_number: int, zoom: float = 1.0) -> QPixmap:
        """Renders a page at the specified zoom level into a PyQt6 QPixmap."""
        qimg = self.render_page_qimage(page_number, zoom)
        return QPixmap.fromImage(qimg)

    def get_page_text_words(self, page_number: int) -> List[Tuple[float, float, float, float, str, int, int, int]]:
        """
        Extracts words with their bounding boxes:
        Returns list of tuples: (x0, y0, x1, y1, word_str, block_no, line_no, word_no)
        """
        page = self.get_page(page_number)
        return page.get_text("words")

    def get_page_text(self, page_number: int) -> str:
        """Returns full text of a page."""
        page = self.get_page(page_number)
        return page.get_text("text")

    def get_page_images(self, page_number: int) -> List[Dict[str, Any]]:
        """
        Returns all embedded images on a page with their xref and bounding boxes.
        """
        page = self.get_page(page_number)
        image_list = page.get_images(full=True)
        results = []

        for img_info in image_list:
            xref = img_info[0]
            rects = page.get_image_rects(xref)
            bbox = rects[0] if rects else None
            
            results.append({
                "xref": xref,
                "name": img_info[7],
                "width": img_info[2],
                "height": img_info[3],
                "bpc": img_info[4],
                "colorspace": img_info[5],
                "bbox": bbox
            })
        return results

    def extract_image_bytes(self, xref: int) -> Tuple[bytes, str]:
        """Extracts raw image bytes and file extension for an embedded image."""
        if not self.is_open:
            raise ValueError("Document not open")
        base_image = self.doc.extract_image(xref)
        return base_image["image"], base_image["ext"]

    def replace_image(self, xref: int, new_image_path: str) -> bool:
        """
        Replaces an embedded image (by xref) with a new image file in-place!
        This updates all pages displaying this image.
        """
        if not self.is_open:
            return False

        try:
            with open(new_image_path, "rb") as f:
                new_image_bytes = f.read()

            self.doc.update_stream(xref, new_image_bytes)
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error replacing image xref {xref}: {e}")
            return False

    def replace_page_with_scanned_image(self, page_number: int, image_path: str) -> bool:
        """
        Replaces a full scanned page's content with an edited image.
        """
        if not self.is_open:
            return False

        try:
            page = self.get_page(page_number)
            rect = page.rect
            
            imgs = self.get_page_images(page_number)
            if imgs:
                return self.replace_image(imgs[0]["xref"], image_path)
            else:
                page.insert_image(rect, filename=image_path, overlay=True)
                self.is_modified = True
                return True
        except Exception as e:
            print(f"Error replacing page with image: {e}")
            return False

    def whiteout_area(self, page_number: int, rect: fitz.Rect, fill_color: Tuple[float, float, float] = (1, 1, 1)) -> bool:
        """
        Draws an opaque rectangle to whiteout / erase unwanted marks/drawings.
        Coordinates are in PDF points.
        """
        if not self.is_open:
            return False
        try:
            page = self.get_page(page_number)
            page.add_redact_annot(rect, fill=fill_color)
            page.apply_redactions()
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error whiting out area: {e}")
            return False

    def add_text(self, page_number: int, point: Tuple[float, float], text: str, 
                 fontsize: float = 12.0, fontname: str = "helv", 
                 color: Tuple[float, float, float] = (0, 0, 0)) -> bool:
        """Inserts text at a specific coordinate on the page."""
        if not self.is_open:
            return False
        try:
            page = self.get_page(page_number)
            page.insert_text(fitz.Point(point[0], point[1]), text, 
                             fontsize=fontsize, fontname=fontname, color=color)
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error inserting text: {e}")
            return False

    def add_image_stamp(self, page_number: int, rect: fitz.Rect, image_path: str) -> bool:
        """Places an image (e.g. signature, stamp) onto the page at specified rect."""
        if not self.is_open:
            return False
        try:
            page = self.get_page(page_number)
            page.insert_image(rect, filename=image_path, keep_proportion=True)
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error adding image stamp: {e}")
            return False

    def rotate_page(self, page_number: int, angle_delta: int = 90) -> int:
        """Rotates a page by angle_delta (e.g. 90, -90, 180). Returns new rotation."""
        page = self.get_page(page_number)
        current_rot = page.rotation
        new_rot = (current_rot + angle_delta) % 360
        page.set_rotation(new_rot)
        self.is_modified = True
        return new_rot

    def delete_page(self, page_number: int) -> bool:
        """Deletes a page from the document."""
        if not self.is_open or self.page_count <= 1:
            return False
        self.doc.delete_page(page_number)
        self.is_modified = True
        return True

    def move_page(self, from_index: int, to_index: int) -> bool:
        """Moves a page from one index to another."""
        if not self.is_open or from_index == to_index:
            return False
        self.doc.move_page(from_index, to_index)
        self.is_modified = True
        return True

    def insert_blank_page(self, index: int = -1, width: float = 595.0, height: float = 842.0) -> int:
        """Inserts a blank page (default A4: 595 x 842 pt). Returns new page index."""
        if not self.is_open:
            return -1
        idx = self.doc.insert_page(index, width=width, height=height)
        self.is_modified = True
        return idx

    def insert_file(self, file_path: str, at_index: int = -1) -> bool:
        """Inserts pages from an external PDF."""
        if not self.is_open:
            return False
        try:
            other_doc = fitz.open(file_path)
            self.doc.insert_pdf(other_doc, start_at=at_index if at_index >= 0 else self.page_count)
            other_doc.close()
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error inserting external PDF: {e}")
            return False

    def save(self, target_path: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Saves changes to target_path or overwrites original file safely.
        Optionally encrypts with password.
        """
        if not self.is_open:
            return False

        save_path = target_path or self.file_path
        if not save_path:
            return False

        try:
            encrypt_kw = {}
            if password:
                encrypt_kw = {
                    "encryption": fitz.PDF_ENCRYPT_AES_256,
                    "owner_pw": password,
                    "user_pw": password,
                    "permissions": fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY | fitz.PDF_PERM_ANNOTATE
                }

            if save_path == self.file_path:
                temp_path = save_path + ".nengi_temp"
                self.doc.save(temp_path, garbage=3, deflate=True, **encrypt_kw)
                self.doc.close()
                os.replace(temp_path, save_path)
                self.open(save_path, password=password)
            else:
                self.doc.save(save_path, garbage=3, deflate=True, **encrypt_kw)
                self.file_path = save_path

            self.is_modified = False
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False

    def close(self):
        """Closes the document."""
        if self.is_open:
            self.doc.close()
            self.doc = None
            self.file_path = None
            self.is_modified = False
