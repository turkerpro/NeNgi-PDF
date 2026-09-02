"""
NeNgi PDF - Application Entry Point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from nengi.ui.main_window import MainWindow


def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NeNgi PDF")
    app.setOrganizationName("NeNgi")

    # Set default clean Segoe UI font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()

    # If file arguments passed from CLI or Windows Explorer (open with...)
    if len(sys.argv) > 1:
        initial_file = sys.argv[1]
        if os.path.exists(initial_file):
            window.open_pdf(initial_file)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
