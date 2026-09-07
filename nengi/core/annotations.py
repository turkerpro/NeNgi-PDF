import fitz

class AnnotationManager:
    """Manages PDF annotations using PyMuPDF (fitz) API."""
    
    @staticmethod
    def add_highlight(page, quads, color=(1, 1, 0), opacity=0.5) -> fitz.Annot:
        """Add highlight annotation over text quads."""
        annot = page.add_highlight_annot(quads)
        annot.set_colors(stroke=color)
        annot.set_opacity(opacity)
        annot.update()
        return annot
    
    @staticmethod
    def add_underline(page, quads, color=(0, 0, 1)) -> fitz.Annot:
        annot = page.add_underline_annot(quads)
        annot.set_colors(stroke=color)
        annot.update()
        return annot
    
    @staticmethod
    def add_strikethrough(page, quads, color=(1, 0, 0)) -> fitz.Annot:
        annot = page.add_strikeout_annot(quads)
        annot.set_colors(stroke=color)
        annot.update()
        return annot
    
    @staticmethod
    def add_sticky_note(page, point, text, icon='Note', color=(1, 1, 0)):
        annot = page.add_text_annot(point, text, icon=icon)
        annot.set_colors(stroke=color)
        annot.update()
        return annot
    
    @staticmethod
    def add_freetext(page, rect, text, fontsize=12, color=(0,0,0), fill=(1,1,1)):
        annot = page.add_freetext_annot(rect, text, fontsize=fontsize, text_color=color, fill_color=fill)
        annot.update()
        return annot
    
    @staticmethod
    def add_line(page, p1, p2, color=(1, 0, 0), width=1.5, end_style=None):
        annot = page.add_line_annot(p1, p2)
        annot.set_colors(stroke=color)
        annot.set_border(width=width)
        if end_style:  # e.g. fitz.PDF_ANNOT_LE_CLOSED_ARROW
            annot.set_line_ends(0, end_style)
        annot.update()
        return annot
    
    @staticmethod
    def add_rect(page, rect, color=(0,0,1), fill=None, width=1.5):
        annot = page.add_rect_annot(rect)
        if fill:
            annot.set_colors(stroke=color, fill=fill)
        else:
            annot.set_colors(stroke=color)
        annot.set_border(width=width)
        annot.update()
        return annot
    
    @staticmethod
    def add_circle(page, rect, color=(0,0,1), fill=None, width=1.5):
        annot = page.add_circle_annot(rect)
        if fill:
            annot.set_colors(stroke=color, fill=fill)
        else:
            annot.set_colors(stroke=color)
        annot.set_border(width=width)
        annot.update()
        return annot
    
    @staticmethod
    def add_ink(page, paths, color=(0,0,0), width=2.0):
        """Add freehand ink annotation. paths is list of point lists."""
        annot = page.add_ink_annot(paths)
        annot.set_colors(stroke=color)
        annot.set_border(width=width)
        annot.update()
        return annot
    
    @staticmethod
    def add_polygon(page, points, color=(0,0,1), fill=None, width=1.5):
        annot = page.add_polygon_annot(points)
        if fill:
            annot.set_colors(stroke=color, fill=fill)
        else:
            annot.set_colors(stroke=color)
        annot.set_border(width=width)
        annot.update()
        return annot
    
    @staticmethod
    def add_stamp(page, rect, stamp_name='Draft'):
        stamp_map = {
            "ONAYLANDI": 0,    # Approved
            "TASLAK": 4,       # Draft
            "GİZLİ": 2,        # Confidential
            "SON": 7,          # Final
            "REDDEDİLDİ": 10,  # NotApproved
            "GEÇERSİZ": 6,     # Expired
        }
        stamp_val = stamp_map.get(stamp_name, 4) # Default to Draft
        annot = page.add_stamp_annot(rect, stamp=stamp_val)
        annot.update()
        return annot
    
    @staticmethod
    def get_all_annotations(page):
        return list(page.annots())
    
    @staticmethod
    def delete_annotation(page, annot):
        page.delete_annot(annot)
    
    @staticmethod
    def export_annotations_xfdf(doc, output_path):
        """Export all annotations to XFDF format."""
        pass
    
    @staticmethod
    def import_annotations_xfdf(doc, xfdf_path):
        """Import annotations from XFDF file."""
        pass
