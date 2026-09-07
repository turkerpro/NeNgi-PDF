from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSpinBox, QPushButton, QGroupBox,
    QFileDialog, QLineEdit
)

class SplitDocumentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Belgeyi Böl")
        self.resize(400, 250)
        
        self.out_dir = ""
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Mode
        mode_group = QGroupBox("Bölme Yöntemi")
        m_layout = QVBoxLayout()
        
        hbox = QHBoxLayout()
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["Sayfa Sayısı", "Dosya Boyutu (MB)", "Yer İmlerine Göre"])
        hbox.addWidget(QLabel("Bölme Kriteri:"))
        hbox.addWidget(self.cb_mode)
        m_layout.addLayout(hbox)
        
        hbox2 = QHBoxLayout()
        self.sp_val = QSpinBox()
        self.sp_val.setRange(1, 1000)
        self.sp_val.setValue(1)
        hbox2.addWidget(QLabel("Değer:"))
        hbox2.addWidget(self.sp_val)
        m_layout.addLayout(hbox2)
        
        mode_group.setLayout(m_layout)
        layout.addWidget(mode_group)
        
        self.cb_mode.currentIndexChanged.connect(self._on_mode_changed)
        
        # Output
        out_group = QGroupBox("Çıktı")
        o_layout = QVBoxLayout()
        
        box1 = QHBoxLayout()
        self.btn_browse = QPushButton("Klasör Seç...")
        self.btn_browse.clicked.connect(self.browse_dir)
        self.lbl_dir = QLabel("Seçilmedi")
        box1.addWidget(self.btn_browse)
        box1.addWidget(self.lbl_dir)
        o_layout.addLayout(box1)
        
        box2 = QHBoxLayout()
        box2.addWidget(QLabel("Dosya Ön Eki:"))
        self.le_prefix = QLineEdit("bolunmus")
        box2.addWidget(self.le_prefix)
        o_layout.addLayout(box2)
        
        out_group.setLayout(o_layout)
        layout.addWidget(out_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Böl")
        btn_cancel = QPushButton("İptal")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def _on_mode_changed(self, idx):
        self.sp_val.setEnabled(idx != 2)
        
    def browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Çıktı Klasörü Seç")
        if d:
            self.out_dir = d
            self.lbl_dir.setText(d)
            
    def get_config(self):
        idx = self.cb_mode.currentIndex()
        if idx == 0:
            mode = 'page_count'
        elif idx == 1:
            mode = 'file_size'
        else:
            mode = 'bookmarks'
            
        return {
            'mode': mode,
            'value': self.sp_val.value(),
            'output_dir': self.out_dir,
            'prefix': self.le_prefix.text()
        }
