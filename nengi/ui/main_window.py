"""
NeNgi PDF - Main Fluent Application Window
Integrates multi-tab browsing, ribbon toolbar, PDF viewing, side-by-side DIFF comparison,
image roundtrip editing, visual page organization, security, and conversion.
"""

from __future__ import annotations
import os
import sys
from typing import Optional, List, Dict
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QLabel, 
    QSplitter, QInputDialog, QComboBox, QToolButton
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence

from nengi.core.pdf_document import PDFDocument
from nengi.core.page_manager import PageManager
from nengi.core.security import SecurityManager
from nengi.core.converter import FormatConverter
from nengi.ui.pdf_view import PDFViewer
from nengi.ui.diff_view import DiffView
from nengi.ui.thumbnail_bar import ThumbnailBar
from nengi.ui.signature_dialog import SignatureDialog
from nengi.ui.password_dialog import PasswordDialog
from nengi.ui.page_manager_dialog import PageManagerDialog
from nengi.ui.styles import DARK_THEME, LIGHT_THEME


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
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

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

        # DIFF Action (Prominent)
        act_diff = tb_main.addAction("⚖️ İki PDF Karşılaştır (DIFF)")
        act_diff.setToolTip("İki PDF arasındaki metin değişikliklerini yan yana senkronize gör")
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

    def get_current_viewer(self) -> Optional[PDFViewer]:
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, PDFViewer):
            return current_widget
        return None

    def get_current_doc(self) -> Optional[PDFDocument]:
        viewer = self.get_current_viewer()
        return viewer.doc if viewer else None

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF Dosyası Aç", "", "PDF Dosyaları (*.pdf)")
        if file_path:
            self.open_pdf(file_path)

    def open_pdf(self, file_path: str):
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
        self.show_status_message(f"'{tab_title}' başarıyla açıldı.")

    def open_diff_dialog(self):
        """Dialog to select two PDFs and open a side-by-side DIFF tab."""
        file_a, _ = QFileDialog.getOpenFileName(self, "Orijinal (Eski) PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
        if not file_a:
            return

        file_b, _ = QFileDialog.getOpenFileName(self, "Revize Edilmiş (Yeni) PDF Dosyasını Seç", "", "PDF Dosyaları (*.pdf)")
        if not file_b:
            return

        doc_a = PDFDocument(file_a)
        doc_b = PDFDocument(file_b)

        diff_view = DiffView(self)
        diff_view.status_message.connect(self.show_status_message)
        diff_view.load_diff(doc_a, doc_b, os.path.basename(file_a), os.path.basename(file_b))

        tab_title = f"⚖️ DIFF: {os.path.basename(file_a)} ⟷ {os.path.basename(file_b)}"
        tab_idx = self.tabs.addTab(diff_view, tab_title)
        self.tabs.setCurrentIndex(tab_idx)

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
        # Uncheck others
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
