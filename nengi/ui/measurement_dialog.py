"""
NeNgi PDF - Measurement Scale & Calibration Dialog
Sets drawing scale ratio (e.g., 1 cm = 5 meters) and units for distance/area tools.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QDoubleSpinBox, QComboBox, QPushButton, QGroupBox, QWidget
)
from nengi.core.measurement import ScaleRatio


class MeasurementScaleDialog(QDialog):
    """Configures scale ratio for measurement tools."""

    def __init__(self, current_scale: Optional[ScaleRatio] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("📐 Ölçüm Ölçeği & Birim Ayarları - NeNgi PDF")
        self.resize(380, 240)
        self.scale = current_scale or ScaleRatio(1.0, "cm", 1.0, "m")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        grp = QGroupBox("Çizim Ölçeği Oranı")
        grid = QGridLayout(grp)

        grid.addWidget(QLabel("Belgedeki Uzunluk:"), 0, 0)
        self.spn_page_val = QDoubleSpinBox()
        self.spn_page_val.setRange(0.01, 1000.0)
        self.spn_page_val.setValue(self.scale.page_value)
        grid.addWidget(self.spn_page_val, 0, 1)

        self.cb_page_unit = QComboBox()
        self.cb_page_unit.addItems(["cm", "mm", "inch", "pt"])
        self.cb_page_unit.setCurrentText(self.scale.page_unit)
        grid.addWidget(self.cb_page_unit, 0, 2)

        grid.addWidget(QLabel("="), 1, 1, Qt.AlignmentFlag.AlignCenter)

        grid.addWidget(QLabel("Gerçek Dünya Uzunluğu:"), 2, 0)
        self.spn_real_val = QDoubleSpinBox()
        self.spn_real_val.setRange(0.01, 100000.0)
        self.spn_real_val.setValue(self.scale.real_value)
        grid.addWidget(self.spn_real_val, 2, 1)

        self.cb_real_unit = QComboBox()
        self.cb_real_unit.addItems(["m", "cm", "mm", "km", "ft", "yd"])
        self.cb_real_unit.setCurrentText(self.scale.real_unit)
        grid.addWidget(self.cb_real_unit, 2, 2)

        layout.addWidget(grp)

        # Quick Presets
        h_presets = QHBoxLayout()
        h_presets.addWidget(QLabel("Hızlı Ön Ayar:"))
        cb_preset = QComboBox()
        cb_preset.addItems(["Özel", "1:100 (1 cm = 1 m)", "1:50 (1 cm = 0.5 m)", "1:200 (1 cm = 2 m)", "1:500 (1 cm = 5 m)", "1:1000 (1 cm = 10 m)"])
        cb_preset.currentIndexChanged.connect(self._on_preset_changed)
        h_presets.addWidget(cb_preset)
        layout.addLayout(h_presets)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_apply = QPushButton("Ölçeği Uygula")
        btn_apply.setObjectName("accentButton")
        btn_apply.clicked.connect(self._apply)
        btn_layout.addWidget(btn_apply)

        layout.addLayout(btn_layout)

    def _on_preset_changed(self, idx: int):
        presets = {
            1: (1.0, "cm", 1.0, "m"),
            2: (1.0, "cm", 0.5, "m"),
            3: (1.0, "cm", 2.0, "m"),
            4: (1.0, "cm", 5.0, "m"),
            5: (1.0, "cm", 10.0, "m"),
        }
        if idx in presets:
            pv, pu, rv, ru = presets[idx]
            self.spn_page_val.setValue(pv)
            self.cb_page_unit.setCurrentText(pu)
            self.spn_real_val.setValue(rv)
            self.cb_real_unit.setCurrentText(ru)

    def _apply(self):
        self.scale = ScaleRatio(
            self.spn_page_val.value(),
            self.cb_page_unit.currentText(),
            self.spn_real_val.value(),
            self.cb_real_unit.currentText(),
        )
        self.accept()
