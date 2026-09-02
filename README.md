# 📑 NeNgi PDF
> **Windows için Açık Kaynaklı, Akıllı ve Metin Odaklı Yan Yana DIFF (Karşılaştırma) Destekli PDF Düzenleyici**

NeNgi PDF; yüksek performanslı, modern Windows 11 arayüzüne sahip, gelişmiş belge karşılaştırma ve kapsamlı düzenleme yetenekleri sunan bağımsız, açık kaynaklı bir masaüstü uygulamasıdır.

---

## ✨ Öne Çıkan Özellikler

### 1. ⚖️ Yan Yana Metin Karşılaştırması (DIFF) & Açık Sekmeler Arasında Karşılaştırma
- **E-Postadan Gelen Belgeleri Kaydetmeden Karşılaştırın:** Mail ekindeki iki PDF'e peş peşe tıkladığınızda ayrı pencereler açılmaz; ikisi de aynı pencerede sekmeler halinde açılır.
- **Açık Sekmeleri Tek Tıkla Karşılaştırma:** Menüdeki **"Açık Sekmeleri Karşılaştır"** butonuyla veya herhangi bir sekmeye sağ tıklayarak açık olan iki belgeyi diskte dosya aramadan anında yan yana DIFF ekranına getirin.
- **Orijinal ve Revize Belge Yan Yana:** İki PDF dosyasını seçip anında karşılaştırın.
- **Senkronize Kaydırma (Sync-Scroll):** Bir belgede aşağı kaydırdığınızda diğeri de otomatik olarak aynı oranda kayar.
- **Renk Kodlu Anlık Vurgulama:**
  - 🟢 **Yeşil:** Yeni eklenen metin ve paragraflar (Revize belgede).
  - 🔴 **Kırmızı:** Silinen kısımlar (Orijinal belgede).
  - 🟡 **Sarı:** Değiştirilen kelimeler / rakamlar.
- **Farklar Listesi & Hızlı Gezinti:** Sağ panelde tespit edilen tüm farklar listelenir; tıklanan farka her iki belgede otomatik olarak odaklanılır.
- **Fark Raporu Dışa Aktarma:** Değişiklik listesini tek tıkla `.txt` raporu olarak kaydedin.

### 2. ⚡ Tek Pencerede Çoklu Sekme (Single-Instance) & Windows Varsayılan PDF Okuyucu
- **Tekil Oturum (IPC Socket):** Windows'ta çift tıklanan veya e-posta istemcilerinden (Outlook, Thunderbird vb.) açılan tüm PDF'ler tek bir NeNgi PDF penceresinde yeni sekmeler olarak toplanır.
- **Varsayılan PDF Okuyucusu Yap:** Menüden tek tıkla NeNgi PDF'i Windows'un varsayılan PDF uygulaması olarak ayarlayın (`.pdf` uzantı kaydı ve ProgID entegrasyonu).

### 3. 🖌️ Harici Editörle Görsel ve Tarama Temizleme Döngüsü (Roundtrip Edit)
- Taranmış bir sayfadaki veya PDF'teki bir görsele tıklayıp **"Paint'te Aç ve Düzenle"** diyebilirsiniz.
- Sistemdeki varsayılan resim programında (MS Paint, Photoshop vb.) kalem izlerini, mürekkep lekelerini veya istenmeyen notları temizleyin.
- Resim programında `Ctrl + S` yapıp kaydettiğiniz anda NeNgi PDF dosya değişikliğini yakalar ve **PDF içindeki sayfayı otomatik olarak günceller**.

### 4. ◻️ Hızlı Beyazlatma & Silgi (Whiteout)
- Harici programa gitmeye gerek kalmadan, sayfa üzerindeki tükenmez kalem izlerinin veya silinmesi gereken alanların üzerini fare ile dikdörtgen çizerek anında temizleyin.

### 5. ✍️ Doğrudan Metin ve İmza Ekleme
- Sayfanın herhangi bir noktasına tıklayarak yeni metin kutusu ekleyin.
- **İmza Ekle:** Mouse veya kalem ile ekranda kendi imzanızı çizin ya da hazır imza resminizi yükleyip belgenin dilediğiniz yerine boyutlandırarak yapıştırın.

### 6. 📑 Görsel Sayfa Yönetimi
- Sayfaları 90°, 180°, 270° döndürün.
- İstenmeyen sayfaları silin.
- Sayfaların sırasını yukarı/aşağı taşıyarak değiştirin.
- Boş A4 sayfası ekleyin veya başka bir PDF'teki sayfaları mevcut belgeye ekleyin (Merge).

