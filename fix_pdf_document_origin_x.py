import os

filepath = 'nengi/core/pdf_document.py'
with open(filepath, 'r') as f:
    content = f.read()

old_sig = """    def replace_text_block(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0),
        baseline_y: float = None
    ) -> bool:"""

new_sig = """    def replace_text_block(
        self, page_number: int, rect: fitz.Rect, new_text: str,
        fontname: str = "helv", fontsize: float = 11.0, color: Tuple[float, float, float] = (0, 0, 0),
        baseline_y: float = None, origin_x: float = None
    ) -> bool:"""
content = content.replace(old_sig, new_sig)

old_insert = """            lines = new_text.splitlines()
            if len(lines) == 1:
                # Single line: use exact baseline if provided, else use textbox for perfect bounds
                if baseline_y is not None:
                    page.insert_text((rect.x0, baseline_y), lines[0], fontsize=fontsize, fontname=target_font, color=color)"""

new_insert = """            lines = new_text.splitlines()
            if len(lines) == 1:
                # Single line: use exact baseline if provided, else use textbox for perfect bounds
                if baseline_y is not None:
                    x_pos = origin_x if origin_x is not None else rect.x0
                    page.insert_text((x_pos, baseline_y), lines[0], fontsize=fontsize, fontname=target_font, color=color)"""
content = content.replace(old_insert, new_insert)

with open(filepath, 'w') as f:
    f.write(content)
