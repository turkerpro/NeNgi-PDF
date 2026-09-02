"""
NeNgi PDF - Password Protection & Removal Dialogs
"""

from __future__ import annotations
from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox
)


class PasswordDialog(QDialog):
    """Dialog to set AES-256 password protection on a PDF."""

    def __init__(self, mode: str = "encrypt", parent: Optional[QDialog] = None):
        super().__init__(parent)
        self.mode = mode
        self.password: Optional[str] = None
        self.setWindowTitle("PDF Parola Koruması" if mode == "encrypt" else "Parola Girin")
        self.setFixedSize(360, 180)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        lbl = QLabel("Belgeyi açmak için gerekli parolayı belirleyin:" if self.mode == "encrypt" else "Bu PDF şifrelidir. Lütfen parolayı girin:")
        layout.addWidget(lbl)

        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.setPlaceholderText("Parola...")
        layout.addWidget(self.txt_pass)

        if self.mode == "encrypt":
            self.txt_confirm = QLineEdit()
            self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.txt_confirm.setPlaceholderText("Parolayı Tekrar Girin...")
            layout.addWidget(self.txt_confirm)

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_ok = QPushButton("Tamam")
        btn_ok.setObjectName("accentButton")
        btn_ok.clicked.connect(self._validate)
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)

    def _validate(self):
        pw = self.txt_pass.text()
        if not pw:
            QMessageBox.warning(self, "Uyarı", "Parola boş bırakılamaz.")
            return

        if self.mode == "encrypt":
            pw2 = self.txt_confirm.text()
            if pw != pw2:
                QMessageBox.warning(self, "Hata", "Parolalar birbiriyle uyuşmuyor!")
                return

        self.password = pw
        self.accept()
