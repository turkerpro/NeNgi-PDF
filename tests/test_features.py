"""
NeNgi PDF - Comprehensive Feature Test Suite
Tests newly implemented features: Annotations, Form Designer, Measurement,
Redaction & Sanitization, Accessibility, Attachments, and Optimization.
"""

import unittest
import os
import tempfile
import pymupdf as fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.annotations import AnnotationManager
from nengi.core.form_designer import FormDesigner, FormFieldConfig, FIELD_TEXT, FIELD_CHECKBOX
from nengi.core.measurement import MeasurementEngine, ScaleRatio
from nengi.core.redaction import RedactionEngine
from nengi.core.accessibility import AccessibilityChecker
from nengi.core.attachments import AttachmentManager
from nengi.core.pdf_optimizer import PDFOptimizer


class TestNeNgiAdvancedFeatures(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample_pdf = os.path.join(self.temp_dir.name, "test_doc.pdf")
        
        # Create a clean sample PDF
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.insert_text((50, 100), "Gizli Rapor: TC Kimlik No 12345678901 ve e-posta test@ornek.com", fontsize=12)
        page.insert_text((50, 150), "Adres: Istiklal Caddesi No: 42 Beyoglu Istanbul", fontsize=12)
        doc.save(self.sample_pdf)
        doc.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_annotations_crud(self):
        """Tests adding and managing annotations via AnnotationManager."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))
        page = doc.get_page(0)

        # Highlight
        quad = fitz.Rect(50, 90, 200, 110).quad
        annot_hl = AnnotationManager.add_highlight(page, [quad], color=(1, 1, 0))
        self.assertIsNotNone(annot_hl)

        # Underline
        annot_ul = AnnotationManager.add_underline(page, [quad], color=(0, 0, 1))
        self.assertIsNotNone(annot_ul)

        # Sticky note
        annot_note = AnnotationManager.add_sticky_note(page, fitz.Point(100, 100), "Önemli Not")
        self.assertIsNotNone(annot_note)

        # Line & Rect
        annot_line = AnnotationManager.add_line(page, fitz.Point(50, 200), fitz.Point(200, 200))
        self.assertIsNotNone(annot_line)

        annot_rect = AnnotationManager.add_rect(page, fitz.Rect(50, 250, 150, 300))
        self.assertIsNotNone(annot_rect)

        annots = AnnotationManager.get_all_annotations(page)
        self.assertGreaterEqual(len(annots), 5)

        doc.close()

    def test_form_designer_and_data_exchange(self):
        """Tests creating form fields, filling them, and exporting/importing form data."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))

        # Create text field
        cfg_text = FormFieldConfig(
            field_type=FIELD_TEXT,
            name="ad_soyad",
            rect=fitz.Rect(100, 200, 280, 225),
            value="Ahmet Yilmaz"
        )
        w_text = FormDesigner.create_field(doc, 0, cfg_text)
        self.assertIsNotNone(w_text)

        # Create checkbox
        cfg_chk = FormFieldConfig(
            field_type=FIELD_CHECKBOX,
            name="onay_kutusu",
            rect=fitz.Rect(100, 240, 120, 260),
            value="Yes"
        )
        w_chk = FormDesigner.create_field(doc, 0, cfg_chk)
        self.assertIsNotNone(w_chk)

        fields = FormDesigner.get_fields_on_page(doc, 0)
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0]["name"], "ad_soyad")

        # Export to CSV
        csv_path = os.path.join(self.temp_dir.name, "form_data.csv")
        self.assertTrue(FormDesigner.export_form_data(doc, csv_path, fmt="csv"))
        self.assertTrue(os.path.exists(csv_path))

        # Clear fields
        cleared = FormDesigner.clear_all_fields(doc)
        self.assertEqual(cleared, 2)

        # Import back from CSV
        imported = FormDesigner.import_form_data(doc, csv_path, fmt="csv")
        self.assertEqual(imported, 2)

        doc.close()

    def test_measurement_engine(self):
        """Tests geometric measurement calculations and scale ratio conversions."""
        p1 = fitz.Point(100, 100)
        p2 = fitz.Point(100, 200)

        # Distance is 100 points
        dist_pts = MeasurementEngine.calculate_distance(p1, p2)
        self.assertAlmostEqual(dist_pts, 100.0, places=2)

        # Scale ratio: 1 cm on page = 1 meter real
        scale = ScaleRatio(page_value=1.0, page_unit="cm", real_value=1.0, real_unit="m")
        # 1 cm = 72 / 2.54 = ~28.346 pt
        real_dist = scale.points_to_real_distance(dist_pts)
        self.assertGreater(real_dist, 3.0)  # ~3.52 meters

        # Polygon area (100x100 square = 10,000 sq points)
        poly = [fitz.Point(0, 0), fitz.Point(100, 0), fitz.Point(100, 100), fitz.Point(0, 100)]
        area = MeasurementEngine.calculate_polygon_area(poly)
        self.assertAlmostEqual(area, 10000.0, places=1)

        perim = MeasurementEngine.calculate_perimeter(poly, closed=True)
        self.assertAlmostEqual(perim, 400.0, places=1)

    def test_redaction_and_sanitization(self):
        """Tests pattern search (TCKN, email) and permanent sanitization."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))

        # Search TCKN pattern
        matches = RedactionEngine.search_patterns(doc, "tckn", is_custom_regex=False)
        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0]["text"], "12345678901")

        # Mark for redaction
        marked = RedactionEngine.mark_for_redaction(doc, matches, overlay_text="REDACTED")
        self.assertEqual(marked, len(matches))

        # Apply redaction permanently
        self.assertTrue(RedactionEngine.apply_redactions(doc))

        # Verify text was obliterated
        page = doc.get_page(0)
        text_after = page.get_text("text")
        self.assertNotIn("12345678901", text_after)

        # Sanitize metadata
        res = RedactionEngine.sanitize_document(doc, remove_metadata=True)
        self.assertEqual(res["metadata_cleared"], 1)

        doc.close()

    def test_accessibility_checker(self):
        """Tests accessibility auditing on document."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))

        results = AccessibilityChecker.audit_document(doc)
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 5)

        categories = {r["category"] for r in results}
        self.assertIn("Belge", categories)

        doc.close()

    def test_attachments_manager(self):
        """Tests embedding, listing, and extracting attachments."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))

        # Create dummy file to attach
        dummy_file = os.path.join(self.temp_dir.name, "ek_belge.txt")
        with open(dummy_file, "w", encoding="utf-8") as f:
            f.write("Bu bir test eki metnidir.")

        # Embed attachment
        self.assertTrue(AttachmentManager.add_attachment(doc, dummy_file, "Test Açıklaması"))

        atts = AttachmentManager.get_attachments(doc)
        self.assertEqual(len(atts), 1)
        self.assertEqual(atts[0]["name"], "ek_belge.txt")

        # Extract attachment
        extracted_file = os.path.join(self.temp_dir.name, "cikartilan.txt")
        self.assertTrue(AttachmentManager.extract_attachment(doc, "ek_belge.txt", extracted_file))
        with open(extracted_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Bu bir test eki metnidir.")

        # Delete attachment
        self.assertTrue(AttachmentManager.delete_attachment(doc, "ek_belge.txt"))
        atts_after = AttachmentManager.get_attachments(doc)
        self.assertEqual(len(atts_after), 0)

        doc.close()

    def test_pdf_optimizer(self):
        """Tests PDF size optimization and space audit."""
        doc = PDFDocument()
        self.assertTrue(doc.open(self.sample_pdf))

        audit = PDFOptimizer.get_space_usage(doc)
        self.assertIn("total_size", audit)

        opt_success = PDFOptimizer.optimize(doc, {"deflate": True, "garbage_collect": True})
        self.assertTrue(opt_success)

        doc.close()


if __name__ == "__main__":
    unittest.main()
