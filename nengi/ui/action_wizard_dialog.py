"""
NeNgi PDF - Action Wizard Dialog
Batch processing interface allowing users to select multiple PDFs, pick automated actions, and run batch jobs.
"""

from __future__ import annotations
from typing import Optional, List
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QFileDialog, QProgressBar,
    QCheckBox, QGroupBox, QLineEdit, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt

from nengi.core.action_wizard import ActionWizard, ActionStep


class ActionWizardDialog(QDialog):
    """Multi-file batch automation wizard."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("⚡ Eylem Sihirbazı (Toplu Belge İşleme) - NeNgi PDF")
        self.resize(600, 520)
        self.file_paths: List[str] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # 1. File List
        grp_files = QGroupBox("İşlenecek PDF Belgeleri")
        lay_f = QVBoxLayout(grp_files)

        self.list_files = QListWidget()
        lay_f.addWidget(self.list_files)

        h_fbtns = QHBoxLayout()
        btn_add_files = QPushButton("➕ Dosya(lar) Ekle...")
        btn_add_files.clicked.connect(self._add_files)
        h_fbtns.addWidget(btn_add_files)

        btn_add_dir = QPushButton("📁 Klasör Ekle...")
        btn_add_dir.clicked.connect(self._add_folder)
        h_fbtns.addWidget(btn_add_dir)

        btn_clear = QPushButton("Listeyi Temizle")
        btn_clear.clicked.connect(self._clear_files)
        h_fbtns.addWidget(btn_clear)

        lay_f.addLayout(h_fbtns)
        layout.addWidget(grp_files)

        # 2. Steps to execute
        grp_steps = QGroupBox("Uygulanacak Eylemler (Sırayla)")
        lay_s = QVBoxLayout(grp_steps)

        self.chk_compress = QCheckBox("🗜️ PDF Boyutunu Küçült (Optimize Et)")
        self.chk_compress.setChecked(True)
        lay_s.addWidget(self.chk_compress)

        self.chk_watermark = QCheckBox("💧 Filigran Ekle:")
        self.txt_watermark = QLineEdit("GİZLİDİR")
        h_wm = QHBoxLayout()
        h_wm.addWidget(self.chk_watermark)
        h_wm.addWidget(self.txt_watermark)
        lay_s.addLayout(h_wm)

        self.chk_encrypt = QCheckBox("🔒 Parola ile Şifrele:")
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Şifreleme parolası girin...")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        h_enc = QHBoxLayout()
        h_enc.addWidget(self.chk_encrypt)
        h_enc.addWidget(self.txt_password)
        lay_s.addLayout(h_enc)

        layout.addWidget(grp_steps)

        # 3. Output Directory
        h_out = QHBoxLayout()
        h_out.addWidget(QLabel("Hedef Klasör:"))
        self.txt_out_dir = QLineEdit()
        btn_browse_out = QPushButton("Gözat...")
        btn_browse_out.clicked.connect(self._browse_out_dir)
        h_out.addWidget(self.txt_out_dir)
        h_out.addWidget(btn_browse_out)
        layout.addLayout(h_out)

        # 4. Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel("Hazır.")
        layout.addWidget(self.lbl_status)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal / Kapat")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_run = QPushButton("⚡ Toplu İşlemi Başlat")
        btn_run.setObjectName("accentButton")
        btn_run.clicked.connect(self._run_batch)
        btn_layout.addWidget(btn_run)

        layout.addLayout(btn_layout)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "PDF Belgeleri Seç", "", "PDF Dosyaları (*.pdf)")
        for f in files:
            if f not in self.file_paths:
                self.file_paths.append(f)
                self.list_files.addItem(os.path.basename(f))

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "PDF İçeren Klasör Seç")
        if folder:
            for root, _, filenames in os.walk(folder):
                for fn in filenames:
                    if fn.lower().endswith(".pdf"):
                        full_p = os.path.join(root, fn)
                        if full_p not in self.file_paths:
                            self.file_paths.append(full_p)
                            self.list_files.addItem(fn)

    def _clear_files(self):
        self.file_paths.clear()
        self.list_files.clear()

    def _browse_out_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Hedef Klasör Seç")
        if folder:
            self.txt_out_dir.setText(folder)

    def _run_batch(self):
        if not self.file_paths:
            QMessageBox.warning(self, "Uyarı", "Lütfen işlenecek en az bir PDF dosyası ekleyin.")
            return

        out_dir = self.txt_out_dir.text().strip()
        if not out_dir:
            QMessageBox.warning(self, "Uyarı", "Lütfen işlenen belgelerin kaydedileceği hedef klasörü seçin.")
            return

        steps: List[ActionStep] = []
        if self.chk_compress.isChecked():
            steps.append(ActionStep("compress", "Optimize", {"garbage_collect": True, "deflate": True}))

        if self.chk_watermark.isChecked():
            wm_text = self.txt_watermark.text().strip() or "CONFIDENTIAL"
            steps.append(ActionStep("watermark", "Filigran", {"text": wm_text, "opacity": 0.3, "rotation": 45}))

        if self.chk_encrypt.isChecked():
            pwd = self.txt_password.text()
            if not pwd:
                QMessageBox.warning(self, "Uyarı", "Şifreleme kutusu işaretli ancak parola girilmedi.")
                return
            steps.append(ActionStep("encrypt", "Şifreleme", {"password": pwd}))

        if not steps:
            QMessageBox.warning(self, "Uyarı", "Lütfen uygulanacak en az bir eylem seçin.")
            return

        self.progress_bar.setMaximum(len(self.file_paths))
        self.progress_bar.setValue(0)

        def on_prog(cur, total, msg):
            self.progress_bar.setValue(cur)
            self.lbl_status.setText(f"{msg} ({cur}/{total})")

        results = ActionWizard.run_batch(self.file_paths, steps, out_dir, progress_callback=on_prog)

        success_count = sum(1 for r in results if r["success"])
        fail_count = len(results) - success_count

        QMessageBox.information(
            self, "Toplu İşlem Tamamlandı",
            f"Toplam {len(results)} belgeden {success_count} tanesi başarıyla işlendi ve kaydedildi.\n"
            f"Hatalı: {fail_count}\n\nHedef: {out_dir}"
        )
        self.accept()
