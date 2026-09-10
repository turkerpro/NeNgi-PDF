"""NeNgi PDF - Batch (toplu) işlem motoru.

Klasördeki PDF'lere kuyruklu işlem uygular:
  ocr, redact_phrases, encrypt, watermark, convert_images, optimize

Özellikler:
  - Hata toleransı: tek dosya patlasa bile kuyruk devam eder.
  - JSON log: her dosyanın sonucu + özet, dosyaya yazılır.
  - İlerleme callback: ``progress_callback(current, total, filename)``.
"""

from __future__ import annotations

import glob
import json
import os
import re
from typing import Callable, Dict, List, Optional

from nengi.core.converter import FormatConverter
from nengi.core.pdf_document import PDFDocument
from nengi.core.pdf_optimizer import PDFOptimizer
from nengi.core.redaction import RedactionEngine
from nengi.core.security import SecurityManager

ProgressCallback = Callable[[int, int, str], None]

DEFAULT_WATERMARK = {
    "type": "text",
    "text": "NeNgi",
    "font": "helv",
    "font_size": 48,
    "color": (0.5, 0.5, 0.5),
    # Not: PDFDocument.add_watermark -> page.insert_text(rotate=...)
    # yalnızca 0/90/180/270 kabul eder; 45 gibi değerler hata verir.
    "rotation": 0,
    "opacity": 0.4,
    "position": "center",
    "overlay": True,
    "page_range": "all",
}


def _sanitize_rotation(value) -> int:
    """Kullanıcı rotasyonunu insert_text'in kabul ettiği değere yuvarla."""
    try:
        v = int(value) % 360
    except (TypeError, ValueError):
        return 0
    return min((0, 90, 180, 270), key=lambda c: abs(c - v))


