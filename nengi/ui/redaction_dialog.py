"""
NeNgi PDF - Search & Redact / Document Sanitization Dialogs
Interactive tools to find and permanently redact sensitive PII and sanitize document metadata.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QCheckBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QGroupBox, QWidget, QRadioButton
)
from PyQt6.QtCore import Qt

from nengi.core.pdf_document import PDFDocument
from nengi.core.redaction import RedactionEngine, PII_PATTERNS


class SearchAndRedactDialog(QDialog):
    """Searches for sensitive patterns (TCKN, credit cards, emails) and marks/applies redactions."""

    def __init__(self, doc: PDFDocument, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🛡️ Arama ve Kalıcı Redaksiyon (Kişisel Veri Temizleme)")
        self.resize(560, 480)
        self.doc = doc
        self.found_matches: List[Dict[str, Any]] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        grp_search = QGroupBox("Arama Kriteri")
        lay_s = QVBoxLayout(grp_search)

        self.rb_pii = QRadioButton("Hazır Hassas Veri Şablonu (PII):")
        self.rb_pii.setChecked(True)
        self.cb_pii = QComboBox()
        for key, info in PII_PATTERNS.items():
            self.cb_pii.addItem(info["label"], key)
        lay_s.addWidget(self.rb_pii)
        lay_s.addWidget(self.cb_pii)

        self.rb_custom = QRadioButton("Özel Metin veya Düzenli İfade (Regex):")
        self.txt_custom = QLineEdit()
        self.txt_custom.setPlaceholderText("Örn: Gizli Müşteri Adı veya [A-Z]{3}-\\d{4}")
        lay_s.addWidget(self.rb_custom)
        lay_s.addWidget(self.txt_custom)

        btn_search = QPushButton("🔍 Belgede Ara")
        btn_search.clicked.connect(self._do_search)
        lay_s.addWidget(btn_search)

        layout.addWidget(grp_search)

        # Results
        self.lbl_results = QLabel("Bulunan eşleşmeler:")
        layout.addWidget(self.lbl_results)

        self.list_results = QListWidget()
        layout.addWidget(self.list_results)

        # Options
        h_opts = QHBoxLayout()
        h_opts.addWidget(QLabel("Yer Paylaşım Metni:"))
        self.txt_overlay = QLineEdit("GİZLENDİ")
        h_opts.addWidget(self.txt_overlay)
        layout.addLayout(h_opts)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_mark = QPushButton("Redaksiyon Olarak İşaretle")
        btn_mark.clicked.connect(self._mark_redactions)
        btn_layout.addWidget(btn_mark)

        btn_apply = QPushButton("🔥 Kalıcı Olarak Sil ve Uygula")
        btn_apply.setObjectName("accentButton")
        btn_apply.setStyleSheet("background-color: #D83B01; color: white; font-weight: bold;")
        btn_apply.clicked.connect(self._apply_permanent)
        btn_layout.addWidget(btn_apply)

        layout.addLayout(btn_layout)

    def _do_search(self):
        self.list_results.clear()
        if not self.doc or not self.doc.is_open:
            return

        if self.rb_pii.isChecked():
            key = self.cb_pii.currentData()
            self.found_matches = RedactionEngine.search_patterns(self.doc, key, is_custom_regex=False)
        else:
            txt = self.txt_custom.text().strip()
            if not txt:
                QMessageBox.warning(self, "Uyarı", "Lütfen aranacak bir metin veya regex ifadesi girin.")
                return
            self.found_matches = RedactionEngine.search_patterns(self.doc, txt, is_custom_regex=True)

        self.lbl_results.setText(f"Bulunan eşleşmeler ({len(self.found_matches)} adet):")
        for m in self.found_matches:
            item = QListWidgetItem(f"Sayfa {m['page']+1}: \"{m['text']}\"")
            self.list_results.addItem(item)

        if not self.found_matches:
            QMessageBox.information(self, "Bilgi", "Belgede belirtilen kritere uygun veri bulunamadı.")

    def _mark_redactions(self):
        if not self.found_matches:
            QMessageBox.information(self, "Bilgi", "İşaretlenecek eşleşme yok.")
            return

        overlay = self.txt_overlay.text().strip() or "REDACTED"
        count = RedactionEngine.mark_for_redaction(self.doc, self.found_matches, overlay_text=overlay)
        QMessageBox.information(self, "Tamamlandı", f"{count} adet hassas veri kırmızı redaksiyon çerçevesiyle işaretlendi.")
        self.accept()

    def _apply_permanent(self):
        if not self.found_matches:
            QMessageBox.information(self, "Bilgi", "Uygulanacak eşleşme yok.")
            return

        reply = QMessageBox.warning(
            self, "DİKKAT: Kalıcı Silme",
            f"Seçilen {len(self.found_matches)} adet veri belgeden KALICI OLARAK silinecek ve piksel düzeyinde kaldırılacak.\n"
            "Bu işlem kaydedildiğinde geri alınamaz.\n\nDevam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            overlay = self.txt_overlay.text().strip() or "REDACTED"
            RedactionEngine.mark_for_redaction(self.doc, self.found_matches, overlay_text=overlay)
            RedactionEngine.apply_redactions(self.doc)
            QMessageBox.information(self, "Başarılı", "Hassas veriler belgeden kalıcı olarak silindi ve üzerine maske çizildi.")
            self.accept()


class SanitizeDocumentDialog(QDialog):
    """Strips metadata, attachments, links, and hidden information for secure publication."""

    def __init__(self, doc: PDFDocument, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🧹 Belgeyi Temizle (Gizli Bilgileri Kaldır)")
        self.resize(440, 320)
        self.doc = doc
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(
            "Belgeyi güvenli şekilde paylaşmadan önce metaverileri (yazar, başlık, oluşturma tarihi), "
            "ekli dosyaları ve gizli komutları kaldırarak gizliliği sağlayabilirsiniz."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        grp = QGroupBox("Kaldırılacak Öğeler")
        lay_g = QVBoxLayout(grp)

        self.chk_meta = QCheckBox("Belge Metaverileri (Yazar, Konu, Başlık, vb.)")
        self.chk_meta.setChecked(True)
        lay_g.addWidget(self.chk_meta)

        self.chk_attach = QCheckBox("Gömülü Ek Dosyalar")
        self.chk_attach.setChecked(True)
        lay_g.addWidget(self.chk_attach)

        self.chk_links = QCheckBox("Tüm Dış Web ve Dosya Bağlantıları")
        lay_g.addWidget(self.chk_links)

        self.chk_bookmarks = QCheckBox("Yer İmleri (İçindekiler Ağacı)")
        lay_g.addWidget(self.chk_bookmarks)

        self.chk_annots = QCheckBox("Yorumlar ve Çizim Açıklamaları")
        lay_g.addWidget(self.chk_annots)

        layout.addWidget(grp)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_sanitize = QPushButton("🧹 Belgeyi Temizle")
        btn_sanitize.setObjectName("accentButton")
        btn_sanitize.clicked.connect(self._do_sanitize)
        btn_layout.addWidget(btn_sanitize)

        layout.addLayout(btn_layout)

    def _do_sanitize(self):
        if not self.doc or not self.doc.is_open:
            return

        res = RedactionEngine.sanitize_document(
            self.doc,
            remove_metadata=self.chk_meta.isChecked(),
            remove_attachments=self.chk_attach.isChecked(),
            remove_links=self.chk_links.isChecked(),
            remove_bookmarks=self.chk_bookmarks.isChecked(),
            remove_annotations=self.chk_annots.isChecked(),
        )

        msg = f"Temizleme tamamlandı!\n- Metaveri sıfırlandı: {'Evet' if res.get('metadata_cleared') else 'Hayır'}\n"
        msg += f"- Kaldırılan Ekler: {res.get('attachments_removed', 0)}\n"
        msg += f"- Kaldırılan Bağlantılar: {res.get('links_removed', 0)}\n"
        msg += f"- Kaldırılan Açıklamalar: {res.get('annotations_removed', 0)}"

        QMessageBox.information(self, "Temizlendi", msg)
        self.accept()
