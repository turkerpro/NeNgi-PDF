"""
NeNgi PDF - Windows Virtual Printer Manager
Installs and manages the 'NeNgi PDF' virtual printer in Windows,
allowing users to print from Excel, Word, Chrome, Outlook, and any Windows application directly into NeNgi PDF.
"""

from __future__ import annotations
import os
import sys
import subprocess
from typing import Tuple, List


class VirtualPrinterManager:
    """Manages the 'NeNgi PDF' virtual printer in Windows."""

    PRINTER_NAME = "NeNgi PDF"
    DRIVER_NAME = "Microsoft Print to PDF"

    @classmethod
    def is_windows(cls) -> bool:
        return sys.platform == "win32" or os.name == "nt"

    @classmethod
    def is_printer_installed(cls) -> bool:
        """Checks if the 'NeNgi PDF' virtual printer is installed in Windows."""
        if not cls.is_windows():
            return False
        try:
            ps_cmd = f"Get-Printer -Name '{cls.PRINTER_NAME}' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"
            cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return cls.PRINTER_NAME.lower() in res.stdout.lower()
        except Exception:
            return False

    @classmethod
    def get_spool_dir(cls) -> str:
        """
        Returns the machine-wide or user-local spool directory.
        Prefers ProgramData (accessible to both elevated and non-elevated processes).
        """
        prog_data = os.environ.get("ProgramData")
        if prog_data and os.path.exists(prog_data):
            spool_dir = os.path.join(prog_data, "NeNgi_PDF", "spool")
        else:
            local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            spool_dir = os.path.join(local_app, "NeNgi_PDF", "spool")

        try:
            os.makedirs(spool_dir, exist_ok=True)
        except Exception:
            local_app = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
            spool_dir = os.path.join(local_app, "NeNgi_PDF", "spool")
            os.makedirs(spool_dir, exist_ok=True)

        return spool_dir

    @classmethod
    def get_spool_file_path(cls) -> str:
        return os.path.join(cls.get_spool_dir(), "nengi_print.pdf")

    @classmethod
    def get_spool_candidate_paths(cls) -> List[str]:
        """Returns all potential spool file locations to check for printed documents."""
        candidates = []
        prog_data = os.environ.get("ProgramData") or "C:\\ProgramData"
        candidates.append(os.path.join(prog_data, "NeNgi_PDF", "spool", "nengi_print.pdf"))
        
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            candidates.append(os.path.join(local_app, "NeNgi_PDF", "spool", "nengi_print.pdf"))
            
        user_home = os.path.expanduser("~")
        candidates.append(os.path.join(user_home, "AppData", "Local", "NeNgi_PDF", "spool", "nengi_print.pdf"))
        
        unique: List[str] = []
        for p in candidates:
            if p not in unique:
                unique.append(p)
        return unique

    @classmethod
    def install_printer(cls) -> Tuple[bool, str]:
        """
        Installs the 'NeNgi PDF' virtual printer using the built-in Microsoft Print to PDF driver
        connected to a dedicated automated spool file port.
        Also clears Outlook outlprnt cache so Outlook recognizes the printer without errors.
        """
        if not cls.is_windows():
            return False, "Sanal yazıcı sadece Windows işletim sisteminde desteklenmektedir."

        try:
            spool_file = cls.get_spool_file_path().replace("\\", "\\\\")
            ps_script = (
                f"$p = '{cls.PRINTER_NAME}'; $d = '{cls.DRIVER_NAME}'; "
                f"$port = '{spool_file}'; "
                f"$spoolDir = Split-Path $port; "
                f"if (-not (Test-Path $spoolDir)) {{ New-Item -ItemType Directory -Path $spoolDir -Force | Out-Null }}; "
                f"try {{ $acl = Get-Acl $spoolDir; $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('Users', 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'); $acl.AddAccessRule($rule); Set-Acl $spoolDir $acl -ErrorAction SilentlyContinue }} catch {{}}; "
                f"if (-not (Test-Path $port)) {{ [System.IO.File]::WriteAllBytes($port, @()) }}; "
                f"Remove-Printer -Name $p -ErrorAction SilentlyContinue; "
                f"if (-not (Get-PrinterPort -Name $port -ErrorAction SilentlyContinue)) {{ "
                f"try {{ Add-PrinterPort -Name $port -ErrorAction Stop }} catch {{ "
                f"Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Ports' -Name $port -Value '' -Type String -Force -ErrorAction SilentlyContinue; "
                f"Restart-Service -Name Spooler -Force -ErrorAction SilentlyContinue }} }}; "
                f"$driver = (Get-PrinterDriver -Name $d -ErrorAction SilentlyContinue); "
                f"if (-not $driver) {{ $driverName = (Get-PrinterDriver | Where-Object {{ $_.Name -like '*PDF*' }} | Select-Object -First 1 -ExpandProperty Name) }} else {{ $driverName = $d }}; "
                f"if (-not $driverName) {{ $driverName = 'Microsoft Print to PDF' }}; "
                f"Add-Printer -Name $p -DriverName $driverName -PortName $port -PrintProcessor 'winprint' -ErrorAction SilentlyContinue; "
                f"if (-not (Get-Printer -Name $p -ErrorAction SilentlyContinue)) {{ "
                f"$source = Get-Printer -Name $d -ErrorAction SilentlyContinue; "
                f"if ($source) {{ Add-Printer -Name $p -DriverName $source.DriverName -PortName $source.PortName -PrintProcessor 'winprint' -ErrorAction SilentlyContinue }}; }}; "
                f"$outlprnt = \"$env:APPDATA\\Microsoft\\Outlook\\outlprnt\"; "
                f"if (Test-Path $outlprnt) {{ Remove-Item $outlprnt -Force -ErrorAction SilentlyContinue }};"
            )
            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if cls.is_printer_installed():
                return True, f"'{cls.PRINTER_NAME}' yazıcısı Windows'a başarıyla eklendi ve Outlook önbelleği sıfırlandı."
            else:
                return False, f"Yazıcı eklenirken hata oluştu. Lütfen Yönetici Olarak Çalıştırın:\n{res.stderr.strip() or res.stdout.strip()}"
        except Exception as e:
            return False, f"Yazıcı kurulum hatası: {e}"

    @classmethod
    def uninstall_printer(cls) -> Tuple[bool, str]:
        """Removes the 'NeNgi PDF' virtual printer from Windows."""
        if not cls.is_windows():
            return False, "Sanal yazıcı sadece Windows işletim sisteminde desteklenmektedir."

        try:
            ps_script = f"Remove-Printer -Name '{cls.PRINTER_NAME}' -ErrorAction SilentlyContinue"
            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script]
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return True, f"'{cls.PRINTER_NAME}' yazıcısı kaldırıldı."
        except Exception as e:
            return False, f"Yazıcı kaldırma hatası: {e}"
