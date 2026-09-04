@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: Yonetici haklari kontrolu ve otomatik UAC yukseltme
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Yonetici yetkileri aliniyor, lutfen acilan onay penceresinde 'Evet'i tiklayin...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo ========================================================
echo   NeNgi PDF - Windows Sanal Yazici Kurulumu
echo ========================================================
echo.
echo 'NeNgi PDF' sanal yazicisi kuruluyor ve yapilandiriliyor...
echo.

echo [1/3] Windows PDF yazdirma bileseni kontrol ediliyor...
dism /Online /Enable-Feature /FeatureName:"Printing-PrintToPDFServices-Features" /NoRestart >nul 2>&1

echo [2/3] 'NeNgi PDF' yazici portu ve yazici kuyrugu olusturuluyor...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = 'NeNgi PDF'; $d = 'Microsoft Print to PDF'; $spoolDir = \"$env:ProgramData\NeNgi_PDF\spool\"; if (-not (Test-Path $spoolDir)) { New-Item -ItemType Directory -Path $spoolDir -Force | Out-Null }; try { $acl = Get-Acl $spoolDir; $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('Users', 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'); $acl.AddAccessRule($rule); Set-Acl $spoolDir $acl -ErrorAction SilentlyContinue } catch {}; $spoolFile = \"$spoolDir\nengi_print.pdf\"; if (-not (Test-Path $spoolFile)) { [System.IO.File]::WriteAllBytes($spoolFile, @()) }; Remove-Printer -Name $p -ErrorAction SilentlyContinue; if (-not (Get-PrinterPort -Name $spoolFile -ErrorAction SilentlyContinue)) { try { Add-PrinterPort -Name $spoolFile -ErrorAction Stop } catch { Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Ports' -Name $spoolFile -Value '' -Type String -Force -ErrorAction SilentlyContinue; Restart-Service -Name Spooler -Force -ErrorAction SilentlyContinue } }; $driver = (Get-PrinterDriver -Name $d -ErrorAction SilentlyContinue); if (-not $driver) { $driverName = (Get-PrinterDriver | Where-Object { $_.Name -like '*PDF*' } | Select-Object -First 1 -ExpandProperty Name) } else { $driverName = $d }; if (-not $driverName) { $driverName = 'Microsoft Print to PDF' }; Add-Printer -Name $p -DriverName $driverName -PortName $spoolFile -PrintProcessor 'winprint' -ErrorAction SilentlyContinue; if (-not (Get-Printer -Name $p -ErrorAction SilentlyContinue)) { $src = Get-Printer -Name $d -ErrorAction SilentlyContinue; if ($src) { Add-Printer -Name $p -DriverName $src.DriverName -PortName $src.PortName -PrintProcessor 'winprint' -ErrorAction SilentlyContinue } }"

echo [3/3] Outlook yazici onbellegi temizleniyor...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$outlprnt = \"$env:APPDATA\Microsoft\Outlook\outlprnt\"; if (Test-Path $outlprnt) { Remove-Item $outlprnt -Force -ErrorAction SilentlyContinue; Write-Host 'Outlook onbellegi basariyla temizlendi.' }"

powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Printer -Name 'NeNgi PDF' -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  [BASARILI] 'NeNgi PDF' Sanal Yazicisi Basariyla Kuruldu!
    echo ========================================================
    echo.
    echo Artik Outlook, Word, Excel, Chrome ve tum programlardan:
    echo 1. Yazdir (Ctrl+P) tusuna basin
    echo 2. Yazici olarak 'NeNgi PDF' secin
    echo 3. Yazdir'a basin - Belgeniz aninda NeNgi PDF'te acilacaktir!
    echo.
    echo ONEMLI: Eger su an Outlook aciksa, yeni yazicinin taninmasi
    echo         icin lutfen Outlook'u bir kez kapatip yeniden acin.
) else (
    echo.
    echo [HATA] 'NeNgi PDF' yazicisi eklenemedi.
)

echo.
pause
