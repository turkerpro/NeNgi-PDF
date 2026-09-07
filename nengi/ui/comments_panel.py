from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QFrame, QPushButton, QComboBox, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .icons import get_svg_icon
from .styles import DARK_THEME, LIGHT_THEME

class CommentWidget(QFrame):
    clicked = pyqtSignal(object) # Emit the annotation dict/object
    status_changed = pyqtSignal(object, str)
    
    def __init__(self, annot_info, is_dark=False):
        super().__init__()
        self.annot_info = annot_info
        self.is_dark = is_dark
        self._setup_ui()
        self.update_theme(is_dark)
        
    def _setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        header = QHBoxLayout()
        icon_lbl = QLabel()
        # For simplicity, use a comment icon
        color = "#D0D4DC" if self.is_dark else "#475569"
        icon_lbl.setPixmap(get_svg_icon("comments", color).pixmap(16, 16))
        
        author = self.annot_info.get("info", {}).get("title", "Bilinmeyen")
        author_lbl = QLabel(author)
        author_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        page_lbl = QLabel(f"Sayfa {self.annot_info.get('page', 0) + 1}")
        page_lbl.setStyleSheet("color: gray; font-size: 10px;")
        
        header.addWidget(icon_lbl)
        header.addWidget(author_lbl)
        header.addStretch()
        header.addWidget(page_lbl)
        layout.addLayout(header)
        
        content = self.annot_info.get("info", {}).get("content", "")
        if not content:
            content = f"[{self.annot_info.get('type', 'Annotation')}]"
            
        content_lbl = QLabel(content)
        content_lbl.setWordWrap(True)
        layout.addWidget(content_lbl)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.annot_info)
        super().mousePressEvent(event)
        
    def _show_context_menu(self, pos):
        menu = QMenu(self)
        statuses = ["Yok", "Kabul Edildi", "Reddedildi", "Tamamlandı"]
        for s in statuses:
            action = menu.addAction(s)
            action.triggered.connect(lambda checked, st=s: self.status_changed.emit(self.annot_info, st))
        menu.exec(self.mapToGlobal(pos))
        
    def update_theme(self, is_dark):
        self.is_dark = is_dark
        bg = "#26292E" if is_dark else "#F8FAFC"
        border = "#383C44" if is_dark else "#E2E8F0"
        hover = "#30343B" if is_dark else "#EDF2F7"
        text = "#D0D4DC" if is_dark else "#1E293B"
        self.setStyleSheet(f"""
            CommentWidget {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                margin-bottom: 4px;
            }}
            CommentWidget:hover {{
                background-color: {hover};
            }}
            QLabel {{ color: {text}; border: none; }}
        """)

class CommentsPanel(QWidget):
    annotation_clicked = pyqtSignal(int, object) # page_idx, annot_info
    
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.all_annots = []
        self._setup_ui()
        self.update_theme(is_dark)
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Yorumlar ve Notlar")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        h_layout.addWidget(title)
        layout.addWidget(header)
        
        # Filter / Search
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(8, 0, 8, 0)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Yorumlarda ara...")
        self.search_box.textChanged.connect(self._filter_comments)
        filter_layout.addWidget(self.search_box)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tümü", "Vurgu", "Not", "Damga", "Çizim"])
        self.type_filter.currentTextChanged.connect(self._filter_comments)
        filter_layout.addWidget(self.type_filter)
        layout.addLayout(filter_layout)
        
        # Scroll area for comments
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        # Export btn
        export_btn = QPushButton("Özeti Dışa Aktar")
        layout.addWidget(export_btn)
        
    def load_annotations(self, annots):
        """Load annotations into the panel. annots is a list of dicts."""
        self.all_annots = annots
        self._refresh_list()
        
    def _refresh_list(self):
        # Clear existing
        for i in reversed(range(self.scroll_layout.count())): 
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
                
        search_text = self.search_box.text().lower()
        type_text = self.type_filter.currentText()
        
        for ann in self.all_annots:
            content = ann.get("info", {}).get("content", "").lower()
            if search_text and search_text not in content:
                continue
                
            ann_type = ann.get("type", "")
            # Simple type matching (would be more robust in real implementation)
            if type_text != "Tümü":
                if type_text == "Vurgu" and "Highlight" not in ann_type: continue
                if type_text == "Not" and "Text" not in ann_type: continue
                if type_text == "Damga" and "Stamp" not in ann_type: continue
                
            w = CommentWidget(ann, self.is_dark)
            w.clicked.connect(self._on_comment_clicked)
            w.status_changed.connect(self._on_status_changed)
            self.scroll_layout.addWidget(w)
            
    def _filter_comments(self):
        self._refresh_list()
        
    def _on_comment_clicked(self, ann):
        self.annotation_clicked.emit(ann.get("page", 0), ann)
        
    def _on_status_changed(self, ann, status):
        # Update annotation status logic here
        pass
        
    def update_theme(self, is_dark: bool):
        self.is_dark = is_dark
        bg = "#17181A" if is_dark else "#FFFFFF"
        bg_input = "#202226" if is_dark else "#F1F5F9"
        border = "#26292E" if is_dark else "#E2E8F0"
        text = "#D0D4DC" if is_dark else "#0F172A"
        
        self.setStyleSheet(f"""
            QWidget {{ background-color: {bg}; color: {text}; }}
            QLineEdit, QComboBox {{
                background-color: {bg_input};
                border: 1px solid {border};
                padding: 4px;
                border-radius: 4px;
                color: {text};
            }}
            QScrollArea {{ border: none; background: transparent; }}
        """)
        for i in range(self.scroll_layout.count()):
            w = self.scroll_layout.itemAt(i).widget()
            if isinstance(w, CommentWidget):
                w.update_theme(is_dark)
