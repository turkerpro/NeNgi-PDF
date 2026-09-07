from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGroupBox, QFileDialog, QProgressBar
)

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dışa Aktar")
        self.resize(350, 200)
        self.out_path = ""
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Format
        fmt_group = QGroupBox("Format")
        f_layout = QHBoxLayout()
        f_layout.addWidget(QLabel("Dışa Aktar:"))
        self.cb_fmt = QComboBox()
        self.cb_fmt.addItems(["Word (.docx)", "Excel (.xlsx)", "PowerPoint (.pptx)", "HTML"])
        f_layout.addWidget(self.cb_fmt)
        fmt_group.setLayout(f_layout)
        layout.addWidget(fmt_group)
        
        # Output
        out_group = QGroupBox("Kayıt Yeri")
        o_layout = QHBoxLayout()
        self.btn_browse = QPushButton("Gözat...")
        self.btn_browse.clicked.connect(self.browse_file)
        self.lbl_path = QLabel("Seçilmedi")
        o_layout.addWidget(self.btn_browse)
        o_layout.addWidget(self.lbl_path)
        out_group.setLayout(o_layout)
        layout.addWidget(out_group)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Dışa Aktar")
        btn_cancel = QPushButton("İptal")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
    def browse_file(self):
        idx = self.cb_fmt.currentIndex()
        if idx == 0: filt = "Word Documents (*.docx)"
        elif idx == 1: filt = "Excel Spreadsheets (*.xlsx)"
        elif idx == 2: filt = "PowerPoint Presentations (*.pptx)"
        else: filt = "HTML Files (*.html)"
        
        path, _ = QFileDialog.getSaveFileName(self, "Kayıt Yeri", "", filt)
        if path:
            self.out_path = path
            self.lbl_path.setText(path.split("/")[-1])
            
    def get_config(self):
        idx = self.cb_fmt.currentIndex()
        if idx == 0: fmt = 'docx'
        elif idx == 1: fmt = 'xlsx'
        elif idx == 2: fmt = 'pptx'
        else: fmt = 'html'
        
        return {
            'format': fmt,
            'output_path': self.out_path
        }
