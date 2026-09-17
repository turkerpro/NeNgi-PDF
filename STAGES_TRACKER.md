# NeNgi-PDF v2.0.9-beta — STAGES_TRACKER.md

> **Proje Durumu**: Beta, aktif geliştirme. Mimari: Python 3.10+ / PyQt6 / PyMuPDF (fitz).
> **Son 3 Büyük Değişiklik**:
> - **0cb842c (2.0.6-beta)**: Türkçe glif çözümü (`_resolve_tr_font` + `insert_font`), Updater `runas` UAC yükseltme, atomik indirme (`.part`), minimum boyut doğrulama.
> - **408e807 (2.0.5-beta)**: "Less is more" — emoji purge, bağlamsal araç çubuğu, 3-kontrollü footer, **tek editör** (`InlineTextEditor`), `text_editor_dialog.py` silindi.
> - **0ceca3a (2.0.4-beta)**: Token tabanlı tasarım sistemi (`styles.py`), header sadeleştirme.

---

## STAGE 1 — MİMARİ VE KOD KALİTESİ (Foundation)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 1a | **pdf_document.py'yi modülerleştir**: `TextEditor`, `ImageHandler`, `AnnotationProxy`, `FontResolver` ayrı dosyalara çıkarıldı (tek dosya 1100+ satır → SRP). | 🔴 Kritik | ⬜ |
| 1b | **Result pattern %100 benimseme**: `bool/None` döndüren tüm core metodları `Result[T]`'a geçirildi (örn. `PDFDocument.save`, `rotate_page`, `delete_page`, `crop_page`, `move_page`, `insert_blank_page`). | 🔴 Kritik | ⬜ |
| 1c | **Tip güvenliği**: `mypy --strict` geçecek seviyeye type hint'ler eklendi; `Optional`, `List`, `Dict` yerinde `from __future__ import annotations` ile forward-ref. | 🟠 Yüksek | ⬜ |
| 1d | **Logging standardizasyonu**: `logging.getLogger(__name__)` her modülde; seviye: DEBUG(ice), INFO(akış), WARNING(geri dönüş), ERROR(veri kaybı riski). | 🟠 Yüksek | ⬜ |
| 1e | **Config/State merkezi**: `QSettings` anahtarları `settings_keys.py` sabitleri toplandı; şema versiyonlama + migration helper eklendi. | 🟡 Orta | ⬜ |

---

## STAGE 2 — TEST VE KALİTE GARANTİ (Quality Gate)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 2a | **Pytest altyapısı**: `tests/` altında `conftest.py` (tmp_path, sample PDF fixture), `pytest.ini`, CI için `github-actions.yml` (ubuntu + windows matrix). | 🔴 Kritik | ⬜ |
| 2b | **Core unit testleri**: `pdf_document` (open/save/undo/redo), `diff_engine`, `redaction`, `security`, `form_designer`, `page_manager`, `updater` (version parse/compare, download atomic). | 🔴 Kritik | ⬜ |
| 2c | **Integration testleri**: PDF aç → metin ekle → kaydet → yeniden aç → metin duruyor; DIFF iki belge; batch kuyruğu; updater indirme simülasyonu (mock HTTP). | 🟠 Yüksek | ⬜ |
| 2d | **UI smoke testleri**: `pytest-qt` ile MainWindow açılış, sekme ekleme, araç değiştirme, inline editor commit/cancel. | 🟠 Yüksek | ⬜ |
| 2e | **Coverage hedefi**: `coverage.py` ≥ 80% core, ≥ 60% UI; `codecov` entegrasyonu. | 🟡 Orta | ⬜ |
| 2f | **Regression suite**: Her bug fix için `tests/regression/test_<issue>.py` eklendi (ör. TR glif, whiteout boyut, zoom kayması). | 🟡 Orta | ⬜ |

---

