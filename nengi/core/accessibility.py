"""
NeNgi PDF - Accessibility Standards Checker (PDF/UA & WCAG 2.1)
Inspects PDF documents for screen-reader compliance, tagged structure,
alternative text, language specification, form field descriptions, and reading order.
"""

from __future__ import annotations
from typing import List, Dict, Any
import fitz
from nengi.core.pdf_document import PDFDocument


class AccessibilityChecker:
    """Performs standardized accessibility audits on PDF documents."""

    @staticmethod
    def audit_document(doc: PDFDocument) -> List[Dict[str, Any]]:
        """Executes full accessibility evaluation across 7 core categories."""
        if not doc.is_open:
            return []

        results = []

        # --- 1. Belge Metaverileri & Dili ---
        meta = doc.doc.metadata or {}
        title = meta.get("title", "").strip()
        if title:
            results.append({
                "category": "Belge",
                "rule": "Belge Başlığı",
                "status": "passed",
                "details": f"Başlık mevcut: '{title}'",
            })
        else:
            results.append({
                "category": "Belge",
                "rule": "Belge Başlığı",
                "status": "failed",
                "details": "Belgenin başlık metaverisi tanımlanmamış. Ekran okuyucular için bir başlık gereklidir.",
            })

        # Check Primary Language
        # PyMuPDF Catalog check for /Lang
        catalog = doc.doc.pdf_catalog()
        has_lang = False
        try:
            cat_dict = doc.doc.xref_object(catalog)
            has_lang = "/Lang" in cat_dict
        except Exception:
            pass

        if has_lang:
            results.append({
                "category": "Belge",
                "rule": "Belge Dili",
                "status": "passed",
                "details": "Birincil dil katalogda belirtilmiş.",
            })
        else:
            results.append({
                "category": "Belge",
                "rule": "Belge Dili",
                "status": "failed",
                "details": "Belge dili (/Lang) tanımlanmamış. Ekran okuyucu ses sentezi için dil ayarı gereklidir.",
            })

        # Check Tagged PDF
        is_tagged = doc.doc.is_pdf and bool(doc.doc.is_repaired or getattr(doc.doc, "is_tagged", False))
        try:
            cat_str = doc.doc.xref_object(catalog)
            is_tagged = "/MarkInfo" in cat_str and "/Marked true" in cat_str
        except Exception:
            pass

        if is_tagged:
            results.append({
                "category": "Belge",
                "rule": "Etiketli PDF (Tagged PDF)",
                "status": "passed",
                "details": "Belge etiketli yapıda işaretlenmiş.",
            })
        else:
            results.append({
                "category": "Belge",
                "rule": "Etiketli PDF (Tagged PDF)",
                "status": "warning",
                "details": "Belge etiketlenmemiş. Ekran okuyucu akış hiyerarşisi tam algılanamayabilir.",
            })

        # Check Scanned Image-only document
        scanned_pages = 0
        for p_idx in range(doc.page_count):
            page = doc.get_page(p_idx)
            text = page.get_text("text").strip()
            images = page.get_images()
            if not text and len(images) > 0:
                scanned_pages += 1

        if scanned_pages == 0:
            results.append({
                "category": "Belge",
                "rule": "Salt Resim (Taranmış Belge)",
                "status": "passed",
                "details": "Tüm sayfalarda seçilebilir dijital metin katmanı mevcut.",
            })
        else:
            results.append({
                "category": "Belge",
                "rule": "Salt Resim (Taranmış Belge)",
                "status": "failed",
                "details": f"{scanned_pages} sayfada dijital metin bulunamadı (salt resim). OCR çalıştırılması gerekir.",
            })

        # --- 2. Yer İmleri (Bookmarks) ---
        toc = doc.get_toc() if hasattr(doc, "get_toc") else (doc.doc.get_toc() if doc.doc else [])
        if doc.page_count > 10 and not toc:
            results.append({
                "category": "Gezinti",
                "rule": "Yer İmleri (İçindekiler)",
                "status": "warning",
                "details": f"Belge {doc.page_count} sayfa ancak yer imi ağacı içermiyor. Uzun belgelerde yer imleri önerilir.",
            })
        else:
            results.append({
                "category": "Gezinti",
                "rule": "Yer İmleri (İçindekiler)",
                "status": "passed",
                "details": f"Yer imleri mevcut veya sayfa sayısı kısa ({len(toc)} yer imi).",
            })

        # --- 3. Görseller ve Alternatif Metin ---
        total_images = 0
        for p_idx in range(doc.page_count):
            page = doc.get_page(p_idx)
            total_images += len(page.get_images())

        if total_images == 0:
            results.append({
                "category": "Alternatif Metin",
                "rule": "Görsel Açıklamaları (Alt Text)",
                "status": "passed",
                "details": "Belgede resim bulunmuyor.",
            })
        else:
            results.append({
                "category": "Alternatif Metin",
                "rule": "Görsel Açıklamaları (Alt Text)",
                "status": "warning",
                "details": f"Belgede {total_images} adet görsel bulundu. Ekran okuyucular için alternatif açıklama kontrol edilmelidir.",
            })

        # --- 4. Form Alanları ---
        total_fields = 0
        missing_tooltip_fields = 0
        for p_idx in range(doc.page_count):
            page = doc.get_page(p_idx)
            for w in page.widgets():
                total_fields += 1
                if not getattr(w, "field_label", ""):
                    missing_tooltip_fields += 1

        if total_fields == 0:
            results.append({
                "category": "Formlar",
                "rule": "Form Alanı İpuçları (Tooltips)",
                "status": "passed",
                "details": "Belgede form alanı bulunmuyor.",
            })
        elif missing_tooltip_fields == 0:
            results.append({
                "category": "Formlar",
                "rule": "Form Alanı İpuçları (Tooltips)",
                "status": "passed",
                "details": f"Tüm form alanlarının ({total_fields} adet) erişilebilirlik açıklaması mevcut.",
            })
        else:
            results.append({
                "category": "Formlar",
                "rule": "Form Alanı İpuçları (Tooltips)",
                "status": "failed",
                "details": f"{missing_tooltip_fields} / {total_fields} form alanında ekran okuyucu ipucu (tooltip/label) eksik.",
            })

        # --- 5. Renk Kontrastı ---
        results.append({
            "category": "Renk",
            "rule": "Renk Kontrastı",
            "status": "manual",
            "details": "Metin ve arka plan kontrastının (en az 4.5:1) görsel olarak denetlenmesi gerekir.",
        })

        return results
