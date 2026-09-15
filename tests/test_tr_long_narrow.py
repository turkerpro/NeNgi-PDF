"""Dar kutuya uzun Türkçe metin replace edilince tam okunabilmeli.

Regresyon: commit dar pdf_rect gönderiyor, editör geniş kutuda farklı
satır kırıyor; ölçüm helv ile, yazım tr-sans ile yapılınca harfler
üst üste/devasa çıkıyordu. Bu test aynı gömülü fontla ölçüm+yazım
sonucu metnin get_text ile eksiksiz okunduğunu doğrular.
"""

import os
import tempfile

import fitz

from nengi.core.pdf_document import PDFDocument


def _make_doc(tmp_dir, stub_text="kısa not"):
    path = os.path.join(tmp_dir, "tr_narrow.pdf")
    d = fitz.open()
    d.new_page(width=595, height=842)
    d[0].insert_text(fitz.Point(50, 200), stub_text, fontsize=11)
    d.save(path)
    d.close()
    return PDFDocument(path)


def test_replace_long_turkish_text_narrow_box_fully_readable():
    tmp_dir = tempfile.mkdtemp(prefix="nengi_tr_narrow_")
    doc = _make_doc(tmp_dir)
    narrow = fitz.Rect(50, 50, 150, 65)  # dar kutu: 100x15
    long_text = (
        "Türkiye'de güneşli günlerde şeker pancarı işçileri çiğ köfte "
        "yoğurup şaşkın ördeği izlerken ılık süt içti; "
        "büyük ÇĞŞİÖÜ harfleri de kaybolmamalı"
    )
    result = doc.replace_text_block(0, narrow, long_text, fontsize=11.0)
    assert result.success, result
    assert result.value is True
    page_text = doc.get_page(0).get_text("text")
    doc.close()
    for token in (
        "Türkiye", "güneşli", "şeker", "pancarı", "çiğ",
        "köfte", "şaşkın", "ılık", "ÇĞŞİÖÜ",
    ):
        assert token in page_text, f"eksik token: {token!r}\n--- sayfa ---\n{page_text}"


def test_inline_editor_commit_sends_effective_rect():
    """Commit, orijinal dar rect yerine editörün GÜNCEL boyutundan
    türetilmiş rect (width()/zoom, height()/zoom, aynı origin) göndermeli."""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PyQt6.QtWidgets import QApplication
    from nengi.ui.inline_editor import InlineTextEditor

    app = QApplication.instance() or QApplication([])
    orig = fitz.Rect(50, 50, 150, 65)  # dar kutu: 100x15
    style = {
        "family": "Arial", "size": 11.0, "is_bold": False,
        "is_italic": False, "color_rgb": (0.0, 0.0, 0.0),
        "fitz_font": "helv",
    }
    zoom = 1.0
    ed = InlineTextEditor("merhaba dünya", style, orig, zoom)
    ed.resize(300, 200)  # kullanıcı kutuyu genişletti
    captured = {}

    def _slot(text, s, r, eff):
        captured["text"] = text
        captured["orig"] = fitz.Rect(r)
        captured["eff"] = fitz.Rect(eff)

    ed.editing_finished.connect(_slot)
    ed.commit()
    app.processEvents()
    assert captured.get("text") == "merhaba dünya"
    eff = captured["eff"]
    assert eff.x0 == orig.x0 and eff.y0 == orig.y0
    assert abs(eff.width - 300.0) < 2.0, f"eff width {eff.width} != 300"
    assert abs(eff.height - 200.0) < 2.0, f"eff height {eff.height} != 200"
    assert eff.width > orig.width
