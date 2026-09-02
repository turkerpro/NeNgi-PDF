"""
NeNgi PDF - Robust Single-Instance & Multi-Tab IPC Manager
Ensures that all PDF files opened from Windows Explorer, email attachments,
or command line always open as new tabs within the existing NeNgi PDF window
without opening separate application windows.
"""

from __future__ import annotations
import sys
import os
import time
from typing import List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

IPC_SOCKET_NAME = "NeNgiPDF_SingleInstance_App_Server_v2"


class SingleInstanceManager(QObject):
    """Manages single-instance enforcement and inter-process file passing."""

    file_received = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.server: Optional[QLocalServer] = None

    @staticmethod
    def try_send_to_existing_instance(args: List[str]) -> bool:
        """
        Attempts to connect to an already running instance.
        If an instance exists, sends the file paths and returns True.
        """
        socket = QLocalSocket()

        # Brief retry loop (up to 600ms) to accommodate startup race conditions
        for _ in range(3):
            socket.connectToServer(IPC_SOCKET_NAME)
            if socket.waitForConnected(200):
                # Clean and resolve file paths
                clean_files = []
                for a in args:
                    clean = a.strip().strip('"').strip("'")
                    if clean:
                        clean_files.append(os.path.abspath(clean))

                payload = "\n".join(clean_files) if clean_files else "__ACTIVATE__"
                socket.write(payload.encode("utf-8"))
                socket.waitForBytesWritten(1500)
                # Wait briefly for server ACK
                socket.waitForReadyRead(1000)
                socket.disconnectFromServer()
                return True
            time.sleep(0.08)

        return False

    def start_listening(self) -> bool:
        """Starts listening for incoming files from secondary instances."""
        self.server = QLocalServer(self)
        try:
            self.server.setSocketOptions(QLocalServer.SocketOption.WorldAccessOption)
        except Exception:
            pass

        # Clean up any leftover dead socket from previous abnormal shutdown
        self.server.removeServer(IPC_SOCKET_NAME)

        if not self.server.listen(IPC_SOCKET_NAME):
            # If listen fails, try sending to the existing instance one last time
            if self.try_send_to_existing_instance(sys.argv[1:]):
                sys.exit(0)
            return False

        self.server.newConnection.connect(self._on_new_connection)
        return True

    def _on_new_connection(self):
        client = self.server.nextPendingConnection()
        if not client:
            return

        if client.waitForReadyRead(1500):
            raw_data = client.readAll().data().decode("utf-8")
            # Send ACK
            client.write(b"ACK")
            client.waitForBytesWritten(500)
            client.disconnectFromServer()

            lines = raw_data.strip().splitlines()
            for line in lines:
                line = line.strip()
                if line and line != "__ACTIVATE__":
                    self.file_received.emit(line)
                elif line == "__ACTIVATE__":
                    self.file_received.emit("")
