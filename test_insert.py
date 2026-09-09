import fitz

doc = fitz.open("resources/samples/sozlesme_orijinal.pdf")
page = doc[0]

rect = fitz.Rect(50, 50, 200, 100)
page.add_redact_annot(rect, fill=(1,1,1))
page.apply_redactions()

page.insert_textbox(rect, "test", fontsize=12, fontname="helv", color=(0,0,0))
doc.save("test_out.pdf")
