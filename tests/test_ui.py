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

    def test_compare_open_tabs(self):
        # Open both PDFs into tabs
        self.window.open_pdf(self.orig_pdf)
        self.window.open_pdf(self.rev_pdf)
        self.assertEqual(self.window.tabs.count(), 2)

        # Call compare_open_tabs directly
        self.window.compare_open_tabs()
        # Should now have 3 tabs: Tab 1, Tab 2, and the new DIFF tab!
        self.assertEqual(self.window.tabs.count(), 3)
        diff_tab = self.window.tabs.widget(2)
        self.assertIsInstance(diff_tab, DiffView)
        self.assertGreater(len(diff_tab.changes), 0)

    def test_merge_files_dialog(self):
        from nengi.ui.merge_dialog import MergeFilesDialog
        dlg = MergeFilesDialog(initial_files=[self.orig_pdf, self.rev_pdf], parent=self.window)
        self.assertEqual(len(dlg.files), 2)
        # Test move down
        dlg.list_widget.setCurrentRow(0)
        dlg._move_down()
        self.assertEqual(dlg.files[0], self.rev_pdf)

    def test_viewer_set_tool_and_stamp(self):
        self.window.open_pdf(self.orig_pdf)
        viewer = self.window.get_current_viewer()
        self.assertIsNotNone(viewer)
        # Verify set_tool doesn't crash
        viewer.set_tool("text")
        self.assertEqual(viewer.current_mode, "text")
        viewer.set_tool("whiteout")
        self.assertEqual(viewer.current_mode, "whiteout")
        # Verify set_stamp_image doesn't crash
        viewer.set_stamp_image(self.orig_pdf)
        self.assertEqual(viewer.current_mode, "stamp")
        self.assertEqual(viewer.stamp_image_path, self.orig_pdf)

    def test_draggable_text_widget(self):
        from nengi.ui.draggable_text import DraggableTextWidget
        from PyQt6.QtCore import QPoint
        self.window.open_pdf(self.orig_pdf)
        viewer = self.window.get_current_viewer()
        self.assertIsNotNone(viewer)
        pw = viewer.page_widgets[0]
        box = DraggableTextWidget(
            page_widget=pw,
            initial_pos=QPoint(100, 150),
            text="Test Sürüklenebilir Metin",
            fontsize=12,
            zoom=1.0,
            parent=pw
        )
        self.assertEqual(box.text, "Test Sürüklenebilir Metin")
        self.assertEqual(box.pos(), QPoint(100, 150))
        # Test moving
        box.move(QPoint(120, 180))
        self.assertEqual(box.pos(), QPoint(120, 180))
        # Commit
        box.commit_to_pdf()
        txt = pw.doc.get_page(0).get_text()
        self.assertIn("Test Sürüklenebilir Metin", txt)

    def test_draggable_stamp_widget_and_undo(self):
        """Tests Acrobat style interactive signature box, resizing, committing and undoing."""
        from nengi.ui.draggable_stamp import DraggableStampWidget
        from PyQt6.QtCore import QPoint
        import tempfile
        from PIL import Image

        self.window.open_pdf(self.orig_pdf)
        viewer = self.window.get_current_viewer()
        self.assertIsNotNone(viewer)
        pw = viewer.page_widgets[0]

        # Create dummy signature image
        tmp_img = tempfile.mktemp(suffix=".png")
        img = Image.new("RGBA", (140, 50), color=(0, 100, 200, 255))
        img.save(tmp_img)

        stamp = DraggableStampWidget(
            page_widget=pw,
            initial_pos=QPoint(50, 80),
            image_path=tmp_img,
            zoom=1.0,
            initial_width=140,
            initial_height=50,
            parent=pw
        )
        self.assertEqual(stamp.pos(), QPoint(50, 80))
        # Move
        stamp.move(QPoint(75, 120))
        self.assertEqual(stamp.pos(), QPoint(75, 120))
        # Resize
        stamp.resize(200, 80)
        self.assertEqual(stamp.width(), 200)
        self.assertEqual(stamp.height(), 80)

        # Commit to PDF
        initial_img_count = len(pw.doc.get_page(0).get_images())
        stamp.commit_to_pdf()
        after_img_count = len(pw.doc.get_page(0).get_images())
        self.assertGreater(after_img_count, initial_img_count)

        # Test Undo
        self.assertTrue(pw.doc.can_undo)
        pw.doc.undo()
        undone_img_count = len(pw.doc.get_page(0).get_images())
        self.assertEqual(undone_img_count, initial_img_count)

        if os.path.exists(tmp_img):
            os.unlink(tmp_img)


if __name__ == "__main__":
    unittest.main()
