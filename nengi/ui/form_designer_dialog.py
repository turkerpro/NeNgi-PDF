"""
NeNgi PDF - Form Designer & Field Properties Dialog
Allows users to visually add or modify form fields (Text, Checkbox, Radio, Dropdown, Listbox, Button).
"""

from __future__ import annotations
from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QTabWidget, QWidget, QColorDialog, QMessageBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

import pymupdf as fitz
from nengi.core.pdf_document import PDFDocument
from nengi.core.form_designer import (
    FormDesigner, FormFieldConfig,
    FIELD_TEXT, FIELD_CHECKBOX, FIELD_RADIO,
    FIELD_COMBO, FIELD_LISTBOX, FIELD_BUTTON, FIELD_SIGNATURE,
    FIELD_TYPE_LABELS
)


class FormFieldPropertiesDialog(QDialog):
    """Dialog to edit/create a form field's detailed properties."""

    def __init__(self, config: Optional[FormFieldConfig] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("📋 Form Alanı Özellikleri - NeNgi PDF")
        self.resize(480, 420)
        self.config = config or FormFieldConfig()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Tab 1: Genel
        tab_general = QWidget()
        lay_gen = QGridLayout(tab_general)

        lay_gen.addWidget(QLabel("Alan Türü:"), 0, 0)
        self.cb_type = QComboBox()
        for ftype, label in FIELD_TYPE_LABELS.items():
            self.cb_type.addItem(label, ftype)
        idx = self.cb_type.findData(self.config.field_type)
        if idx >= 0:
            self.cb_type.setCurrentIndex(idx)
        lay_gen.addWidget(self.cb_type, 0, 1)

        lay_gen.addWidget(QLabel("Alan Adı:"), 1, 0)
        self.txt_name = QLineEdit(self.config.name)
        lay_gen.addWidget(self.txt_name, 1, 1)

        lay_gen.addWidget(QLabel("İpucu (Tooltip):"), 2, 0)
        self.txt_tooltip = QLineEdit(self.config.tooltip)
        lay_gen.addWidget(self.txt_tooltip, 2, 1)

        lay_gen.addWidget(QLabel("Varsayılan Değer:"), 3, 0)
        self.txt_value = QLineEdit(self.config.value or self.config.default_value)
        lay_gen.addWidget(self.txt_value, 3, 1)

        self.chk_readonly = QCheckBox("Salt Okunur (Read-only)")
        self.chk_readonly.setChecked(self.config.is_readonly)
        lay_gen.addWidget(self.chk_readonly, 4, 1)

        self.chk_required = QCheckBox("Doldurulması Zorunlu (Required)")
        self.chk_required.setChecked(self.config.is_required)
        lay_gen.addWidget(self.chk_required, 5, 1)

        self.chk_multiline = QCheckBox("Çok Satırlı Metin (Multiline)")
        self.chk_multiline.setChecked(self.config.is_multiline)
        lay_gen.addWidget(self.chk_multiline, 6, 1)

        self.chk_password = QCheckBox("Parola Alanı (Maskeli)")
        self.chk_password.setChecked(self.config.is_password)
        lay_gen.addWidget(self.chk_password, 7, 1)

        tabs.addTab(tab_general, "Genel")

        # Tab 2: Görünüm
        tab_app = QWidget()
        lay_app = QGridLayout(tab_app)

        lay_app.addWidget(QLabel("Yazı Boyutu (pt):"), 0, 0)
        self.spn_fontsize = QDoubleSpinBox()
        self.spn_fontsize.setRange(6.0, 72.0)
        self.spn_fontsize.setValue(self.config.font_size)
        lay_app.addWidget(self.spn_fontsize, 0, 1)

        lay_app.addWidget(QLabel("Kenarlık Kalınlığı:"), 1, 0)
        self.spn_borderwidth = QDoubleSpinBox()
        self.spn_borderwidth.setRange(0.5, 10.0)
        self.spn_borderwidth.setValue(self.config.border_width)
        lay_app.addWidget(self.spn_borderwidth, 1, 1)

        lay_app.addWidget(QLabel("Kenarlık Stili:"), 2, 0)
        self.cb_borderstyle = QComboBox()
        self.cb_borderstyle.addItems(["solid", "dashed", "beveled", "inset", "underline"])
        self.cb_borderstyle.setCurrentText(self.config.border_style)
        lay_app.addWidget(self.cb_borderstyle, 2, 1)

        tabs.addTab(tab_app, "Görünüm")

        # Tab 3: Seçenekler (Açılır Liste ve Liste Kutusu için)
        tab_opts = QWidget()
        lay_opts = QVBoxLayout(tab_opts)
        lay_opts.addWidget(QLabel("Seçenek Listesi Elemanları:"))

        self.list_options = QListWidget()
        for opt in self.config.options:
            self.list_options.addItem(opt)
        lay_opts.addWidget(self.list_options)

        h_opt_add = QHBoxLayout()
        self.txt_new_opt = QLineEdit()
        self.txt_new_opt.setPlaceholderText("Yeni seçenek girin...")
        btn_add_opt = QPushButton("Ekle")
        btn_add_opt.clicked.connect(self._add_option)
        btn_rem_opt = QPushButton("Sil")
        btn_rem_opt.clicked.connect(self._remove_option)
        h_opt_add.addWidget(self.txt_new_opt)
        h_opt_add.addWidget(btn_add_opt)
        h_opt_add.addWidget(btn_rem_opt)
        lay_opts.addLayout(h_opt_add)

        tabs.addTab(tab_opts, "Seçenekler")

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Kaydet")
        btn_save.setObjectName("accentButton")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _add_option(self):
        text = self.txt_new_opt.text().strip()
        if text:
            self.list_options.addItem(text)
            self.txt_new_opt.clear()

    def _remove_option(self):
        row = self.list_options.currentRow()
        if row >= 0:
            self.list_options.takeItem(row)

    def _save(self):
        self.config.field_type = self.cb_type.currentData()
        self.config.name = self.txt_name.text().strip()
        self.config.tooltip = self.txt_tooltip.text().strip()
        self.config.value = self.txt_value.text().strip()
        self.config.is_readonly = self.chk_readonly.isChecked()
        self.config.is_required = self.chk_required.isChecked()
        self.config.is_multiline = self.chk_multiline.isChecked()
        self.config.is_password = self.chk_password.isChecked()
        self.config.font_size = self.spn_fontsize.value()
        self.config.border_width = self.spn_borderwidth.value()
        self.config.border_style = self.cb_borderstyle.currentText()

        opts = [self.list_options.item(i).text() for i in range(self.list_options.count())]
        self.config.options = opts

        self.accept()


class FormDesignerDialog(QDialog):
    """Management window for form fields across the current PDF document."""

    field_added = pyqtSignal(FormFieldConfig)

    def __init__(self, doc: PDFDocument, current_page: int = 0, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("🛠️ Form Tasarımcısı & Alan Yönetimi - NeNgi PDF")
        self.resize(650, 480)
        self.doc = doc
        self.current_page = current_page
        self._init_ui()
        self._load_fields()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top_info = QLabel("Bu sayfada ve belgedeki form alanlarını düzenleyebilir, yeni alanlar ekleyebilir veya otomatik algılatabilirsiniz.")
        top_info.setWordWrap(True)
        layout.addWidget(top_info)

        # Field List
        self.field_list = QListWidget()
        self.field_list.itemDoubleClicked.connect(self._edit_selected_field)
        layout.addWidget(self.field_list)

        # Action Buttons
        btn_grid = QGridLayout()

        btn_add_text = QPushButton("➕ Metin Alanı Ekle")
        btn_add_text.clicked.connect(lambda: self._add_field(FIELD_TEXT))
        btn_grid.addWidget(btn_add_text, 0, 0)

        btn_add_chk = QPushButton("☑️ Onay Kutusu Ekle")
        btn_add_chk.clicked.connect(lambda: self._add_field(FIELD_CHECKBOX))
        btn_grid.addWidget(btn_add_chk, 0, 1)

        btn_add_radio = QPushButton("🔘 Radyo Düğmesi Ekle")
        btn_add_radio.clicked.connect(lambda: self._add_field(FIELD_RADIO))
        btn_grid.addWidget(btn_add_radio, 0, 2)

        btn_add_combo = QPushButton("▼ Açılır Liste Ekle")
        btn_add_combo.clicked.connect(lambda: self._add_field(FIELD_COMBO))
        btn_grid.addWidget(btn_add_combo, 1, 0)

        btn_add_btn = QPushButton("🔲 Düğme Ekle")
        btn_add_btn.clicked.connect(lambda: self._add_field(FIELD_BUTTON))
        btn_grid.addWidget(btn_add_btn, 1, 1)

        btn_autodetect = QPushButton("🪄 Form Alanlarını Otomatik Algıla")
        btn_autodetect.clicked.connect(self._auto_detect)
        btn_grid.addWidget(btn_autodetect, 1, 2)

        layout.addLayout(btn_grid)

        # Bottom row
        bot_layout = QHBoxLayout()
        btn_delete = QPushButton("🗑️ Seçili Alanı Sil")
        btn_delete.clicked.connect(self._delete_selected_field)
        bot_layout.addWidget(btn_delete)

        btn_clear_all = QPushButton("Tüm Formu Temizle")
        btn_clear_all.clicked.connect(self._clear_all_fields)
        bot_layout.addWidget(btn_clear_all)

        bot_layout.addStretch()

        btn_close = QPushButton("Kapat")
        btn_close.clicked.connect(self.accept)
        bot_layout.addWidget(btn_close)

        layout.addLayout(bot_layout)

    def _load_fields(self):
        self.field_list.clear()
        if not self.doc or not self.doc.is_open:
            return

        fields = FormDesigner.get_fields_on_page(self.doc, self.current_page)
        for f in fields:
            name = f.get("name") or "(İsimsiz Alan)"
            tlabel = f.get("type_label", "Alan")
            val = f.get("value", "")
            item = QListWidgetItem(f"[{tlabel}] {name}  =  '{val}'")
            item.setData(Qt.ItemDataRole.UserRole, f)
            self.field_list.addItem(item)

    def _add_field(self, field_type: int):
        default_w = 40 if field_type in (FIELD_CHECKBOX, FIELD_RADIO) else 180
        default_h = 24
        rect = fitz.Rect(50, 100, 50 + default_w, 100 + default_h)
        cfg = FormFieldConfig(field_type=field_type, name=f"field_{len(self.field_list) + 1}", rect=rect)

        dlg = FormFieldPropertiesDialog(cfg, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            FormDesigner.create_field(self.doc, self.current_page, dlg.config)
            self._load_fields()

    def _edit_selected_field(self, item: QListWidgetItem):
        f = item.data(Qt.ItemDataRole.UserRole)
        if not f:
            return
        widget = f.get("widget")
        cfg = FormFieldConfig(
            field_type=f.get("type", FIELD_TEXT),
            name=f.get("name", ""),
            rect=f.get("rect"),
            tooltip=f.get("tooltip", ""),
            value=f.get("value", ""),
            is_readonly=f.get("readonly", False),
            is_required=f.get("required", False),
            font_size=f.get("font_size", 11.0),
            options=f.get("options", [])
        )
        dlg = FormFieldPropertiesDialog(cfg, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            FormDesigner.update_field(self.doc, self.current_page, widget, dlg.config)
            self._load_fields()

    def _delete_selected_field(self):
        item = self.field_list.currentItem()
        if not item:
            QMessageBox.information(self, "Bilgi", "Lütfen silinecek bir alan seçin.")
            return
        f = item.data(Qt.ItemDataRole.UserRole)
        widget = f.get("widget")
        if widget:
            FormDesigner.delete_field(self.doc, self.current_page, widget)
            self._load_fields()

    def _clear_all_fields(self):
        reply = QMessageBox.question(
            self, "Onay", "Belgedeki tüm form alanlarının değerleri temizlenecek. Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            count = FormDesigner.clear_all_fields(self.doc)
            QMessageBox.information(self, "Bilgi", f"{count} form alanı temizlendi.")
            self._load_fields()

    def _auto_detect(self):
        suggestions = FormDesigner.auto_detect_fields(self.doc, self.current_page)
        if not suggestions:
            QMessageBox.information(self, "Bilgi", "Bu sayfada otomatik form alanı tespit edilemedi.")
            return

        reply = QMessageBox.question(
            self, "Otomatik Algılama",
            f"Sayfada {len(suggestions)} potansiyel form alanı tespit edildi. Bu alanlar oluşturulsun mu?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for cfg in suggestions:
                FormDesigner.create_field(self.doc, self.current_page, cfg)
            self._load_fields()
            QMessageBox.information(self, "Tamamlandı", f"{len(suggestions)} form alanı başarıyla oluşturuldu!")
