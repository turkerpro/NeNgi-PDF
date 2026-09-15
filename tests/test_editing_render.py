"""Editing-render regression: dar kutuya uzun metin replace edilirken
kalıcı boş ekran (redact sil + insert çizme + True dön) olmamalı."""

import os
import tempfile

import fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.result import Result


def _make_doc(tmp_dir, stub_text="kisa not"):
    path = os.path.join(tmp_dir, "edit.pdf")
    d = fitz.open()
    d.new_page(width=595, height=842)
    d[0].insert_text(fitz.Point(50, 60), stub_text, fontsize=11)
    d.save(path)
    d.close()
    return PDFDocument(path)


def test_replace_long_text_into_narrow_box_stays_readable():
    tmp_dir = tempfile.mkdtemp(prefix="nengi_edit_")
    doc = _make_doc(tmp_dir)
    narrow = fitz.Rect(50, 50, 150, 65)  # dar kutu: 100x15
    long_text = (
        "Bu uzun bir yedek metindir ve dar kutuya sigmalidir "
        "duzgun sarmalama ve punto kuculme ile kaybolmamalidir"
    )
    result = doc.replace_text_block(0, narrow, long_text, fontsize=11.0)
    assert result.success
    ok = result.value
    page_text = doc.get_page(0).get_text("text")
    doc.close()
    assert ok is True
    # Yeni metin sayfada okunabilmeli (bos ekran regresyonu yok).
    assert "uzun bir yedek" in page_text


def test_overflow_never_returns_true_with_blank_page():
    tmp_dir = tempfile.mkdtemp(prefix="nengi_edit_")
    doc = _make_doc(tmp_dir)
    tiny = fitz.Rect(50, 820, 70, 830)  # sayfa altinda minik kutu
    token = "SIGMAYANDEVASA"
    giant = " ".join([token] * 800)
    result = doc.replace_text_block(0, tiny, giant, fontsize=11.0)
    ok = result.value if result and result.success else False
    page_text = doc.get_page(0).get_text("text")
    doc.close()
    if ok:
        # True döndüyse metin gerçekten çizilmiş olmalı (sessiz boşluk yok).
        assert token in page_text
    else:
        # False döndüyse redact otomatik undo ile geri alınmış olmalı:
        # boş ekran yok, orijinal stub yerinde, dev metin çizilmemiş.
        assert token not in page_text
        assert "kisa not" in page_text
