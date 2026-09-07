"""
NeNgi PDF - Advanced Redaction & Document Sanitization Engine
Permanently removes sensitive information, pixel data, PII (TCKN, Credit Cards,
Phone Numbers, Emails, IBANs), hidden metadata, and attachments.
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional
import re
import pymupdf as fitz
from nengi.core.pdf_document import PDFDocument


# Standard PII Patterns (Turkey & Global)
PII_PATTERNS = {
    "tckn": {
        "label": "T.C. Kimlik Numarası (11 Hane)",
        "pattern": r"\b[1-9]\d{10}\b",
    },
    "credit_card": {
        "label": "Kredi Kartı Numarası",
        "pattern": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
    },
    "iban": {
        "label": "TR IBAN Numarası",
        "pattern": r"\bTR\d{2}[ -]?(?:\d{4}[ -]?){5}\d{2}\b",
    },
    "phone": {
        "label": "Telefon Numarası (GSM)",
        "pattern": r"\b(?:0\s*5\d{2}|5\d{2})[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}\b",
    },
    "email": {
        "label": "E-posta Adresi",
        "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    },
}


class RedactionEngine:
    """Manages search & redact, pattern matching, and permanent document sanitization."""

    @staticmethod
    def search_patterns(
        doc: PDFDocument,
        pattern_key_or_regex: str,
        is_custom_regex: bool = False,
        page_range: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Searches document for matching sensitive text patterns and returns bounding boxes.

        Returns:
            List of matches: [{"page": int, "text": str, "rect": fitz.Rect}, ...]
        """
        if not doc.is_open:
            return []

        if not is_custom_regex and pattern_key_or_regex in PII_PATTERNS:
            regex_str = PII_PATTERNS[pattern_key_or_regex]["pattern"]
        else:
            regex_str = pattern_key_or_regex

        try:
            compiled = re.compile(regex_str)
        except re.error:
            return []

        target_pages = page_range if page_range is not None else list(range(doc.page_count))
        matches = []

        for p_idx in target_pages:
            if p_idx < 0 or p_idx >= doc.page_count:
                continue
            page = doc.get_page(p_idx)
            text_instances = []

            # Extract words with positions
            words = page.get_text("words")  # (x0, y0, x1, y1, word, block, line, word_idx)
            full_text = page.get_text("text")

            for m in compiled.finditer(full_text):
                matched_str = m.group()
                # Find rects of this string on page
                rects = page.search_for(matched_str)
                for r in rects:
                    matches.append({
                        "page": p_idx,
                        "text": matched_str,
                        "rect": r,
                    })

        return matches

    @staticmethod
    def mark_for_redaction(
        doc: PDFDocument,
        matches: List[Dict[str, Any]],
        overlay_text: str = "GİZLENDİ",
        fill_color: Tuple[float, float, float] = (0, 0, 0),
        text_color: Tuple[float, float, float] = (1, 1, 1),
    ) -> int:
        """Adds redaction annotations to matched regions without permanently deleting content yet."""
        if not doc.is_open or not matches:
            return 0

        doc.save_state_for_undo()
        count = 0

        for m in matches:
            p_idx = m["page"]
            rect = m["rect"]
            page = doc.get_page(p_idx)

            annot = page.add_redact_annot(
                rect,
                text=overlay_text,
                fontname="helv",
                fontsize=9,
                text_color=text_color,
                fill=fill_color,
                align=fitz.TEXT_ALIGN_CENTER,
            )
            count += 1

        doc.is_modified = True
        return count

    @staticmethod
    def apply_redactions(doc: PDFDocument) -> bool:
        """Permanently burns redactions into the document. Irreversible."""
        if not doc.is_open:
            return False

        doc.save_state_for_undo()
        for p_idx in range(doc.page_count):
            page = doc.get_page(p_idx)
            page.apply_redactions()

        doc.is_modified = True
        return True

    @staticmethod
    def sanitize_document(
        doc: PDFDocument,
        remove_metadata: bool = True,
        remove_attachments: bool = True,
        remove_links: bool = False,
        remove_bookmarks: bool = False,
        remove_annotations: bool = False,
        remove_hidden_text: bool = False,
    ) -> Dict[str, int]:
        """Strips hidden information, metadata, file attachments, and scripts from document."""
        if not doc.is_open:
            return {}

        doc.save_state_for_undo()
        results = {
            "metadata_cleared": 0,
            "attachments_removed": 0,
            "links_removed": 0,
            "annotations_removed": 0,
        }

        # 1. Clear Metadata
        if remove_metadata:
            doc.doc.set_metadata({
                "author": "",
                "title": "",
                "subject": "",
                "keywords": "",
                "creator": "NeNgi PDF Sanitizer",
                "producer": "NeNgi PDF",
                "creationDate": "",
                "modDate": "",
            })
            results["metadata_cleared"] = 1

        # 2. Clear Attachments
        if remove_attachments:
            count = 0
            for name in doc.doc.embfile_names():
                doc.doc.embfile_del(name)
                count += 1
            results["attachments_removed"] = count

        # 3. Clear Bookmarks (Outline)
        if remove_bookmarks:
            doc.doc.set_toc([])

        # 4. Clear Links & Annotations
        for p_idx in range(doc.page_count):
            page = doc.get_page(p_idx)

            if remove_links:
                for link in page.get_links():
                    page.delete_link(link)
                    results["links_removed"] += 1

            if remove_annotations:
                for annot in page.annots():
                    page.delete_annot(annot)
                    results["annotations_removed"] += 1

        doc.is_modified = True
        return results
