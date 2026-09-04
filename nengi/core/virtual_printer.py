"""
NeNgi PDF - Windows Virtual Printer Manager
Installs and manages the 'NeNgi PDF' virtual printer in Windows,
allowing users to print from Excel, Word, Chrome, and any Windows application directly into NeNgi PDF.
"""

from __future__ import annotations
import os
import sys
import subprocess
from typing import Tuple


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
    def install_printer(cls) -> Tuple[bool, str]:
        """
        Installs the 'NeNgi PDF' virtual printer using the built-in Microsoft Print to PDF driver.
        """
        if not cls.is_windows():
            return False, "Sanal yazıcı sadece Windows işletim sisteminde desteklenmektedir."

        try:
            ps_script = (
                f"$p = '{cls.PRINTER_NAME}'; $d = '{cls.DRIVER_NAME}'; "
                f"if (-not (Get-Printer -Name $p -ErrorAction SilentlyContinue)) {{ "
                f"$port = (Get-Printer -Name $d -ErrorAction SilentlyContinue).PortName; "
                f"if (-not $port) {{ $port = (Get-PrinterPort | Where-Object {{ $_.Name -like '*PROMPT*' -or $_.Name -like '*PDF*' -or $_.Name -eq 'FILE:' }} | Select-Object -First 1 -ExpandProperty Name) }}; "
                f"if (-not $port) {{ $port = 'FILE:' }}; "
                f"Add-Printer -Name $p -DriverName $d -PortName $port }}"
            )
            cmd = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                return True, f"'{cls.PRINTER_NAME}' yazıcısı Windows'a başarıyla eklendi."
            else:
                return False, f"Yazıcı eklenirken hata: {res.stderr.strip() or res.stdout.strip()}"
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
