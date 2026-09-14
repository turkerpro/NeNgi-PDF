"""
Unit tests for NeNgi PDF Core Engine:
Tests PDFDocument, DiffEngine, ImageRoundtrip, Security, Page Operations, and Conversion.
"""

import os
import sys
import tempfile
import unittest
import fitz
from PIL import Image
from PyQt6.QtWidgets import QApplication

from nengi.core.pdf_document import PDFDocument
from nengi.core.result import Result
from nengi.core.diff_engine import DiffEngine
from nengi.core.page_manager import PageManager
from nengi.core.security import SecurityManager
from nengi.core.converter import FormatConverter

# Initialize GUI application for QPixmap/QImage operations
app = QApplication.instance() or QApplication(sys.argv)


class TestNeNgiCore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="nengi_test_")
        self.doc_a_path = os.path.join(self.temp_dir, "original.pdf")
        self.doc_b_path = os.path.join(self.temp_dir, "revised.pdf")
        self._create_sample_pdfs()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_sample_pdfs(self):
        # Create Doc A (Original)
        doc_a = fitz.open()
        p1 = doc_a.new_page(width=595, height=842)
        p1.insert_text(fitz.Point(50, 100), "Sözleşme Maddesi 1: Taraflar anlaşmayı 30 gün içinde onaylayacaktır.", fontsize=14)
        p1.insert_text(fitz.Point(50, 150), "Bu eski ve silinecek olan gereksiz bir paragraftır.", fontsize=12)
        p1.insert_text(fitz.Point(50, 200), "Ödeme bedeli 1000 TL olarak belirlenmiştir.", fontsize=12)
        doc_a.save(self.doc_a_path)
        doc_a.close()

        # Create Doc B (Revised)
        doc_b = fitz.open()
        p1 = doc_b.new_page(width=595, height=842)
        p1.insert_text(fitz.Point(50, 100), "Sözleşme Maddesi 1: Taraflar anlaşmayı 45 gün içinde onaylayacaktır.", fontsize=14)
        # Second paragraph deleted!
        p1.insert_text(fitz.Point(50, 200), "Ödeme bedeli 2500 TL olarak belirlenmiştir.", fontsize=12)
        p1.insert_text(fitz.Point(50, 250), "YENİ EKLENEN ŞART: Gecikme halinde %5 faiz uygulanır.", fontsize=12)
        doc_b.save(self.doc_b_path)
        doc_b.close()

    def test_pdf_open_and_render(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        self.assertTrue(doc.is_open)
        self.assertEqual(doc.page_count, 1)
        pix_result = doc.render_page_pixmap(0, zoom=1.0)
        self.assertTrue(pix_result)
        pix = pix_result.value
        self.assertGreater(pix.width(), 0)
        self.assertGreater(pix.height(), 0)

        # Test file_name property
        self.assertEqual(doc.file_name, os.path.basename(self.doc_a_path))

        # Test DPI rendering for printing
        qimg_result = doc.render_page_qimage(0, dpi=300)
        self.assertTrue(qimg_result)
        qimg_dpi = qimg_result.value
        self.assertFalse(qimg_dpi.isNull())
        self.assertGreater(qimg_dpi.width(), pix.width())
        self.assertGreater(qimg_dpi.height(), pix.height())

        doc.close()

    def test_diff_engine(self):
        doc_a = PDFDocument(self.doc_a_path)
        doc_b = PDFDocument(self.doc_b_path)
        engine = DiffEngine(doc_a, doc_b)
        changes = engine.run_diff()

        self.assertGreater(len(changes), 0)
        summary = engine.summary_counts
        self.assertGreater(summary["total"], 0)

        # Highlights check
        hl_a = engine.get_highlights_for_page("A", 0)
        hl_b = engine.get_highlights_for_page("B", 0)
        self.assertTrue(any(h.diff_type in ["deleted", "modified"] for h in hl_a))
        self.assertTrue(any(h.diff_type in ["added", "modified"] for h in hl_b))

        doc_a.close()
        doc_b.close()

    def test_page_operations(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        init_count = doc.page_count
        new_idx_result = doc.insert_blank_page()
        self.assertTrue(new_idx_result)
        new_idx = new_idx_result.value
        self.assertEqual(doc.page_count, init_count + 1)
        
        rot_result = doc.rotate_page(0, 90)
        self.assertTrue(rot_result)
        self.assertEqual(rot_result.value, 90)

        del_result = doc.delete_page(new_idx)
        self.assertTrue(del_result)
        self.assertEqual(doc.page_count, init_count)
        doc.close()

    def test_security_encryption_and_decryption(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        enc_path = os.path.join(self.temp_dir, "encrypted.pdf")
        enc_result = SecurityManager.encrypt_document(doc, "secret123", enc_path)
        self.assertTrue(enc_result)
        doc.close()

        # Check that it's encrypted
        enc_doc = PDFDocument(enc_path)
        open_result2 = enc_doc.open(enc_path)
        self.assertTrue(open_result2)
        self.assertTrue(enc_doc.is_encrypted)
        self.assertFalse(enc_doc.is_authenticated)

        # Authenticate
        auth_result = enc_doc.authenticate("secret123")
        self.assertTrue(auth_result)

        # Decrypt
        dec_path = os.path.join(self.temp_dir, "decrypted.pdf")
        dec_result = SecurityManager.remove_password(enc_doc, dec_path)
        self.assertTrue(dec_result)
        enc_doc.close()

        # Recheck decrypted
        clean_doc = PDFDocument(dec_path)
        open_result3 = clean_doc.open(dec_path)
        self.assertTrue(open_result3)
        self.assertFalse(clean_doc.is_encrypted)
        clean_doc.close()

    def test_format_converter(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        img_out = os.path.join(self.temp_dir, "page_1.png")
        img_result = FormatConverter.export_page_as_image(doc, 0, img_out, dpi=150)
        self.assertTrue(img_result)
        self.assertTrue(os.path.exists(img_out))
        doc.close()

        # Convert image back to PDF
        new_pdf_out = os.path.join(self.temp_dir, "from_image.pdf")
        pdf_result = FormatConverter.images_to_pdf([img_out], new_pdf_out)
        self.assertTrue(pdf_result)
        self.assertTrue(os.path.exists(new_pdf_out))
        res_doc = PDFDocument(new_pdf_out)
        open_result2 = res_doc.open(new_pdf_out)
        self.assertTrue(open_result2)
        self.assertEqual(res_doc.page_count, 1)
        res_doc.close()

    def test_text_words_and_in_place_edit(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        words_result = doc.get_page_text_words(0)
        self.assertTrue(words_result)
        words = words_result.value
        self.assertGreater(len(words), 0)
        
        # Find first word
        target_word = words[0]
        rect = fitz.Rect(target_word[0], target_word[1], target_word[2], target_word[3])
        
        # Edit text in-place
        edit_result = doc.edit_text_at_rect(0, rect, "TEST_METIN_GUNCEL")
        self.assertTrue(edit_result)
        self.assertTrue(doc.is_modified)
        
        # Verify that "TEST_METIN_GUNCEL" appears in the page text
        page_text = doc.get_page(0).get_text("text")
        self.assertIn("TEST_METIN_GUNCEL", page_text)
        doc.close()

    def test_undo_redo_and_block_font_detection(self):
        doc = PDFDocument(self.doc_a_path)
        open_result = doc.open(self.doc_a_path)
        self.assertTrue(open_result)
        orig_text = doc.get_page(0).get_text("text")

        # 1. Blocks detection
        blocks_result = doc.get_page_blocks(0)
        self.assertTrue(blocks_result)
        blocks = blocks_result.value
        self.assertGreater(len(blocks), 0)
        block = blocks[0]
        block_rect = fitz.Rect(block[0], block[1], block[2], block[3])

        # 2. Font style detection
        style_result = doc.detect_text_style_at_rect(0, block_rect)
        self.assertTrue(style_result)
        style = style_result.value
        self.assertIn("family", style)
        self.assertIn("size", style)
        self.assertGreater(style["size"], 0)

        # 3. Replace paragraph block
        replace_result = doc.replace_text_block(0, block_rect, "PARAGRAF_DEGISIMI_TEST", fontsize=style["size"])
        self.assertTrue(replace_result)
        mod_text = doc.get_page(0).get_text("text")
        self.assertIn("PARAGRAF_DEGISIMI_TEST", mod_text)

        # 4. Undo the change
        self.assertTrue(doc.can_undo())
        undo_result = doc.undo()
        self.assertTrue(undo_result)
        reverted_text = doc.get_page(0).get_text("text")
        self.assertNotIn("PARAGRAF_DEGISIMI_TEST", reverted_text)
        self.assertEqual(reverted_text, orig_text)

        # 5. Redo the change
        self.assertTrue(doc.can_redo())
        redo_result = doc.redo()
        self.assertTrue(redo_result)
        redone_text = doc.get_page(0).get_text("text")
        self.assertIn("PARAGRAF_DEGISIMI_TEST", redone_text)

        # 6. Test insert_new_text with undo
        pt = fitz.Point(100, 200)
        insert_result = doc.insert_new_text(0, pt, "YENI_STUDIO_METIN")
        self.assertTrue(insert_result)
        self.assertIn("YENI_STUDIO_METIN", doc.get_page(0).get_text("text"))
        undo_result2 = doc.undo()
        self.assertTrue(undo_result2)
        self.assertNotIn("YENI_STUDIO_METIN", doc.get_page(0).get_text("text"))

        doc.close()

    def test_turkish_text_insertion(self):
        doc = PDFDocument()
        doc.doc = fitz.open()
        doc.doc.new_page()
        # Insert Turkish text
        turkish_sample = "Deneme: Şş Çç Ğğ Iı İi Öö Üü"
        insert_result = doc.insert_new_text(0, fitz.Point(50, 50), turkish_sample)
        self.assertTrue(insert_result)
        txt = doc.get_page(0).get_text()
        self.assertIn("Şş", txt)
        self.assertIn("Çç", txt)
        self.assertIn("Ğğ", txt)
        self.assertIn("Öö", txt)
        self.assertIn("Üü", txt)
        doc.close()

    def test_virtual_printer_manager(self):
        from nengi.core.virtual_printer import VirtualPrinterManager
        self.assertEqual(VirtualPrinterManager.PRINTER_NAME, "NeNgi PDF")
        self.assertEqual(VirtualPrinterManager.DRIVER_NAME, "Microsoft Print to PDF")
        # Ensure is_printer_installed runs safely without throwing
        res = VirtualPrinterManager.is_printer_installed()
        self.assertIsInstance(res.success, bool)

    def test_corrupted_pdf_handling(self):
        # Create a half-written/corrupted PDF file
        bad_file = os.path.join(self.temp_dir, "corrupted.pdf")
        with open(bad_file, "wb") as f:
            f.write(b"%PDF-1.4\n%corrupted truncated content without EOF")

        doc = PDFDocument()
        is_ok = doc.open(bad_file)
        self.assertFalse(is_ok)
        self.assertFalse(doc.is_open)
        self.assertEqual(doc.page_count, 0)


if __name__ == "__main__":
    unittest.main()
