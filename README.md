# 📑 NeNgi PDF
> **Açık Kaynaklı, Akıllı, Yapay Zeka Destekli ve Yan Yana Karşılaştırma (DIFF) Özellikli PDF Düzenleyici**

NeNgi PDF; yüksek performanslı, modern bir arayüze sahip, gelişmiş belge karşılaştırma, yapay zeka entegrasyonu ve kapsamlı düzenleme yetenekleri sunan bağımsız ve açık kaynaklı bir masaüstü uygulamasıdır. 

---

## ✨ Öne Çıkan Özellikler

### 1. ⚖️ Yan Yana Metin Karşılaştırması (DIFF)
- **Açık Sekmeleri Tek Tıkla Karşılaştırma:** Farklı sekmelerde açık olan iki belgeyi anında yan yana karşılaştırma ekranına alın.
- **Senkronize Kaydırma (Sync-Scroll):** Bir belgede aşağı kaydırdığınızda diğeri de otomatik olarak aynı oranda kayar.
- **Renk Kodlu Anlık Vurgulama:**
  - 🟢 **Yeşil:** Yeni eklenen metin ve paragraflar.
  - 🔴 **Kırmızı:** Silinen kısımlar.
  - 🟡 **Sarı:** Değiştirilen kelime ve rakamlar.
- **Fark Listesi ve Raporlama:** Tespit edilen tüm farklar bir panelde listelenir, tıklandığında ilgili satıra atlanır. Çıktı olarak `.txt` formatında rapor alınabilir.

### 2. 🤖 Yapay Zeka Destekli Asistan (Copilot)
- **Akıllı Sohbet Paneli:** Belge ile ilgili sorularınızı doğrudan sağ panelden yapay zekaya sorun.
- **Sayfa Özeti ve Analizi:** Mevcut sayfayı tek tıkla özetletin veya metin içindeki karmaşık kavramların açıklamasını isteyin. (Google Gemini ve yerel modeller ile tam uyumludur).

### 3. ✍️ Zengin Açıklama ve Çizim Araçları (Annotations)
- **Metin İşaretleme:** Hızlıca kelimeleri veya paragrafları Vurgulayın, Altını Çizin veya Üstünü Çizin.
- **Serbest Çizim ve Şekiller:** Ok, Çizgi, Dikdörtgen, Elips, Çokgen ve Bulut araçlarıyla belgelerinize notlar ekleyin, serbest çizimler yapın.
- **Şeffaflık ve Kalınlık Ayarı:** Eklenen tüm şekil ve çizimlerin rengini, çizgi kalınlığını ve şeffaflık oranını anlık olarak değiştirin.

### 4. ✂️ Gelişmiş Metin Taşıma ve Düzenleme (Kusursuz Sürükle-Bırak)
- **Orijinal Metni Taşıma:** PDF'teki herhangi bir paragrafı veya metni seçip sağ tıklayarak **"Seçili Metni Taşı"** diyebilirsiniz. Orijinal metin anında şeffaf ve sürüklenebilir bir bloğa dönüşür; istediğiniz yere bıraktığınızda belgeye kusursuz ve vektörel biçimde, formatı bozulmadan yerleşir.
- **Akıllı Metin Kutuları:** İstediğiniz yere tıklayarak yeni metinler ekleyin; eklendikten sonra serbestçe sürükleyerek yerini ayarlayın.

### 5. ⚡ Tek Pencerede Çoklu Sekme Sistemi (Single-Instance)
- Arka arkaya açılan veya e-posta ekinden tıklanan tüm PDF dosyaları ayrı ayrı pencereler açmak yerine **tek bir NeNgi PDF penceresi altında yeni sekmeler** olarak düzenli bir şekilde toplanır.
- İşletim sisteminde varsayılan PDF okuyucu olarak ayarlandığında tam entegre çalışır.

### 6. 🖌️ Harici Düzenleyici ile Temizleme Döngüsü (Roundtrip Edit)
- Taranmış bir sayfayı veya PDF içindeki görseli, sisteminizde bulunan herhangi bir resim düzenleyiciye tek tıkla gönderin.
- Harici düzenleyicide leke temizliği veya not silme işlemini yapıp dosyayı kaydettiğiniz anda, NeNgi PDF arka planda değişikliği anında algılayarak **belgeyi otomatik günceller**.

