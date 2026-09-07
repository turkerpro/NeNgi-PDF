from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QSpinBox, QSlider, QPushButton, QGroupBox, 
    QRadioButton, QFileDialog, QColorDialog
)
from PyQt6.QtCore import Qt
from nengi.ui.icons import get_svg_icon

class WatermarkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filigran Ekle")
        self.resize(500, 450)
        
        self.img_path = ""
        self.current_color = (0.5, 0.5, 0.5)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Source
        src_group = QGroupBox("Kaynak")
        src_layout = QVBoxLayout()
        
        self.rb_text = QRadioButton("Metin:")
        self.rb_text.setChecked(True)
        self.le_text = QLineEdit("Gizli")
        
        text_opts = QHBoxLayout()
        self.cb_font = QComboBox()
        self.cb_font.addItems(["Helvetica", "Arial", "Times-Roman"])
        self.sp_size = QSpinBox()
        self.sp_size.setRange(12, 144)
        self.sp_size.setValue(48)
        self.btn_color = QPushButton("Renk Seç")
        self.btn_color.clicked.connect(self.choose_color)
        text_opts.addWidget(self.cb_font)
        text_opts.addWidget(self.sp_size)
        text_opts.addWidget(self.btn_color)
        
        self.rb_img = QRadioButton("Görsel:")
        self.btn_browse = QPushButton("Gözat...")
        self.btn_browse.clicked.connect(self.browse_image)
        self.lbl_img_path = QLabel("Seçilmedi")
        
        src_layout.addWidget(self.rb_text)
        src_layout.addWidget(self.le_text)
        src_layout.addLayout(text_opts)
        src_layout.addWidget(self.rb_img)
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.btn_browse)
        img_layout.addWidget(self.lbl_img_path)
        src_layout.addLayout(img_layout)
        src_group.setLayout(src_layout)
        layout.addWidget(src_group)
        
        # Appearance
        app_group = QGroupBox("Görünüm")
        app_layout = QVBoxLayout()
        
        rot_layout = QHBoxLayout()
        rot_layout.addWidget(QLabel("Döndürme:"))
        self.cb_rot = QComboBox()
        self.cb_rot.addItems(["0°", "45°", "-45°", "90°"])
        rot_layout.addWidget(self.cb_rot)
        app_layout.addLayout(rot_layout)
        
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Şeffaflık:"))
        self.sl_opacity = QSlider(Qt.Orientation.Horizontal)
        self.sl_opacity.setRange(0, 100)
        self.sl_opacity.setValue(50)
        op_layout.addWidget(self.sl_opacity)
        app_layout.addLayout(op_layout)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # Position
        pos_group = QGroupBox("Konum ve Katman")
        pos_layout = QVBoxLayout()
        self.cb_loc = QComboBox()
        self.cb_loc.addItems(["Sayfanın üstünde", "Sayfanın arkasında"])
        pos_layout.addWidget(self.cb_loc)
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
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
        
    def choose_color(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.current_color = (col.red()/255.0, col.green()/255.0, col.blue()/255.0)
            
    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Görsel Seç", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.img_path = path
            self.lbl_img_path.setText(path.split("/")[-1])
            self.rb_img.setChecked(True)
            
    def get_config(self):
        t = 'text' if self.rb_text.isChecked() else 'image'
        rot_str = self.cb_rot.currentText().replace("°", "")
        rot = int(rot_str) if rot_str else 0
        
        return {
            'type': t,
            'text': self.le_text.text(),
            'image_path': self.img_path,
            'font': self.cb_font.currentText(),
            'font_size': self.sp_size.value(),
            'color': self.current_color,
            'rotation': rot,
            'opacity': self.sl_opacity.value() / 100.0,
            'scale': 1.0,
            'position': 'center',
            'overlay': (self.cb_loc.currentIndex() == 0),
            'page_range': 'all'
        }
