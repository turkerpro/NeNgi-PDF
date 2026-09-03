"""
NeNgi PDF - NextGen Studio Main Application Window
Modern 3-column layout featuring:
- Left Navigation Rail (Brand, Home, Recent, Documents, Diff, Tools, Settings)
- Top Global Header with Search Pill & Quick Actions
- Central Multi-Tab Document Canvas with Floating Bottom Pill Toolbar
- Right Collapsible Copilot & AI Tools Panel
- Bottom Pagination & Zoom Footer Bar
"""

from __future__ import annotations
import os
import sys
from typing import Optional, List, Tuple
from PyQt6.QtCore import Qt, QSize, QPoint, QRect, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QStatusBar, QFileDialog, QMessageBox, QLabel, QLineEdit,
    QSplitter, QInputDialog, QComboBox, QMenu, QDialog, QPushButton,
    QFrame
)
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QPixmap, QPainter, QFont
import pymupdf as fitz

from nengi.core.pdf_document import PDFDocument
from nengi.core.page_manager import PageManager
from nengi.core.security import SecurityManager
from nengi.core.converter import FormatConverter
from nengi.core.printer import PDFPrinter
from nengi.core.windows_integration import register_as_default_pdf_viewer, open_windows_default_apps_settings, is_windows
from nengi.ui.pdf_view import PDFViewer
from nengi.ui.diff_view import DiffView
from nengi.ui.thumbnail_bar import ThumbnailBar
from nengi.ui.signature_dialog import SignatureDialog
from nengi.ui.password_dialog import PasswordDialog
from nengi.ui.page_manager_dialog import PageManagerDialog
from nengi.ui.settings_dialog import SettingsDialog
from nengi.ui.merge_dialog import MergeFilesDialog
from nengi.ui.navigation_rail import NavigationRail
from nengi.ui.floating_toolbar import FloatingPillToolbar
from nengi.ui.copilot_panel import CopilotPanel
from nengi.ui.styles import DARK_THEME, LIGHT_THEME
from nengi.ui.icons import get_svg_icon


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
        layout.setSpacing(12)

        lbl_info = QLabel("Karşılaştırmak istediğiniz iki açık PDF sekmesini seçin:")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(lbl_info)

        # Tab A combo
        h_a = QHBoxLayout()
        lbl_a = QLabel("🔴 Orijinal Belge (A):")
        lbl_a.setFixedWidth(140)
        self.cb_a = QComboBox()
        for idx, name, _ in self.open_tabs:
            self.cb_a.addItem(f"{idx+1}. {name}", idx)
        if 0 <= self.selected_a_idx < len(self.open_tabs):
            self.cb_a.setCurrentIndex(self.selected_a_idx)
        h_a.addWidget(lbl_a)
        h_a.addWidget(self.cb_a)
        layout.addLayout(h_a)

        # Tab B combo
        h_b = QHBoxLayout()
        lbl_b = QLabel("🟢 Revize Belge (B):")
        lbl_b.setFixedWidth(140)
        self.cb_b = QComboBox()
        for idx, name, _ in self.open_tabs:
            self.cb_b.addItem(f"{idx+1}. {name}", idx)
        if 0 <= self.selected_b_idx < len(self.open_tabs):
            self.cb_b.setCurrentIndex(self.selected_b_idx)
        h_b.addWidget(lbl_b)
        h_b.addWidget(self.cb_b)
        layout.addLayout(h_b)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_compare = QPushButton("⚖️ Yan Yana Karşılaştır")
        btn_compare.setObjectName("accentButton")
        btn_compare.clicked.connect(self._on_compare)
        btn_layout.addWidget(btn_compare)

        layout.addLayout(btn_layout)

    def _on_compare(self):
        self.selected_a_idx = self.cb_a.currentData()
        self.selected_b_idx = self.cb_b.currentData()
        if self.selected_a_idx == self.selected_b_idx:
            QMessageBox.warning(self, "Uyarı", "Lütfen karşılaştırmak için iki farklı belge seçin.")
            return
        self.accept()


