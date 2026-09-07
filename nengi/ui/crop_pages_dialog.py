from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QPushButton, QGroupBox
)
import pymupdf as fitz

class CropPagesDialog(QDialog):
    def __init__(self, current_rect=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sayfaları Kırp")
        self.resize(400, 300)
        
        self.rect = current_rect or fitz.Rect(0, 0, 595, 842)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Margins
        margin_group = QGroupBox("Kenar Boşlukları (Nokta)")
        m_layout = QHBoxLayout()
        
        self.sp_top = QSpinBox(); self.sp_top.setRange(0, 1000)
        self.sp_bottom = QSpinBox(); self.sp_bottom.setRange(0, 1000)
        self.sp_left = QSpinBox(); self.sp_left.setRange(0, 1000)
        self.sp_right = QSpinBox(); self.sp_right.setRange(0, 1000)
        
        m_layout.addWidget(QLabel("Üst:"))
        m_layout.addWidget(self.sp_top)
        m_layout.addWidget(QLabel("Alt:"))
        m_layout.addWidget(self.sp_bottom)
        margin_group.setLayout(m_layout)
        
        m_layout2 = QHBoxLayout()
        m_layout2.addWidget(QLabel("Sol:"))
        m_layout2.addWidget(self.sp_left)
        m_layout2.addWidget(QLabel("Sağ:"))
        m_layout2.addWidget(self.sp_right)
        
        layout.addWidget(margin_group)
        layout.addLayout(m_layout2)
        
        self.btn_auto = QPushButton("Beyaz Kenarları Otomatik Kaldır")
        layout.addWidget(self.btn_auto)
        
        # Options
        opt_group = QGroupBox("Seçenekler")
        o_layout = QVBoxLayout()
        
        box_l = QHBoxLayout()
        box_l.addWidget(QLabel("Kutu Tipi:"))
        self.cb_box = QComboBox()
        self.cb_box.addItems(["CropBox", "TrimBox", "BleedBox", "ArtBox"])
        box_l.addWidget(self.cb_box)
        o_layout.addLayout(box_l)
        
        rng_l = QHBoxLayout()
        rng_l.addWidget(QLabel("Sayfalar:"))
        self.cb_range = QComboBox()
        self.cb_range.addItems(["Geçerli Sayfa", "Tümü"])
        rng_l.addWidget(self.cb_range)
        o_layout.addLayout(rng_l)
        
        opt_group.setLayout(o_layout)
        layout.addWidget(opt_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Uygula")
        btn_cancel = QPushButton("İptal")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def get_config(self):
        # Calculate new rect
        x0 = self.rect.x0 + self.sp_left.value()
        y0 = self.rect.y0 + self.sp_top.value()
        x1 = self.rect.x1 - self.sp_right.value()
        y1 = self.rect.y1 - self.sp_bottom.value()
        
        return {
            'rect': fitz.Rect(x0, y0, x1, y1),
            'box_type': self.cb_box.currentText(),
            'page_range': 'all' if self.cb_range.currentIndex() == 1 else 'current'
        }
