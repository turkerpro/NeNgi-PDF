@echo off
chcp 65001 >nul
echo ========================================================
echo               NeNgi PDF Baslatici
echo ========================================================
echo.

:: Calisan eski arka plan sureci varsa sonlandir
taskkill /F /IM NeNgi_PDF.exe >nul 2>&1

echo [1/2] Guncellemeler kontrol ediliyor...
git fetch origin main
git checkout main
git reset --hard origin/main

echo.
echo [2/2] NeNgi PDF baslatiliyor...
echo ========================================================
echo.

python -m nengi.main

echo.
echo ========================================================
echo Program sonlandi veya bir hata ile karsilasildi.
echo Hatayi inceleyebilmeniz icin bu pencere acik tutuluyor.
echo ========================================================
pause
