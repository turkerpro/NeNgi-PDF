"""
NeNgi PDF - Export Engine
Converts PDF to various formats (Word, Excel, PowerPoint, HTML).
"""
import os
import io
import fitz
from PIL import Image

class ExportEngine:
    @staticmethod
    def pdf_to_docx(doc, output_path, options=None):
        """Convert PDF to Word (.docx) using python-docx."""
        if doc is None or getattr(doc, "doc", None) is None or not getattr(doc, "is_open", False):
            return False
        try:
            from docx import Document
            from docx.shared import Pt
        except ImportError:
            raise ImportError("python-docx gerekli. Lütfen kurun (pip install python-docx).")
            
        word_doc = Document()
        for i in range(len(doc.doc)):
            page = doc.get_page(i)
            text = page.get_text("text")
            if text.strip():
                p = word_doc.add_paragraph(text)
            if i < len(doc.doc) - 1:
                word_doc.add_page_break()
                
        word_doc.save(output_path)
        return True

    @staticmethod
    def pdf_to_xlsx(doc, output_path, options=None):
        """Convert PDF to Excel (.xlsx) using openpyxl."""
        if doc is None or getattr(doc, "doc", None) is None or not getattr(doc, "is_open", False):
            return False
        try:
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("openpyxl gerekli. Lütfen kurun (pip install openpyxl).")
            
        wb = Workbook()
        ws = wb.active
        
        row_idx = 1
        for i in range(len(doc.doc)):
            page = doc.get_page(i)
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
        return True

    @staticmethod
    def pdf_to_pptx(doc, output_path, options=None):
        """Convert PDF to PowerPoint (.pptx) using python-pptx."""
        if doc is None or getattr(doc, "doc", None) is None or not getattr(doc, "is_open", False):
            return False
        try:
            from pptx import Presentation
            from pptx.util import Inches
        except ImportError:
            raise ImportError("python-pptx gerekli. Lütfen kurun (pip install python-pptx).")
            
        prs = Presentation()
        blank_slide_layout = prs.slide_layouts[6]
        
        for i in range(len(doc.doc)):
            page = doc.get_page(i)
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
        return True

    @staticmethod
    def pdf_to_html(doc, output_path, options=None):
        """Convert PDF to HTML."""
        if doc is None or getattr(doc, "doc", None) is None or not getattr(doc, "is_open", False):
            return False
        html_content = "<html><body>"
        for i in range(len(doc.doc)):
            page = doc.get_page(i)
            html_content += f"<div id='page_{i+1}'>"
            html_content += page.get_text("html")
            html_content += "</div><hr/>"
        html_content += "</body></html>"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
