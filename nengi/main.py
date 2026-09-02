"""
NeNgi PDF - Application Entry Point with Single-Instance Multi-Tab IPC
When a user opens multiple PDFs (e.g. from email attachments or Windows Explorer),
they all open as new tabs within the same single window instead of creating separate windows.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtNetwork import QLocalSocket, QLocalServer

from nengi.ui.main_window import MainWindow

SERVER_NAME = "NeNgiPDF_SingleInstance_App_Server"


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

    # Check if another instance is already running
    client_socket = QLocalSocket()
    client_socket.connectToServer(SERVER_NAME)
    if client_socket.waitForConnected(400):
        # Connected to running instance! Send command line arguments (files) to it
        args = sys.argv[1:]
        if args:
            message = "\n".join(os.path.abspath(f) for f in args if os.path.exists(f))
            if message:
                client_socket.write(message.encode("utf-8"))
                client_socket.waitForBytesWritten(1000)
        client_socket.disconnectFromServer()
        # Exit immediately so only the existing window stays open
        sys.exit(0)

    # If we reach here, we are the primary instance
    window = MainWindow()

    # Set up local IPC server to listen for files from secondary instances (e.g. double-clicked from email)
    local_server = QLocalServer()
    local_server.removeServer(SERVER_NAME)  # Clean up stale socket from previous abnormal termination
    local_server.listen(SERVER_NAME)

    def on_new_connection():
        sock = local_server.nextPendingConnection()
        if not sock:
            return
        if sock.waitForReadyRead(1000):
            data = sock.readAll().data().decode("utf-8")
            for file_path in data.splitlines():
                file_path = file_path.strip()
                if file_path and os.path.exists(file_path):
                    window.open_pdf(file_path)
            window.showNormal()
            window.raise_()
            window.activateWindow()

    local_server.newConnection.connect(on_new_connection)

    # If files passed directly on initial launch
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            if os.path.exists(f):
                window.open_pdf(os.path.abspath(f))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
