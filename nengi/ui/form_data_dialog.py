"""
NeNgi PDF - Form Data Import / Export Wizard
Allows exporting and importing interactive form field values to/from CSV, XML, and JSON.
"""

from __future__ import annotations
from typing import Optional
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QPushButton, QFileDialog, QMessageBox, QGroupBox, QWidget
)
from nengi.core.pdf_document import PDFDocument
from nengi.core.form_designer import FormDesigner


class FormDataDialog(QDialog):
    """Wizard to import or export form data."""

    def __init__(self, doc: PDFDocument, mode: str = "export", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc = doc
        self.mode = mode  # "export" or "import"
        title = "📤 Form Verilerini Dışa Aktar" if mode == "export" else "📥 Form Verilerini İçe Aktar"
        self.setWindowTitle(f"{title} - NeNgi PDF")
        self.resize(400, 240)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            "Form alanlarının verilerini CSV, XML veya JSON formatında dışa aktarabilir "
            "veya kaydedilmiş verileri belgeye otomatik doldurabilirsiniz."
            if self.mode == "export" else
            "Daha önce dışa aktarılmış form verisi dosyasını seçerek belgedeki form alanlarını otomatik doldurun."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        grp_fmt = QGroupBox("Dosya Formatı")
        lay_fmt = QVBoxLayout(grp_fmt)

        self.rb_csv = QRadioButton("CSV (Virgülle Ayrılmış Değerler - Excel Uyumlu)")
        self.rb_csv.setChecked(True)
        lay_fmt.addWidget(self.rb_csv)

        self.rb_xml = QRadioButton("XML (Genişletilebilir İşaretleme Dili)")
        lay_fmt.addWidget(self.rb_xml)

        self.rb_json = QRadioButton("JSON (JavaScript Nesne Gösterimi)")
        lay_fmt.addWidget(self.rb_json)

        layout.addWidget(grp_fmt)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        action_btn_text = "Dışa Aktar..." if self.mode == "export" else "Dosya Seç ve İçe Aktar..."
        btn_action = QPushButton(action_btn_text)
        btn_action.setObjectName("accentButton")
        btn_action.clicked.connect(self._do_action)
        btn_layout.addWidget(btn_action)

        layout.addLayout(btn_layout)

    def _get_format(self) -> str:
        if self.rb_csv.isChecked():
            return "csv"
        elif self.rb_xml.isChecked():
            return "xml"
        return "json"

    def _do_action(self):
        fmt = self._get_format()
        filter_str = f"{fmt.upper()} Dosyaları (*.{fmt})"

        if self.mode == "export":
            path, _ = QFileDialog.getSaveFileName(self, "Form Verisini Kaydet", f"form_verisi.{fmt}", filter_str)
            if not path:
                return
            success = FormDesigner.export_form_data(self.doc, path, fmt=fmt)
            if success:
                QMessageBox.information(self, "Başarılı", f"Form verileri başarıyla aktarıldı:\n{os.path.basename(path)}")
                self.accept()
            else:
                QMessageBox.warning(self, "Uyarı", "Belgede dışa aktarılacak form alanı veya veri bulunamadı.")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Form Verisi Dosyası Seç", "", filter_str)
            if not path:
                return
            count = FormDesigner.import_form_data(self.doc, path, fmt=fmt)
            if count > 0:
                QMessageBox.information(self, "Başarılı", f"{count} form alanı başarıyla dolduruldu!")
                self.accept()
            else:
                QMessageBox.warning(self, "Uyarı", "Seçilen dosyadan eşleşen form alanı verisi aktarılamadı.")
