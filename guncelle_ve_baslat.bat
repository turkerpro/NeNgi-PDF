@echo off
chcp 65001 >nul
echo ========================================================
echo               NeNgi PDF Baslatici
echo ========================================================
echo.

:: Calisan eski sureci sonlandir
taskkill /F /IM NeNgi_PDF.exe >nul 2>&1

echo [1/2] Guncellemeler kontrol ediliyor ve cekiliyor...
git fetch origin main
git checkout main
git reset --hard origin/main

echo.
echo [2/2] NeNgi PDF v1.8.1 baslatiliyor...
echo ========================================================
echo.

python -m nengi.main

echo.
echo ========================================================
echo Program kapandi veya durduruldu.
echo Hata ve loglari gorebilmeniz icin bu ekran acik tutuluyor.
echo ========================================================
pause
