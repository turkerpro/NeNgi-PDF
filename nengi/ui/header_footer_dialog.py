from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QSpinBox, QPushButton, QGroupBox, QCheckBox, 
    QGridLayout, QColorDialog
)
from PyQt6.QtCore import Qt
from nengi.ui.icons import get_svg_icon

class HeaderFooterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Üstbilgi & Altbilgi Ekle")
        self.resize(600, 500)
        
        self.config = {}
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Macros
        macro_group = QGroupBox("Makrolar")
        macro_layout = QHBoxLayout()
        self.btn_page = QPushButton("Sayfa Numarası Ekle")
        self.btn_date = QPushButton("Tarih Ekle")
        macro_layout.addWidget(self.btn_page)
        macro_layout.addWidget(self.btn_date)
        macro_group.setLayout(macro_layout)
        layout.addWidget(macro_group)
        
        # Slots
        slots_group = QGroupBox("Metin Alanları")
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Sol Üstbilgi:"), 0, 0)
        self.le_top_left = QLineEdit()
        grid.addWidget(self.le_top_left, 0, 1)
        
        grid.addWidget(QLabel("Orta Üstbilgi:"), 0, 2)
        self.le_top_center = QLineEdit()
        grid.addWidget(self.le_top_center, 0, 3)
        
        grid.addWidget(QLabel("Sağ Üstbilgi:"), 0, 4)
        self.le_top_right = QLineEdit()
        grid.addWidget(self.le_top_right, 0, 5)
        
        grid.addWidget(QLabel("Sol Altbilgi:"), 1, 0)
        self.le_bottom_left = QLineEdit()
        grid.addWidget(self.le_bottom_left, 1, 1)
        
        grid.addWidget(QLabel("Orta Altbilgi:"), 1, 2)
        self.le_bottom_center = QLineEdit()
        grid.addWidget(self.le_bottom_center, 1, 3)
        
        grid.addWidget(QLabel("Sağ Altbilgi:"), 1, 4)
        self.le_bottom_right = QLineEdit()
        grid.addWidget(self.le_bottom_right, 1, 5)
        
        slots_group.setLayout(grid)
        layout.addWidget(slots_group)
        
        # Appearance
        app_group = QGroupBox("Görünüm ve Konum")
        app_layout = QHBoxLayout()
        
        self.cb_font = QComboBox()
        self.cb_font.addItems(["Helvetica", "Arial", "Times-Roman", "Courier"])
        app_layout.addWidget(QLabel("Yazı Tipi:"))
        app_layout.addWidget(self.cb_font)
        
        self.sp_size = QSpinBox()
        self.sp_size.setRange(6, 72)
        self.sp_size.setValue(10)
        app_layout.addWidget(QLabel("Boyut:"))
        app_layout.addWidget(self.sp_size)
        
        self.btn_color = QPushButton("Renk Seç")
        self.current_color = (0, 0, 0)
        self.btn_color.clicked.connect(self.choose_color)
        app_layout.addWidget(self.btn_color)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # Range
        range_group = QGroupBox("Sayfa Aralığı")
        r_layout = QHBoxLayout()
        self.cb_range = QComboBox()
        self.cb_range.addItems(["Tümü", "Tek Sayfalar", "Çift Sayfalar"])
        r_layout.addWidget(QLabel("Uygula:"))
        r_layout.addWidget(self.cb_range)
        range_group.setLayout(r_layout)
        layout.addWidget(range_group)
        
        # Options
        self.chk_shrink = QCheckBox("Belgenin metnini ve grafiklerini üzerine yazmamak için küçült")
        layout.addWidget(self.chk_shrink)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Uygula")
        btn_cancel = QPushButton("İptal")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        
        layout.addWidget(QLabel("Canlı önizleme için sayfa görünümüne bakın."))
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.btn_page.clicked.connect(lambda: self._insert_macro("Sayfa {page} / {total}"))
        self.btn_date.clicked.connect(lambda: self._insert_macro("GG/AA/YYYY"))
        
    def choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.current_color = (col.red()/255.0, col.green()/255.0, col.blue()/255.0)
            
    def _insert_macro(self, text):
        w = self.focusWidget()
        if isinstance(w, QLineEdit):
            w.setText(w.text() + " " + text)
            
    def get_config(self):
        rng = 'all'
        if self.cb_range.currentIndex() == 1: rng = 'odd'
        elif self.cb_range.currentIndex() == 2: rng = 'even'
        
        return {
            'slots': {
                'left_header': self.le_top_left.text(),
                'center_header': self.le_top_center.text(),
                'right_header': self.le_top_right.text(),
                'left_footer': self.le_bottom_left.text(),
                'center_footer': self.le_bottom_center.text(),
                'right_footer': self.le_bottom_right.text()
            },
            'font': self.cb_font.currentText(),
            'font_size': self.sp_size.value(),
            'color': self.current_color,
            'page_range': rng,
            'shrink_content': self.chk_shrink.isChecked(),
            'margins': {'top': 30, 'bottom': 30, 'left': 50, 'right': 50}
        }
