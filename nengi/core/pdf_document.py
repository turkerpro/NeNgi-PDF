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
import sys

_cached_font_buffer: Optional[bytes] = None


def get_unicode_font_buffer() -> Optional[bytes]:
    """Finds and loads a TrueType font buffer that supports Turkish and Unicode characters."""
    global _cached_font_buffer
    if _cached_font_buffer is not None:
        return _cached_font_buffer

    candidates = []
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates.append(os.path.join(base_dir, "resources", "fonts", "LiberationSans-Regular.ttf"))
    if hasattr(sys, "_MEIPASS"):
        candidates.append(os.path.join(sys._MEIPASS, "resources", "fonts", "LiberationSans-Regular.ttf"))

    # Windows fonts
    candidates.extend([
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf"
    ])

    # Linux fonts
    candidates.extend([
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ])

    for p in candidates:
        if p and os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    _cached_font_buffer = f.read()
                    return _cached_font_buffer
            except Exception:
                pass
    return None


class PDFDocument:
    """Wrapper around PyMuPDF Document providing high-level PDF manipulation."""

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self.doc: Optional[fitz.Document] = None
        self.is_modified: bool = False
        self.is_encrypted: bool = False
        self.is_authenticated: bool = False
        self._undo_stack: List[bytes] = []
        self._redo_stack: List[bytes] = []
        self._max_history: int = 30
        
        if file_path:
            self.open(file_path)

    def save_state_for_undo(self):
        """Saves current document snapshot into in-memory undo stack."""
        if not self.is_open:
            return
        try:
            data = self.doc.tobytes(garbage=3, deflate=True)
            self._undo_stack.append(data)
            if len(self._undo_stack) > self._max_history:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
        except Exception as e:
            print(f"Could not save undo state: {e}")

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self) -> bool:
        """Restores previous document state."""
        if not self.can_undo():
            return False
        try:
            current_data = self.doc.tobytes(garbage=3, deflate=True)
            self._redo_stack.append(current_data)
            prev_data = self._undo_stack.pop()
            
            file_path = self.file_path
            self.doc.close()
            self.doc = fitz.open("pdf", prev_data)
            self.file_path = file_path
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error during undo: {e}")
            return False

    def redo(self) -> bool:
        """Restores next document state."""
        if not self.can_redo():
            return False
        try:
            current_data = self.doc.tobytes(garbage=3, deflate=True)
            self._undo_stack.append(current_data)
            next_data = self._redo_stack.pop()
            
            file_path = self.file_path
            self.doc.close()
            self.doc = fitz.open("pdf", next_data)
            self.file_path = file_path
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error during redo: {e}")
            return False

    def open(self, file_path: str, password: Optional[str] = None) -> bool:
        """Opens a PDF file, checking for encryption."""
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.is_modified = False
        self.is_encrypted = self.doc.is_encrypted
        self._undo_stack.clear()
        self._redo_stack.clear()

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
            self.save_state_for_undo()
            page = self.get_page(page_number)
            page.add_redact_annot(rect, fill=fill_color)
            page.apply_redactions()
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error whiting out area: {e}")
            return False

    def get_page_text_words(self, page_number: int) -> List[Tuple[float, float, float, float, str, int, int, int]]:
        """
        Returns list of words on page with coordinates:
        (x0, y0, x1, y1, word_text, block_no, line_no, word_no).
        """
        if not self.is_open:
            return []
        try:
            page = self.get_page(page_number)
            return page.get_text("words")
        except Exception:
            return []

    def get_page_blocks(self, page_number: int) -> List[Tuple[float, float, float, float, str, int, int]]:
        """
        Returns text paragraph blocks on page:
        (x0, y0, x1, y1, text, block_no, block_type).
        block_type == 0 is text.
        """
        if not self.is_open:
            return []
        try:
            page = self.get_page(page_number)
            blocks = page.get_text("blocks")
            return [b for b in blocks if b[6] == 0 and b[4].strip()]
        except Exception:
            return []

    def detect_text_style_at_rect(self, page_number: int, rect: fitz.Rect) -> dict:
        """
        Inspects spans within or intersecting rect to detect font family,
        font size, flags (bold/italic), and color.
        """
        default_style = {
            "family": "Arial",
            "size": 11.0,
            "is_bold": False,
            "is_italic": False,
            "color_rgb": (0.0, 0.0, 0.0),
            "raw_font": "Helvetica",
            "fitz_font": "helv"
        }
        if not self.is_open:
            return default_style

        try:
            page = self.get_page(page_number)
            d = page.get_text("dict")
            matching_spans = []
            for b in d.get("blocks", []):
                if "lines" in b:
                    for line in b["lines"]:
                        for span in line.get("spans", []):
                            span_rect = fitz.Rect(span["bbox"])
                            if span_rect.intersects(rect):
                                matching_spans.append(span)

            if not matching_spans:
                return default_style

            # Pick largest span as representative
            span = max(matching_spans, key=lambda s: len(s.get("text", "")))
            raw_font = span.get("font", "Helvetica")
            size = float(span.get("size", 11.0))
            color_int = span.get("color", 0)

            # Convert color int to RGB
            r = ((color_int >> 16) & 0xFF) / 255.0
            g = ((color_int >> 8) & 0xFF) / 255.0
            b_val = (color_int & 0xFF) / 255.0
            color_rgb = (r, g, b_val)

            # Analyze font name & flags
            raw_lower = raw_font.lower()
            flags = span.get("flags", 0)
            is_bold = bool(flags & 2**4) or any(k in raw_lower for k in ["bold", "black", "heavy", "medium"])
            is_italic = bool(flags & 2**1) or any(k in raw_lower for k in ["italic", "oblique"])

            clean_family = raw_font.split("+")[-1].split("-")[0].split(",")[0]
            if "arial" in raw_lower:
                family = "Arial"
                fitz_base = "helv"
            elif "times" in raw_lower:
                family = "Times New Roman"
                fitz_base = "times"
            elif "calibri" in raw_lower:
                family = "Calibri"
                fitz_base = "helv"
            elif "courier" in raw_lower or "mono" in raw_lower:
                family = "Courier New"
                fitz_base = "couri"
            elif "segoe" in raw_lower:
                family = "Segoe UI"
                fitz_base = "helv"
            elif "helv" in raw_lower:
                family = "Helvetica"
                fitz_base = "helv"
            else:
                family = clean_family
                fitz_base = "helv"

            # Determine fitz builtin fontname
            if fitz_base == "helv":
                fitz_font = "hebi" if is_bold and is_italic else ("hebo" if is_bold else ("heit" if is_italic else "helv"))
            elif fitz_base == "times":
                fitz_font = "tibi" if is_bold and is_italic else ("tibo" if is_bold else ("tiit" if is_italic else "tiro"))
            elif fitz_base == "couri":
                fitz_font = "cobi" if is_bold and is_italic else ("cobo" if is_bold else ("coit" if is_italic else "couri"))
            else:
                fitz_font = "helv"

            return {
                "family": family,
                "size": round(size, 1),
                "is_bold": is_bold,
                "is_italic": is_italic,
                "color_rgb": color_rgb,
                "raw_font": raw_font,
                "fitz_font": fitz_font
            }
        except Exception as e:
            print(f"Error detecting text style: {e}")
            return default_style

    def edit_text_at_rect(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontsize: Optional[float] = None, fontname: str = "helv", color: Tuple[float, float, float] = (0, 0, 0)
    ) -> bool:
        """
        Directly edits and replaces text at specified rect:
        1. Saves undo state.
        2. Whites out the original text bounding rectangle.
        3. Inserts new_text at the baseline coordinates with matching font size.
        """
        if not self.is_open:
            return False
        try:
            self.save_state_for_undo()
            page = self.get_page(page_number)
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            if fontsize is None:
                h = rect.y1 - rect.y0
                fontsize = max(7.0, min(36.0, h * 0.85))

            insert_point = fitz.Point(rect.x0, rect.y1 - 1.5)
            font_buf = get_unicode_font_buffer()
            target_font = fontname
            if font_buf:
                try:
                    page.insert_font(fontname="f_unicode", fontbuffer=font_buf)
                    target_font = "f_unicode"
                except Exception:
                    pass
            page.insert_text(insert_point, new_text, fontsize=fontsize, fontname=target_font, color=color)
            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error editing text at rect: {e}")
            return False

    def replace_text_block(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0)
    ) -> bool:
        """
        Replaces a paragraph or multi-line text block:
        1. Saves undo state.
        2. Applies whiteout redaction to the block rectangle.
        3. Inserts replacement text line by line preserving paragraph bounds.
        """
        if not self.is_open:
            return False
        try:
            self.save_state_for_undo()
            page = self.get_page(page_number)
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()

            font_buf = get_unicode_font_buffer()
            target_font = fontname
            if font_buf:
                try:
                    page.insert_font(fontname="f_unicode", fontbuffer=font_buf)
                    target_font = "f_unicode"
                except Exception:
                    pass

            lines = new_text.splitlines()
            line_height = fontsize * 1.25
            y_pos = rect.y0 + fontsize
            for line in lines:
                if y_pos > page.rect.height - 10:
                    break
                page.insert_text((rect.x0, y_pos), line, fontsize=fontsize, fontname=target_font, color=color)
                y_pos += line_height

            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error replacing text block: {e}")
            return False

    def insert_new_text(
        self, page_number: int, point: fitz.Point, text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0)
    ) -> bool:
        """
        Acrobat Pro style text insertion at point.
        Saves undo state and inserts text lines with full Turkish/Unicode support.
        """
        if not self.is_open:
            return False
        try:
            self.save_state_for_undo()
            page = self.get_page(page_number)

            font_buf = get_unicode_font_buffer()
            target_font = fontname
            if font_buf:
                try:
                    page.insert_font(fontname="f_unicode", fontbuffer=font_buf)
                    target_font = "f_unicode"
                except Exception:
                    pass

            lines = text.splitlines()
            line_height = fontsize * 1.25
            y_pos = point.y
            for line in lines:
                page.insert_text((point.x, y_pos), line, fontsize=fontsize, fontname=target_font, color=color)
                y_pos += line_height

            self.is_modified = True
            return True
        except Exception as e:
            print(f"Error inserting new text: {e}")
            return False

    def ocr_page(self, page_number: int) -> List[Tuple[float, float, float, float, str]]:
        """
        Runs OCR on a scanned page, extracts text blocks and coordinates,
        and embeds a searchable text layer onto the page.
        """
        if not self.is_open:
            return []
        try:
            # Check if RapidOCR is installed
            try:
                from rapidocr_onnxruntime import RapidOCR
                import numpy as np
                from PIL import Image
                ocr = RapidOCR()
                page = self.get_page(page_number)
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                results, _ = ocr(np.array(img))
                if not results:
                    return []
                
                scale_x = page.rect.width / pix.width
                scale_y = page.rect.height / pix.height

                recognized_items = []
                for box, text, score in results:
                    x0 = min(p[0] for p in box) * scale_x
                    y0 = min(p[1] for p in box) * scale_y
                    x1 = max(p[0] for p in box) * scale_x
                    y1 = max(p[1] for p in box) * scale_y
                    recognized_items.append((x0, y0, x1, y1, text))
                    
                    # Insert invisible/searchable text layer onto the page
                    h = y1 - y0
                    fs = max(6.0, min(32.0, h * 0.8))
                    page.insert_text(fitz.Point(x0, y1 - 1), text, fontsize=fs, fontname="helv", color=(0, 0, 0), render_mode=3)

                self.is_modified = True
                return recognized_items
            except ImportError:
                return []
        except Exception as e:
            print(f"Error running OCR: {e}")
            return []

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
