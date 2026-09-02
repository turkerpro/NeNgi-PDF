"""
NeNgi PDF - Main Fluent Application Window
Integrates multi-tab browsing, ribbon toolbar, PDF viewing, side-by-side DIFF comparison,
open tab comparison, external image roundtrip editing, page management, security, and Windows integration.
"""

from __future__ import annotations
import os
import sys
from typing import Optional, List, Tuple
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QLabel, 
    QSplitter, QInputDialog, QComboBox, QMenu, QDialog, QPushButton
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence

from nengi.core.pdf_document import PDFDocument
from nengi.core.page_manager import PageManager
from nengi.core.security import SecurityManager
from nengi.core.converter import FormatConverter
from nengi.core.windows_integration import register_as_default_pdf_viewer, open_windows_default_apps_settings, is_windows
from nengi.ui.pdf_view import PDFViewer
from nengi.ui.diff_view import DiffView
from nengi.ui.thumbnail_bar import ThumbnailBar
from nengi.ui.signature_dialog import SignatureDialog
from nengi.ui.password_dialog import PasswordDialog
from nengi.ui.page_manager_dialog import PageManagerDialog
from nengi.ui.styles import DARK_THEME, LIGHT_THEME


class OpenTabsDiffDialog(QDialog):
    """Dialog allowing user to choose which two open tabs to compare with DIFF."""

    def __init__(self, open_tabs: List[Tuple[int, str, PDFDocument]], default_a: int = 0, default_b: int = 1, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Açık Sekmeleri Karşılaştır (DIFF)")
        self.setFixedSize(450, 220)
        self.open_tabs = open_tabs
        self.selected_a_idx = default_a
        self.selected_b_idx = default_b

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        lbl_info = QLabel("Gelen e-postalardan veya dosyalardan açık olan sekmeleri seçin:")
        lbl_info.setStyleSheet("color: #C0C0C0; margin-bottom: 5px;")
        layout.addWidget(lbl_info)

        # Tab A
        layout.addWidget(QLabel("🔴 Orijinal (Eski) Belge:"))
        self.combo_a = QComboBox()
        for idx, title, _ in self.open_tabs:
            self.combo_a.addItem(f"Sekme {idx + 1}: {title}", idx)
        self.combo_a.setCurrentIndex(min(self.selected_a_idx, self.combo_a.count() - 1))
        layout.addWidget(self.combo_a)

        # Tab B
        layout.addWidget(QLabel("🟢 Revize Edilmiş (Yeni) Belge:"))
        self.combo_b = QComboBox()
        for idx, title, _ in self.open_tabs:
            self.combo_b.addItem(f"Sekme {idx + 1}: {title}", idx)
        # Select second tab by default if exists
        target_b = self.selected_b_idx if self.selected_b_idx < self.combo_b.count() else 0
        self.combo_b.setCurrentIndex(target_b)
        layout.addWidget(self.combo_b)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_compare = QPushButton("⚖️ Sekmeleri Karşılaştır")
        btn_compare.setObjectName("accentButton")
        btn_compare.clicked.connect(self._on_compare)
        btn_layout.addWidget(btn_compare)

        layout.addLayout(btn_layout)

    def _on_compare(self):
        self.selected_a_idx = self.combo_a.currentData()
        self.selected_b_idx = self.combo_b.currentData()

        if self.selected_a_idx == self.selected_b_idx:
            QMessageBox.warning(self, "Uyarı", "Lütfen karşılaştırmak için iki farklı sekme seçin.")
            return

        self.accept()


class MainWindow(QMainWindow):
    """Main Application Window for NeNgi PDF."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeNgi PDF - Akıllı ve DIFF Destekli PDF Düzenleyici")
        self.resize(1280, 840)
        self.is_dark_mode = True

        self._init_ui()
        self.apply_theme(DARK_THEME)

    def _init_ui(self):
        # Create Central Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        # Tab bar context menu for comparing open tabs and tab management
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)

        # Create Left Sidebar (Thumbnails)
        self.thumbnail_bar = ThumbnailBar()
        self.thumbnail_bar.page_selected.connect(self._on_thumbnail_page_selected)
        self.thumbnail_bar.pages_modified.connect(self._on_pages_modified)

        # Main horizontal splitter with thumbnails and central tabs
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.thumbnail_bar)
        self.splitter.addWidget(self.tabs)
        self.splitter.setSizes([180, 1100])
        self.setCentralWidget(self.splitter)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_page = QLabel("Sayfa: - / -")
        self.lbl_status_page.setStyleSheet("padding: 0 10px;")
        self.status_bar.addPermanentWidget(self.lbl_status_page)

        self.lbl_status_zoom = QLabel("Yakınlaştırma: %120")
        self.lbl_status_zoom.setStyleSheet("padding: 0 10px;")
        self.status_bar.addPermanentWidget(self.lbl_status_zoom)

        # Toolbars / Ribbon
        self._create_toolbars()

    def _create_toolbars(self):
        # 1. Main Action Toolbar
        tb_main = QToolBar("Ana Araçlar")
        tb_main.setIconSize(QSize(20, 20))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb_main)

        # File actions
        act_open = tb_main.addAction("📂 PDF Aç")
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self.open_file_dialog)

        act_save = tb_main.addAction("💾 Kaydet")
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_current_file)

        act_save_as = tb_main.addAction("💾 Farklı Kaydet")
        act_save_as.triggered.connect(self.save_current_file_as)

        tb_main.addSeparator()

        # DIFF Actions
        act_diff_open_tabs = tb_main.addAction("⚖️ Açık Sekmeleri Karşılaştır (DIFF)")
        act_diff_open_tabs.setToolTip("Gelen maillerdeki açık olan iki PDF sekmesini kaydetmeden anında karşılaştır")
        act_diff_open_tabs.triggered.connect(self.compare_open_tabs)

        act_diff = tb_main.addAction("⚖️ İki Dosya Seçip Karşılaştır...")
        act_diff.setToolTip("Bilgisayardan iki farklı PDF seçip yan yana karşılaştır")
        act_diff.triggered.connect(self.open_diff_dialog)

        tb_main.addSeparator()

        # Tools
        self.act_tool_view = tb_main.addAction("👆 Gezin / Seç")
        self.act_tool_view.setCheckable(True)
        self.act_tool_view.setChecked(True)
        self.act_tool_view.triggered.connect(lambda: self._set_viewer_tool("view"))

        self.act_tool_whiteout = tb_main.addAction("◻️ Beyazlat / Silgi")
        self.act_tool_whiteout.setCheckable(True)
        self.act_tool_whiteout.setToolTip("Taranmış yazı, leke veya kalem izlerini dikdörtgen seçerek temizle")
        self.act_tool_whiteout.triggered.connect(lambda: self._set_viewer_tool("whiteout"))

        self.act_tool_text = tb_main.addAction("✍️ Metin Ekle")
        self.act_tool_text.setCheckable(True)
        self.act_tool_text.setToolTip("Sayfa üzerinde istenen yere tıklayıp yeni metin ekle")
        self.act_tool_text.triggered.connect(lambda: self._set_viewer_tool("text"))

        act_paint = tb_main.addAction("🖌️ Paint'te Aç ve Düzenle")
        act_paint.setToolTip("Taranmış evrağı Paint programında açıp temizle; kaydedince PDF otomatik güncellenir")
        act_paint.triggered.connect(self._launch_external_image_edit)

        act_sig = tb_main.addAction("🖊️ İmza Ekle")
        act_sig.setToolTip("Kendi el yazısı imzanızı çizin veya imza resmi yükleyip sayfaya ekleyin")
        act_sig.triggered.connect(self._open_signature_dialog)

        tb_main.addSeparator()

        # Page Management
        act_manage_pages = tb_main.addAction("📑 Sayfaları Yönet")
        act_manage_pages.setToolTip("Sayfaları görsel olarak sırala, döndür, sil veya boş sayfa ekle")
        act_manage_pages.triggered.connect(self._open_page_manager)

        act_rot_cw = tb_main.addAction("🔄 Döndür")
        act_rot_cw.triggered.connect(self._rotate_current_page)

        tb_main.addSeparator()

        # Security & Conversion
        act_protect = tb_main.addAction("🔒 Parola Koy")
        act_protect.triggered.connect(self._encrypt_current_doc)

        act_unprotect = tb_main.addAction("🔓 Şifre Kaldır")
        act_unprotect.triggered.connect(self._decrypt_current_doc)

        act_export_pages = tb_main.addAction("🖼️ Resme Çevir")
        act_export_pages.triggered.connect(self._export_pages_as_images)

        act_img_to_pdf = tb_main.addAction("📑 Resimlerden PDF Yap")
        act_img_to_pdf.triggered.connect(self._convert_images_to_pdf)

        tb_main.addSeparator()

        # Windows integration & Default app
        act_default_app = tb_main.addAction("⚙️ Varsayılan PDF Aracı Yap")
        act_default_app.setToolTip("NeNgi PDF'i Windows'un varsayılan PDF okuyucusu yap")
        act_default_app.triggered.connect(self._set_as_default_pdf_app)

        # Zoom actions
        act_zoom_in = tb_main.addAction("🔍➕")
        act_zoom_in.triggered.connect(self._zoom_in)

        act_zoom_out = tb_main.addAction("🔍➖")
        act_zoom_out.triggered.connect(self._zoom_out)

        # Theme toggle
        act_theme = tb_main.addAction("🌓 Tema")
        act_theme.triggered.connect(self._toggle_theme)

    def apply_theme(self, stylesheet: str):
        self.setStyleSheet(stylesheet)

    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme(DARK_THEME if self.is_dark_mode else LIGHT_THEME)

    def get_open_pdf_tabs(self) -> List[Tuple[int, str, PDFViewer]]:
        """Returns list of (tab_index, title, viewer) for all currently open PDF tabs."""
        results = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, PDFViewer) and w.doc and w.doc.is_open:
                title = self.tabs.tabText(i)
                results.append((i, title, w))
        return results

    def compare_open_tabs(self, default_tab_a: int = 0, default_tab_b: int = 1):
        """
        Compares two open tabs side-by-side with DIFF.
        If exactly 2 tabs are open, launches immediately!
        If > 2 tabs open, prompts with dropdown.
        If < 2 tabs open, guides user to open the second document.
        """
        open_tabs = self.get_open_pdf_tabs()
        if len(open_tabs) < 2:
            if len(open_tabs) == 1:
                # Offer to pick the 2nd PDF to compare with this open tab
                reply = QMessageBox.question(
                    self, "DIFF Karşılaştırma",
                    f"Şu anda yalnızca '{open_tabs[0][1]}' açık.\n\nBu belgeyle karşılaştırmak istediğiniz ikinci PDF dosyasını seçmek ister misiniz?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    file_b, _ = QFileDialog.getOpenFileName(self, "Karşılaştırılacak 2. PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
                    if file_b:
                        doc_b = PDFDocument(file_b)
                        self._launch_diff(open_tabs[0][2].doc, doc_b, open_tabs[0][1], os.path.basename(file_b))
            else:
                QMessageBox.information(
                    self, "Bilgi", 
                    "Karşılaştırma yapabilmek için lütfen karşılaştırmak istediğiniz PDF'leri açın (örneğin maillerinizdeki iki PDF'e tıklayarak sekmelerde açabilirsiniz)."
                )
            return

        if len(open_tabs) == 2:
            # Exactly two tabs: compare immediately!
            tab_a = open_tabs[0]
            tab_b = open_tabs[1]
            self._launch_diff(tab_a[2].doc, tab_b[2].doc, tab_a[1], tab_b[1])
        else:
            # More than two tabs: let user choose
            dlg = OpenTabsDiffDialog(open_tabs, default_tab_a, default_tab_b, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                viewer_a = self.tabs.widget(dlg.selected_a_idx)
                viewer_b = self.tabs.widget(dlg.selected_b_idx)
                title_a = self.tabs.tabText(dlg.selected_a_idx)
                title_b = self.tabs.tabText(dlg.selected_b_idx)
                if isinstance(viewer_a, PDFViewer) and isinstance(viewer_b, PDFViewer):
                    self._launch_diff(viewer_a.doc, viewer_b.doc, title_a, title_b)

    def _launch_diff(self, doc_a: PDFDocument, doc_b: PDFDocument, label_a: str, label_b: str):
        diff_view = DiffView(self)
        diff_view.status_message.connect(self.show_status_message)
        diff_view.load_diff(doc_a, doc_b, label_a, label_b)

        tab_title = f"⚖️ DIFF: {label_a} ⟷ {label_b}"
        tab_idx = self.tabs.addTab(diff_view, tab_title)
        self.tabs.setCurrentIndex(tab_idx)
        self.show_status_message(f"Karşılaştırma açıldı: {label_a} ⟷ {label_b}")

    def _show_tab_context_menu(self, pos: QPoint):
        """Right-click menu on tabs."""
        tab_bar = self.tabs.tabBar()
        tab_idx = tab_bar.tabAt(pos)
        if tab_idx < 0:
            return

        menu = QMenu(self)
        open_tabs = self.get_open_pdf_tabs()

        if len(open_tabs) >= 2 and isinstance(self.tabs.widget(tab_idx), PDFViewer):
            act_diff_this = menu.addAction("⚖️ Bu Sekmeyi Diğer Açık Sekmeyle Karşılaştır (DIFF)")
            act_diff_this.triggered.connect(lambda: self.compare_open_tabs(default_tab_a=tab_idx))
            menu.addSeparator()

        act_close = menu.addAction("❌ Bu Sekmeyi Kapat")
        act_close.triggered.connect(lambda: self._close_tab(tab_idx))

        act_close_others = menu.addAction("🧹 Diğer Sekmeleri Kapat")
        act_close_others.triggered.connect(lambda: self._close_other_tabs(tab_idx))

        menu.exec(tab_bar.mapToGlobal(pos))

    def _close_other_tabs(self, keep_idx: int):
        for i in range(self.tabs.count() - 1, -1, -1):
            if i != keep_idx:
                self._close_tab(i)

    def _set_as_default_pdf_app(self):
        """Sets NeNgi PDF as the default PDF handler in Windows."""
        if not is_windows():
            QMessageBox.information(
                self, "Bilgi", 
                "Windows entegrasyonu özelliği Windows işletim sisteminde aktiftir.\n\nWindows bilgisayarınızda bu butona tıkladığınızda NeNgi PDF otomatik olarak varsayılan PDF okuyucusu olarak ayarlanır."
            )
            return

        ok, msg = register_as_default_pdf_viewer()
        if ok:
            reply = QMessageBox.question(
                self, "Başarılı",
                f"{msg}\n\nWindows 'Varsayılan Uygulamalar' ayarlarını da açıp onaylamak ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                open_windows_default_apps_settings()
        else:
            QMessageBox.warning(self, "Hata", msg)

    def get_current_viewer(self) -> Optional[PDFViewer]:
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, PDFViewer):
            return current_widget
        return None

    def get_current_doc(self) -> Optional[PDFDocument]:
        viewer = self.get_current_viewer()
        return viewer.doc if viewer else None

    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "PDF Dosyası Aç", "", "PDF Dosyaları (*.pdf)")
        if file_paths:
            for f in file_paths:
                self.open_pdf(f)

    def open_pdf(self, file_path: str):
        # Check if this exact file is already open in one of the tabs
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, PDFViewer) and w.doc and w.doc.file_path == file_path:
                self.tabs.setCurrentIndex(i)
                self.show_status_message(f"'{os.path.basename(file_path)}' sekmesine geçildi.")
                return

        doc = PDFDocument()
        is_ok = doc.open(file_path)
        
        # If encrypted, prompt for password
        if doc.is_encrypted and not is_ok:
            dlg = PasswordDialog(mode="decrypt", parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.password:
                if not doc.authenticate(dlg.password):
                    QMessageBox.critical(self, "Hata", "Girilen parola hatalı.")
                    return
            else:
                return

        viewer = PDFViewer(self)
        viewer.load_document(doc)
        viewer.page_changed.connect(self._on_viewer_page_changed)
        viewer.document_modified.connect(self._on_doc_modified)
        viewer.status_message.connect(self.show_status_message)

        tab_title = os.path.basename(file_path)
        tab_idx = self.tabs.addTab(viewer, tab_title)
        self.tabs.setCurrentIndex(tab_idx)

        self.thumbnail_bar.load_thumbnails(doc)
        self.show_status_message(f"'{tab_title}' yeni sekmede açıldı.")

    def open_diff_dialog(self):
        """Dialog to select two PDFs from disk and open a side-by-side DIFF tab."""
        file_a, _ = QFileDialog.getOpenFileName(self, "Orijinal (Eski) PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
        if not file_a:
            return

        file_b, _ = QFileDialog.getOpenFileName(self, "Revize Edilmiş (Yeni) PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
        if not file_b:
            return

        doc_a = PDFDocument(file_a)
        doc_b = PDFDocument(file_b)
        self._launch_diff(doc_a, doc_b, os.path.basename(file_a), os.path.basename(file_b))

    def save_current_file(self):
        doc = self.get_current_doc()
        if not doc:
            return
        if doc.save():
            self.show_status_message("Belge kaydedildi.")
            viewer = self.get_current_viewer()
            if viewer:
                viewer.refresh_all_pages()
        else:
            QMessageBox.critical(self, "Hata", "Dosya kaydedilemedi.")

    def save_current_file_as(self):
        doc = self.get_current_doc()
        if not doc:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", "", "PDF Dosyaları (*.pdf)")
        if file_path:
            if doc.save(file_path):
                self.show_status_message(f"Farklı kaydedildi: {file_path}")
            else:
                QMessageBox.critical(self, "Hata", "Dosya kaydedilemedi.")

    def _set_viewer_tool(self, tool_mode: str):
        self.act_tool_view.setChecked(tool_mode == "view")
        self.act_tool_whiteout.setChecked(tool_mode == "whiteout")
        self.act_tool_text.setChecked(tool_mode == "text")

        viewer = self.get_current_viewer()
        if viewer:
            viewer.set_tool_mode(tool_mode)

    def _launch_external_image_edit(self):
        viewer = self.get_current_viewer()
        if viewer and viewer.doc:
            current_page = viewer.current_page_idx
            viewer.roundtrip_handler.edit_scanned_page(viewer.doc, current_page)

    def _open_signature_dialog(self):
        viewer = self.get_current_viewer()
        if not viewer or not viewer.doc:
            QMessageBox.information(self, "Bilgi", "Lütfen önce bir PDF açın.")
            return

        dlg = SignatureDialog(self)
        if dlg.exec() == SignatureDialog.DialogCode.Accepted and dlg.saved_signature_path:
            viewer.set_tool_mode("stamp", stamp_path=dlg.saved_signature_path)
            self.show_status_message("İmza hazır! Belgede imzalamak istediğiniz yere tıklayın.")

    def _open_page_manager(self):
        doc = self.get_current_doc()
        if not doc:
            return
        dlg = PageManagerDialog(doc, self)
        if dlg.exec() == PageManagerDialog.DialogCode.Accepted:
            viewer = self.get_current_viewer()
            if viewer:
                viewer.refresh_all_pages()
            self.thumbnail_bar.load_thumbnails(doc)

    def _rotate_current_page(self):
        viewer = self.get_current_viewer()
        if viewer and viewer.doc:
            viewer.doc.rotate_page(viewer.current_page_idx, 90)
            viewer.refresh_page(viewer.current_page_idx)
            self.thumbnail_bar.load_thumbnails(viewer.doc)

    def _encrypt_current_doc(self):
        doc = self.get_current_doc()
        if not doc:
            return
        dlg = PasswordDialog(mode="encrypt", parent=self)
        if dlg.exec() == PasswordDialog.DialogCode.Accepted and dlg.password:
            out_file, _ = QFileDialog.getSaveFileName(self, "Şifreli PDF'i Kaydet", "", "PDF Dosyası (*.pdf)")
            if out_file:
                if SecurityManager.encrypt_document(doc, dlg.password, out_file):
                    QMessageBox.information(self, "Başarılı", "Belge başarıyla parolayla şifrelendi.")
                else:
                    QMessageBox.critical(self, "Hata", "Şifreleme başarısız oldu.")

    def _decrypt_current_doc(self):
        doc = self.get_current_doc()
        if not doc:
            return
        out_file, _ = QFileDialog.getSaveFileName(self, "Parolasız Kopyayı Kaydet", "", "PDF Dosyası (*.pdf)")
        if out_file:
            if SecurityManager.remove_password(doc, out_file):
                QMessageBox.information(self, "Başarılı", "Belgenin şifresi kaldırıldı ve kaydedildi.")
            else:
                QMessageBox.critical(self, "Hata", "Şifre kaldırma başarısız oldu.")

    def _export_pages_as_images(self):
        doc = self.get_current_doc()
        if not doc:
            return
        dir_path = QFileDialog.getExistingDirectory(self, "Resimlerin Kaydedileceği Klasörü Seç")
        if dir_path:
            results = FormatConverter.export_all_pages(doc, dir_path, format_ext="png", dpi=300)
            QMessageBox.information(self, "Tamamlandı", f"{len(results)} sayfa yüksek çözünürlüklü PNG olarak kaydedildi.")

    def _convert_images_to_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, "PDF'e Dönüştürülecek Resimleri Seç", "", "Resimler (*.png *.jpg *.jpeg *.bmp)")
        if files:
            out_pdf, _ = QFileDialog.getSaveFileName(self, "Oluşturulacak PDF Dosyası", "", "PDF Dosyası (*.pdf)")
            if out_pdf:
                if FormatConverter.images_to_pdf(files, out_pdf):
                    QMessageBox.information(self, "Başarılı", "Resimler tek bir PDF dosyasında birleştirildi.")
                    self.open_pdf(out_pdf)

    def _zoom_in(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.zoom_in()
            self.lbl_status_zoom.setText(f"Yakınlaştırma: %{int(viewer.zoom * 100)}")

    def _zoom_out(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.zoom_out()
            self.lbl_status_zoom.setText(f"Yakınlaştırma: %{int(viewer.zoom * 100)}")

    def _close_tab(self, index: int):
        widget = self.tabs.widget(index)
        if isinstance(widget, PDFViewer) and widget.doc:
            widget.doc.close()
        self.tabs.removeTab(index)

    def _on_tab_changed(self, index: int):
        viewer = self.get_current_viewer()
        if viewer and viewer.doc:
            self.thumbnail_bar.load_thumbnails(viewer.doc)
            self.lbl_status_page.setText(f"Sayfa: {viewer.current_page_idx + 1} / {viewer.doc.page_count}")
            self.lbl_status_zoom.setText(f"Yakınlaştırma: %{int(viewer.zoom * 100)}")
        else:
            self.thumbnail_bar.list_widget.clear()
            self.lbl_status_page.setText("Sayfa: - / -")

    def _on_thumbnail_page_selected(self, page_idx: int):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.scroll_to_page(page_idx)

    def _on_viewer_page_changed(self, current: int, total: int):
        self.lbl_status_page.setText(f"Sayfa: {current} / {total}")
        self.thumbnail_bar.select_page(current - 1)

    def _on_doc_modified(self):
        viewer = self.get_current_viewer()
        if viewer and viewer.doc:
            self.thumbnail_bar.load_thumbnails(viewer.doc)

    def _on_pages_modified(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.refresh_all_pages()

    def show_status_message(self, message: str):
        self.status_bar.showMessage(message, 5000)
