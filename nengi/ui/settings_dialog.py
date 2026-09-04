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
        tabs.addTab(tab_general, "Genel & Varsayılan")

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

        lbl_version = QLabel("Sürüm: 1.6.3 (Gelişmiş Canlı Katmanlar & Akıllı El Aracı)")
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

    def _on_theme_changed(self, index: int):
        theme_name = "dark" if index == 0 else "light"
        self.theme_changed.emit(theme_name)