### 7. ◻️ Hızlı Beyazlatma (Silgi / Whiteout)
- Harici bir programa gitmeye dahi gerek kalmadan, farenizle istemediğiniz bölümleri (tükenmez kalem izleri, hatalı rakamlar vb.) dikdörtgen içine alarak saniyeler içinde kalıcı olarak beyazlatıp silin.

### 8. ↩️ Geri Al / İleri Al Desteği (Undo & Redo)
- Yapılan tüm metin ekleme, çizim, taşıma ve silme işlemlerini `Ctrl + Z` ile geri alabilir, `Ctrl + Y` ile işlemleri ileri sarabilirsiniz. Hata yapmaktan korkmayın.

### 9. ✒️ Pratik İmza ve Kaşe Ekleme
- **İmza Ekranı:** Fareniz veya dokunmatik ekranınız ile kendi imzanızı çizin, boyutlandırarak istediğiniz yere yapıştırın.
- **Kaşe/Görsel Ekleme:** Bilgisayarınızdaki mevcut kaşe veya imza görsellerini belge üzerine damgalayın.

### 10. 📑 Sayfa Yönetimi ve Düzenleme
- Sayfaları 90°, 180°, 270° döndürün, istemediğiniz sayfaları tamamen silin.
- Sayfaların sırasını basitçe taşıyarak değiştirin (Sürükle/Bırak destekli görsel sayfa yöneticisi).
- Farklı belgelerdeki sayfaları mevcut belgenizin arasına ekleyin (Merge).

### 11. 🔒 Güvenlik & Format Dönüştürme
- **AES-256 Parola Koruması:** Belgenizi güçlü şifreleme algoritmalarıyla koruma altına alın veya mevcut şifreleri kaldırıp yeni bir kopya oluşturun.
- **Yüksek Çözünürlüklü Dışa Aktarma:** Sayfaları yüksek kaliteli görseller (PNG vb.) olarak dışa aktarın.
- **Resimden PDF'e:** Bilgisayarınızdaki JPG/PNG formatındaki dosyaları hızla tek bir PDF belgesinde birleştirin.

---

## 🚀 Hızlı Başlangıç & Kurulum

### Gereksinimler
- Python 3.10 veya daha yenisi

### 1. Depoyu İndirin
```bash
git clone https://github.com/turkerpro/NeNgi-PDF.git
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

## 📦 Kurulum Paketi (Setup.exe) ve Taşınabilir Sürüm

NeNgi PDF iki farklı formatta dağıtılmaktadır:

1. **Kurulum Paketi (`NeNgi_PDF_Setup.exe`):**
   - Uygulamayı bilgisayarınıza standart bir masaüstü yazılımı gibi kurar.
   - Masaüstüne kısayollar ekler, otomatik dosya eşleştirmelerini (PDF uzantısı) yapar.

2. **Taşınabilir Sürüm (`NeNgi_PDF_Portable.exe`):**
   - Kurulum gerektirmeden, USB bellekten veya indirilen klasörden çift tıkla doğrudan çalıştırılabilen sürümdür.

> [!TIP]
> Proje içinde bulunan GitHub Actions iş akışı (workflow) sayesinde her yeni sürümde `Setup.exe` ve `Portable.exe` dosyaları bulutta otomatik olarak derlenip GitHub Releases (Sürümler) sayfasına eklenir.

---

## 🧪 Testleri Çalıştırma

Geliştiriciler için, çekirdek motor ve arayüz testlerini tek komutla çalıştırabilirsiniz:

```bash
PYTHONPATH=. pytest tests/
```

---

## 📄 Lisans
Bu proje MIT Lisansı kapsamında açık kaynaklı olarak paylaşılmaktadır.

---

## 🤖 Yapay Zeka Hakkında
Bu proje, kodlama sürecinden yeni özelliklerin tasarımına kadar pek çok aşamada **Yapay Zeka (YZ) desteğiyle** sıfırdan geliştirilmiştir. Açık kaynak kod dünyasına ve üretken yapay zekanın gücüne bir teşekkür olarak sunulur.
