"""
NeNgi PDF - Bookmarks Panel
Displays the PDF outline (table of contents).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QLabel, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt

from nengi.core.pdf_document import PDFDocument
from nengi.ui.icons import get_svg_icon


class BookmarksPanel(QWidget):
    page_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_svg_icon("bookmark").pixmap(20, 20))
        title_lbl = QLabel("📑 Yer İmleri")
        title_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        btn_expand = QPushButton("Genişlet")
        btn_expand.clicked.connect(self.expand_all)
        btn_collapse = QPushButton("Daralt")
        btn_collapse.clicked.connect(self.collapse_all)
        
        header_layout.addWidget(btn_expand)
        header_layout.addWidget(btn_collapse)
        
        layout.addLayout(header_layout)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def load_document(self, doc: PDFDocument):
        self.doc = doc
        self.tree.clear()
        
        if not self.doc or not self.doc.is_open:
            return
            
        toc = self.doc.doc.get_toc()
        if not toc:
            item = QTreeWidgetItem(["Yer imi bulunamadı."])
            self.tree.addTopLevelItem(item)
            return

        items = {}
        for level, title, page in toc:
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, page)
            
            if level == 1:
                self.tree.addTopLevelItem(item)
            else:
                parent = items.get(level - 1)
                if parent:
                    parent.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)
                    
            items[level] = item

    def expand_all(self):
        self.tree.expandAll()

    def collapse_all(self):
        self.tree.collapseAll()

    def _on_item_clicked(self, item, column):
        page = item.data(0, Qt.ItemDataRole.UserRole)
        if page is not None:
            # fitz toc pages are 1-indexed
            self.page_requested.emit(page - 1)

    def update_theme(self, is_dark: bool):
        bg = "#1A1D21" if is_dark else "#FFFFFF"
        fg = "#E0E0E0" if is_dark else "#2D2D2D"
        border = "#333333" if is_dark else "#E5E5E5"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
            }}
            QTreeWidget {{
                border: 1px solid {border};
                background-color: {bg};
                border-radius: 4px;
            }}
            QTreeWidget::item:hover {{
                background-color: {'#2D3239' if is_dark else '#F0F0F0'};
            }}
            QTreeWidget::item:selected {{
                background-color: #0078D7;
                color: white;
            }}
            QPushButton {{
                background-color: {'#2D3239' if is_dark else '#F0F0F0'};
                border: 1px solid {border};
                border-radius: 4px;
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {'#3D444D' if is_dark else '#E0E0E0'};
            }}
        """)
