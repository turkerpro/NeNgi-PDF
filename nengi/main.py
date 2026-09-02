"""
NeNgi PDF - Application Entry Point with Single-Instance Multi-Tab Architecture
When a user opens multiple PDFs (e.g. from email attachments or Windows Explorer),
they all open as new tabs within the same single window instead of creating separate windows.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from nengi.ui.main_window import MainWindow
from nengi.core.single_instance import SingleInstanceManager
from nengi.core.tray_agent import NeNgiTrayAgent


def main():
    # 1. Attempt to send arguments to an already running instance
    # If successful, this process will terminate immediately!
    if SingleInstanceManager.try_send_to_existing_instance(sys.argv[1:]):
        sys.exit(0)

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NeNgi PDF")
    app.setOrganizationName("NeNgi")

    # Set application icon globally
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "resources", "app_icon.png")
    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "resources", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Set default clean Segoe UI font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # 2. We are the primary instance
    window = MainWindow()

    # Setup background System Tray daemon
    tray_agent = NeNgiTrayAgent(window)
    window.tray_agent = tray_agent

    # 3. Start listening for incoming files from future launches (e.g. email attachments)
    instance_mgr = SingleInstanceManager(window)
    instance_mgr.file_received.connect(window.handle_external_file)
    instance_mgr.start_listening()

    # 4. Open files or execute flags passed on initial launch
    is_tray_launch = any(arg in sys.argv for arg in ["--tray", "--minimized", "-minimized"])
    if len(sys.argv) > 1 and not is_tray_launch:
        window.handle_external_file(" ".join(sys.argv[1:]))

    if not is_tray_launch:
        window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
