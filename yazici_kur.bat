@echo off
chcp 65001 >nul
echo ========================================================
echo   NeNgi PDF - Windows Sanal Yazici Kurulumu
echo ========================================================
echo.
echo 'NeNgi PDF' yazicisi Windows'a ekleniyor...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = 'NeNgi PDF'; $d = 'Microsoft Print to PDF'; if (-not (Get-Printer -Name $p -ErrorAction SilentlyContinue)) { $port = (Get-Printer -Name $d -ErrorAction SilentlyContinue).PortName; if (-not $port) { $port = (Get-PrinterPort | Where-Object { $_.Name -like '*PROMPT*' -or $_.Name -like '*PDF*' -or $_.Name -eq 'FILE:' } | Select-Object -First 1 -ExpandProperty Name) }; if (-not $port) { $port = 'FILE:' }; Add-Printer -Name $p -DriverName $d -PortName $port }"

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
