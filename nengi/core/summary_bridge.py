"""V2 (src/core/summarize.py) analyze_pdf + summarize mantiginin NeNgi adaptoru.

Girdi olarak dosya yolu (str | Path) veya acik bir
``nengi.core.pdf_document.PDFDocument`` kabul eder; PDFDocument verildiginde
belge kapatilmaz, yalnizca okunur.

Bagimliliklar: fitz + Pillow + stdlib (re, collections, pathlib).
TR + EN stopword listeleri V2'den aynen gomuludur.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Union

import fitz
from PIL import Image  # noqa: F401  (adaptör bağımlılığı: fitz+Pillow+stdlib)

try:
    from .pdf_document import PDFDocument
except Exception:  # pragma: no cover - dogrudan script olarak import edilirse
    PDFDocument = None  # type: ignore[assignment,misc]

# --- Gomulu stopword listeleri (V2 src/core/summarize.py ile birebir) ---
STOPWORDS_TR = frozenset(
    """
    acak ecek ama ancak arada artık ayrıca bana bazı belki ben beni benim beri
    bile bir birisi birçok biri birkaç biz bize bizi bu bunu bunun burada böyle
    çünkü da daha de değil diğer diye eğer en ise için ile ilgili kadar kendi
    ki kim kimse mi mı mu mü nasıl ne neden nere nerede nasıl niçin o olan
    olarak olur olsa olsun onun onlar onlara onları seni senin sizi sizin siz
    şey şu şunlar ve veya ya yani yok yüzünden hem hep hepsi her hangi hatta
    çok daha en ise diye kadar gibi göre sonra önce sonra üzere şimdi şöyle
    işte dahi rağmen karşın karşı yine yeniden zaten ise
    """.split()
)

STOPWORDS_EN = frozenset(
    """
    a about above after again against all am an and any are as at be because
    been before being below between both but by can cannot could did do does
    doing down during each few for from further had has have having he her here
    hers herself him himself his how i if in into is it its itself like me more
    most my myself no nor not of off on once only or other ought our ours
    ourselves out over own same she should so some such than that the their
    theirs them themselves then there these they this those through to too
    under until up very was we were what when where which while who whom why
    with would you your yours yourself yourselves
    """.split()
)

STOPWORDS = STOPWORDS_TR | STOPWORDS_EN

_WORD_RE = re.compile(r"[^\W\d_]{2,}", re.UNICODE)
_SENT_RE = re.compile(r"(?<=[.!?…])\s+|\n+")


def _is_pdf_document(obj) -> bool:
    return PDFDocument is not None and isinstance(obj, PDFDocument)


def _iter_pages(doc: fitz.Document):
    yield from doc


def _stats_from_doc(doc: fitz.Document) -> dict:
    pages = doc.page_count
    words = 0
    images = 0
    has_forms = False
    for page in _iter_pages(doc):
        words += len(page.get_text().split())
        images += len(page.get_images(full=True))
        if not has_forms:
            try:
                if list(page.widgets()):
                    has_forms = True
            except Exception:
                pass
    if not has_forms:
        try:
            if doc.is_form_pdf:
                has_forms = True
        except Exception:
            pass
    avg = (words / pages) if pages else 0
    is_scanned = bool(pages) and avg < 20
    return {
        "pages": pages,
        "words": words,
        "images": images,
        "is_scanned": is_scanned,
        "has_forms": bool(has_forms),
        "encrypted": False,
    }


def analyze_pdf(input: Union[str, Path, "PDFDocument"]) -> dict:
    """PDF hakkinda temel istatistikler dondur.

    Dondurur: {"pages": int, "words": int, "images": int,
                "is_scanned": bool, "has_forms": bool, "encrypted": bool}
    """
    if _is_pdf_document(input):
        if not input.is_open:
            return {
                "pages": 0,
                "words": 0,
                "images": 0,
                "is_scanned": False,
                "has_forms": False,
                "encrypted": True,
            }
        try:
            if getattr(input.doc, "needs_pass", False) or getattr(
                input.doc, "is_encrypted", False
            ):
                if not getattr(input, "is_authenticated", True):
                    try:
                        pages = input.doc.page_count
                    except Exception:
                        pages = 0
                    return {
                        "pages": pages,
                        "words": 0,
                        "images": 0,
                        "is_scanned": False,
                        "has_forms": False,
                        "encrypted": True,
                    }
        except Exception:
            pass
        return _stats_from_doc(input.doc)

    path = Path(str(input))
    try:
        doc = fitz.open(path)
    except Exception:
        # Sifreli/bozuk dosya fitz.open'da patlayabilir
        return {
            "pages": 0,
            "words": 0,
            "images": 0,
            "is_scanned": False,
            "has_forms": False,
            "encrypted": True,
        }
    try:
        if getattr(doc, "needs_pass", False) or getattr(doc, "is_encrypted", False):
            try:
                pages = doc.page_count
            except Exception:
                pages = 0
            return {
                "pages": pages,
                "words": 0,
                "images": 0,
                "is_scanned": False,
                "has_forms": False,
                "encrypted": True,
            }
        return _stats_from_doc(doc)
    finally:
        doc.close()


def analyze_document(doc: "PDFDocument") -> dict:
    """Acik bir PDFDocument uzerinden :func:`analyze_pdf` calistir."""
    return analyze_pdf(doc)


def _sentences(text: str) -> list[str]:
    parts = [s.strip() for s in _SENT_RE.split(text.strip()) if s.strip()]
    return [p for p in parts if len(p.split()) >= 3]


def _extract_full_text_doc(doc: fitz.Document) -> str:
    return "\n".join(page.get_text() for page in _iter_pages(doc))


def _summarize_text(text: str, sentences: int = 8) -> dict:
    sents = _sentences(text)
    if not sents:
        return {"summary": "", "keywords": []}

    tokens = [w.lower() for w in _WORD_RE.findall(text)]
    content = [t for t in tokens if t not in STOPWORDS and len(t) >= 3]
    if not content:
        return {"summary": " ".join(sents[:sentences]), "keywords": []}

    freq = Counter(content)
    ceiling = max(freq.values())
    norm = {w: c / ceiling for w, c in freq.items()}

    scored: list[tuple[float, int, str]] = []
    for idx, s in enumerate(sents):
        stoks = [w.lower() for w in _WORD_RE.findall(s)]
        frac = [t for t in stoks if t not in STOPWORDS and len(t) >= 3]
        if not frac:
            continue
        score = sum(norm[t] for t in frac) / (len(frac) ** 0.5)
        scored.append((score, idx, s))

    if not scored:  # tum cumleler stopword ise ilk N cumleyi al
        return {"summary": " ".join(sents[:sentences]), "keywords": []}

    scored.sort(key=lambda t: (-t[0], t[1]))
    top = sorted(scored[: max(1, sentences)], key=lambda t: t[1])
    summary = " ".join(s for _, _, s in top)
    keywords = [w for w, _ in freq.most_common(10)]
    return {"summary": summary, "keywords": keywords}


def summarize(input: Union[str, Path, "PDFDocument"], sentences: int = 8) -> dict:
    """Frekans skorlu extractive ozet + anahtar kelimeler.

    Dondurur: {"summary": str, "keywords": list[str]}
    """
    if _is_pdf_document(input):
        if not input.is_open:
            return {"summary": "", "keywords": []}
        text = _extract_full_text_doc(input.doc)
        return _summarize_text(text, sentences=sentences)

    doc = fitz.open(input)
    try:
        text = _extract_full_text_doc(doc)
    finally:
        doc.close()
    return _summarize_text(text, sentences=sentences)


def summarize_document(doc: "PDFDocument", sentences: int = 8) -> dict:
    """Acik bir PDFDocument uzerinden :func:`summarize` calistir."""
    return summarize(doc, sentences=sentences)
