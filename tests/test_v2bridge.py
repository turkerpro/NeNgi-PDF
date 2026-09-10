"""V2 kopru adaptorleri testleri: summary_bridge, visual_diff, pagespec."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import fitz
import pytest

from nengi.core.pagespec import parse_pagespec
from nengi.core.summary_bridge import analyze_pdf, summarize
from nengi.core.visual_diff import (
    compare_visual,
    save_visual_diff,
    visual_diff_as_diff_highlights,
    visual_diff_highlights,
)
from nengi.core.pdf_document import PDFDocument


def _make_pdf(path: Path, pages_texts: list[str]) -> Path:
    doc = fitz.open()
    for text in pages_texts:
        page = doc.new_page(width=595, height=842)
        y = 72.0
        for line in text.split("\n"):
            page.insert_text(fitz.Point(72, y), line, fontsize=12)
            y += 18
    doc.save(path)
    doc.close()
    return path


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    p = tmp_path / "sample.pdf"
    body = (
        "NeNgi PDF ozet testi. Bu belge extractive ozet algoritmasini dogrular. "
        "Ozet algoritmasi kelime frekanslarini skorlar ve en bilgilendirici cumleleri secer.\n"
        "Ikinci paragraf farkli kelimeler icerir. Ankara Istanbul Izmir gibi sehirler ornek verilir. "
        "Belge analizi sayfa kelime ve gorsel istatistiklerini hesaplar."
    )
    return _make_pdf(p, [body, "Kisa ikinci sayfa metni burada yer alir. " * 12])


# --- pagespec ---

def test_pagespec_basic():
    assert parse_pagespec("1-3,5") == [0, 1, 2, 4]


def test_pagespec_total_ok_and_overflow():
    assert parse_pagespec("1-3,5", total=5) == [0, 1, 2, 4]
    with pytest.raises(ValueError):
        parse_pagespec("1-3,5", total=4)


def test_pagespec_invalid():
    with pytest.raises(ValueError):
        parse_pagespec("0")
    with pytest.raises(ValueError):
        parse_pagespec("3-2")


# --- summary_bridge ---

def test_analyze_pdf_path(sample_pdf: Path):
    stats = analyze_pdf(sample_pdf)
    assert stats["pages"] == 2
    assert stats["words"] > 10
    assert stats["encrypted"] is False
    assert stats["is_scanned"] is False


def test_analyze_pdf_with_pdfdocument(sample_pdf: Path):
    doc = PDFDocument(str(sample_pdf))
    try:
        stats = analyze_pdf(doc)
        assert stats["pages"] == 2
        assert stats["words"] > 10
    finally:
        doc.close()


def test_summarize_path_and_document(sample_pdf: Path):
    out = summarize(sample_pdf, sentences=2)
    assert out["summary"].strip()
    assert isinstance(out["keywords"], list) and out["keywords"]

    doc = PDFDocument(str(sample_pdf))
    try:
        out2 = summarize(doc, sentences=2)
        assert out2["summary"].strip()
        assert isinstance(out2["keywords"], list)
    finally:
        doc.close()


# --- visual_diff ---

def test_compare_visual_identical(tmp_path: Path, sample_pdf: Path):
    images = compare_visual(sample_pdf, sample_pdf, dpi=72)
    assert len(images) == 2
    out = tmp_path / "diff.pdf"
    saved = save_visual_diff(images, out)
    assert Path(saved).exists() and os.path.getsize(saved) > 0


def test_visual_diff_highlights_changed(tmp_path: Path, sample_pdf: Path):
    other = tmp_path / "other.pdf"
    _make_pdf(other, ["Tamamen farkli bir icerik burada. " * 10, "Kisa ikinci sayfa metni burada yer alir. " * 12])
    hl = visual_diff_highlights(sample_pdf, other, dpi=72)
    assert hl, "farkli belgelerde highlight beklenir"
    for item in hl:
        assert set(item.keys()) >= {"page", "rect"}
        assert isinstance(item["rect"], fitz.Rect)

    same = visual_diff_highlights(sample_pdf, sample_pdf, dpi=72)
    assert same == []

    as_dh = visual_diff_as_diff_highlights(sample_pdf, other, dpi=72)
    assert as_dh and all(hasattr(h, "rect") and hasattr(h, "page_num") for h in as_dh)


def test_save_visual_diff_empty_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        save_visual_diff([], tmp_path / "x.pdf")
