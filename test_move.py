import fitz

doc = fitz.open("resources/samples/sozlesme_orijinal.pdf")
page = doc[0]

# Let's say we want to move the block at (50, 50, 200, 100) to (100, 200)
clip_rect = fitz.Rect(50, 50, 200, 100)
new_rect = fitz.Rect(100, 200, 100 + clip_rect.width, 200 + clip_rect.height)

# Create temp doc
tmp_doc = fitz.open()
tmp_doc.insert_pdf(doc, from_page=0, to_page=0)

# Redact original
page.add_redact_annot(clip_rect, fill=(1,1,1))
page.apply_redactions()

# Draw from tmp
page.show_pdf_page(new_rect, tmp_doc, 0, clip=clip_rect)

doc.save("test_moved.pdf")
print("Done")
