"""
NeNgi PDF - Settings & Preferences Dialog
Configures default PDF handler, themes, zoom defaults, and comparison behaviors.
"""

from __future__ import annotations
from typing import Optional, Callable
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, 
    QLabel, QPushButton, QComboBox, QCheckBox, QGroupBox, 
    QMessageBox, QFrame
)
from nengi.core.windows_integration import (
    register_as_default_pdf_viewer, 
    open_windows_default_apps_settings, 
    is_windows
)
from nengi.core.virtual_printer import VirtualPrinterManager


class SettingsDialog(QDialog):
    """Modern Options and Settings Dialog for NeNgi PDF."""

    theme_changed = pyqtSignal(str)       # "dark" or "light"
    zoom_default_changed = pyqtSignal(float)

    def __init__(self, current_is_dark: bool = True, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Seçenekler ve Ayarlar - NeNgi PDF")
        self.resize(560, 420)
        self.current_is_dark = current_is_dark

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # ---------------- Tab 1: Varsayılan Uygulama & Genel ----------------
        tab_general = QWidget()
        lay_gen = QVBoxLayout(tab_general)
        lay_gen.setSpacing(14)

        # Default App Card
        grp_default = QGroupBox("📌 Varsayılan PDF Görüntüleyicisi (Windows)")
        lay_def = QVBoxLayout(grp_default)
        lay_def.setSpacing(8)

        lbl_def_info = QLabel(
            "Tüm PDF dosyalarınızın doğrudan NeNgi PDF ile açılması için Windows varsayılan uygulama ayarlarını buradan yapabilirsiniz."
        )
        lbl_def_info.setWordWrap(True)
        lbl_def_info.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        lay_def.addWidget(lbl_def_info)

        h_btns = QHBoxLayout()
        btn_set_default = QPushButton("🚀 NeNgi PDF'i Varsayılan Yap")
        btn_set_default.setObjectName("accentButton")
        btn_set_default.clicked.connect(self._on_set_default)
        h_btns.addWidget(btn_set_default)

        btn_open_win_settings = QPushButton("⚙️ Windows Ayarlarını Aç")
        btn_open_win_settings.clicked.connect(self._on_open_win_settings)
        h_btns.addWidget(btn_open_win_settings)
        lay_def.addLayout(h_btns)

        lay_gen.addWidget(grp_default)

        # Virtual Printer Card
        grp_printer = QGroupBox("🖨️ NeNgi PDF Sanal Yazıcısı (Print to NeNgi PDF)")
        lay_ptr = QVBoxLayout(grp_printer)
        lay_ptr.setSpacing(8)

        lbl_ptr_info = QLabel(
            "Excel, Word, Chrome veya herhangi bir programdan 'Yazdır (Ctrl+P)' dediğinizde 'NeNgi PDF' yazıcısını seçerek belgeleri doğrudan PDF olarak kaydedebilirsiniz."
        )
        lbl_ptr_info.setWordWrap(True)
        lbl_ptr_info.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        lay_ptr.addWidget(lbl_ptr_info)

        h_ptr_btns = QHBoxLayout()
        self.btn_install_printer = QPushButton("🖨️ NeNgi PDF Yazıcısını Kur / Aktifleştir")
        self.btn_install_printer.setObjectName("accentButton")
        self.btn_install_printer.clicked.connect(self._on_install_printer)
        h_ptr_btns.addWidget(self.btn_install_printer)

        self.btn_uninstall_printer = QPushButton("🗑️ Yazıcıyı Kaldır")
        self.btn_uninstall_printer.clicked.connect(self._on_uninstall_printer)
        h_ptr_btns.addWidget(self.btn_uninstall_printer)
        lay_ptr.addLayout(h_ptr_btns)

        lay_gen.addWidget(grp_printer)

        # Single Instance Card
        grp_instance = QGroupBox("📑 Sekme ve Açılış Davranışı")
        lay_inst = QVBoxLayout(grp_instance)
        self.chk_single_instance = QCheckBox("E-postalardan ve klasörlerden açılan tüm PDF'leri aynı pencerede sekmelerde topla")
        self.chk_single_instance.setChecked(True)
        lay_inst.addWidget(self.chk_single_instance)

        self.chk_sync_default = QCheckBox("Karşılaştırma (DIFF) ekranında senkron kaydırma başlangıçta açık olsun")
        self.chk_sync_default.setChecked(True)
        lay_inst.addWidget(self.chk_sync_default)

        lay_gen.addWidget(grp_instance)
        lay_gen.addStretch()
        tabs.addTab(tab_general, "Genel & Yazıcı")

        # ---------------- Tab 2: Görünüm & Tema ----------------
        tab_appearance = QWidget()
        lay_app = QVBoxLayout(tab_appearance)
        lay_app.setSpacing(14)

        grp_theme = QGroupBox("🎨 Arayüz Teması")
        lay_thm = QVBoxLayout(grp_theme)

        h_thm = QHBoxLayout()
        h_thm.addWidget(QLabel("Tema Seçimi:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Windows 11 Koyu Tema (Dark)", "Windows 11 Aydınlık Tema (Light)"])
        self.combo_theme.setCurrentIndex(0 if self.current_is_dark else 1)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        h_thm.addWidget(self.combo_theme)
        lay_thm.addLayout(h_thm)
        lay_app.addWidget(grp_theme)

        grp_zoom = QGroupBox("🔍 Varsayılan Yakınlaştırma (Zoom)")
        lay_zm = QVBoxLayout(grp_zoom)
        h_zm = QHBoxLayout()
        h_zm.addWidget(QLabel("Belge Açılış Yakınlaştırması:"))
        self.combo_zoom = QComboBox()
        self.combo_zoom.addItems(["%100 (Standart)", "%120 (Önerilen)", "%150 (Büyük)", "%80 (Kompakt)"])
        self.combo_zoom.setCurrentIndex(1)
        h_zm.addWidget(self.combo_zoom)
        lay_zm.addLayout(h_zm)
        lay_app.addWidget(grp_zoom)

        lay_app.addStretch()
        tabs.addTab(tab_appearance, "Görünüm")

        # ---------------- Tab 3: Hakkında ----------------
        tab_about = QWidget()
        lay_abt = QVBoxLayout(tab_about)
        lay_abt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_abt.setSpacing(10)

        lbl_app_title = QLabel("📑 NeNgi PDF")
        lbl_app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078D4;")
        lay_abt.addWidget(lbl_app_title)

        lbl_version = QLabel("Sürüm: 2.0.0")
        lbl_version.setStyleSheet("color: #AAAAAA;")
        lay_abt.addWidget(lbl_version)

        lbl_desc = QLabel(
            "Açık kaynaklı, modern Windows 11 arayüzüne sahip, akıllı metin DIFF karşılaştırma ve derin düzenleme özellikli PDF uygulaması."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setStyleSheet("color: #CCCCCC; max-width: 440px; margin: 10px 0;")
        lay_abt.addWidget(lbl_desc)

        lbl_license = QLabel("Lisans: MIT Open Source License")
        lbl_license.setStyleSheet("color: #888888; font-size: 11px;")
        lay_abt.addWidget(lbl_license)

        lbl_github = QLabel("GitHub: https://github.com/turkerpro/NeNgi-PDF")
        lbl_github.setStyleSheet("color: #0078D4; font-size: 11px;")
        lay_abt.addWidget(lbl_github)

        self.btn_check_update = QPushButton("🔄 Güncellemeleri Denetle")
        self.btn_check_update.setObjectName("accentButton")
        self.btn_check_update.clicked.connect(self._on_check_updates)
        lay_abt.addWidget(self.btn_check_update)

        self.lbl_update_status = QLabel("")
        self.lbl_update_status.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_update_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_abt.addWidget(self.lbl_update_status)

        tabs.addTab(tab_about, "Hakkında")

        layout.addWidget(tabs)

        # Bottom close button
        btn_close = QPushButton("Kapat")
        btn_close.setObjectName("accentButton")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignRight)

    def _on_set_default(self):
        if not is_windows():
            QMessageBox.information(
                self, "Bilgi", 
                "Windows entegrasyonu özelliği Windows işletim sisteminde aktiftir.\n\nWindows bilgisayarınızda bu butona bastığınızda tüm .pdf uzantılı dosyalar otomatik olarak NeNgi PDF ile açılacaktır."
            )
            return

        ok, msg = register_as_default_pdf_viewer()
        if ok:
            reply = QMessageBox.question(
                self, "Başarılı",
                f"{msg}\n\nWindows 'Varsayılan Uygulamalar' ayar sayfasını da açmak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                open_windows_default_apps_settings()
        else:
            QMessageBox.warning(self, "Hata", msg)

    def _on_open_win_settings(self):
        if not is_windows():
            QMessageBox.information(self, "Bilgi", "Bu kısayol Windows 10 ve Windows 11 üzerinde çalışır.")
            return
        open_windows_default_apps_settings()

    def _on_install_printer(self):
        if not is_windows():
            QMessageBox.information(
                self, "Bilgi",
                "Windows sanal yazıcı entegrasyonu Windows 10 ve Windows 11 üzerinde aktiftir.\n\nKurulum yapıldığında Excel, Word, Chrome gibi tüm programların yazıcı listesinde 'NeNgi PDF' belirecektir."
            )
            return

        ok, msg = VirtualPrinterManager.install_printer()
        if ok:
            QMessageBox.information(
                self, "Başarılı",
                f"{msg}\n\nArtık Excel, Word ve tüm programlardan 'Yazdır' diyerek 'NeNgi PDF' yazıcısını seçebilirsiniz."
            )
        else:
            QMessageBox.warning(self, "Yazıcı Kurulum Hatası", msg)

    def _on_uninstall_printer(self):
        if not is_windows():
            return
        ok, msg = VirtualPrinterManager.uninstall_printer()
        QMessageBox.information(self, "Bilgi", msg)

    def _on_theme_changed(self, index: int):
        theme_name = "dark" if index == 0 else "light"
        self.theme_changed.emit(theme_name)

    # ---------------- Güncelleme (main_window ile aynı UpdateChecker) ----------------
    def _on_check_updates(self):
        from nengi.core.updater import UpdateCheckWorker
        if getattr(self, "_update_check_worker", None) and self._update_check_worker.isRunning():
            return
        self.btn_check_update.setEnabled(False)
        self.lbl_update_status.setText("Güncellemeler denetleniyor...")
        self._update_check_worker = UpdateCheckWorker(parent=self)
        self._update_check_worker.finished.connect(self._on_update_check_finished)
        self._update_check_worker.failed.connect(self._on_update_check_failed)
        self._update_check_worker.start()

    def _on_update_check_failed(self, message: str):
        self.btn_check_update.setEnabled(True)
        self.lbl_update_status.setText("")
        QMessageBox.warning(self, "Güncelleme", message)

    def _on_update_check_finished(self, info):
        self.btn_check_update.setEnabled(True)
        self.lbl_update_status.setText("")
        if not info.has_update:
            QMessageBox.information(
                self, "Güncelleme",
                f"NeNgi PDF güncel. (Sürüm {info.local_version})",
            )
            return
        reply = QMessageBox.question(
            self, "Yeni Sürüm Mevcut",
            f"Yeni sürüm bulundu: {info.local_version} → {info.remote_version}\n\n"
            "Kurulum dosyası indirilip sessiz kuruluma başlansın mı?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._start_update_download(info.download_url)

    def _start_update_download(self, url: str):
        from PyQt6.QtWidgets import QProgressDialog
        from nengi.core.updater import UpdateDownloadWorker
        self._update_progress = QProgressDialog(
            "Kurulum dosyası indiriliyor...", "İptal", 0, 100, self
        )
        self._update_progress.setWindowTitle("Güncelleme İndiriliyor")
        self._update_progress.setMinimumDuration(0)
        self._update_progress.setAutoClose(True)
        self._update_dl_worker = UpdateDownloadWorker(url, parent=self)
        self._update_dl_worker.progress.connect(self._on_update_download_progress)
        self._update_dl_worker.finished.connect(self._on_update_download_finished)
        self._update_dl_worker.failed.connect(self._on_update_check_failed)
        self._update_progress.canceled.connect(self._update_dl_worker.terminate)
        self._update_dl_worker.start()
        self._update_progress.show()

    def _on_update_download_progress(self, downloaded: int, total: int):
        dlg = getattr(self, "_update_progress", None)
        if dlg is None:
            return
        if total > 0:
            dlg.setMaximum(100)
            dlg.setValue(int(downloaded * 100 / total))
        else:
            dlg.setMaximum(0)

    def _on_update_download_finished(self, installer_path: str):
        from PyQt6.QtWidgets import QApplication
        from nengi.core.updater import launch_silent_install
        dlg = getattr(self, "_update_progress", None)
        if dlg is not None:
            dlg.close()
        reply = QMessageBox.question(
            self, "Kurulum Hazır",
            "Yeni sürüm indirildi. Kurulum başlatılıp uygulama kapatılsın mı?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            launch_silent_install(installer_path)
        except Exception as e:
            QMessageBox.warning(self, "Güncelleme", f"Kurulum başlatılamadı: {e}")
            return
        self.accept()
        app = QApplication.instance()
        if app is not None:
            app.quit()
