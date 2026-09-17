# HATA LİSTESİ - NeNgi PDF Test Sonuçları

**Tarih:** 2026-09-17  
**Test Ortamı:** Linux, Python 3.14.4, pytest-9.1.1, PyQt6 offscreen platform  
**Proje:** /home/turker/Documents/playground/nengi-pdf

---

## ÖZET

| Kategori | Test Sayısı | Başarılı | Başarısız | Atlandı |
|----------|-------------|----------|-----------|---------|
| **Toplam** | **49** | **49** | **0** | **0** |

**Tüm testler başarıyla geçti. Hiçbir hata, traceback veya başarısız test tespit edilmedi.**

---

## ÇALIŞTIRILAN TEST KATEGORİLERİ

### 1. Core Testler (`tests/test_core.py` - 10 test)
- ✅ `test_corrupted_pdf_handling` - Bozuk PDF işleme
- ✅ `test_diff_engine` - Diff motoru
- ✅ `test_format_converter` - Format dönüştürücü
- ✅ `test_page_operations` - Sayfa işlemleri
- ✅ `test_pdf_open_and_render` - PDF açma ve render
- ✅ `test_security_encryption_and_decryption` - Şifreleme/çözme
- ✅ `test_text_words_and_in_place_edit` - Metin kelimeleri ve yerinde düzenleme
- ✅ `test_turkish_text_insertion` - Türkçe metin ekleme
- ✅ `test_undo_redo_and_block_font_detection` - Undo/redo ve blok font tespiti
- ✅ `test_virtual_printer_manager` - Sanal yazıcı yöneticisi

### 2. Batch Testler (`tests/test_batch.py` - 2 test)
- ✅ `test_encrypt_watermark_chain` - Şifreleme + filigran zinciri
- ✅ `test_error_tolerance_and_json_log` - Hata toleransı ve JSON log

### 3. Editing/Render Testler (`tests/test_editing_render.py` - 2 test)
- ✅ `test_replace_long_text_into_narrow_box_stays_readable` - Dar kutuya uzun metin replace
- ✅ `test_overflow_never_returns_true_with_blank_page` - Overflow boş sayfa döndürmez

### 4. Turkish Long/Narrow Testler (`tests/test_tr_long_narrow.py` - 2 test)
- ✅ `test_replace_long_turkish_text_narrow_box_fully_readable` - Dar kutuya uzun TR metni
- ✅ `test_inline_editor_commit_sends_effective_rect` - Inline editör commit rect gönderimi

### 5. UI Testler (`tests/test_ui.py` - 10 test)
- ✅ `test_main_window_open_pdf` - Ana pencere PDF açma
- ✅ `test_diff_view_loading` - Diff görünümü yükleme
- ✅ `test_draggable_text_widget` - Sürüklenebilir metin widget
- ✅ `test_draggable_stamp_widget_and_undo` - Sürüklenebilir damga widget + undo
- ✅ `test_spacebar_hand_pan_and_rotated_page_insertion` - Spacebar pan + döndürülmüş sayfa ekleme
- ✅ `test_viewer_set_tool_and_stamp` - Görüntüleyici araç ve damga ayarlama
- ✅ `test_virtual_printer_spool_watcher` - Sanal yazıcı spool izleyici
- ✅ `test_compare_open_tabs` - Açık sekmeleri karşılaştır
- ✅ `test_merge_files_dialog` - Dosya birleştirme diyalogu

### 6. Updater Testler (`tests/test_updater.py` - 8 test)
- ✅ `test_yeni_surum_algilanir` - Yeni sürüm algılanır
- ✅ `test_guncel_surumde_guncelleme_yok` - Güncel sürümde güncelleme yok
- ✅ `test_ag_hatasinda_graceful_mesaj` - Ağ hatasında graceful mesaj
- ✅ `test_kanal_tag_eslemesi` - Kanal-tag eşleşmesi
- ✅ `test_beta_tag_url` - Beta tag URL
- ✅ `test_beta_soneki_karsilastirma` - Beta eki karşılaştırması
- ✅ `test_beta_kanali_beta_releasesini_sorgular` - Beta kanalı beta release sorgular
- ✅ `test_stabil_kanal_latest_build_sorgular` - Stabil kanalı latest-build sorgular

### 7. V2Bridge Testler (`tests/test_v2bridge.py` - 8 test)
- ✅ `test_pagespec_basic` - Temel pagespec
- ✅ `test_pagespec_total_ok_and_overflow` - Pagespec total OK ve overflow
- ✅ `test_pagespec_invalid` - Geçersiz pagespec
- ✅ `test_analyze_pdf_path` - PDF yolu analizi
- ✅ `test_analyze_pdf_with_pdfdocument` - PDFDocument ile analiz
- ✅ `test_summarize_path_and_document` - Yol ve belge özeti
- ✅ `test_compare_visual_identical` - Görsel karşılaştırma identical
- ✅ `test_visual_diff_highlights_changed` - Görsel diff değişenleri vurgular
- ✅ `test_save_visual_diff_empty_rejected` - Boş görsel diff reddedilir

