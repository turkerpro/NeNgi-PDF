"""'1-3,5' gibi sayfa secimi parseri. Cikti 0-indexed listedir.

V2 (src/utils/pagespec.py) ile birebir tasinmistir.
"""


def parse_pagespec(spec: str, total: int | None = None) -> list[int]:
    """Orn: '1-3,5' -> [0,1,2,4]. total verilirse aralik kontrolu yapar."""
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            start, end = int(a), int(b)
            if start < 1 or end < start:
                raise ValueError(f"geçersiz aralık: {part!r}")
            out.extend(range(start - 1, end))  # end dahil
        else:
            n = int(part)
            if n < 1:
                raise ValueError(f"geçersiz sayfa: {part!r}")
            out.append(n - 1)
    # Sirali + tekil
    out = sorted(set(out))
    if total is not None:
        bad = [i + 1 for i in out if i >= total]
        if bad:
            raise ValueError(f"sayfa aralığı aşıldı (toplam {total}): {bad}")
    return out
