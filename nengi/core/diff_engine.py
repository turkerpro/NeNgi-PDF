"""
NeNgi PDF - High Precision Text DIFF Engine
Performs word-by-word diff analysis between two PDF documents,
computes bounding box highlight rectangles (added/deleted/modified),
and generates a structured difference navigation model.
"""

from __future__ import annotations
import difflib
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import pymupdf as fitz
from .pdf_document import PDFDocument


@dataclass
class DiffHighlight:
    """Represents a highlighted change rectangle on a specific page."""
    page_num: int
    rect: fitz.Rect
    diff_type: str  # "added" (green), "deleted" (red), "modified" (yellow/orange)
    text: str


@dataclass
class DiffChangeItem:
    """Represents a unified change item linking original and revised documents."""
    change_id: int
    diff_type: str  # "added", "deleted", "modified"
    page_a: Optional[int]
    page_b: Optional[int]
    rects_a: List[fitz.Rect]
    rects_b: List[fitz.Rect]
    text_a: str
    text_b: str
    description: str


class DiffEngine:
    """Compares two PDF documents and extracts visual text differences."""

    def __init__(self, doc_a: PDFDocument, doc_b: PDFDocument):
        self.doc_a = doc_a
        self.doc_b = doc_b
        self.changes: List[DiffChangeItem] = []
        self.highlights_a: Dict[int, List[DiffHighlight]] = {}  # page -> highlights
        self.highlights_b: Dict[int, List[DiffHighlight]] = {}  # page -> highlights

    def run_diff(self) -> List[DiffChangeItem]:
        """Runs the comparison across all pages of both documents."""
        self.changes.clear()
        self.highlights_a.clear()
        self.highlights_b.clear()

        max_pages = max(self.doc_a.page_count, self.doc_b.page_count)
        change_counter = 1

        for page_idx in range(max_pages):
            has_page_a = page_idx < self.doc_a.page_count
            has_page_b = page_idx < self.doc_b.page_count

            words_a = self.doc_a.get_page_text_words(page_idx) if has_page_a else []
            words_b = self.doc_b.get_page_text_words(page_idx) if has_page_b else []

            tokens_a = [w[4] for w in words_a]
            tokens_b = [w[4] for w in words_b]

            matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)

            page_highlights_a: List[DiffHighlight] = []
            page_highlights_b: List[DiffHighlight] = []

            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    continue

                sub_words_a = words_a[i1:i2]
                sub_words_b = words_b[j1:j2]

                rects_a = [fitz.Rect(w[0], w[1], w[2], w[3]) for w in sub_words_a]
                rects_b = [fitz.Rect(w[0], w[1], w[2], w[3]) for w in sub_words_b]

                text_a = " ".join(tokens_a[i1:i2])
                text_b = " ".join(tokens_b[j1:j2])

                diff_type = tag
                if tag == "delete":
                    desc = f"Silindi: '{text_a}'"
                    for r in rects_a:
                        page_highlights_a.append(DiffHighlight(page_idx, r, "deleted", text_a))
                elif tag == "insert":
                    desc = f"Eklendi: '{text_b}'"
                    for r in rects_b:
                        page_highlights_b.append(DiffHighlight(page_idx, r, "added", text_b))
                elif tag == "replace":
                    desc = f"Değişti: '{text_a}' ➔ '{text_b}'"
                    for r in rects_a:
                        page_highlights_a.append(DiffHighlight(page_idx, r, "modified", text_a))
                    for r in rects_b:
                        page_highlights_b.append(DiffHighlight(page_idx, r, "modified", text_b))
                else:
                    continue

                item = DiffChangeItem(
                    change_id=change_counter,
                    diff_type=diff_type,
                    page_a=page_idx if has_page_a else None,
                    page_b=page_idx if has_page_b else None,
                    rects_a=rects_a,
                    rects_b=rects_b,
                    text_a=text_a,
                    text_b=text_b,
                    description=desc
                )
                self.changes.append(item)
                change_counter += 1

            if page_highlights_a:
                self.highlights_a[page_idx] = page_highlights_a
            if page_highlights_b:
                self.highlights_b[page_idx] = page_highlights_b

        return self.changes

    def get_highlights_for_page(self, doc_side: str, page_idx: int) -> List[DiffHighlight]:
        """Returns list of highlight rectangles for a specific page of Doc A or B."""
        if doc_side == "A":
            return self.highlights_a.get(page_idx, [])
        return self.highlights_b.get(page_idx, [])

    @property
    def summary_counts(self) -> Dict[str, int]:
        """Returns summary counts of changes."""
        counts = {"insert": 0, "delete": 0, "replace": 0, "total": len(self.changes)}
        for c in self.changes:
            if c.diff_type in counts:
                counts[c.diff_type] += 1
        return counts
