"""NeNgi PDF - Toplu (Batch) İşlem Dialogu.

Klasördeki PDF'lere kuyruklu işlem: klasör seç, işlem checkboxları,
çalıştır/durdur, ilerleme çubuğu, log penceresi.
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class BatchDialog(QDialog):
    """Toplu işlem kuyruğu arayüzü (BatchEngine ön yüzü)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Toplu İşlem (Batch)")
        self.resize(560, 520)
        self._engine = None
        self._init_ui()

    # -- UI ------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Girdi klasörü
        row_in = QHBoxLayout()
        row_in.addWidget(QLabel("Girdi klasörü:"))
        self.le_input = QLineEdit()
        self.le_input.setPlaceholderText("PDF klasörünü seçin...")
        btn_in = QPushButton("Gözat...")
        btn_in.clicked.connect(self._browse_input)
        row_in.addWidget(self.le_input)
        row_in.addWidget(btn_in)
        layout.addLayout(row_in)

        # Çıktı klasörü
        row_out = QHBoxLayout()
        row_out.addWidget(QLabel("Çıktı klasörü:"))
        self.le_output = QLineEdit()
        self.le_output.setPlaceholderText("Sonuç klasörü (boşsa girdi/out)...")
        btn_out = QPushButton("Gözat...")
        btn_out.clicked.connect(self._browse_output)
        row_out.addWidget(self.le_output)
        row_out.addWidget(btn_out)
        layout.addLayout(row_out)

        # İşlem checkboxları
        layout.addWidget(QLabel("İşlemler:"))
        self.cb_ocr = QCheckBox("OCR (taranmış sayfaları aranabilir yap)")
        self.cb_redact = QCheckBox("Kelimeleri gizle (redact)")
        self.cb_encrypt = QCheckBox("Şifrele (AES-256)")
        self.cb_watermark = QCheckBox("Filigran ekle")
        self.cb_images = QCheckBox("Sayfaları görsele çevir (PNG)")
        self.cb_optimize = QCheckBox("Optimize et (sıkıştır)")
        for cb in (self.cb_ocr, self.cb_redact, self.cb_encrypt,
                   self.cb_watermark, self.cb_images, self.cb_optimize):
            layout.addWidget(cb)
        self.cb_encrypt.setChecked(True)
        self.cb_watermark.setChecked(True)

        # Parametre satırları
        row_phrases = QHBoxLayout()
        row_phrases.addWidget(QLabel("Gizli kelimeler (, ile):"))
        self.le_phrases = QLineEdit()
        self.le_phrases.setPlaceholderText("örn. gizli, TCKN")
        row_phrases.addWidget(self.le_phrases)
        layout.addLayout(row_phrases)

        row_pw = QHBoxLayout()
        row_pw.addWidget(QLabel("Şifre:"))
        self.le_password = QLineEdit()
        self.le_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.le_password.setText("1234")
        row_pw.addWidget(self.le_password)
        row_pw.addWidget(QLabel("Filigran:"))
        self.le_watermark = QLineEdit("NeNgi")
        row_pw.addWidget(self.le_watermark)
        layout.addLayout(row_pw)

        # Çalıştır / Durdur
        row_btn = QHBoxLayout()
        self.btn_run = QPushButton("Çalıştır")
        self.btn_run.clicked.connect(self._run_batch)
        self.btn_stop = QPushButton("Durdur")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_batch)
        row_btn.addStretch()
        row_btn.addWidget(self.btn_stop)
        row_btn.addWidget(self.btn_run)
        layout.addLayout(row_btn)

        # İlerleme + log
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("İşlem günlüğü burada görünür...")
        layout.addWidget(self.log_view)

    # -- slotlar ---------------------------------------------------------
    def _browse_input(self):
        d = QFileDialog.getExistingDirectory(self, "Girdi Klasörünü Seç")
        if d:
            self.le_input.setText(d)
            if not self.le_output.text().strip():
                self.le_output.setText(os.path.join(d, "out"))

    def _browse_output(self):
        d = QFileDialog.getExistingDirectory(self, "Çıktı Klasörünü Seç")
        if d:
            self.le_output.setText(d)

    def _log(self, msg: str):
        self.log_view.append(msg)

    def _build_operations(self) -> dict:
        ops: dict = {}
        if self.cb_ocr.isChecked():
            ops["ocr"] = True
        if self.cb_redact.isChecked():
            phrases = [p.strip() for p in self.le_phrases.text().split(",") if p.strip()]
            if phrases:
                ops["redact_phrases"] = phrases
        if self.cb_encrypt.isChecked():
            ops["encrypt"] = {"password": self.le_password.text()}
        if self.cb_watermark.isChecked():
            ops["watermark"] = {"text": self.le_watermark.text() or "NeNgi"}
        if self.cb_images.isChecked():
            ops["convert_images"] = {"format": "png", "dpi": 150}
        if self.cb_optimize.isChecked():
            ops["optimize"] = {"garbage_collect": True, "deflate": True}
        return ops

    def _run_batch(self):
        from PyQt6.QtWidgets import QApplication
        from nengi.core.batch_engine import BatchEngine

        input_dir = self.le_input.text().strip()
        output_dir = self.le_output.text().strip() or os.path.join(input_dir, "out")
        if not input_dir or not os.path.isdir(input_dir):
            QMessageBox.warning(self, "Uyarı", "Geçerli bir girdi klasörü seçin.")
            return
        ops = self._build_operations()
        if not ops:
            QMessageBox.warning(self, "Uyarı", "En az bir işlem seçin.")
            return

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress.setValue(0)
        self.log_view.clear()
        self._log(f"Başladı: {input_dir} → {output_dir}")

        def on_progress(current: int, total: int, filename: str):
            pct = int(current * 100 / max(total, 1))
            self.progress.setValue(pct)
            self._log(f"[{current}/{total}] {filename}")
            QApplication.processEvents()

        self._engine = BatchEngine(input_dir, output_dir, ops,
                                   progress_callback=on_progress)
        try:
            summary = self._engine.run()
        finally:
            self.btn_run.setEnabled(True)
            self.btn_stop.setEnabled(False)

        self.progress.setValue(100)
        self._log(f"Bitti: {summary['succeeded']} ok, {summary['failed']} hata "
                  f"(toplam {summary['total']})")
        if summary["failed"]:
            for e in summary["results"]:
                if e["status"] != "ok":
                    self._log(f"  HATA {e['file']}: {e.get('error')}")

    def _stop_batch(self):
        if self._engine is not None:
            self._engine.request_stop()
            self._log("Durdurma istendi (mevcut dosya bitince durur)...")
