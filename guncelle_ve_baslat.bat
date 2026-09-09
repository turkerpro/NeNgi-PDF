@echo off
chcp 65001 >nul
setlocal

echo ========================================================
echo               NeNgi PDF Baslatici
echo ========================================================
echo.

:: Kurulum dizini - exe buraya indirilir
set "INSTALL_DIR=%LOCALAPPDATA%\NeNgi PDF"
set "EXE_PATH=%INSTALL_DIR%\NeNgi_PDF.exe"
set "VER_PATH=%INSTALL_DIR%\version.txt"
set "RELEASES_API=https://api.github.com/repos/turkerpro/NeNgi-PDF/releases/tags/latest-build"

:: Klasoru olustur
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [1/3] Guncel surum kontrol ediliyor...

:: GitHub API ile son surum bilgisini al
set "TMP_JSON=%TEMP%\nengi_release.json"
powershell -NoProfile -Command ^
  "try { Invoke-RestMethod -Uri '%RELEASES_API%' -OutFile '%TMP_JSON%' } catch { exit 1 }"

if errorlevel 1 (
    echo [UYARI] Internet baglantisi kurulamadi veya GitHub'a erisim saglanamadi.
    echo         Mevcut surumu calistiriliyor...
    goto :launch
)

:: Son release'deki Setup.exe URL'sini bul (Portable veya Setup)
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command ^
  "$j=Get-Content '%TMP_JSON%' | ConvertFrom-Json; ($j.assets | Where-Object { $_.name -like '*_Setup.exe' } | Select-Object -First 1).browser_download_url"`) do (
    set "DOWNLOAD_URL=%%i"
)

:: Versiyon bilgisini al
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command ^
  "$j=Get-Content '%TMP_JSON%' | ConvertFrom-Json; $j.name"`) do (
    set "REMOTE_VER=%%i"
)

:: Yerel versiyon ile karsilastir
set "LOCAL_VER=YOK"
if exist "%VER_PATH%" set /p LOCAL_VER=<"%VER_PATH%"

echo    Yerel  : %LOCAL_VER%
echo    Uzak   : %REMOTE_VER%

if "%LOCAL_VER%"=="%REMOTE_VER%" (
    echo [OK] Surum guncel, indirme atlanıyor.
    goto :launch
)

if "%DOWNLOAD_URL%"=="" (
    echo [UYARI] Indirme linki bulunamadi. Mevcut surumu calistiriliyor...
    goto :launch
)

echo.
echo [2/3] Yeni surum indiriliyor: %REMOTE_VER%
echo       Kaynak: %DOWNLOAD_URL%

set "TMP_SETUP=%TEMP%\NeNgi_PDF_Setup_new.exe"

powershell -NoProfile -Command ^
  "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TMP_SETUP%' -UseBasicParsing; exit 0 } catch { Write-Host 'Indirme hatasi:' $_.Exception.Message; exit 1 }"

if errorlevel 1 (
    echo [HATA] Indirme basarisiz oldu. Mevcut surumu calistiriliyor...
    goto :launch
)

echo [3/3] Kurulum paketi calistiriliyor...
echo       Setup tamamlandiktan sonra uygulama otomatik baslar.

:: Versiyon dosyasini guncelle
echo %REMOTE_VER%>"%VER_PATH%"

:: Setup'i sessiz modda calistir (NSIS /S parametresi)
start /wait "" "%TMP_SETUP%" /S

echo.
echo ========================================================
echo Kurulum tamamlandi! Uygulama baslatiliyor...
echo ========================================================
goto :launch_direct

:launch
echo.
echo [3/3] NeNgi PDF baslatiliyor...
echo ========================================================

:: Kurulu exe'yi bul ve calistir
if exist "%PROGRAMFILES%\NeNgi PDF\NeNgi_PDF.exe" (
    start "" "%PROGRAMFILES%\NeNgi PDF\NeNgi_PDF.exe" %*
    goto :end
)
if exist "%PROGRAMFILES(X86)%\NeNgi PDF\NeNgi_PDF.exe" (
    start "" "%PROGRAMFILES(X86)%\NeNgi PDF\NeNgi_PDF.exe" %*
    goto :end
)
if exist "%EXE_PATH%" (
    start "" "%EXE_PATH%" %*
    goto :end
)

echo [HATA] NeNgi_PDF.exe bulunamadi!
echo        Lutfen once GitHub'dan Setup.exe'yi indirip kurun:
echo        https://github.com/turkerpro/NeNgi-PDF/releases/tag/latest-build
echo.
pause
goto :end

:launch_direct
if exist "%PROGRAMFILES%\NeNgi PDF\NeNgi_PDF.exe" (
    start "" "%PROGRAMFILES%\NeNgi PDF\NeNgi_PDF.exe" %*
)
goto :end

:end
endlocal
