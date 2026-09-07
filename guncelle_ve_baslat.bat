@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title NeNgi PDF - Başlatıcı ve Güncelleyici

echo ========================================================
echo               NeNgi PDF Başlatıcı
echo ========================================================
echo.
echo [1/3] Güncellemeler kontrol ediliyor...

:: Git baglantisini kontrol et ve uzak sunucudaki son durumu cek
git fetch origin main >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [UYARI] GitHub sunucusuna baglanilamadi. Mevcut surumle devam ediliyor...
    goto LAUNCH
)

:: Yerel ve uzak commit hash'lerini karsilastir
for /f %%i in ('git rev-parse HEAD 2^>nul') do set LOCAL_HASH=%%i
for /f %%i in ('git rev-parse origin/main 2^>nul') do set REMOTE_HASH=%%i

if "%LOCAL_HASH%" == "%REMOTE_HASH%" (
    echo [BILGI] Program zaten en guncel surumde.
) else (
    echo [GUNCELLEME] Yeni surum bulundu! Guncelleniyor...
    git checkout main >nul 2>&1
    git reset --hard origin/main
    echo [TAMAMLANDI] NeNgi PDF basariyla en son surume guncellendi!
    echo.
    echo [2/3] Bagimliliklar kontrol ediliyor...
    python -m pip install -r requirements.txt --quiet
)

:LAUNCH
echo.
echo [3/3] NeNgi PDF baslatiliyor...
echo ========================================================
echo.

python -m nengi.main

echo.
echo ========================================================
echo  NeNgi PDF sonlandirildi.
echo ========================================================
echo.
echo Pencereyi kapatmak icin herhangi bir tusa basin...
pause >nul