class MainWindow(QMainWindow):
    """NextGen Studio Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeNgi PDF")
        self.resize(1340, 860)
        self.is_dark_mode = True
        self.recent_files: List[str] = []
        self.tray_agent = None
        self._is_running_ocr = False

        self._pending_merge_files: List[str] = []
        self._merge_debounce_timer = QTimer(self)
        self._merge_debounce_timer.setSingleShot(True)
        self._merge_debounce_timer.timeout.connect(self._flush_pending_merge_files)

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "resources", "app_icon.png")
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, "resources", "app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._init_ui()
        self.apply_theme(DARK_THEME)

    def _init_ui(self):
        root_widget = QWidget()
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Global Header Bar
        header = self._create_header()
        root_layout.addWidget(header, 0)

        # 2. Main Central Splitter (Left Rail + Center Canvas + Right Copilot)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)

        # 2a. Left Navigation Rail
        self.nav_rail = NavigationRail()
        self.nav_rail.nav_changed.connect(self._on_nav_rail_action)
        self.main_splitter.addWidget(self.nav_rail)

        # 2b. Central Canvas (Tabs + Floating Pill Toolbar)
        self.canvas_widget = self._create_canvas()
        self.main_splitter.addWidget(self.canvas_widget)

        # 2c. Right Copilot Panel
        self.copilot_panel = CopilotPanel()
        self.copilot_panel.closed.connect(lambda: self.copilot_panel.setVisible(False))
        self.copilot_panel.action_triggered.connect(self._on_copilot_action)
        self.copilot_panel.query_submitted.connect(self._on_copilot_query)
        self.main_splitter.addWidget(self.copilot_panel)

        self.main_splitter.setSizes([220, 820, 300])
        root_layout.addWidget(self.main_splitter, 1)

        # 3. Bottom Footer (Pagination & Zoom)
        footer = self._create_footer()
        root_layout.addWidget(footer, 0)

        self.setCentralWidget(root_widget)

        # Keyboard shortcuts
        self._setup_shortcuts()

    def _create_header(self) -> QFrame:
        """Creates top search & quick action header bar."""
        header = QFrame()
        header.setObjectName("topHeader")
        header.setFixedHeight(52)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 6, 16, 6)
        h_layout.setSpacing(12)

        # Center search pill
        h_layout.addSpacing(220) # Align with rail width
        self.txt_search = QLineEdit()
        self.txt_search.setObjectName("searchBox")
        self.txt_search.setPlaceholderText("Belgelerde veya metinlerde ara... (Enter)")
        self.txt_search.returnPressed.connect(self._on_search_triggered)
        h_layout.addWidget(self.txt_search, 1)

        # Undo & Redo buttons
        self.btn_undo = QPushButton()
        self.btn_undo.setIcon(get_svg_icon("undo", "#D0D4DC", 16))
        self.btn_undo.setIconSize(QSize(16, 16))
        self.btn_undo.setFixedSize(34, 34)
        self.btn_undo.setToolTip("Geri Al (Ctrl+Z)")
        self.btn_undo.clicked.connect(self.undo_current)
        h_layout.addWidget(self.btn_undo)

        self.btn_redo = QPushButton()
        self.btn_redo.setIcon(get_svg_icon("redo", "#D0D4DC", 16))
        self.btn_redo.setIconSize(QSize(16, 16))
        self.btn_redo.setFixedSize(34, 34)
        self.btn_redo.setToolTip("Yinele (Ctrl+Y)")
        self.btn_redo.clicked.connect(self.redo_current)
        h_layout.addWidget(self.btn_redo)

        # Right quick action buttons with SVG icons
        self.btn_print = QPushButton("  Yazdır")
        self.btn_print.setIcon(get_svg_icon("print", "#D0D4DC", 16))
        self.btn_print.setIconSize(QSize(16, 16))
        self.btn_print.setToolTip("Belgeyi Yazdır veya PDF Yap (Ctrl+P)")
        self.btn_print.clicked.connect(self.print_current_document)
        h_layout.addWidget(self.btn_print)

        self.btn_save = QPushButton("  Kaydet")
        self.btn_save.setIcon(get_svg_icon("save", "#D0D4DC", 16))
        self.btn_save.setIconSize(QSize(16, 16))
        self.btn_save.setToolTip("Değişiklikleri Kaydet (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_current_file)
        h_layout.addWidget(self.btn_save)

        self.btn_theme = QPushButton()
        self.btn_theme.setIcon(get_svg_icon("theme", "#D0D4DC", 18))
        self.btn_theme.setIconSize(QSize(18, 18))
        self.btn_theme.setFixedSize(36, 36)
        self.btn_theme.setToolTip("Koyu / Açık Tema Değiştir")
        self.btn_theme.clicked.connect(self._toggle_theme)
        h_layout.addWidget(self.btn_theme)

        # Tools Panel Toggle Button (No Copilot / No AI)
        self.btn_toggle_copilot = QPushButton("  Araçlar")
        self.btn_toggle_copilot.setIcon(get_svg_icon("panel", "#D0D4DC", 16))
        self.btn_toggle_copilot.setIconSize(QSize(16, 16))
        self.btn_toggle_copilot.setCheckable(True)
        self.btn_toggle_copilot.setChecked(True)
        self.btn_toggle_copilot.setStyleSheet("font-weight: 600; padding: 6px 14px;")
        self.btn_toggle_copilot.clicked.connect(self._toggle_copilot_panel)
        h_layout.addWidget(self.btn_toggle_copilot)

        # User Badge
        badge_user = QLabel("Standart Plan")
        badge_user.setStyleSheet(
            "background-color: #24272D; border: 1px solid #353942; border-radius: 14px; padding: 5px 12px; color: #A0A5AD; font-size: 11.5px; font-weight: 500;"
        )
        h_layout.addWidget(badge_user)

        return header

    def _create_canvas(self) -> QWidget:
        """Creates central canvas with document tabs and floating pill toolbar."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        # Splitter between thumbnails sidebar and tabs
        self.doc_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.doc_splitter.setHandleWidth(1)

        # Thumbnails Bar (Collapsible / hidden by default for clean look)
        self.thumbnail_bar = ThumbnailBar()
        self.thumbnail_bar.setVisible(False)
        self.thumbnail_bar.page_selected.connect(self._on_thumbnail_page_selected)
        self.thumbnail_bar.pages_modified.connect(self._on_pages_modified)
        self.doc_splitter.addWidget(self.thumbnail_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)
        self.doc_splitter.addWidget(self.tabs)

        self.doc_splitter.setSizes([0, 820])
        layout.addWidget(self.doc_splitter, 1)

        # Floating Bottom Pill Toolbar (Centered capsule island)
        pill_container = QHBoxLayout()
        pill_container.setContentsMargins(0, 0, 0, 2)
        pill_container.addStretch()

        self.floating_toolbar = FloatingPillToolbar()
        self.floating_toolbar.tool_changed.connect(self._on_floating_tool_changed)
        pill_container.addWidget(self.floating_toolbar)

        pill_container.addStretch()
        layout.addLayout(pill_container)

        return container

    def _create_footer(self) -> QFrame:
        """Creates bottom pagination and zoom footer."""
        footer = QFrame()
        footer.setObjectName("bottomFooter")
        footer.setFixedHeight(38)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(16, 4, 16, 4)
        f_layout.setSpacing(12)

        # Left: Page Stepper with SVG icons
        self.btn_prev = QPushButton()
        self.btn_prev.setIcon(get_svg_icon("prev", "#D0D4DC", 14))
        self.btn_prev.setIconSize(QSize(14, 14))
        self.btn_prev.setFixedSize(28, 26)
        self.btn_prev.setToolTip("Önceki Sayfa")
        self.btn_prev.clicked.connect(self._prev_page)
        f_layout.addWidget(self.btn_prev)

        self.lbl_footer_page = QLabel("Sayfa: - / -")
        self.lbl_footer_page.setStyleSheet("padding: 0 4px; font-weight: 500;")
        f_layout.addWidget(self.lbl_footer_page)

        self.btn_next = QPushButton()
        self.btn_next.setIcon(get_svg_icon("next", "#D0D4DC", 14))
        self.btn_next.setIconSize(QSize(14, 14))
        self.btn_next.setFixedSize(28, 26)
        self.btn_next.setToolTip("Sonraki Sayfa")
        self.btn_next.clicked.connect(self._next_page)
        f_layout.addWidget(self.btn_next)

        # Center Status Message
        self.lbl_footer_status = QLabel("Hazır")
        self.lbl_footer_status.setStyleSheet("color: #727883; margin-left: 20px;")
        f_layout.addWidget(self.lbl_footer_status, 1)

        # Right: Zoom & View controls with SVG icons
        self.btn_zoom_out = QPushButton()
        self.btn_zoom_out.setIcon(get_svg_icon("zoom_out", "#D0D4DC", 14))
        self.btn_zoom_out.setIconSize(QSize(14, 14))
        self.btn_zoom_out.setFixedSize(28, 26)
        self.btn_zoom_out.setToolTip("Uzaklaştır")
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        f_layout.addWidget(self.btn_zoom_out)

        self.lbl_footer_zoom = QLabel("%120")
        self.lbl_footer_zoom.setStyleSheet("font-weight: 600; min-width: 44px; text-align: center;")
        f_layout.addWidget(self.lbl_footer_zoom)

        self.btn_zoom_in = QPushButton()
        self.btn_zoom_in.setIcon(get_svg_icon("zoom_in", "#D0D4DC", 14))
        self.btn_zoom_in.setIconSize(QSize(14, 14))
        self.btn_zoom_in.setFixedSize(28, 26)
        self.btn_zoom_in.setToolTip("Yakınlaştır")
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        f_layout.addWidget(self.btn_zoom_in)

        # Thumbnails toggle with SVG icon
        self.btn_thumbs = QPushButton()
        self.btn_thumbs.setIcon(get_svg_icon("thumbnails", "#D0D4DC", 16))
        self.btn_thumbs.setIconSize(QSize(16, 16))
        self.btn_thumbs.setFixedSize(30, 26)
        self.btn_thumbs.setToolTip("Sayfa Küçük Resimleri Panelini Aç / Kapat")
        self.btn_thumbs.clicked.connect(self._toggle_thumbnails)
        f_layout.addWidget(self.btn_thumbs)

        return footer

    def _setup_shortcuts(self):
        """Registers keyboard shortcuts."""
        # Open
        act_open = QAction(self)
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self.open_file_dialog)
        self.addAction(act_open)

        # Save
        act_save = QAction(self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_current_file)
        self.addAction(act_save)

        # Print
        act_print = QAction(self)
        act_print.setShortcut(QKeySequence("Ctrl+P"))
        act_print.triggered.connect(self.print_current_document)
        self.addAction(act_print)

        # Undo
        act_undo = QAction(self)
        act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        act_undo.triggered.connect(self.undo_current)
        self.addAction(act_undo)

        # Redo
        act_redo = QAction(self)
        act_redo.setShortcut(QKeySequence("Ctrl+Y"))
        act_redo.triggered.connect(self.redo_current)
        self.addAction(act_redo)

    # ==========================================
    # Navigation & Interaction Handlers
    # ==========================================

    def _on_nav_rail_action(self, key: str):
        if key == "home" or key == "documents":
            self.open_file_dialog()
        elif key == "recent":
            self._show_recent_files_menu()
        elif key == "diff":
            if self.tabs.count() >= 2:
                self.compare_open_tabs()
            else:
                self.open_diff_dialog()
        elif key == "tools":
            self._toggle_copilot_panel()
        elif key == "settings":
            self._open_settings_dialog()

    def _on_floating_tool_changed(self, tool_id: str):
        if tool_id in ["view", "text", "whiteout"]:
            self._set_viewer_tool(tool_id)
        elif tool_id == "edit_text":
            self._edit_selected_text_trigger()
        elif tool_id == "signature":
            self._open_signature_dialog()
        elif tool_id == "rotate":
            self._rotate_current_page()
        elif tool_id == "pages":
            self._open_page_manager()
        elif tool_id == "undo":
            self.undo_current()
        elif tool_id == "redo":
            self.redo_current()

    def _toggle_copilot_panel(self):
        is_vis = not self.copilot_panel.isVisible()
        self.copilot_panel.setVisible(is_vis)
        self.btn_toggle_copilot.setChecked(is_vis)

    def _toggle_thumbnails(self):
        is_vis = not self.thumbnail_bar.isVisible()
        self.thumbnail_bar.setVisible(is_vis)
        self.doc_splitter.setSizes([160 if is_vis else 0, 800])

    def _show_recent_files_menu(self):
        if not self.recent_files:
            QMessageBox.information(self, "Son Dosyalar", "Henüz açılmış bir son dosya geçmişi yok.")
            return
        menu = QMenu(self)
        for f in self.recent_files[:10]:
            act = menu.addAction(f"📄 {os.path.basename(f)}")
            act.triggered.connect(lambda checked, path=f: self.open_pdf(path))
        menu.exec(self.nav_rail.mapToGlobal(QPoint(220, 100)))

    def _on_copilot_action(self, action_key: str):
        if action_key == "merge":
            self.open_merge_dialog()
            return
        elif action_key == "diff":
            self.compare_open_tabs()
            return

        doc = self.get_current_doc()
        viewer = self.get_current_viewer()
        if not doc or not doc.is_open:
            self.copilot_panel.add_message("Lütfen önce işlem yapılacak bir PDF açın.")
            return

        curr_page = viewer.current_page_idx if viewer else 0

        if action_key == "summarize":
            words = doc.get_page_text_words(curr_page)
            text = " ".join(w[4] for w in words)
            if text:
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(text)
                self.copilot_panel.add_message(
                    f"✅ Sayfa {curr_page+1} metinleri kopyalandı ({len(words)} kelime):\n\n\"{text[:200]}...\""
                )
            else:
                self.copilot_panel.add_message("Bu sayfada seçilebilir metin bulunamadı. OCR çalıştırmayı deneyin.")
        elif action_key == "ocr":
            self.copilot_panel.add_message("🔍 OCR metin taraması başlatılıyor...")
            self._run_ocr_trigger()
        elif action_key == "protect":
            self._encrypt_current_doc()

    def _on_copilot_query(self, query: str):
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            self.copilot_panel.add_message("Arama yapabilmek için lütfen bir belge açın.")
            return

        # Simple fast keyword lookup across document pages
        matches = []
        q_lower = query.lower()
        for idx in range(doc.page_count):
            txt = doc.get_page(idx).get_text("text").lower()
            if q_lower in txt:
                matches.append(idx + 1)

        if matches:
            pages_str = ", ".join(str(p) for p in matches[:8])
            self.copilot_panel.add_message(
                f"🔎 '{query}' ifadesi şu sayfalarda bulundu: Sayfa {pages_str}"
            )
            viewer = self.get_current_viewer()
            if viewer and matches:
                viewer.go_to_page(matches[0] - 1)
        else:
            self.copilot_panel.add_message(f"'{query}' belgede bulunamadı.")

    def _on_search_triggered(self):
        query = self.txt_search.text().strip()
        if query:
            self._on_copilot_query(query)

    # ==========================================
    # Document & Tab Management
    # ==========================================

    def get_current_viewer(self) -> Optional[PDFViewer]:
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, PDFViewer):
            return current_widget
        return None

    def get_current_doc(self) -> Optional[PDFDocument]:
        viewer = self.get_current_viewer()
        return viewer.doc if viewer else None

    def open_file_dialog(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "PDF Dosyası Aç", "", "PDF Dosyaları (*.pdf);;Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_paths:
            for f in file_paths:
                self.open_pdf(f)

    def print_current_document(self):
        doc = self.get_current_doc()
        viewer = self.get_current_viewer()
        if not doc or not doc.is_open:
            QMessageBox.information(self, "Bilgi", "Lütfen önce yazdırılacak bir PDF açın.")
            return
        curr_page = viewer.current_page_idx if viewer else 0
        PDFPrinter.print_document(doc, parent=self, current_page=curr_page)

    def undo_current(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.undo()
            self._update_footer_page_info()

    def redo_current(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.redo()
            self._update_footer_page_info()

    def open_merge_dialog(self, files: Optional[List[str]] = None):
        try:
            dlg = MergeFilesDialog(initial_files=files, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.output_pdf_path:
                self.open_pdf(dlg.output_pdf_path)
        except Exception as e:
            print(f"Error opening merge dialog: {e}")

    def _flush_pending_merge_files(self):
        if self._pending_merge_files:
            files_to_merge = list(self._pending_merge_files)
            self._pending_merge_files.clear()
            self.open_merge_dialog(files_to_merge)

    def convert_file_to_pdf(self, file_path: str):
        if not os.path.exists(file_path):
            return
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            self.open_pdf(file_path)
            return

        target_pdf = os.path.splitext(file_path)[0] + ".pdf"
        try:
            doc = fitz.open(file_path)
            pdf_bytes = doc.convert_to_pdf()
            doc.close()
            with open(target_pdf, "wb") as f:
                f.write(pdf_bytes)
            self.open_pdf(target_pdf)
            self.show_status_message(f"PDF'e dönüştürüldü ve açıldı: {os.path.basename(target_pdf)}")
        except Exception as e:
            QMessageBox.critical(self, "Dönüştürme Hatası", f"Dosya PDF'e dönüştürülemedi:\n{e}")

    def handle_external_file(self, raw_arg: str):
        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

        if not raw_arg:
            return

        clean_arg = raw_arg.strip()
        import shlex
        try:
            tokens = shlex.split(clean_arg)
        except Exception:
            tokens = clean_arg.split()

        if not tokens:
            return

        cmd = tokens[0]
        if cmd == "--merge":
            files = [f.strip().strip('"').strip("'") for f in tokens[1:] if f.strip()]
            for f in files:
                if f and os.path.exists(f) and f not in self._pending_merge_files:
                    self._pending_merge_files.append(f)
            # Debounce timer to aggregate rapid multi-file right-click selections from Windows
            self._merge_debounce_timer.start(250)
        elif cmd == "--convert":
            file_to_conv = " ".join(tokens[1:]).strip().strip('"').strip("'") if len(tokens) > 1 else ""
            if os.path.exists(file_to_conv):
                self.convert_file_to_pdf(file_to_conv)
        elif cmd == "--print":
            file_to_print = " ".join(tokens[1:]).strip().strip('"').strip("'") if len(tokens) > 1 else ""
            if os.path.exists(file_to_print):
                self.open_pdf(file_to_print)
                self.print_current_document()
        else:
            path = clean_arg.strip('"').strip("'")
            if os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                if ext == ".pdf":
                    self.open_pdf(path)
                elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
                    self.convert_file_to_pdf(path)

        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_pdf(self, file_path: str):
        # Check if already open
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, PDFViewer) and w.doc and w.doc.file_path == file_path:
                self.tabs.setCurrentIndex(i)
                self.show_status_message(f"'{os.path.basename(file_path)}' sekmesine geçildi.")
                return

        doc = PDFDocument()
        is_ok = doc.open(file_path)
        
        if doc.is_encrypted and not is_ok:
            dlg = PasswordDialog(mode="decrypt", parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.password:
                if not doc.authenticate(dlg.password):
                    QMessageBox.critical(self, "Hata", "Hatalı parola girdiniz.")
                    return
            else:
                return

        viewer = PDFViewer(doc=doc, parent=self)
        viewer.page_changed.connect(self._on_page_changed)
        viewer.document_modified.connect(self._on_document_modified)
        viewer.status_message.connect(self.show_status_message)

        tab_title = os.path.basename(file_path) if file_path else "Yeni Belge"
        idx = self.tabs.addTab(viewer, tab_title)
        self.tabs.setCurrentIndex(idx)

        # Track recent files
        if file_path and file_path not in self.recent_files:
            self.recent_files.insert(0, file_path)

        self.thumbnail_bar.load_document(doc)
        self._update_footer_page_info()
        self.show_status_message(f"Açıldı: {tab_title}")

    def save_current_file(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.commit_pending_edits()
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
        if not doc.file_path:
            self.save_current_file_as()
            return
        if doc.save():
            self.show_status_message(f"Kaydedildi: {os.path.basename(doc.file_path)}")
        else:
            self.save_current_file_as()

    def save_current_file_as(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.commit_pending_edits()
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
        suggested = os.path.basename(doc.file_path) if doc.file_path else "Belge.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Farklı Kaydet", suggested, "PDF Dosyaları (*.pdf)")
        if file_path:
            if doc.save(file_path):
                curr_idx = self.tabs.currentIndex()
                self.tabs.setTabText(curr_idx, os.path.basename(file_path))
                self.show_status_message(f"Farklı kaydedildi: {os.path.basename(file_path)}")

    def _close_tab(self, index: int):
        widget = self.tabs.widget(index)
        if isinstance(widget, PDFViewer) and widget.doc and widget.doc.is_modified:
            reply = QMessageBox.question(
                self, "Kaydedilmemiş Değişiklikler",
                "Bu belgede kaydedilmemiş değişiklikler var. Kapatmadan önce kaydetmek istiyor musunuz?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.save_current_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        if isinstance(widget, PDFViewer) and widget.doc:
            widget.doc.close()

        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.thumbnail_bar.clear()
            self._update_footer_page_info()

    def _on_tab_changed(self, index: int):
        doc = self.get_current_doc()
        if doc and doc.is_open:
            self.thumbnail_bar.load_document(doc)
        else:
            self.thumbnail_bar.clear()
        self._update_footer_page_info()

    def _update_footer_page_info(self):
        doc = self.get_current_doc()
        viewer = self.get_current_viewer()
        if doc and doc.is_open and viewer:
            curr = viewer.current_page_idx + 1
            tot = doc.page_count
            self.lbl_footer_page.setText(f"Sayfa {curr} / {tot}")
            self.lbl_footer_zoom.setText(f"%{int(viewer.zoom * 100)}")
            self.thumbnail_bar.set_active_page(viewer.current_page_idx)
        else:
            self.lbl_footer_page.setText("Sayfa: - / -")
            self.lbl_footer_zoom.setText("%100")

    def _prev_page(self):
        viewer = self.get_current_viewer()
        if viewer and viewer.current_page_idx > 0:
            viewer.go_to_page(viewer.current_page_idx - 1)

    def _next_page(self):
        viewer = self.get_current_viewer()
        doc = self.get_current_doc()
        if viewer and doc and viewer.current_page_idx < doc.page_count - 1:
            viewer.go_to_page(viewer.current_page_idx + 1)

    def _zoom_in(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.zoom_in()
            self.lbl_footer_zoom.setText(f"%{int(viewer.zoom * 100)}")

    def _zoom_out(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.zoom_out()
            self.lbl_footer_zoom.setText(f"%{int(viewer.zoom * 100)}")

    def _on_page_changed(self, page_idx: int):
        self._update_footer_page_info()

    def _on_document_modified(self):
        curr_idx = self.tabs.currentIndex()
        doc = self.get_current_doc()
        if doc:
            base = os.path.basename(doc.file_path) if doc.file_path else "Yeni Belge"
            self.tabs.setTabText(curr_idx, f"*{base}")
            self.thumbnail_bar.load_document(doc)

    def _on_thumbnail_page_selected(self, page_idx: int):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.go_to_page(page_idx)

    def _on_pages_modified(self):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.refresh_all_pages()
        self._on_document_modified()

    def show_status_message(self, message: str):
        self.lbl_footer_status.setText(message)

    # ==========================================
    # Tools, Editing, DIFF & OCR
    # ==========================================

    def _set_viewer_tool(self, tool_name: str):
        viewer = self.get_current_viewer()
        if viewer:
            viewer.set_tool(tool_name)
        self.floating_toolbar.set_active_tool(tool_name)

    def _edit_selected_text_trigger(self):
        viewer = self.get_current_viewer()
        if viewer and viewer.page_widgets:
            curr_pw = viewer.page_widgets[viewer.current_page_idx]
            curr_pw.prompt_edit_selected_text()

    def _run_ocr_trigger(self):
        if self._is_running_ocr:
            return
        self._is_running_ocr = True
        try:
            viewer = self.get_current_viewer()
            if viewer:
                viewer.run_ocr(viewer.current_page_idx)
        finally:
            self._is_running_ocr = False

    def _rotate_current_page(self):
        doc = self.get_current_doc()
        viewer = self.get_current_viewer()
        if doc and viewer:
            doc.rotate_page(viewer.current_page_idx, 90)
            viewer.refresh_page(viewer.current_page_idx)
            self._on_document_modified()

    def _open_page_manager(self):
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
        dlg = PageManagerDialog(doc, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            viewer = self.get_current_viewer()
            if viewer:
                viewer.refresh_all_pages()
            self._on_document_modified()

    def _open_signature_dialog(self):
        dlg = SignatureDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            sig_path = getattr(dlg, "signature_path", None) or getattr(dlg, "saved_signature_path", None)
            if sig_path and os.path.exists(sig_path):
                viewer = self.get_current_viewer()
                if viewer:
                    viewer.set_stamp_image(sig_path)
                    self.show_status_message("İmzayı yerleştirmek için sayfada istediğiniz yere tıklayın.")

    def _encrypt_current_doc(self):
        doc = self.get_current_doc()
        if not doc or not doc.is_open:
            return
        dlg = PasswordDialog(mode="encrypt", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.password:
            out_path, _ = QFileDialog.getSaveFileName(self, "Şifrelenmiş PDF'i Kaydet", "Sifreli_Belge.pdf", "PDF Dosyaları (*.pdf)")
            if out_path:
                SecurityManager.encrypt_pdf(doc, dlg.password, out_path)
                self.show_status_message(f"Belge parola ile şifrelendi: {os.path.basename(out_path)}")

    def _show_tab_context_menu(self, pos: QPoint):
        tab_idx = self.tabs.tabBar().tabAt(pos)
        if tab_idx < 0:
            return
        menu = QMenu(self)
        act_compare = menu.addAction("⚖️ Açık Sekmeleri Karşılaştır (DIFF)")
        act_close = menu.addAction("Kapat")
        act = menu.exec(self.tabs.tabBar().mapToGlobal(pos))
        if act == act_compare:
            self.compare_open_tabs()
        elif act == act_close:
            self._close_tab(tab_idx)

    def compare_open_tabs(self):
        open_tabs: List[Tuple[int, str, PDFDocument]] = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, PDFViewer) and w.doc and w.doc.is_open:
                name = os.path.basename(w.doc.file_path) if w.doc.file_path else f"Sekme {i+1}"
                open_tabs.append((i, name, w.doc))

        if len(open_tabs) < 2:
            QMessageBox.information(
                self, "Bilgi", 
                "Karşılaştırma (DIFF) yapabilmek için en az 2 PDF sekmesinin açık olması gerekir.\n\n"
                "İki farklı dosyayı karşılaştırmak için 'İki Dosya Seçip Karşılaştır' seçeneğini kullanabilirsiniz."
            )
            return

        if len(open_tabs) == 2:
            self._launch_diff(open_tabs[0][2], open_tabs[1][2], open_tabs[0][1], open_tabs[1][1])
            return

        dlg = OpenTabsDiffDialog(open_tabs, default_a=0, default_b=1, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            idx_a = dlg.selected_a_idx
            idx_b = dlg.selected_b_idx
            self._launch_diff(open_tabs[idx_a][2], open_tabs[idx_b][2], open_tabs[idx_a][1], open_tabs[idx_b][1])

    def _launch_diff(self, doc_a: PDFDocument, doc_b: PDFDocument, name_a: str, name_b: str):
        diff_view = DiffView(doc_a, doc_b, parent=self)
        diff_tab_idx = self.tabs.addTab(diff_view, f"⚖️ DIFF: {name_a} vs {name_b}")
        self.tabs.setCurrentIndex(diff_tab_idx)

    def open_diff_dialog(self):
        f_a, _ = QFileDialog.getOpenFileName(self, "Orijinal PDF'i Seçin (A)", "", "PDF Dosyaları (*.pdf)")
        if not f_a:
            return
        f_b, _ = QFileDialog.getOpenFileName(self, "Revize PDF'i Seçin (B)", "", "PDF Dosyaları (*.pdf)")
        if not f_b:
            return

        doc_a = PDFDocument(f_a)
        doc_b = PDFDocument(f_b)
        diff_view = DiffView(doc_a, doc_b, parent=self)
        idx = self.tabs.addTab(diff_view, f"⚖️ DIFF: {os.path.basename(f_a)} vs {os.path.basename(f_b)}")
        self.tabs.setCurrentIndex(idx)

    def _open_settings_dialog(self):
        dlg = SettingsDialog(current_is_dark=self.is_dark_mode, parent=self)
        dlg.theme_changed.connect(self._on_settings_theme_changed)
        dlg.exec()

    def _on_settings_theme_changed(self, theme_name: str):
        self.is_dark_mode = (theme_name == "dark")
        self.apply_theme(DARK_THEME if self.is_dark_mode else LIGHT_THEME)

    def _toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme(DARK_THEME if self.is_dark_mode else LIGHT_THEME)

    def apply_theme(self, stylesheet: str):
        self.setStyleSheet(stylesheet)
        self.update_theme_icons(self.is_dark_mode)

    def update_theme_icons(self, is_dark: bool):
        """Updates all SVG icon colors across the interface to contrast with current theme."""
        icon_color = "#D0D4DC" if is_dark else "#374151"

        if hasattr(self, "btn_undo"):
            self.btn_undo.setIcon(get_svg_icon("undo", icon_color, 16))
        if hasattr(self, "btn_redo"):
            self.btn_redo.setIcon(get_svg_icon("redo", icon_color, 16))
        if hasattr(self, "btn_print"):
            self.btn_print.setIcon(get_svg_icon("print", icon_color, 16))
        if hasattr(self, "btn_save"):
            self.btn_save.setIcon(get_svg_icon("save", icon_color, 16))
        if hasattr(self, "btn_theme"):
            self.btn_theme.setIcon(get_svg_icon("theme", icon_color, 18))
        if hasattr(self, "btn_toggle_copilot"):
            self.btn_toggle_copilot.setIcon(get_svg_icon("panel", icon_color, 16))

        if hasattr(self, "btn_prev"):
            self.btn_prev.setIcon(get_svg_icon("prev", icon_color, 14))
        if hasattr(self, "btn_next"):
            self.btn_next.setIcon(get_svg_icon("next", icon_color, 14))
        if hasattr(self, "btn_zoom_out"):
            self.btn_zoom_out.setIcon(get_svg_icon("zoom_out", icon_color, 14))
        if hasattr(self, "btn_zoom_in"):
            self.btn_zoom_in.setIcon(get_svg_icon("zoom_in", icon_color, 14))
        if hasattr(self, "btn_thumbs"):
            self.btn_thumbs.setIcon(get_svg_icon("thumbnails", icon_color, 16))

        if hasattr(self, "nav_rail") and hasattr(self.nav_rail, "update_theme"):
            self.nav_rail.update_theme(is_dark)
        if hasattr(self, "floating_toolbar") and hasattr(self.floating_toolbar, "update_theme"):
            self.floating_toolbar.update_theme(is_dark)
        if hasattr(self, "copilot_panel") and hasattr(self.copilot_panel, "update_theme"):
            self.copilot_panel.update_theme(is_dark)

    def closeEvent(self, event):
        """Minimizes to system tray if tray agent is attached."""
        if hasattr(self, "tray_agent") and self.tray_agent:
            self.tray_agent.handle_window_close(event)
        else:
            event.accept()