### 8. Features Testler (`tests/test_features.py` - 7 test)
- ✅ `test_accessibility_checker` - Erişilebilirlik kontrolcü
- ✅ `test_annotations_crud` - Anotasyon CRUD
- ✅ `test_attachments_manager` - Ekli dosya yöneticisi
- ✅ `test_form_designer_and_data_exchange` - Form tasarımcısı ve veri değişimi
- ✅ `test_measurement_engine` - Ölçüm motoru
- ✅ `test_pdf_optimizer` - PDF optimizer
- ✅ `test_redaction_and_sanitization` - Redaksiyon ve temizleme

---

## MANUEL DOĞRULAMA TESTLERİ (Offscreen Platform)

### UI Smoke Test - MainWindow Açılımı
```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -c "
from nengi.ui.main_window import MainWindow
window = MainWindow()
window.open_pdf('resources/samples/sozlesme_orijinal.pdf')
# Tabs count: 1, Viewer page_count: 1
window.close()
```
**Sonuç:** ✅ **BAŞARILI** - MainWindow oluşturuldu, PDF açıldı, sekme sayısı 1, sayfa sayısı 1

### Updater Akışı Testleri (Mock ile)

#### `download_file` Testleri
- ✅ Ağ hatasında `UpdateCheckError` fırlatır
- ✅ Mock başarılı indirme (11MB fake .exe) - dosya atomik yazılır, boyut doğrulanır
- ✅ Minimum boyut kontrolü (10MB) çalışır
- ✅ Content-Length mismatch'te hata fırlatır
- ✅ İptal durumunda `.part` dosyası temizlenir

#### `launch_silent_install` Testleri
- ✅ Olmayan dosya için `UpdateCheckError` fırlatır: "Kurulum dosyası bulunamadı."
- ✅ 0 bayt dosya için hata fırlatır
- ✅ Windows'ta `ShellExecuteW` + `runas` + `/S` çağrısı yapılır (mock doğrulandı)

#### `shutdown_app_for_update` Testleri
- ✅ MainWindow'a `_updating_for_restart = True` bayrağı koyar
- ✅ Tray agent'ın `_is_quitting = True` bayrağını koyar
- ✅ Tray ikonunu gizler
- ✅ Single-instance QLocalServer'ı kapatır ve socket'i temizler
- ✅ Hiçbir adımda exception fırlatmaz (graceful)

### Inline Editing - Türkçe Glif Testi

#### Font Çözümleme
```python
_resolve_tr_font()  # → /resources/fonts/LiberationSans-Regular.ttf ✅
font_supports_tr('Türkçe: ğüşİıöç')  # → True ✅
resolve_font_for_text('Türkçe')  # → fontname='tr-sans', ok=True ✅
```

#### `replace_text_block` Türkçe Metin ile
```python
doc.replace_text_block(0, narrow_rect, 'Bu uzun bir Türkçe metindir: ğüşİıöçĞÜŞİÖÇ', fontsize=11.0)
# Result: success=True, value=True
# Page text: 'Bu uzun bir Türkçe metindir:\nğüşİıöçĞÜŞİÖÇ\n' ✅
```

#### `InlineTextEditor` Widget Testi
- ✅ Widget oluşturulur, geometri hesaplanır
- ✅ Türkçe metinle oluşturulur
- ✅ `fitz_font` doğru çözülür (helv/tr-sans)
- ✅ `_effective_pdf_rect()` güncel widget boyutundan PDF rect türetir
- ✅ `commit()` sinyali gönderilir (bağlı olmasa bile hata vermez)

---

## TESPİT EDİLEN SORUNLAR

**YOK** - Tüm otomatik testler ve manuel doğrulama testleri başarıyla geçti.

---

## NOTLAR

1. **Font Desteği:** Proje `resources/fonts/LiberationSans-Regular.ttf` içeriyor, Türkçe glifler (ğ, ü, ş, ı, ö, ç, Ğ, Ü, Ş, İ, Ö, Ç) bu font ile sorunsuz render ediliyor.

2. **Offscreen Platform:** Qt offscreen platformunda (`QT_QPA_PLATFORM=offscreen`) tüm UI testleri başarıyla çalışıyor. Bazı uyarılar çıkıyor (`This plugin does not support propagateSizeHints()`, `This plugin does not support raise()`) ama bu test sonuçlarını etkilemiyor.

3. **Updater Akışı:** Ağ çağrıları `urllib` ile yapılıyor, `requests` veya `QNetworkAccessManager` bağımlılığı yok. Mock testlerde tüm akış (check → download → install → shutdown) başarıyla simüle edildi.

4. **Inline Editing:** `InlineTextEditor` widget'ı offscreen'de oluşturulabiliyor, Türkçe metinle çalışıyor, `editing_finished` sinyali `eff_rect` (güncel widget boyutundan türetilmiş rect) ile birlikte gönderiliyor.

---

## ÇALIŞTIRMA KOMUTLARI

```bash
# Tüm testler
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m pytest tests/ -v

# Sadece UI testleri
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m pytest tests/test_ui.py -v

# Sadece Updater testleri
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m pytest tests/test_updater.py -v

# Sadece Editing testleri
QT_QPA_PLATFORM=offscreen PYTHONPATH=. python3 -m pytest tests/test_editing_render.py tests/test_tr_long_narrow.py -v
```