## STAGE 3 — METİN DÜZENLEME VE TÜRKÇE DESTEK (Text & i18n)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 3a | **FontResolver tek kaynağı**: `_resolve_tr_font`, `get_unicode_font_buffer`, `resolve_font_for_text`, `font_supports_tr` → `nengi/core/font_resolver.py` (singleton, cache'li, test edilebilir). | 🔴 Kritik | ⬜ |
| 3b | **InlineTextEditor hardening**: Focus-out race condition fix (QTimer.singleShot 0), IME composition desteği, RTL metin (Arapça/Farsça) temel desteği. | 🔴 Kritik | ⬜ |
| 3c | **replace_text_block / edit_text_at_rect** güvenlik: `font_supports_tr` guard **redact öncesi** çalışıyor mu? (Evet, kodda var) — test ile kanıtla. | 🔴 Kritik | ⬜ |
| 3d | **Paragraph reflow**: Çok satırlı blokta `insert_textbox` sığmazsa otomatik font küçültme (6pt alt sınır) + rect genişletme (sayfa altına kadar) — edge-case testleri. | 🟠 Yüksek | ⬜ |
| 3e | **Kopyala/Yapıştır**: `Ctrl+C` (seçili kelimeler), `Ctrl+V` (yeni metin bloğu olarak insert) — clipboard HTML/zengin metin temizleme. | 🟡 Orta | ⬜ |
| 3f | **Harf/kelime arama**: Arama çubuğu (header) → tüm sayfalarda highlight + sayfa atlama (next/prev), regex opsiyonu. | 🟡 Orta | ⬜ |

---

## STAGE 4 — GÖRSEL KARŞILAŞTIRMA VE DIFF (Visual Diff)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 4a | **DiffEngine (metin tabanlı) stabilizasyon**: `difflib.SequenceMatcher` token bazlı; boşluk/boşluk normalizasyonu, satır sonu hassasiyeti. | 🟠 Yüksek | ⬜ |
| 4b | **visual_diff (piksel tabanlı) iyileştirme**: `_mask_components_to_rects` stride/min_pixels/dilate parametreleri UI'da ayarlanabilir; DPI bağımsız rect hesaplama. | 🟠 Yüksek | ⬜ |
| 4c | **DiffView (ui/diff_view.py)**: Yan yana iki PDF, senkron kaydırma (toggle), değişiklik listesi panel (tıklayınca her iki tarafta da odaklanma). | 🟠 Yüksek | ⬜ |
| 4d | **Semantik diff**: Sadece görsel piksel değil, yapısal değişiklik (tablo satırı eklendi, paragraf taşındı) — `pdfplumber`/`tabula-py` opsiyonel bağımlılıkla. | 🟡 Orta | ⬜ |
| 4e | **Karşılaştırma raporu**: HTML/PDF raporu üret (değişiklik özeti + görsel vurgular). | 🟢 Düşük | ⬜ |

---

## STAGE 5 — FORM VE ERİŞİLEBİLİRLİK (Forms & A11y)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 5a | **FormDesignerDialog tamAMLAMA**: Alan hizalama (grid snap), çoklu seçim + toplu özellik değiştirme, kopyala/yapıştır alan, tab order düzenleme. | 🟠 Yüksek | ⬜ |
| 5b | **Form veri import/export**: CSV/JSON/XML round-trip testleri; encoding (UTF-8 BOM), büyük veri setleri (10k+ alan). | 🟠 Yüksek | ⬜ |
| 5c | **AccessibilityDialog**: PDF/UA kontrol listesi (PAC 3 uyumlu) — etiketli PDF, başlık hiyerarşisi, alt text, form tooltip, dil belirtimi. Otomatik düzeltme önerileri. | 🟠 Yüksek | ⬜ |
| 5d | **Tagged PDF yazma**: `fitz` 1.23+ `add_tagged_text` / structure tree — dışa aktarma (docx/html) sırasında erişilebilirlik etiketleri korunur. | 🟡 Orta | ⬜ |
| 5e | **OCR entegrasyonu**: `rapidocr_onnxruntime` opsiyonel; `OCRCorrectionDialog` şüpheli kelimeler (düşük confidence) için inline düzeltme. | 🟡 Orta | ⬜ |

---

## STAGE 6 — GÜNCELLEME VE DAĞITIM (Updater & Distribution)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 6a | **Updater production hardening**: GitHub API rate limit (tokenlı `Authorization: Bearer`), retry/backoff, proxy destek (`HTTP_PROXY`), imza doğrulama (cosign/minisign) — `Setup.exe` SHA256 manifest. | 🔴 Kritik | ⬜ |
| 6b | **Delta güncelleme**: `bsdiff`/`courgette` ile diferansiyel yama (100MB → ~5MB) — NSIS installer `ApplyPatch` desteği. | 🟠 Yüksek | ⬜ |
| 6c | **Kanal stratejisi**: `beta` (her push) / `stabil` (tagged release) — `latest-build` rolling tag yerine `vX.Y.Z` semver tag'leri; `published_at` rolling-tag körlüğü kaldırıldı. | 🟠 Yüksek | ⬜ |
| 6d | **Windows kod imzalama**: EV sertifikası + Azure SignTool / GitHub Actions `signcode`; SmartScreen reputation. | 🟡 Orta | ⬜ |
| 6e | **Linux/Flatpak + macOS**: `flatpak-builder` manifest, `pyinstaller` spec macOS (notarization), AppImage. | 🟢 Düşük | ⬜ |

