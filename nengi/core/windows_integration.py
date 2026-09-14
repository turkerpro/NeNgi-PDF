"""
NeNgi PDF - Windows System & Registry Integration
Registers NeNgi PDF as the default handler for .pdf files in Windows,
sets file associations, and launches Windows Default Apps settings.
"""

import sys
import os
import subprocess
from nengi.core.result import Result


def is_windows() -> bool:
    return sys.platform == "win32"


def get_executable_path() -> str:
    """Gets the path to the current executable or python entry point."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller compiled .exe
        return sys.executable
    else:
        # Running as script
        return sys.executable


def register_as_default_pdf_viewer() -> Result[bool]:
    r"""
    Registers NeNgi PDF in Windows Registry under HKEY_CURRENT_USER.
    Does not require Administrator privileges because it targets HKCU\Software\Classes.
    """
    if not is_windows():
        return Result.fail("Not on Windows", "This feature only works on Windows", "NOT_WINDOWS")

    try:
        import winreg

        exe_path = get_executable_path()
        prog_id = "NeNgiPDF.Document"
        app_name = "NeNgi PDF"
        open_cmd = f'"{exe_path}" "%1"'

        # 1. Register ProgID under HKCU\Software\Classes\NeNgiPDF.Document
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "NeNgi PDF Dokümanı")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\DefaultIcon") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f"{exe_path},0")

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{prog_id}\\shell\\open\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, open_cmd)

        # 2. Register .pdf extension association
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\.pdf") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, prog_id)

        # 3. Register under OpenWithProgids
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Classes\\.pdf\\OpenWithProgids") as key:
            winreg.SetValueEx(key, prog_id, 0, winreg.REG_NONE, b"")

        # 4. Register Capabilities for Windows Default Apps UI
        app_reg = "Software\\NeNgiPDF\\Capabilities"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{app_reg}\\FileAssociations") as key:
            winreg.SetValueEx(key, ".pdf", 0, winreg.REG_SZ, prog_id)

        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\RegisteredApplications") as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_reg)

        return Result.ok(True)
    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.exception("Registry update error")
        return Result.from_exception(e, "Failed to register as default PDF viewer", "REGISTER_FAILED")


def open_windows_default_apps_settings() -> Result[None]:
    """Launches Windows 10/11 Default Apps settings page."""
    if is_windows():
        try:
            os.system("start ms-settings:defaultapps")
            return Result.ok(None)
        except Exception as e:
            logger = __import__('logging').getLogger(__name__)
            logger.exception("Failed to open Windows settings")
            return Result.from_exception(e, "Failed to open Windows settings", "OPEN_SETTINGS_FAILED")
    return Result.fail("Not on Windows", "This feature only works on Windows", "NOT_WINDOWS")


def register_shell_context_menus() -> Result[bool]:
    r"""
    Registers Windows Explorer right-click context menus:
    - '📑 NeNgi PDF ile Birleştir'
    - '📄 NeNgi PDF ile PDF'e Dönüştür'
    """
    if not is_windows():
        return Result.fail("Not on Windows", "This feature only works on Windows", "NOT_WINDOWS")

    try:
        import winreg
        exe_path = get_executable_path()

        # 1. Merge Menu
        merge_key_path = r"Software\Classes\*\shell\NeNgiPDF.Merge"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, merge_key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "NeNgi PDF ile Birleştir")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{exe_path},0")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{merge_key_path}\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" --merge "%1"')

        # 2. Convert Menu
        conv_key_path = r"Software\Classes\*\shell\NeNgiPDF.Convert"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, conv_key_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "NeNgi PDF ile PDF'e Dönüştür")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, f"{exe_path},0")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{conv_key_path}\\command") as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{exe_path}" --convert "%1"')

        return Result.ok(True)
    except Exception as e:
        logger = __import__('logging').getLogger(__name__)
        logger.exception("Context menu registration error")
        return Result.from_exception(e, "Failed to register context menus", "REGISTER_MENU_FAILED")
