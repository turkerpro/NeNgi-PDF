import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_call1 = """                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                        baseline_y=style.get("baseline_y")
                    )"""

new_call1 = """                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                        baseline_y=style.get("baseline_y"), origin_x=style.get("origin_x")
                    )"""
content = content.replace(old_call1, new_call1)

old_call2 = """                self.doc.replace_text_block(
                    self.page_idx, union_rect, dlg.result_text,
                    fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                    baseline_y=style.get("baseline_y")
                )"""

new_call2 = """                self.doc.replace_text_block(
                    self.page_idx, union_rect, dlg.result_text,
                    fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                    baseline_y=style.get("baseline_y"), origin_x=style.get("origin_x")
                )"""
content = content.replace(old_call2, new_call2)

with open(filepath, 'w') as f:
    f.write(content)