---

## STAGE 7 — PERFORMANS VE ÖLÇEKLENDİRME (Performance)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 7a | **Sanal sayfa render**: `PDFViewer` → `QListView` + `QAbstractItemModel` (lazy load), 500+ sayfa PDF'de anında açılış, Bellek < 200MB. | 🔴 Kritik | ⬜ |
| 7b | **ThumbnailBar**: Arka planda thread-pool ile (max 4) thumbnail üretimi; önbellek (LRU 50), `QPixmapCache`. | 🟠 Yüksek | ⬜ |
| 7c | **Büyük dosya optimizasyonu**: `garbage=4`, `deflate=True`, `clean=True` default; `linearize` (fast web view) opsiyonel. | 🟠 Yüksek | ⬜ |
| 7d | **Profiling**: `py-spy` / `cProfile` CI'da; `PDFDocument.open`, `render_page`, `search_for`, `ocr_page` hot path'ler. | 🟡 Orta | ⬜ |
| 7e | **Startup süresi**: `--tray` başlatma < 300ms; `main.py` lazy import (core modülleri ilk kullanımda). | 🟡 Orta | ⬜ |

---

## STAGE 8 — KULLANICI DENEYİMİ VE UI/UX (Polish)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 8a | **Tasarım tokenleri tamAMLAMA**: `styles.py` → `design_tokens.py` (JSON export → Figma sync); tüm widget'lar `get_dark_tokens()/get_light_tokens()` kullanıyor mu? (audit). | 🟠 Yüksek | ⬜ |
| 8b | **Klavye kısayolları haritası**: `Help → Kısayollar` dialog; `Ctrl+Shift+/` toggle; single-key tool shortcuts (U/S/L) çakışma yok. | 🟠 Yüksek | ⬜ |
| 8c | **Toast/Notification system**: `ToastManager` → persistent action'lı toast (ör. "Geri Al" butonlu), kuyrukta max 3, ekran köşesi ayarlanabilir. | 🟡 Orta | ⬜ |
| 8d | **Onboarding / İlk çalıştırma**: Welcome wizard (tema seç, varsayılan yap, sanal yazıcı kur, kısayol öğren). | 🟡 Orta | ⬜ |
| 8e | **Yüksek DPI / Çoklu monitör**: `devicePixelRatio` değişiminde canlı yenileme; pencere monitörler arası taşındığında zoom/fonts yeniden hesaplama. | 🟡 Orta | ⬜ |
| 8f | **Erişilebilirlik UI**: Screen reader (NVDA/JAWS) uyumlu `QAccessible` rolleri; odak sırası, kontrast (WCAG AA), klavye ile tüm işlemler. | 🟢 Düşük | ⬜ |

---

## STAGE 9 — GELİŞMİŞ ÖZELLİKLER (Advanced Features)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 9a | **Eylem Sihirbazı (ActionWizard)**: Kaydedilebilir makro (UI: drag-drop step sıralama, parametre formları, koşullu dallanma `if page_count > 10`). | 🟠 Yüksek | ⬜ |
| 9b | **BatchEngine GUI**: `BatchDialog` → işlem sırası (OCR → Redact → Watermark → Encrypt → Optimize), klasör izleyici (watchdog), zamanlanmış görevler. | 🟠 Yüksek | ⬜ |
| 9c | **Copilot / AI Panel**: Local LLM (llama.cpp/gguf) opsiyonel — belge özeti, soru-cevap, metin yeniden yazma; `summary_bridge` altyapısı hazır. | 🟡 Orta | ⬜ |
| 9d | **E-posta / Share entegrasyonu**: "Paylaş" menüsü → Outlook/Thunderbird/MAPI ile PDF ekli mail taslağı; `mailto:` link. | 🟢 Düşük | ⬜ |
| 9e | **Plugin API**: `nengi/plugins/` — `register_tool`, `register_export_format`, `register_diff_algorithm`; güvenli sandbox (subprocess隔离). | 🟢 Düşük | ⬜ |

---

## STAGE 10 — DOKÜMANTASYON VE RELEASE (Docs & Release)

