"""
NeNgi PDF - Accessibility Audit & Compliance Report Dialog
Runs standardized PDF/UA & WCAG accessibility audits and presents a detailed report.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget,
    QTreeWidgetItem, QPushButton, QMessageBox, QWidget
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

from nengi.core.pdf_document import PDFDocument
from nengi.core.accessibility import AccessibilityChecker


class AccessibilityDialog(QDialog):
    """Displays accessibility inspection results with Passed / Failed / Warning badges."""

    def __init__(self, doc: PDFDocument, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("♿ Erişilebilirlik Tam Denetimi (PDF/UA & WCAG) - NeNgi PDF")
        self.resize(650, 480)
        self.doc = doc
        self._init_ui()
        self._run_audit()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_summary = QLabel("Erişilebilirlik kuralları taranıyor...")
        self.lbl_summary.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.lbl_summary)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Kategori / Kural", "Durum", "Detay"])
        self.tree.setColumnWidth(0, 220)
        self.tree.setColumnWidth(1, 100)
        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        btn_recheck = QPushButton("🔄 Yeniden Denetle")
        btn_recheck.clicked.connect(self._run_audit)
        btn_layout.addWidget(btn_recheck)

        btn_layout.addStretch()

        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)

    def _run_audit(self):
        self.tree.clear()
        if not self.doc or not self.doc.is_open:
            self.lbl_summary.setText("Belge açık değil.")
            return

        results = AccessibilityChecker.audit_document(self.doc)

        passed = sum(1 for r in results if r["status"] == "passed")
        failed = sum(1 for r in results if r["status"] == "failed")
        warning = sum(1 for r in results if r["status"] == "warning")

        self.lbl_summary.setText(f"Denetim Sonucu: {passed} Başarılı, {failed} Başarısız, {warning} Uyarı")

        # Group by category
        categories = {}
        for r in results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(r)

        status_symbols = {
            "passed": ("✅ Başarılı", "#107C41"),
            "failed": ("❌ Başarısız", "#A80000"),
            "warning": ("⚠️ Uyarı", "#D83B01"),
            "manual": ("ℹ️ Manuel Kontrol", "#0078D4"),
        }

        for cat_name, items in categories.items():
            cat_item = QTreeWidgetItem([cat_name])
            cat_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.tree.addTopLevelItem(cat_item)

            for it in items:
                sym, color_hex = status_symbols.get(it["status"], ("?", "#888888"))
                child = QTreeWidgetItem([it["rule"], sym, it["details"]])
                child.setForeground(1, QColor(color_hex))
                cat_item.addChild(child)

            cat_item.setExpanded(True)
