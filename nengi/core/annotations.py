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
        return list(page.annots() or [])
    
    @staticmethod
    def delete_annotation(page, annot):
        page.delete_annot(annot)
    
    @staticmethod
    def export_annotations_xfdf(doc, output_path):
        """Export all annotations to XFDF format (highlight/underline/strike/note)."""
        import xml.etree.ElementTree as ET
        try:
            fitz_doc = getattr(doc, "doc", doc)
            if fitz_doc is None:
                return False

            def _to_hex(color):
                try:
                    if not color:
                        return "#FFFF00"
                    r, g, b = color[:3]
                    return "#{:02X}{:02X}{:02X}".format(
                        max(0, min(255, int(round(r * 255)))),
                        max(0, min(255, int(round(g * 255)))),
                        max(0, min(255, int(round(b * 255)))),
                    )
                except Exception:
                    return "#FFFF00"

            xfdf = ET.Element("xfdf", {
                "xmlns": "http://ns.adobe.com/xfdf/",
                "xml:space": "preserve",
            })
            annots_el = ET.SubElement(xfdf, "annots")
            count = 0
            for page_no in range(len(fitz_doc)):
                page = fitz_doc[page_no]
                for annot in (page.annots() or []):
                    try:
                        code, name = annot.type
                    except Exception:
                        continue
                    lname = str(name or "").lower()
                    if lname == "highlight":
                        tag = "highlight"
                    elif lname == "underline":
                        tag = "underline"
                    elif lname in ("strikeout", "strike-out", "strike"):
                        tag = "strike"
                    elif lname == "text":
                        tag = "text"
                    else:
                        continue
                    colors = {}
                    try:
                        colors = annot.colors or {}
                    except Exception:
                        colors = {}
                    stroke = colors.get("stroke") if isinstance(colors, dict) else None
                    rect = annot.rect
                    el = ET.SubElement(annots_el, tag, {
                        "page": str(page_no),
                        "rect": f"{rect.x0},{rect.y0},{rect.x1},{rect.y1}",
                        "color": _to_hex(stroke),
                    })
                    try:
                        info = annot.info or {}
                        contents = info.get("content", "") or ""
                    except Exception:
                        contents = ""
                    if contents:
                        el.set("contents", contents)
                    if tag in ("highlight", "underline", "strike"):
                        try:
                            verts = annot.vertices or []
                        except Exception:
                            verts = []
                        if verts:
                            coords = ",".join(f"{float(p[0])},{float(p[1])}" for p in verts)
                            el.set("coords", coords)
                    elif tag == "text":
                        try:
                            info = annot.info or {}
                            if info.get("name"):
                                el.set("icon", str(info.get("name")))
                        except Exception:
                            pass
                    count += 1
            tree = ET.ElementTree(xfdf)
            ET.indent(tree, space="  ")
            tree.write(output_path, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error exporting XFDF: {e}")
            return False

    @staticmethod
    def import_annotations_xfdf(doc, xfdf_path):
        """Import annotations from XFDF file (highlight/underline/strike/note)."""
        import xml.etree.ElementTree as ET
        try:
            fitz_doc = getattr(doc, "doc", doc)
            if fitz_doc is None:
                return 0

            def _parse_hex(s):
                s = (s or "#FFFF00").strip().lstrip("#")
                if len(s) == 6:
                    return (int(s[0:2], 16) / 255.0,
                            int(s[2:4], 16) / 255.0,
                            int(s[4:6], 16) / 255.0)
                return (1.0, 1.0, 0.0)

            def _get_page(n):
                if hasattr(doc, "get_page"):
                    return doc.get_page(n)
                return fitz_doc[n]

            tree = ET.parse(xfdf_path)
            root = tree.getroot()
            ns = {"x": "http://ns.adobe.com/xfdf/"}
            annots_el = root.find("x:annots", ns)
            elems = list(annots_el) if annots_el is not None else list(root)
            # Non-namespaced fallback: filter known tags
            if annots_el is None:
                elems = [e for e in root.iter()
                         if e.tag.split("}")[-1] in ("highlight", "underline", "strike", "text")]
            imported = 0
            for el in elems:
                tag = el.tag.split("}")[-1].lower()
                try:
                    page_no = int(el.get("page", "0"))
                except ValueError:
                    continue
                rect_s = el.get("rect", "")
                try:
                    x0, y0, x1, y1 = (float(v) for v in rect_s.split(","))
                    rect = fitz.Rect(x0, y0, x1, y1)
                except Exception:
                    continue
                color = _parse_hex(el.get("color"))
                contents = el.get("contents", "") or ""
                page = _get_page(page_no)
                annot = None
                if tag == "highlight":
                    quads = AnnotationManager._coords_to_quads(el.get("coords"), rect)
                    annot = page.add_highlight_annot(quads)
                    annot.set_colors(stroke=color)
                    annot.update()
                elif tag == "underline":
                    quads = AnnotationManager._coords_to_quads(el.get("coords"), rect)
                    annot = page.add_underline_annot(quads)
                    annot.set_colors(stroke=color)
                    annot.update()
                elif tag == "strike":
                    quads = AnnotationManager._coords_to_quads(el.get("coords"), rect)
                    annot = page.add_strikeout_annot(quads)
                    annot.set_colors(stroke=color)
                    annot.update()
                elif tag == "text":
                    icon = el.get("icon", "Note")
                    point = fitz.Point(rect.x0, rect.y0)
                    annot = page.add_text_annot(point, contents or " ", icon=icon)
                    try:
                        annot.set_colors(stroke=color)
                    except Exception:
                        pass
                    annot.update()
                else:
                    continue
                if annot is not None and contents and tag != "text":
                    try:
                        annot.set_info({"content": contents})
                        annot.update()
                    except Exception:
                        pass
                imported += 1
            try:
                if hasattr(doc, "is_modified"):
                    doc.is_modified = True
            except Exception:
                pass
            return imported
        except Exception as e:
            print(f"Error importing XFDF: {e}")
            return 0

    @staticmethod
    def _coords_to_quads(coords, fallback_rect):
        """Parse XFDF coords string into fitz quads; fallback to rect quad."""
        try:
            if coords:
                nums = [float(v) for v in coords.split(",")]
                quads = []
                for i in range(0, len(nums) - 7, 8):
                    pts = [(nums[i + j], nums[i + j + 1]) for j in range(0, 8, 2)]
                    quads.append(fitz.Quad(
                        fitz.Point(*pts[0]), fitz.Point(*pts[1]),
                        fitz.Point(*pts[2]), fitz.Point(*pts[3])))
                if quads:
                    return quads
        except Exception:
            pass
        return [fallback_rect.quad]
