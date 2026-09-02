"""
NeNgi PDF - Side-by-Side Synchronized Text DIFF Comparison View
Compares Original and Revised PDFs side-by-side with synchronized scrolling,
color-coded difference highlights (Green: Added, Red: Deleted, Yellow: Modified),
and an interactive difference navigation panel.
"""

from __future__ import annotations
from typing import Optional, List, Tuple, Dict
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRectF
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QScrollArea, QMessageBox, QFileDialog, QSizePolicy
)
from PyQt6.QtGui import QColor, QFont
import pymupdf as fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.diff_engine import DiffEngine, DiffChangeItem, DiffHighlight
from nengi.ui.pdf_view import PageRenderWidget


class DiffScrollPane(QScrollArea):
    """Scroll area for one side of the diff view."""
    
    scrolled = pyqtSignal(int)

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title
        self.container = QWidget()
        self.layout_pages = QVBoxLayout(self.container)
        self.layout_pages.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_pages.setSpacing(16)
        self.layout_pages.setContentsMargins(15, 15, 15, 15)
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.page_widgets: List[PageRenderWidget] = []

        self.verticalScrollBar().valueChanged.connect(self._on_scroll)

    def _on_scroll(self, val: int):
        self.scrolled.emit(val)


class DiffView(QWidget):
    """Main Side-by-Side PDF Diff widget."""

    status_message = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.doc_a: Optional[PDFDocument] = None
        self.doc_b: Optional[PDFDocument] = None
        self.engine: Optional[DiffEngine] = None
        self.changes: List[DiffChangeItem] = []
        self.current_change_idx = -1
        self.sync_scroll = True
        self.zoom = 1.0

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Control Bar (Fixed height to eliminate empty vertical space)
        top_bar = QFrame()
        top_bar.setFixedHeight(46)
        top_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        top_bar.setStyleSheet("background-color: #282828; border-bottom: 1px solid #383838; padding: 4px;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 2, 10, 2)

        self.lbl_summary = QLabel("📊 Karşılaştırma Bekleniyor...")
        self.lbl_summary.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")
        top_layout.addWidget(self.lbl_summary)

        top_layout.addSpacing(20)

        # Navigation buttons
        self.btn_prev = QPushButton("◀ Önceki Fark")
        self.btn_prev.clicked.connect(self.goto_previous_change)
        top_layout.addWidget(self.btn_prev)

        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setStyleSheet("font-weight: bold; color: #0078D4; padding: 0 8px;")
        top_layout.addWidget(self.lbl_counter)

        self.btn_next = QPushButton("Sonraki Fark ▶")
        self.btn_next.clicked.connect(self.goto_next_change)
        top_layout.addWidget(self.btn_next)

        top_layout.addSpacing(15)

        self.btn_toggle_sync = QPushButton("🔗 Senkron Kaydırma: Açık")
        self.btn_toggle_sync.setCheckable(True)
        self.btn_toggle_sync.setChecked(True)
        self.btn_toggle_sync.clicked.connect(self._toggle_sync_scroll)
        top_layout.addWidget(self.btn_toggle_sync)

        top_layout.addStretch()

        btn_export = QPushButton("📄 Fark Raporunu Kaydet")
        btn_export.clicked.connect(self._export_diff_report)
        top_layout.addWidget(btn_export)

        main_layout.addWidget(top_bar, 0)

        # Splitter: Left Doc, Right Doc, and Far Right Changes List
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Container (Doc A - Original)
        box_left = QWidget()
        lay_left = QVBoxLayout(box_left)
        lay_left.setContentsMargins(0, 0, 0, 0)
        lay_left.setSpacing(0)
        self.lbl_title_a = QLabel(" 🔴 Orijinal Belge")
        self.lbl_title_a.setFixedHeight(28)
        self.lbl_title_a.setStyleSheet("background-color: #331A1A; color: #FF6B6B; font-weight: bold; padding: 4px 8px; border-bottom: 1px solid #4D2626;")
        lay_left.addWidget(self.lbl_title_a, 0)
        self.pane_a = DiffScrollPane("A")
        lay_left.addWidget(self.pane_a, 1)
        self.main_splitter.addWidget(box_left)

        # Right Container (Doc B - Revised)
        box_right = QWidget()
        lay_right = QVBoxLayout(box_right)
        lay_right.setContentsMargins(0, 0, 0, 0)
        lay_right.setSpacing(0)
        self.lbl_title_b = QLabel(" 🟢 Revize Edilmiş Belge")
        self.lbl_title_b.setFixedHeight(28)
        self.lbl_title_b.setStyleSheet("background-color: #1A331E; color: #6BFF84; font-weight: bold; padding: 4px 8px; border-bottom: 1px solid #264D2D;")
        lay_right.addWidget(self.lbl_title_b, 0)
        self.pane_b = DiffScrollPane("B")
        lay_right.addWidget(self.pane_b, 1)
        self.main_splitter.addWidget(box_right)

        # Right Side Changes Table
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(8, 8, 8, 8)
        lbl_table = QLabel("📋 Tespit Edilen Değişiklikler")
        lbl_table.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        side_layout.addWidget(lbl_table)

        self.table_changes = QTableWidget()
        self.table_changes.setColumnCount(3)
        self.table_changes.setHorizontalHeaderLabels(["No", "Tür", "Açıklama"])
        self.table_changes.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_changes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_changes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_changes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_changes.itemClicked.connect(self._on_table_item_clicked)
        side_layout.addWidget(self.table_changes)
        
        self.main_splitter.addWidget(side_panel)
        self.main_splitter.setSizes([450, 450, 300])

        main_layout.addWidget(self.main_splitter, 1)

        # Connect synchronized scrolling
        self.pane_a.scrolled.connect(self._on_pane_a_scroll)
        self.pane_b.scrolled.connect(self._on_pane_b_scroll)
        self._is_syncing = False

    def load_diff(self, doc_a: PDFDocument, doc_b: PDFDocument, label_a: str = "Orijinal", label_b: str = "Revize"):
        """Runs the diff engine and populates both panes with highlighted changes."""
        self.doc_a = doc_a
        self.doc_b = doc_b
        self.lbl_title_a.setText(f" 🔴 Orijinal Belge: {label_a}")
        self.lbl_title_b.setText(f" 🟢 Revize Edilmiş Belge: {label_b}")

        self.engine = DiffEngine(doc_a, doc_b)
        self.changes = self.engine.run_diff()
        self.current_change_idx = -1

        self._render_pane(self.pane_a, self.doc_a, "A")
        self._render_pane(self.pane_b, self.doc_b, "B")
        self._populate_table()

        # Update summary
        counts = self.engine.summary_counts
        self.lbl_summary.setText(
            f"Farklar: 🟢 {counts['insert']} Eklendi  |  🔴 {counts['delete']} Silindi  |  🟡 {counts['replace']} Değişti  (Toplam: {counts['total']})"
        )
        self.lbl_counter.setText(f"0 / {len(self.changes)}")

        if self.changes:
            self.goto_next_change()

    def _render_pane(self, pane: DiffScrollPane, doc: PDFDocument, side: str):
        """Builds page widgets for one side and overlays diff highlight colors."""
        # Clear existing
        for pw in pane.page_widgets:
            pane.layout_pages.removeWidget(pw)
            pw.deleteLater()
        pane.page_widgets.clear()

        # Colors for highlights
        color_added = QColor(46, 204, 113, 90)     # Green
        color_deleted = QColor(231, 76, 60, 90)     # Red
        color_modified = QColor(241, 196, 15, 90)   # Yellow

        for i in range(doc.page_count):
            pw = PageRenderWidget(doc, i, self.zoom, pane.container)
            
            # Find highlights for this page
            raw_hl = self.engine.get_highlights_for_page(side, i)
            ui_highlights = []
            for h in raw_hl:
                if h.diff_type == "added":
                    c = color_added
                elif h.diff_type == "deleted":
                    c = color_deleted
                else:
                    c = color_modified
                ui_highlights.append((h.rect, c))

            pw.set_highlights(ui_highlights)
            pane.layout_pages.addWidget(pw)
            pane.page_widgets.append(pw)

    def _populate_table(self):
        """Fills the changes list table on the right side."""
        self.table_changes.setRowCount(len(self.changes))
        for row, item in enumerate(self.changes):
            type_label = {
                "insert": "🟢 Eklendi",
                "delete": "🔴 Silindi",
                "replace": "🟡 Değişti"
            }.get(item.diff_type, item.diff_type)

            it_id = QTableWidgetItem(str(item.change_id))
            it_type = QTableWidgetItem(type_label)
            it_desc = QTableWidgetItem(item.description)

            self.table_changes.setItem(row, 0, it_id)
            self.table_changes.setItem(row, 1, it_type)
            self.table_changes.setItem(row, 2, it_desc)

    def _on_table_item_clicked(self, item: QTableWidgetItem):
        row = item.row()
        self.jump_to_change(row)

    def jump_to_change(self, index: int):
        """Jumps and centers both panes on the specified change item."""
        if not self.changes or index < 0 or index >= len(self.changes):
            return

        self.current_change_idx = index
        self.lbl_counter.setText(f"{index + 1} / {len(self.changes)}")
        self.table_changes.selectRow(index)

        change = self.changes[index]

        # Scroll Pane A
        if change.page_a is not None and 0 <= change.page_a < len(self.pane_a.page_widgets):
            pw_a = self.pane_a.page_widgets[change.page_a]
            self.pane_a.ensureWidgetVisible(pw_a, 0, 80)

        # Scroll Pane B
        if change.page_b is not None and 0 <= change.page_b < len(self.pane_b.page_widgets):
            pw_b = self.pane_b.page_widgets[change.page_b]
            self.pane_b.ensureWidgetVisible(pw_b, 0, 80)

    def goto_next_change(self):
        if not self.changes:
            return
        next_idx = (self.current_change_idx + 1) % len(self.changes)
        self.jump_to_change(next_idx)

    def goto_previous_change(self):
        if not self.changes:
            return
        prev_idx = (self.current_change_idx - 1) % len(self.changes)
        self.jump_to_change(prev_idx)

    def _toggle_sync_scroll(self):
        self.sync_scroll = self.btn_toggle_sync.isChecked()
        self.btn_toggle_sync.setText(
            "🔗 Senkron Kaydırma: Açık" if self.sync_scroll else "🔓 Senkron Kaydırma: Kapalı"
        )

    def _on_pane_a_scroll(self, val: int):
        if self.sync_scroll and not self._is_syncing:
            self._is_syncing = True
            # Match scroll percentage
            max_a = self.pane_a.verticalScrollBar().maximum()
            max_b = self.pane_b.verticalScrollBar().maximum()
            if max_a > 0 and max_b > 0:
                ratio = val / max_a
                self.pane_b.verticalScrollBar().setValue(int(ratio * max_b))
            self._is_syncing = False

    def _on_pane_b_scroll(self, val: int):
        if self.sync_scroll and not self._is_syncing:
            self._is_syncing = True
            max_a = self.pane_a.verticalScrollBar().maximum()
            max_b = self.pane_b.verticalScrollBar().maximum()
            if max_a > 0 and max_b > 0:
                ratio = val / max_b
                self.pane_a.verticalScrollBar().setValue(int(ratio * max_a))
            self._is_syncing = False

    def _export_diff_report(self):
        """Exports a human-readable comparison report."""
        if not self.changes:
            QMessageBox.information(self, "Bilgi", "Dışa aktarılacak fark bulunamadı.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Fark Raporunu Kaydet", "nengi_pdf_fark_raporu.txt", "Metin Dosyası (*.txt)")
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("NeNgi PDF - İki Belge Karşılaştırma (DIFF) Raporu\n")
                f.write("=" * 60 + "\n\n")
                counts = self.engine.summary_counts
                f.write(f"Özet: {counts['insert']} Eklendi, {counts['delete']} Silindi, {counts['replace']} Değişti (Toplam {counts['total']} Fark)\n\n")
                f.write("DETAYLI DEĞİŞİKLİKLER LİSTESİ:\n")
                f.write("-" * 60 + "\n")
                for c in self.changes:
                    p_a = f"Sayfa {c.page_a + 1}" if c.page_a is not None else "Yok"
                    p_b = f"Sayfa {c.page_b + 1}" if c.page_b is not None else "Yok"
                    f.write(f"[{c.change_id}] ({c.diff_type.upper()}) [Orijinal: {p_a} | Revize: {p_b}]\n")
                    f.write(f"     {c.description}\n\n")
            QMessageBox.information(self, "Başarılı", f"Rapor başarıyla kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor kaydedilirken hata: {e}")
