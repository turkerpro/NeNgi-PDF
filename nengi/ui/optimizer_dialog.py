from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QPushButton, QGroupBox, QProgressBar
)

class OptimizerDialog(QDialog):
    def __init__(self, usage_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF'i Optimize Et")
        self.resize(350, 300)
        self.usage = usage_data or {}
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Usage Stats
        stat_group = QGroupBox("Mevcut Kullanım")
        s_layout = QVBoxLayout()
        
        tot = self.usage.get('total', 0)
        img = self.usage.get('images', 0)
        fnt = self.usage.get('fonts', 0)
        
        def fmt(sz):
            return f"{sz / 1024 / 1024:.2f} MB" if sz > 0 else "0 MB"
            
        s_layout.addWidget(QLabel(f"Toplam Boyut: {fmt(tot)}"))
        s_layout.addWidget(QLabel(f"Görseller: {fmt(img)}"))
        s_layout.addWidget(QLabel(f"Yazı Tipleri: {fmt(fnt)}"))
        stat_group.setLayout(s_layout)
        layout.addWidget(stat_group)
        
        # Options
        opt_group = QGroupBox("Seçenekler")
        o_layout = QVBoxLayout()
        self.chk_garbage = QCheckBox("Kullanılmayan nesneleri temizle (Garbage Collect)")
        self.chk_garbage.setChecked(True)
        self.chk_deflate = QCheckBox("Akışları sıkıştır (Deflate)")
        self.chk_deflate.setChecked(True)
        self.chk_linearize = QCheckBox("Hızlı web görünümü (Linearize)")
        self.chk_linearize.setChecked(True)
        self.chk_meta = QCheckBox("Üst veriyi (metadata) kaldır")
        
        o_layout.addWidget(self.chk_garbage)
        o_layout.addWidget(self.chk_deflate)
        o_layout.addWidget(self.chk_linearize)
        o_layout.addWidget(self.chk_meta)
        opt_group.setLayout(o_layout)
        layout.addWidget(opt_group)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Optimize Et")
        btn_cancel = QPushButton("İptal")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def get_config(self):
        return {
            'garbage_collect': self.chk_garbage.isChecked(),
            'deflate': self.chk_deflate.isChecked(),
            'linearize': self.chk_linearize.isChecked(),
            'remove_metadata': self.chk_meta.isChecked()
        }
