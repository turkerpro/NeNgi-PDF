"""
NeNgi PDF - System Tray Agent
Keeps NeNgi PDF resident in background memory for instant cold-start (0.1s launch),
manages Windows System Tray icon, and provides quick actions.
"""

from __future__ import annotations
import os
import sys
from typing import Optional, TYPE_CHECKING
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QFileDialog, QApplication

if TYPE_CHECKING:
    from nengi.ui.main_window import MainWindow


class NeNgiTrayAgent(QObject):
    """
    Background tray daemon that maintains app readiness in RAM.
    """

    open_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, main_window: MainWindow, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.main_window = main_window
        self.tray_icon: Optional[QSystemTrayIcon] = None
        self._is_quitting = False
        self._notified_minimize = False

        self._setup_tray()

    def _get_app_icon(self) -> QIcon:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "app_icon.png")
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "resources", "app_icon.png")

        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def _setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon = self._get_app_icon()
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("NeNgi PDF - Hızlı ve Hazır")

        # Tray Menu
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu {"
            "  background-color: #1F2227; color: #E0E0E0; border: 1px solid #353942; border-radius: 8px; padding: 4px;"
            "}"
            "QMenu::item {"
            "  padding: 6px 24px 6px 12px; border-radius: 4px; font-size: 13px;"
            "}"
            "QMenu::item:selected {"
            "  background-color: #0078D4; color: #FFFFFF;"
            "}"
            "QMenu::separator {"
            "  height: 1px; background: #353942; margin: 4px 6px;"
            "}"
        )

        act_show = QAction("📑 NeNgi PDF'i Aç", menu)
        act_show.triggered.connect(self.show_main_window)
        menu.addAction(act_show)

        act_open_file = QAction("📂 Hızlı Belge Aç...", menu)
        act_open_file.triggered.connect(self._on_quick_open_file)
        menu.addAction(act_open_file)

        menu.addSeparator()

        act_quit = QAction("❌ Tamamen Çık", menu)
        act_quit.triggered.connect(self.quit_application)
        menu.addAction(act_quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            if self.main_window.isVisible() and not self.main_window.isMinimized():
                self.main_window.hide()
            else:
                self.show_main_window()

    def show_main_window(self):
        self.main_window.show()
        self.main_window.showNormal()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _on_quick_open_file(self):
        self.show_main_window()
        self.main_window.open_file_dialog()

    def handle_window_close(self, event):
        """Called by MainWindow.closeEvent to hide into tray instead of exiting."""
        if self._is_quitting:
            event.accept()
            return

        event.ignore()
        self.main_window.hide()

        if not self._notified_minimize and self.tray_icon:
            self._notified_minimize = True
            self.tray_icon.showMessage(
                "NeNgi PDF Arka Planda Hazır",
                "Uygulama arka planda hazır bekliyor. Bir PDF açtığınızda anında ekrana gelecektir.",
                QSystemTrayIcon.MessageIcon.Information,
                2500
            )

    def quit_application(self):
        """Permanently closes the daemon and terminates the process."""
        self._is_quitting = True
        if self.tray_icon:
            self.tray_icon.hide()
        self.main_window.close()
        QApplication.quit()
