"""
UI Integration tests for NeNgi PDF MainWindow and DiffView.
"""

import os
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ensure offscreen Qt application
os.environ["QT_QPA_PLATFORM"] = "offscreen"
app = QApplication.instance() or QApplication(sys.argv)

from nengi.ui.main_window import MainWindow
from nengi.ui.diff_view import DiffView
from nengi.core.pdf_document import PDFDocument


class TestNeNgiUI(unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.samples_dir = os.path.join(base_dir, "resources", "samples")
        self.orig_pdf = os.path.join(self.samples_dir, "sozlesme_orijinal.pdf")
        self.rev_pdf = os.path.join(self.samples_dir, "sozlesme_revize.pdf")
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()

    def test_main_window_open_pdf(self):
        self.window.open_pdf(self.orig_pdf)
        self.assertEqual(self.window.tabs.count(), 1)
        viewer = self.window.get_current_viewer()
        self.assertIsNotNone(viewer)
        self.assertEqual(viewer.doc.page_count, 1)

    def test_diff_view_loading(self):
        doc_a = PDFDocument(self.orig_pdf)
        doc_b = PDFDocument(self.rev_pdf)

        diff_view = DiffView()
        diff_view.load_diff(doc_a, doc_b, "Orijinal", "Revize")

        self.assertGreater(len(diff_view.changes), 0)
        self.assertGreater(diff_view.table_changes.rowCount(), 0)

        # Check navigation
        diff_view.goto_next_change()
        self.assertEqual(diff_view.current_change_idx, 1 if len(diff_view.changes) > 1 else 0)

        diff_view.goto_previous_change()
        self.assertEqual(diff_view.current_change_idx, 0)

        doc_a.close()
        doc_b.close()


if __name__ == "__main__":
    unittest.main()
