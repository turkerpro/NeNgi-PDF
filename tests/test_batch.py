"""BatchEngine testleri: temp PDF klasörü + encrypt+watermark zinciri."""

import json
import os

import fitz

from nengi.core.batch_engine import BatchEngine
from nengi.core.pdf_document import PDFDocument


def _make_pdf(path: str, text: str = "Merhaba NeNgi batch testi"):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(50, 100), text, fontsize=14)
    doc.save(path)
    doc.close()


def test_encrypt_watermark_chain(tmp_path):
    """Temp klasördeki 2 PDF'e watermark+encrypt zinciri uygulanır."""
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()

    _make_pdf(str(in_dir / "a.pdf"), "Belge A içerik")
    _make_pdf(str(in_dir / "b.pdf"), "Belge B içerik")

    progress_calls = []
    engine = BatchEngine(
        str(in_dir), str(out_dir),
        operations={
            "watermark": {"text": "BATCHTEST_WM"},
            "encrypt": {"password": "s3cret"},
        },
        progress_callback=lambda c, t, f: progress_calls.append((c, t, f)),
    )
    summary = engine.run()

    assert summary["total"] == 2
    assert summary["succeeded"] == 2
    assert summary["failed"] == 0
    assert len(progress_calls) == 2

    for name in ("a.pdf", "b.pdf"):
        out_pdf = os.path.join(str(out_dir), name)
        assert os.path.exists(out_pdf)
        doc = PDFDocument(out_pdf)
        assert doc.is_encrypted  # şifreli kaydedildi
        assert doc.authenticate("s3cret")
        text = doc.get_page(0).get_text("text")
        assert "BATCHTEST_WM" in text  # filigran zincire girdi
        doc.close()

    # JSON log yazıldı
    assert os.path.exists(engine.log_path)
    with open(engine.log_path, encoding="utf-8") as f:
        payload = json.load(f)
    assert payload["succeeded"] == 2


def test_error_tolerance_and_json_log(tmp_path):
    """Bozuk PDF kuyruğu durdurmaz; sağlam dosya işlenir, log JSON olur."""
    in_dir = tmp_path / "in2"
    out_dir = tmp_path / "out2"
    in_dir.mkdir()

    _make_pdf(str(in_dir / "saglam.pdf"), "Sağlam belge")
    with open(in_dir / "bozuk.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n%bozuk kesik icerik EOF yok")

    engine = BatchEngine(
        str(in_dir), str(out_dir),
        operations={"watermark": {"text": "WM2"}},
    )
    summary = engine.run()

    assert summary["total"] == 2
    assert summary["succeeded"] == 1  # sağlam devam etti
    assert summary["failed"] == 1     # bozuk kaydedildi ama durdurmadı
    assert os.path.exists(os.path.join(str(out_dir), "saglam.pdf"))

    with open(engine.log_path, encoding="utf-8") as f:
        payload = json.load(f)
    assert len(payload["entries"]) == 2
    by_file = {e["file"]: e for e in payload["entries"]}
    assert by_file["saglam.pdf"]["status"] == "ok"
    assert by_file["bozuk.pdf"]["status"] == "failed"
