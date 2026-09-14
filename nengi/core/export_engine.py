"""
NeNgi PDF - Export Engine
Converts PDF to various formats (Word, Excel, PowerPoint, HTML).
"""
import os
import io
import fitz
from PIL import Image
from nengi.core.result import Result

class ExportEngine:
    @staticmethod
    def pdf_to_docx(doc, output_path, options=None) -> Result[bool]:
        """Convert PDF to Word (.docx) using python-docx."""
        fitz_doc = getattr(doc, "doc", doc) if not isinstance(doc, str) else None
        if fitz_doc is None or getattr(fitz_doc, "is_closed", False):
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        try:
            from docx import Document
            from docx.shared import Pt
        except ImportError:
            return Result.fail("python-docx not installed", "Run: pip install python-docx", "MISSING_DEPENDENCY")
        
        word_doc = Document()
        for i in range(len(fitz_doc)):
            page = fitz_doc[i]
            text = page.get_text("text")
            if text.strip():
                p = word_doc.add_paragraph(text)
            if i < len(fitz_doc) - 1:
                word_doc.add_page_break()
                
        word_doc.save(output_path)
        return Result.ok(True)

    @staticmethod
    def pdf_to_xlsx(doc, output_path, options=None) -> Result[bool]:
        """Convert PDF to Excel (.xlsx) using openpyxl."""
        fitz_doc = getattr(doc, "doc", doc) if not isinstance(doc, str) else None
        if fitz_doc is None or getattr(fitz_doc, "is_closed", False):
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        try:
            from openpyxl import Workbook
        except ImportError:
            return Result.fail("openpyxl not installed", "Run: pip install openpyxl", "MISSING_DEPENDENCY")
        
        wb = Workbook()
        ws = wb.active
        
        row_idx = 1
        for i in range(len(fitz_doc)):
            page = fitz_doc[i]
            # Find tables (basic text split for now, real table detection is complex)
            tabs = page.find_tables()
            if tabs:
                for tab in tabs:
                    data = tab.extract()
                    for row in data:
                        ws.append(row)
                        row_idx += 1
            else:
                text = page.get_text("text")
                for line in text.splitlines():
                    if line.strip():
                        ws.cell(row=row_idx, column=1, value=line)
                        row_idx += 1
                        
        wb.save(output_path)
        return Result.ok(True)

    @staticmethod
    def pdf_to_pptx(doc, output_path, options=None) -> Result[bool]:
        """Convert PDF to PowerPoint (.pptx) using python-pptx."""
        fitz_doc = getattr(doc, "doc", doc) if not isinstance(doc, str) else None
        if fitz_doc is None or getattr(fitz_doc, "is_closed", False):
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        try:
            from pptx import Presentation
            from pptx.util import Inches
        except ImportError:
            return Result.fail("python-pptx not installed", "Run: pip install python-pptx", "MISSING_DEPENDENCY")
        
        prs = Presentation()
        blank_slide_layout = prs.slide_layouts[6]
        
        for i in range(len(fitz_doc)):
            page = fitz_doc[i]
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Render page as image and place on slide
            pix = page.get_pixmap(dpi=150)
            img_mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(img_mode, [pix.width, pix.height], pix.samples)
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="PNG")
            buf.seek(0)
            
            slide.shapes.add_picture(buf, 0, 0, prs.slide_width, prs.slide_height)
            
        prs.save(output_path)
        return Result.ok(True)

    @staticmethod
    def pdf_to_txt(doc, output_path, options=None) -> Result[bool]:
        """Convert PDF page texts to a plain-text file."""
        fitz_doc = getattr(doc, "doc", doc) if not isinstance(doc, str) else None
        opened_here = False
        try:
            if isinstance(doc, str):
                fitz_doc = fitz.open(doc)
                opened_here = True
            if fitz_doc is None or getattr(fitz_doc, "is_closed", False):
                return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
            with open(output_path, "w", encoding="utf-8") as f:
                for i in range(len(fitz_doc)):
                    page = fitz_doc[i]
                    f.write(page.get_text("text"))
                    if i < len(fitz_doc) - 1:
                        f.write("\n")
            return Result.ok(True)
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Error exporting TXT")
            return Result.from_exception(e, "Failed to export TXT", "EXPORT_TXT_FAILED")
        finally:
            if opened_here and fitz_doc is not None:
                try:
                    fitz_doc.close()
                except Exception:
                    pass

    @staticmethod
    def pdf_to_html(doc, output_path, options=None) -> Result[bool]:
        """Convert PDF to HTML."""
        fitz_doc = getattr(doc, "doc", doc) if not isinstance(doc, str) else None
        if fitz_doc is None or getattr(fitz_doc, "is_closed", False):
            return Result.fail("Document not open", "Open a document first", "DOC_NOT_OPEN")
        try:
            html_content = "<html><body>"
            for i in range(len(fitz_doc)):
                page = fitz_doc[i]
                html_content += f"<div id='page_{i+1}'>"
                html_content += page.get_text("html")
                html_content += "</div><hr/>"
            html_content += "</body></html>"
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return Result.ok(True)
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Error exporting HTML")
            return Result.from_exception(e, "Failed to export HTML", "EXPORT_HTML_FAILED")