| Alt Aşama | Açıklama | Öncelik | Durum |
|-----------|----------|---------|-------|
| 10a | **Kullanım kılavuzu**: `docs/user_guide.md` (Markdown, MkDocs/ReadTheDocs), ekran görüntüleri, GIF animasyonlar. | 🟠 Yüksek | ⬜ |
| 10b | **Geliştirici dokümantasyonu**: `docs/dev_guide.md` — mimari diyagram (Mermaid), core API referansı (pdoc/mkdocstrings), plugin yazma rehberi. | 🟡 Orta | ⬜ |
| 10c | **CHANGELOG.md**: Keep a Changelog formatı; her release için `## [2.0.x] - YYYY-MM-DD`. | 🟡 Orta | ⬜ |
| 10d | **Release otomasyonu**: `release.yml` — tag push → changelog extract → PyPI/Windows installer artifacts → GitHub Release notes auto. | 🟠 Yüksek | ⬜ |
| 10e | **v2.1.0-stable hedefi**: Tüm 🔴 Kritik + 🟠 Yüksek kapalı; beta etiketi kaldırıldı; semantic versioning `2.1.0`. | 🔴 Kritik | ⬜ |

---

## 📌 KAPATILMASI GEREKEN AÇIK UÇLAR (Open Issues from Code Review)

| # | Dosya / Modül | Sorun | Öneri |
|---|---------------|-------|-------|
| 1 | `pdf_document.py:777-782` | `edit_text_at_rect` → `font_supports_tr` guard **redact'tan önce** ama `resolve_font_for_text` yine de çağrılıyor; `fontfile` None ise `ok=False` dönüyor → **veri kaybı guard** çalışıyor ✓ (test yazılacak). |
| 2 | `pdf_document.py:925-929` | `replace_text_block` → `save_state_for_undo` **redact'tan sonra** çağrılıyor (doğru: ölçüm aynı fontla yapıldıktan sonra undo noktası). |
| 3 | `inline_editor.py:241-253` | `focusOutEvent` → `_maybe_commit_on_focus_out` race: şerit içi gezinti (bold/italic butonları) commit tetiklememeli. `QTimer.singleShot(0, ...)` ile geciktirme önerilir. |
| 4 | `updater.py:538-545` | `ShellExecuteW(..., "runas", ..., "/S")` → UAC reddedilirse hata mesajı Türkçe ama **installer zaten indirildi**; `DownloadCancelledError` yok, kullanıcı "Hayır" derse dosya kalıyor. Temizleme eklenecek. |
| 5 | `batch_engine.py:197-200` | `encrypt` + `optimize` sırası: önce encrypt後 optimize → optimize şifreli dosyayı açamaz. Sıralama: optimize → encrypt. |
| 6 | `pdf_view.py:1051-1054` | `commit_pending_edits` → `commit_all_pending_text` sadece `active_text_widgets`; `active_stamp_widgets` da var (commit edilmiyor). |
| 7 | `main_window.py:1030-1054` | `_toggle_comments_panel` → her açılışta `page.annots()` tekrar taranıyor; cache'li `annotations_model` eklenebilir. |
| 8 | `visual_diff.py:134-202` | `_mask_components_to_rects` BFS → büyük maskelerde (A4 300 DPI ~ 8M px) yavaş; `stride=8` default, `min_pixels=16` önerilir. |
| 9 | `settings_dialog.py:380-394` | `_on_update_download_finished` → `shutdown_app_for_update(self)` çağrılıyor ama `self.accept()` → `QDialog.accept()` event loop'u bitirmiyor; `app.quit()` yeterli mi? (test). |
| 10 | `single_instance.py:74-78` | `listen` başarısız olursa `try_send_to_existing_instance` tekrar deneniyor ama `sys.exit(0)` → **primary instance olmaz**; ikinci process de çıkıyor. Deadlock riski. |

---

## 🎯 YAKIN VADE HEDEFLERİ (Next 2 Weeks)

1. **Stage 1a + 1b** — `pdf_document.py` modülerleştirme + Result pattern %100.
2. **Stage 2a + 2b** — Pytest + CI + core unit testleri (en az 20 test).
3. **Stage 3a + 3c** — FontResolver ayrıştırma + TR glif regression testleri.
4. **Stage 6a** — Updater imza doğrulama + proxy + rate limit handling.
5. **Stage 7a** — Sanal sayfa render (lazy load) prototip.

---

> **Not**: Bu tracker canlıdır. Her PR için ilgili aşama/alt-dal `⬜` → `🟡` → `🟢` güncellenir. `🔴 Kritik` öğeler **release blocker** sayılır.