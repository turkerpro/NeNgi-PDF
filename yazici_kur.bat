@echo off
chcp 65001 >nul
echo ========================================================
echo   NeNgi PDF - Windows Sanal Yazici Kurulumu
echo ========================================================
echo.
echo 'NeNgi PDF' yazicisi Windows'a ekleniyor...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command " = 'NeNgi PDF';  = 'Microsoft Print to PDF'; if (-not (Get-Printer -Name  -ErrorAction SilentlyContinue)) { Add-Printer -Name  -DriverName  -PortName 'PORTPROMPT:' }"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [BASARILI] 'NeNgi PDF' yazicisi Windows'a basariyla kuruldu!
    echo.
    echo Artik Excel, Word, Chrome veya herhangi bir programdan:
    echo 1. Yazdir (Ctrl+P) tusuna basin
    echo 2. Yazici olarak 'NeNgi PDF' secin
    echo 3. Belgenizi aninda PDF olarak kaydedin!
) else (
    echo.
    echo [HATA] Yazici eklenemedi. Lutfen Yonetici Olarak Calistirin.
)

echo.
pause
