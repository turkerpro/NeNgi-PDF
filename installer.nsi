; =========================================================
; NeNgi PDF - Windows NSIS Kurulum Paketi Betiği (Setup.exe)
; C:\Program Files\NeNgi PDF dizinine kurulum yapar,
; Masaüstü ve Başlat Menüsü kısayollarını ve .pdf ilişkisini kurar.
; =========================================================

Unicode true

!define PRODUCT_NAME "NeNgi PDF"
!define PRODUCT_VERSION "1.7.1"
!define PRODUCT_PUBLISHER "NeNgi"
!define PRODUCT_WEB_SITE "https://github.com/turkerpro/NeNgi-PDF"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\NeNgi_PDF.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor /SOLID lzma
RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\app_icon.ico"
!define MUI_UNICON "resources\app_icon.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE "NeNgi PDF Kurulum Sihirbazına Hoş Geldiniz"
!define MUI_WELCOMEPAGE_TEXT "Bu sihirbaz, NeNgi PDF ${PRODUCT_VERSION} sürümünü bilgisayarınıza kuracaktır.$\r$\n$\r$\nÖne Çıkan Geliştirmeler:$\r$\n• Gelişmiş canlı katmanlar ve düzenlenebilir metin/imza nesneleri$\r$\n• Spacebar (Boşluk) tuşu ile serbest el aracı (Pan/Sayfa Sürükleme)$\r$\n• Çoklu dosya seçerek tek tıkla sıralı birleştirme$\r$\n• Taranmış sayfalarda tam açılı metin yerleşimi ve zıplamayan silgi aracı$\r$\n$\r$\nDevam etmek için İleri'ye tıklayın."
!insertmacro MUI_PAGE_WELCOME

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_TITLE "Kurulum Başarıyla Tamamlandı"
!define MUI_FINISHPAGE_TEXT "NeNgi PDF bilgisayarınıza başarıyla kuruldu. Artık PDF dosyalarınızı ultra hızlı açabilir, düzenleyebilir ve yönetebilirsiniz."
!define MUI_FINISHPAGE_RUN "$INSTDIR\NeNgi_PDF.exe"
!define MUI_FINISHPAGE_RUN_TEXT "NeNgi PDF uygulamasını şimdi başlat"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "Turkish"
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "dist\NeNgi_PDF_Setup.exe"
InstallDir "$PROGRAMFILES64\NeNgi PDF"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  ; Çalışan eski sürüm veya arka plan System Tray ajanı varsa sessizce kapat
  nsExec::Exec 'taskkill /F /IM NeNgi_PDF.exe'
  Sleep 500

  SetOutPath "$INSTDIR"
  SetOverwrite on

  ; Kurulacak program dosyaları (Hazır açılmış, anında çalışan klasör yapısı)
  File /r "dist\NeNgi_PDF\*.*"

  ; Masaüstü Kısayolu
  CreateShortCut "$DESKTOP\NeNgi PDF.lnk" "$INSTDIR\NeNgi_PDF.exe" "" "$INSTDIR\NeNgi_PDF.exe" 0

  ; Başlat Menüsü Kısayolları
  CreateDirectory "$SMPROGRAMS\NeNgi PDF"
  CreateShortCut "$SMPROGRAMS\NeNgi PDF\NeNgi PDF.lnk" "$INSTDIR\NeNgi_PDF.exe" "" "$INSTDIR\NeNgi_PDF.exe" 0
  CreateShortCut "$SMPROGRAMS\NeNgi PDF\NeNgi PDF Kaldır (Uninstall).lnk" "$INSTDIR\uninstall.exe"

  ; Windows Açılışında Hızlı Başlatıcı (System Tray Ajanı)
  CreateShortCut "$SMSTARTUP\NeNgi PDF Hızlı Başlatıcı.lnk" "$INSTDIR\NeNgi_PDF.exe" "--tray" "$INSTDIR\NeNgi_PDF.exe" 0

  ; PDF Dosya İlişkilendirmesi (File Association - HKCR & HKCU)
  WriteRegStr HKCR ".pdf" "" "NeNgiPDF.Document"
  WriteRegStr HKCR ".pdf\OpenWithProgids" "NeNgiPDF.Document" ""
  WriteRegStr HKCR "NeNgiPDF.Document" "" "NeNgi PDF Dokümanı"
  WriteRegStr HKCR "NeNgiPDF.Document\DefaultIcon" "" "$INSTDIR\NeNgi_PDF.exe,0"
  WriteRegStr HKCR "NeNgiPDF.Document\shell" "" "open"
  WriteRegStr HKCR "NeNgiPDF.Document\shell\open\command" "" '"$INSTDIR\NeNgi_PDF.exe" "%1"'

  WriteRegStr HKCU "Software\Classes\.pdf" "" "NeNgiPDF.Document"
  WriteRegStr HKCU "Software\Classes\.pdf\OpenWithProgids" "NeNgiPDF.Document" ""
  WriteRegStr HKCU "Software\Classes\NeNgiPDF.Document" "" "NeNgi PDF Dokümanı"
  WriteRegStr HKCU "Software\Classes\NeNgiPDF.Document\DefaultIcon" "" "$INSTDIR\NeNgi_PDF.exe,0"
  WriteRegStr HKCU "Software\Classes\NeNgiPDF.Document\shell" "" "open"
  WriteRegStr HKCU "Software\Classes\NeNgiPDF.Document\shell\open\command" "" '"$INSTDIR\NeNgi_PDF.exe" "%1"'

  ; Windows Explorer Sağ Tık Menüleri (Shell Context Menus)
  ; 1. NeNgi PDF ile Birleştir
  WriteRegStr HKCR "*\shell\NeNgiPDF.Merge" "" "NeNgi PDF ile Birleştir"
  WriteRegStr HKCR "*\shell\NeNgiPDF.Merge" "Icon" "$INSTDIR\NeNgi_PDF.exe,0"
  WriteRegStr HKCR "*\shell\NeNgiPDF.Merge\command" "" '"$INSTDIR\NeNgi_PDF.exe" --merge "%1"'

  ; 2. NeNgi PDF ile PDF'e Dönüştür
  WriteRegStr HKCR "*\shell\NeNgiPDF.Convert" "" "NeNgi PDF ile PDF'e Dönüştür"
  WriteRegStr HKCR "*\shell\NeNgiPDF.Convert" "Icon" "$INSTDIR\NeNgi_PDF.exe,0"
  WriteRegStr HKCR "*\shell\NeNgiPDF.Convert\command" "" '"$INSTDIR\NeNgi_PDF.exe" --convert "%1"'

  ; Windows Default Apps Registration
  WriteRegStr HKLM "Software\NeNgiPDF\Capabilities" "ApplicationDescription" "NeNgi PDF Okuyucu ve Belge Düzenleyici"
  WriteRegStr HKLM "Software\NeNgiPDF\Capabilities" "ApplicationName" "NeNgi PDF"
  WriteRegStr HKLM "Software\NeNgiPDF\Capabilities\FileAssociations" ".pdf" "NeNgiPDF.Document"
  WriteRegStr HKLM "Software\RegisteredApplications" "NeNgi PDF" "Software\NeNgiPDF\Capabilities"

  ; Windows Virtual Printer ("NeNgi PDF" Yazıcısı)
  nsExec::Exec 'powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = '\''NeNgi PDF\''; $d = '\''Microsoft Print to PDF\''; $spoolDir = \"$env:ProgramData\NeNgi_PDF\spool\"; if (-not (Test-Path $spoolDir)) { New-Item -ItemType Directory -Path $spoolDir -Force | Out-Null }; try { $acl = Get-Acl $spoolDir; $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('\''Users\'', '\''FullControl\'', '\''ContainerInherit,ObjectInherit\'', '\''None\'', '\''Allow\''); $acl.AddAccessRule($rule); Set-Acl $spoolDir $acl -ErrorAction SilentlyContinue } catch {}; $spoolFile = \"$spoolDir\nengi_print.pdf\"; if (-not (Test-Path $spoolFile)) { [System.IO.File]::WriteAllBytes($spoolFile, @()) }; Remove-Printer -Name $p -ErrorAction SilentlyContinue; if (-not (Get-PrinterPort -Name $spoolFile -ErrorAction SilentlyContinue)) { try { Add-PrinterPort -Name $spoolFile -ErrorAction Stop } catch { Set-ItemProperty -Path '\''HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Ports'\'' -Name $spoolFile -Value '\'''\'' -Type String -Force -ErrorAction SilentlyContinue; Restart-Service -Name Spooler -Force -ErrorAction SilentlyContinue } }; $driver = (Get-PrinterDriver -Name $d -ErrorAction SilentlyContinue); if (-not $driver) { $driverName = (Get-PrinterDriver | Where-Object { $_.Name -like '\''*PDF*'\'' } | Select-Object -First 1 -ExpandProperty Name) } else { $driverName = $d }; if (-not $driverName) { $driverName = '\''Microsoft Print to PDF'\'' }; Add-Printer -Name $p -DriverName $driverName -PortName $spoolFile -PrintProcessor '\''winprint'\'' -ErrorAction SilentlyContinue; if (-not (Get-Printer -Name $p -ErrorAction SilentlyContinue)) { $src = Get-Printer -Name $d -ErrorAction SilentlyContinue; if ($src) { Add-Printer -Name $p -DriverName $src.DriverName -PortName $src.PortName -PrintProcessor '\''winprint'\'' -ErrorAction SilentlyContinue } }; $outlprnt = \"$env:APPDATA\Microsoft\Outlook\outlprnt\"; if (Test-Path $outlprnt) { Remove-Item $outlprnt -Force -ErrorAction SilentlyContinue }"'

  ; Windows Explorer icon refresh
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\NeNgi_PDF.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\NeNgi_PDF.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Section Uninstall
  ; Kaldırmadan önce çalışan programı kapat
  nsExec::Exec 'taskkill /F /IM NeNgi_PDF.exe'
  Sleep 500

  ; Sanal yazıcıyı kaldır
  nsExec::Exec 'powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Printer -Name '\''NeNgi PDF'\'' -ErrorAction SilentlyContinue"'

  ; Kısayolları sil
  Delete "$DESKTOP\NeNgi PDF.lnk"
  Delete "$SMPROGRAMS\NeNgi PDF\NeNgi PDF.lnk"
  Delete "$SMPROGRAMS\NeNgi PDF\NeNgi PDF Kaldır (Uninstall).lnk"
  Delete "$SMSTARTUP\NeNgi PDF Hızlı Başlatıcı.lnk"
  RMDir "$SMPROGRAMS\NeNgi PDF"

  ; Program dosyalarını sil
  RMDir /r "$INSTDIR"

  ; Kayıt defteri temizliği
  DeleteRegKey HKCR "*\shell\NeNgiPDF.Merge"
  DeleteRegKey HKCR "*\shell\NeNgiPDF.Convert"
  DeleteRegKey HKLM "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  DeleteRegKey HKLM "Software\NeNgiPDF"
  DeleteRegValue HKLM "Software\RegisteredApplications" "NeNgi PDF"

  ; Windows Explorer refresh
  System::Call 'shell32.dll::SHChangeNotify(i, i, i, i) v (0x08000000, 0, 0, 0)'
SectionEnd
