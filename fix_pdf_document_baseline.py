import os

filepath = 'nengi/core/pdf_document.py'
with open(filepath, 'r') as f:
    content = f.read()

# Add baseline_y to detect_text_style_at_rect
old_style_dict = """        default_style = {
            "family": "Arial",
            "size": 11.0,
            "is_bold": False,
            "is_italic": False,
            "color_rgb": (0.0, 0.0, 0.0),
            "raw_font": "Helvetica",
            "fitz_font": "helv"
        }"""

new_style_dict = """        default_style = {
            "family": "Arial",
            "size": 11.0,
            "is_bold": False,
            "is_italic": False,
            "color_rgb": (0.0, 0.0, 0.0),
            "raw_font": "Helvetica",
            "fitz_font": "helv",
            "baseline_y": None,
            "origin_x": None
        }"""
content = content.replace(old_style_dict, new_style_dict)

old_return_style = """            return {
                "family": clean_family,
                "size": size,
                "is_bold": is_bold,
                "is_italic": is_italic,
                "color_rgb": color_rgb,
                "raw_font": raw_font,
                "fitz_font": fitz_font
            }"""

new_return_style = """            return {
                "family": clean_family,
                "size": size,
                "is_bold": is_bold,
                "is_italic": is_italic,
                "color_rgb": color_rgb,
                "raw_font": raw_font,
                "fitz_font": fitz_font,
                "baseline_y": span.get("origin", [0, 0])[1] if "origin" in span else None,
                "origin_x": span.get("origin", [0, 0])[0] if "origin" in span else None
            }"""
content = content.replace(old_return_style, new_return_style)

# Update replace_text_block to optionally accept baseline_y
old_replace_sig = """    def replace_text_block(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0)
    ) -> bool:"""

new_replace_sig = """    def replace_text_block(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0),
        baseline_y: float = None
    ) -> bool:"""
content = content.replace(old_replace_sig, new_replace_sig)

old_insert = """            lines = new_text.splitlines()
            line_height = fontsize * 1.25
            y_pos = rect.y0 + fontsize
            for line in lines:
                if y_pos > page.rect.height - 10:
                    break
                page.insert_text((rect.x0, y_pos), line, fontsize=fontsize, fontname=target_font, color=color)
                y_pos += line_height"""

new_insert = """            lines = new_text.splitlines()
            if len(lines) == 1:
                # Single line: use exact baseline if provided, else use textbox for perfect bounds
                if baseline_y is not None:
                    page.insert_text((rect.x0, baseline_y), lines[0], fontsize=fontsize, fontname=target_font, color=color)
                else:
                    page.insert_textbox(rect, lines[0], fontsize=fontsize, fontname=target_font, color=color, align=0)
            else:
                # Multi-line: use insert_textbox for automatic wrapping and line-heights
                page.insert_textbox(rect, new_text, fontsize=fontsize, fontname=target_font, color=color, align=0)"""
content = content.replace(old_insert, new_insert)

with open(filepath, 'w') as f:
    f.write(content)
