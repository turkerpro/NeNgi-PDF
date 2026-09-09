import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_replace1 = """                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb
                    )"""

new_replace1 = """                    self.doc.replace_text_block(
                        self.page_idx, block_rect, dlg.result_text,
                        fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                        baseline_y=style.get("baseline_y")
                    )"""

if old_replace1 in content:
    content = content.replace(old_replace1, new_replace1)


old_replace2 = """            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.doc.replace_text_block(
                    self.page_idx, union_rect, dlg.result_text,
                    fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb
                )"""

new_replace2 = """            if dlg.exec() == QDialog.DialogCode.Accepted:
                self.doc.replace_text_block(
                    self.page_idx, union_rect, dlg.result_text,
                    fontname=dlg.result_fitz_font, fontsize=dlg.result_fontsize, color=dlg.result_color_rgb,
                    baseline_y=style.get("baseline_y")
                )"""

if old_replace2 in content:
    content = content.replace(old_replace2, new_replace2)

with open(filepath, 'w') as f:
    f.write(content)
