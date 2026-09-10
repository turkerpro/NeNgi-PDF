"""V2 (src/core/compare.py) compare_visual + save_visual_diff mantiginin NeNgi adaptoru.

Gorsel farki once V2'deki gibi kırmızı overlay'li Pillow goruntuleri olarak
uretir, ardindan fark maskesinden bagli bilesen cikarip NeNgi
``DiffEngine`` highlight formatina (``{"page": int, "rect": fitz.Rect}``
sozlukleri / ``DiffHighlight`` nesneleri) kopruler.

Bagimliliklar: fitz + Pillow + stdlib.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Sequence, Union

import fitz
from PIL import Image, ImageChops

try:
    from .diff_engine import DiffHighlight
    from .pdf_document import PDFDocument
except Exception:  # pragma: no cover
    DiffHighlight = None  # type: ignore[assignment,misc]
    PDFDocument = None  # type: ignore[assignment,misc]


def _is_pdf_document(obj) -> bool:
    return PDFDocument is not None and isinstance(obj, PDFDocument)


def _open_docs(a, b) -> tuple[fitz.Document, fitz.Document, bool, bool]:
    """a/b (yol veya PDFDocument) icin fitz Document ciftini dondur.

    Dondurur: (doc_a, doc_b, close_a, close_b)
    """
    if _is_pdf_document(a):
        doc_a = a.doc
        close_a = False
    else:
        doc_a = fitz.open(a)
        close_a = True
    if _is_pdf_document(b):
        doc_b = b.doc
        close_b = False
    else:
        doc_b = fitz.open(b)
        close_b = True
    return doc_a, doc_b, close_a, close_b


def _close_docs(doc_a, doc_b, close_a: bool, close_b: bool) -> None:
    if close_a:
        try:
            doc_a.close()
        except Exception:
            pass
    if close_b:
        try:
            doc_b.close()
        except Exception:
            pass


def _render_page(doc: fitz.Document, pageno: int, dpi: int) -> Image.Image:
    zoom = dpi / 72.0
    pix = doc[pageno].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def _overlay_diff(img_a: Image.Image, img_b: Image.Image) -> Image.Image:
    """Iki RGB goruntuyu karsilastir, farkli pikselleri kirmizi overlay ile isaretle."""
    w, h = max(img_a.width, img_b.width), max(img_a.height, img_b.height)
    canvas_a = Image.new("RGB", (w, h), "white")
    canvas_b = Image.new("RGB", (w, h), "white")
    canvas_a.paste(img_a, (0, 0))
    canvas_b.paste(img_b, (0, 0))

    diff = ImageChops.difference(canvas_a, canvas_b).convert("L")
    mask = diff.point(lambda v: 255 if v > 10 else 0)
    red = Image.new("RGB", (w, h), (255, 0, 0))
    return Image.composite(red, canvas_a, mask)


def _diff_mask(img_a: Image.Image, img_b: Image.Image) -> Image.Image:
    """Iki render arasindaki ikili (L mode) fark maskesini dondur."""
    w, h = max(img_a.width, img_b.width), max(img_a.height, img_b.height)
    canvas_a = Image.new("RGB", (w, h), "white")
    canvas_b = Image.new("RGB", (w, h), "white")
    canvas_a.paste(img_a, (0, 0))
    canvas_b.paste(img_b, (0, 0))
    diff = ImageChops.difference(canvas_a, canvas_b).convert("L")
    return diff.point(lambda v: 255 if v > 10 else 0)


def compare_visual(
    a: Union[str, Path, "PDFDocument"],
    b: Union[str, Path, "PDFDocument"],
    dpi: int = 100,
) -> list[Image.Image]:
    """Sayfa pixmap'lerini karsilastir, farklari kirmizi overlay'li goruntuler dondur.

    Ortak sayfalar: kirmizi overlay'li `a` goruntusu. Sayfa sayisi farkliysa
    fazladan sayfalar duz render olarak eklenir.
    """
    doc_a, doc_b, close_a, close_b = _open_docs(a, b)
    try:
        out: list[Image.Image] = []
        for i in range(max(len(doc_a), len(doc_b))):
            if i < len(doc_a) and i < len(doc_b):
                img_a = _render_page(doc_a, i, dpi)
                img_b = _render_page(doc_b, i, dpi)
                out.append(_overlay_diff(img_a, img_b))
            elif i < len(doc_a):
                out.append(_render_page(doc_a, i, dpi))
            else:
                out.append(_render_page(doc_b, i, dpi))
        return out
    finally:
        _close_docs(doc_a, doc_b, close_a, close_b)


def save_visual_diff(images: Sequence[Image.Image], output: Union[str, Path]) -> Path:
    """Gorsel fark goruntulerini cok sayfali PDF olarak kaydet."""
    output = Path(output)
    if not images:
        raise ValueError("images boş olamaz")
    output.parent.mkdir(parents=True, exist_ok=True)
    pages = [im.convert("RGB") for im in images]
    pages[0].save(output, "PDF", save_all=True, append_images=pages[1:])
    return output


def _mask_components_to_rects(
    mask: Image.Image,
    scale_x: float,
    scale_y: float,
    *,
    stride: int = 4,
    min_pixels: int = 4,
    dilate: float = 1.0,
) -> list[fitz.Rect]:
    """Ikili maskeden bagli bilesenleri cikarip PDF-nokta rect listesine cevir.

    `stride`: hiz icin alt ornekleme adimi (maske pikseli). `scale_x/scale_y`:
    bir maske pikselinin PDF noktasi karsiligi. `dilate`: rect'leri nokta
    cinsinden genisletme payi.
    """
    w, h = mask.size
    px = mask.load()
    sw = (w + stride - 1) // stride
    sh = (h + stride - 1) // stride
    grid = bytearray(sw * sh)
    for gy in range(sh):
        y = min(gy * stride, h - 1)
        for gx in range(sw):
            x = min(gx * stride, w - 1)
            if px[x, y]:
                grid[gy * sw + gx] = 1

    seen = bytearray(sw * sh)
    rects: list[fitz.Rect] = []
    for gy in range(sh):
        for gx in range(sw):
            idx = gy * sw + gx
            if not grid[idx] or seen[idx]:
                continue
            # BFS ile bagli bilesen
            q: deque[tuple[int, int]] = deque([(gx, gy)])
            seen[idx] = 1
            x0 = x1 = gx
            y0 = y1 = gy
            count = 0
            while q:
                cx, cy = q.popleft()
                count += 1
                if cx < x0:
                    x0 = cx
                if cx > x1:
                    x1 = cx
                if cy < y0:
                    y0 = cy
                if cy > y1:
                    y1 = cy
                for nx in (cx - 1, cx, cx + 1):
                    if nx < 0 or nx >= sw:
                        continue
                    for ny in (cy - 1, cy, cy + 1):
                        if ny < 0 or ny >= sh:
                            continue
                        nidx = ny * sw + nx
                        if grid[nidx] and not seen[nidx]:
                            seen[nidx] = 1
                            q.append((nx, ny))
            if count < min_pixels:
                continue
            rx0 = x0 * stride * scale_x - dilate
            ry0 = y0 * stride * scale_y - dilate
            rx1 = min((x1 + 1) * stride, w) * scale_x + dilate
            ry1 = min((y1 + 1) * stride, h) * scale_y + dilate
            rects.append(fitz.Rect(rx0, ry0, rx1, ry1))
    return rects


def visual_diff_highlights(
    a: Union[str, Path, "PDFDocument"],
    b: Union[str, Path, "PDFDocument"],
    dpi: int = 100,
    *,
    stride: int = 4,
    min_pixels: int = 4,
    dilate: float = 1.0,
) -> list[dict]:
    """Gorsel farki NeNgi highlight sozluklerine cevir.

    Dondurur: [{"page": int (0-indexed), "rect": fitz.Rect,
                "diff_type": "modified"/"added"/"deleted"}]
    Ortak sayfalarda maske bilesenleri "modified"; tek tarafta olan
    fazladan sayfalarin tam sayfa rect'i "added"/"deleted" olur.
    """
    doc_a, doc_b, close_a, close_b = _open_docs(a, b)
    try:
        out: list[dict] = []
        zoom = dpi / 72.0
        for i in range(max(len(doc_a), len(doc_b))):
            if i < len(doc_a) and i < len(doc_b):
                img_a = _render_page(doc_a, i, dpi)
                img_b = _render_page(doc_b, i, dpi)
                mask = _diff_mask(img_a, img_b)
                if mask.getbbox() is None:
                    continue
                # Piksel -> PDF noktasi: render zoom'un tersi.
                rects = _mask_components_to_rects(
                    mask,
                    1.0 / zoom,
                    1.0 / zoom,
                    stride=stride,
                    min_pixels=min_pixels,
                    dilate=dilate,
                )
                for r in rects:
                    out.append({"page": i, "rect": r, "diff_type": "modified"})
            elif i < len(doc_a):
                out.append(
                    {
                        "page": i,
                        "rect": fitz.Rect(doc_a[i].rect),
                        "diff_type": "deleted",
                    }
                )
            else:
                out.append(
                    {
                        "page": i,
                        "rect": fitz.Rect(doc_b[i].rect),
                        "diff_type": "added",
                    }
                )
        return out
    finally:
        _close_docs(doc_a, doc_b, close_a, close_b)


def visual_diff_as_diff_highlights(
    a: Union[str, Path, "PDFDocument"],
    b: Union[str, Path, "PDFDocument"],
    dpi: int = 100,
    **kwargs,
) -> list:
    """Gorsel farki ``DiffHighlight`` listesi olarak dondur.

    DiffEngine highlight formati: ``DiffHighlight(page_num, rect, diff_type, text)``.
    """
    items = visual_diff_highlights(a, b, dpi=dpi, **kwargs)
    result = []
    for it in items:
        if DiffHighlight is None:  # pragma: no cover
            result.append(
                {"page_num": it["page"], "rect": it["rect"],
                 "diff_type": it["diff_type"], "text": ""}
            )
        else:
            result.append(
                DiffHighlight(
                    page_num=it["page"],
                    rect=it["rect"],
                    diff_type=it["diff_type"],
                    text="",
                )
            )
    return result