### 7. 🔒 Güvenlik & Format Dönüştürme
- **AES-256 Parola Koruması:** Belgeye şifre koyun.
- **Şifre Kaldırma:** Parolalı bir PDF'in şifresini çözerek korumasız yeni bir kopya kaydedin.
- **Resme Çevir:** PDF sayfalarını 300 DPI yüksek kaliteli PNG/JPG formatında dışa aktarın.
- **Resimlerden PDF Yap:** Bilgisayarınızdaki birden fazla resmi tek tıkla tek bir PDF dosyasında birleştirin.

---

## 🚀 Hızlı Başlangıç & Kurulum

### Gereksinimler
- Python 3.10 veya daha yenisi (Windows / Linux / macOS)

### 1. Depoyu Klonlayın veya İndirin
```bash
git clone https://github.com/KULLANICI_ADINIZ/nengi-pdf.git
cd nengi-pdf
```

### 2. Sanal Ortam Oluşturup Bağımlılıkları Yükleyin
```bash
# Sanal ortam oluşturma
python -m venv .venv

# Sanal ortamı aktif etme (Windows):
.venv\Scripts\activate

# Sanal ortamı aktif etme (Linux / Mac):
source .venv/bin/activate

# Paketleri yükleme
pip install -r requirements.txt
```

### 3. Uygulamayı Başlatın
```bash
python -m nengi.main
```

---

## 📦 Windows Bağımsız .EXE Dosyası Üretme

NeNgi PDF'i herhangi bir Python kurulumu gerektirmeyen, doğrudan çift tıklamayla çalışan bağımsız bir Windows `.exe` dosyası haline getirmek için:

```bash
python build_windows.py
```
İşlem tamamlandığında `dist/NeNgi_PDF/NeNgi_PDF.exe` dosyası hazır olacaktır.

> [!TIP]
> Proje içinde hazır bulunan `.github/workflows/build-windows.yml` sayesinde projeyi GitHub'a yüklediğinizde veya yeni bir sürüm etiketi (örn. `v1.0.0`) açtığınızda GitHub Actions **otomatik olarak Windows .exe dosyasını derleyip Release bölümüne ekler**.

---

## 🧪 Testleri Çalıştırma

Tüm çekirdek motor ve arayüz testlerini tek komutla çalıştırabilirsiniz:

```bash
python -m unittest discover tests
```

---

## 📂 Proje Yapısı

```
nengi-pdf/
├── nengi/
│   ├── main.py                   # Uygulama başlangıç noktası
│   ├── core/
│   │   ├── pdf_document.py       # PyMuPDF motoru (render, metin, resim, kaydetme)
│   │   ├── diff_engine.py        # Metin tabanlı yan yana DIFF algoritması
│   │   ├── image_roundtrip.py    # Harici Paint/editör dosya dinleyicisi
│   │   ├── page_manager.py       # Sayfa döndürme, silme, sıralama, birleştirme
│   │   ├── security.py           # AES-256 şifreleme ve şifre çözme
│   │   ├── converter.py          # PDF <-> Resim dönüştürücü
│   │   └── form_handler.py       # AcroForms form alanları desteği
│   └── ui/
│       ├── main_window.py        # Windows 11 tarzı modern ana pencere & sekmeler
│       ├── pdf_view.py           # Etkileşimli PDF görüntüleyici ve silgi
│       ├── diff_view.py          # Yan yana senkronize DIFF karşılaştırma ekranı
│       ├── thumbnail_bar.py      # Sol sayfa önizleme paneli
│       ├── signature_dialog.py   # El yazısı çizim ve imza yükleme penceresi
│       ├── password_dialog.py    # Parola koyma / çözme penceresi
│       ├── page_manager_dialog.py# Görsel sayfa düzenleme sihirbazı
│       └── styles.py             # Koyu / Açık Windows 11 temaları
├── resources/
│   └── samples/                  # Denemek için hazır orijinal ve revize PDF'ler
├── tests/
│   ├── test_core.py              # Çekirdek motor testleri
│   └── test_ui.py                # Arayüz ve etkileşim testleri
├── .github/workflows/
│   └── build-windows.yml         # GitHub Actions otomatik .exe derleme
├── build_windows.py              # Windows PyInstaller derleme betiği
├── requirements.txt
├── LICENSE                       # MIT Lisansı
└── README.md
```

---

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynaklı olarak paylaşılmaktadır.
