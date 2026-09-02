"""
NeNgi PDF - PyInstaller Windows Executable Build Script
Builds a standalone, single-file Windows executable (NeNgi_PDF.exe).
"""

import os
import sys
import subprocess


def build():
    print("========================================")
    print(" NeNgi PDF - Windows .EXE Derleyici")
    print("========================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_point = os.path.join(base_dir, "nengi", "main.py")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",             # or --onefile
        "--windowed",           # GUI app (no terminal window)
        "--name", "NeNgi_PDF",
        f"--paths={base_dir}",
        "--collect-all", "pymupdf",
        "--collect-all", "fitz",
        "--hidden-import", "PyQt6",
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--hidden-import", "PIL",
        f"--add-data={os.path.join(base_dir, 'resources')}{os.pathsep}resources",
        entry_point
    ]

    print(f"Derleme komutu çalıştırılıyor: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        print("\n[BAŞARILI] NeNgi_PDF.exe başarıyla 'dist/NeNgi_PDF/' dizini altında oluşturuldu!")
    else:
        print(f"\n[HATA] Derleme başarısız oldu (Hata kodu: {result.returncode})")


if __name__ == "__main__":
    build()