class BatchEngine:
    """Klasördeki PDF'lere sırayla işlem uygulayan kuyruklu motor."""

    SUPPORTED_OPS = (
        "ocr",
        "redact_phrases",
        "encrypt",
        "watermark",
        "convert_images",
        "optimize",
    )

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        operations: Optional[Dict] = None,
        log_path: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        self.input_dir = os.path.abspath(input_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.operations: Dict = dict(operations or {})
        self.log_path = log_path or os.path.join(self.output_dir, "batch_log.json")
        self.progress_callback = progress_callback
        self._stop_requested = False
        self.entries: List[Dict] = []

    # -- kontrol ------------------------------------------------------
    def request_stop(self) -> None:
        """Kuyruğu kullanıcı isteğiyle durdur (mevcut dosya bitince çıkar)."""
        self._stop_requested = True

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    def collect_pdfs(self) -> List[str]:
        """Girdi klasöründeki PDF'leri sıralı döndür (recursive değil)."""
        pattern = os.path.join(self.input_dir, "*.pdf")
        files = [f for f in sorted(glob.glob(pattern)) if os.path.isfile(f)]
        # Büyük/küçük harf varyantı (*.PDF) için:
        pattern2 = os.path.join(self.input_dir, "*.PDF")
        for f in sorted(glob.glob(pattern2)):
            if f not in files and os.path.isfile(f):
                files.append(f)
        return sorted(files)

    # -- ana akış ------------------------------------------------------
    def run(self) -> Dict:
        """Kuyruğu çalıştır, özet döndür ve JSON log yaz."""
        os.makedirs(self.output_dir, exist_ok=True)
        pdfs = self.collect_pdfs()
        total = len(pdfs)
        self.entries = []
        succeeded = 0
        failed = 0

        for idx, pdf_path in enumerate(pdfs, start=1):
            if self._stop_requested:
                self.entries.append({
                    "file": os.path.basename(pdf_path),
                    "status": "skipped",
                    "error": "kullanıcı durdurdu",
                    "output": None,
                })
                continue
            entry = self._process_single(pdf_path)
            self.entries.append(entry)
            if entry["status"] == "ok":
                succeeded += 1
            else:
                failed += 1
            if self.progress_callback is not None:
                try:
                    self.progress_callback(idx, total, os.path.basename(pdf_path))
                except Exception:
                    pass
            self._write_log(total=total, succeeded=succeeded, failed=failed)

        summary = {
            "input_dir": self.input_dir,
            "output_dir": self.output_dir,
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "stopped": self._stop_requested,
            "results": self.entries,
        }
        self._write_log(total=total, succeeded=succeeded, failed=failed)
        return summary

    # -- tek dosya ------------------------------------------------------
    def _process_single(self, pdf_path: str) -> Dict:
        basename = os.path.basename(pdf_path)
        output_path = os.path.join(self.output_dir, basename)
        ops = self.operations
        try:
            doc = PDFDocument(pdf_path)
            if not doc.is_open or not doc.is_authenticated:
                return {"file": basename, "status": "failed",
                        "error": "açılamadı (bozuk/şifreli?)", "output": None}

            # 1. OCR (taranmış sayfalara aranabilir katman)
            if ops.get("ocr"):
                try:
                    for p in range(doc.page_count):
                        doc.ocr_page(p)
                except Exception as e:
                    # OCR opsiyonel: başarısızlık dosyayı batırmasın
                    print(f"Batch OCR uyarısı ({basename}): {e}")

            # 2. Redact phrases (literal kelime öbekleri)
            phrases = ops.get("redact_phrases") or []
            if phrases:
                all_matches = []
                for phrase in phrases:
                    if not phrase:
                        continue
                    matches = RedactionEngine.search_patterns(
                        doc, re.escape(phrase), is_custom_regex=True)
                    all_matches.extend(matches)
                if all_matches:
                    RedactionEngine.mark_for_redaction(doc, all_matches)
                    RedactionEngine.apply_redactions(doc)

            # 3. Watermark
            wm_cfg = ops.get("watermark")
            if wm_cfg:
                cfg = dict(DEFAULT_WATERMARK)
                if isinstance(wm_cfg, dict):
                    cfg.update(wm_cfg)
                cfg["rotation"] = _sanitize_rotation(cfg.get("rotation", 0))
                if not doc.add_watermark(cfg):
                    raise RuntimeError("watermark uygulanamadı")

            # 4+5. Kaydet (encrypt varsa SecurityManager ile şifreli)
            enc_cfg = ops.get("encrypt")
            password: Optional[str] = None
            if isinstance(enc_cfg, dict):
                password = enc_cfg.get("password") or None
            elif isinstance(enc_cfg, str) and enc_cfg:
                password = enc_cfg

            if password:
                ok = SecurityManager.encrypt_document(doc, password, output_path)
            else:
                ok = doc.save(output_path)
            if not ok:
                doc.close()
                return {"file": basename, "status": "failed",
                        "error": "kaydetme başarısız", "output": None}

            # 6. Optimize (çıktı kopyası üzerinde; girdiye dokunmaz)
            opt_cfg = ops.get("optimize")
            if opt_cfg:
                opt_opts = opt_cfg if isinstance(opt_cfg, dict) else {}
                try:
                    out_doc = PDFDocument(output_path, password=password)
                    if out_doc.is_open and out_doc.is_authenticated:
                        PDFOptimizer.optimize(out_doc, opt_opts)
                        out_doc.close()
                except Exception as e:
                    print(f"Batch optimize uyarısı ({basename}): {e}")

            # 7. Convert images (sayfaları PNG/JPG'ye çevir)
            img_cfg = ops.get("convert_images")
            if img_cfg:
                img_opts = img_cfg if isinstance(img_cfg, dict) else {}
                fmt = img_opts.get("format", "png")
                dpi = int(img_opts.get("dpi", 150))
                img_dir = os.path.join(
                    self.output_dir, os.path.splitext(basename)[0] + "_images")
                try:
                    FormatConverter.export_all_pages(doc, img_dir, format_ext=fmt, dpi=dpi)
                except Exception as e:
                    print(f"Batch convert_images uyarısı ({basename}): {e}")

            doc.close()
            return {"file": basename, "status": "ok", "error": None, "output": output_path}
        except Exception as e:  # hata toleransı: kuyruk devam eder
            return {"file": basename, "status": "failed",
                    "error": str(e), "output": None}

    # -- log -------------------------------------------------------------
    def _write_log(self, total: int, succeeded: int, failed: int) -> None:
        payload = {
            "input_dir": self.input_dir,
            "output_dir": self.output_dir,
            "total": total,
            "succeeded": succeeded,
            "failed": failed,
            "entries": self.entries,
        }
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.log_path)), exist_ok=True)
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Batch log yazılamadı: {e}")
