from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QButtonGroup, QColorDialog, QMenu, QSlider, QAction
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from .icons import get_svg_icon
from .styles import DARK_THEME, LIGHT_THEME

class AnnotationToolbar(QFrame):
    """Expanded annotation toolbar with tool groups."""
    
    tool_selected = pyqtSignal(str) # Tool name
    color_changed = pyqtSignal(tuple) # RGB tuple 0-1
    property_changed = pyqtSignal(str, object)
    
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.is_dark = is_dark
        self.current_color = (1, 1, 0)
        self.current_opacity = 0.5
        self.current_width = 1.5
        
        self._setup_ui()
        self.update_theme(is_dark)
        
    def _setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # Tools layout
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(4)
        
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        
        # Metin İşaretleme
        tools_layout.addWidget(self._create_section_label("Metin"))
        self._add_tool_button(tools_layout, "highlight", "Vurgula (U)")
        self._add_tool_button(tools_layout, "underline", "Altı Çizili")
        self._add_tool_button(tools_layout, "strikethrough", "Üstü Çizili")
        
        tools_layout.addWidget(self._create_separator())
        
        # Çizim
        tools_layout.addWidget(self._create_section_label("Çizim"))
        self._add_tool_button(tools_layout, "line", "Çizgi (Shift+L)")
        self._add_tool_button(tools_layout, "arrow", "Ok")
        self._add_tool_button(tools_layout, "rect", "Dikdörtgen")
        self._add_tool_button(tools_layout, "oval", "Elips")
        self._add_tool_button(tools_layout, "polygon", "Çokgen")
        self._add_tool_button(tools_layout, "cloud", "Bulut")
        self._add_tool_button(tools_layout, "draw", "Serbest Çizim")
        
        tools_layout.addWidget(self._create_separator())
        
        # Notlar
        tools_layout.addWidget(self._create_section_label("Notlar"))
        self._add_tool_button(tools_layout, "sticky_note", "Not Ekle (S)")
        self._add_tool_button(tools_layout, "text", "Metin Kutusu")
        
        tools_layout.addWidget(self._create_separator())
        
        # Damgalar
        tools_layout.addWidget(self._create_section_label("Damgalar"))
        self._create_stamp_button(tools_layout)
        
        layout.addLayout(tools_layout)
        
        # Properties
        prop_layout = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(24, 24)
        self.color_btn.clicked.connect(self._choose_color)
        self._update_color_btn()
        
        prop_layout.addWidget(QLabel("Renk:"))
        prop_layout.addWidget(self.color_btn)
        
        prop_layout.addSpacing(10)
        
        prop_layout.addWidget(QLabel("Kalınlık:"))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 10)
        self.width_slider.setValue(1)
        self.width_slider.setFixedWidth(100)
        self.width_slider.valueChanged.connect(self._width_changed)
        prop_layout.addWidget(self.width_slider)
        
        prop_layout.addSpacing(10)
        
        prop_layout.addWidget(QLabel("Saydamlık:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(50)
        self.opacity_slider.setFixedWidth(100)
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        prop_layout.addWidget(self.opacity_slider)
        
        prop_layout.addStretch()
        
        layout.addLayout(prop_layout)
        
    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: gray;")
        return lbl
        
    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line
        
    def _add_tool_button(self, layout, name, tooltip):
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setToolTip(tooltip)
        btn.setProperty("tool_name", name)
        btn.setFixedSize(32, 32)
        
        color = DARK_THEME["text"] if self.is_dark else LIGHT_THEME["text"]
        btn.setIcon(get_svg_icon(name, color=color))
        
        self.tool_group.addButton(btn)
        btn.clicked.connect(lambda checked, n=name: self._tool_clicked(n))
        layout.addWidget(btn)
        return btn
        
    def _create_stamp_button(self, layout):
        btn = QPushButton()
        btn.setToolTip("Damga Ekle")
        btn.setFixedSize(32, 32)
        color = DARK_THEME["text"] if self.is_dark else LIGHT_THEME["text"]
        btn.setIcon(get_svg_icon("stamp", color=color))
        
        menu = QMenu(self)
        stamps = ["ONAYLANDI", "TASLAK", "GİZLİ", "SON", "REDDEDİLDİ", "GEÇERSİZ"]
        for s in stamps:
            action = QAction(s, self)
            action.triggered.connect(lambda checked, name=s: self._stamp_selected(name))
            menu.addAction(action)
            
        btn.setMenu(menu)
        layout.addWidget(btn)
        
    def _tool_clicked(self, name):
        self.tool_selected.emit(name)
        
    def _stamp_selected(self, name):
        # We can uncheck others and emit stamp_preset
        if self.tool_group.checkedButton():
            self.tool_group.setExclusive(False)
            self.tool_group.checkedButton().setChecked(False)
            self.tool_group.setExclusive(True)
            
        self.tool_selected.emit("stamp_preset")
        self.property_changed.emit("stamp_name", name)
        
    def _choose_color(self):
        r = int(self.current_color[0]*255)
        g = int(self.current_color[1]*255)
        b = int(self.current_color[2]*255)
        color = QColorDialog.getColor(QColor(r, g, b), self, "Renk Seç")
        if color.isValid():
            self.current_color = (color.redF(), color.greenF(), color.blueF())
            self._update_color_btn()
            self.color_changed.emit(self.current_color)
            
    def _update_color_btn(self):
        r = int(self.current_color[0]*255)
        g = int(self.current_color[1]*255)
        b = int(self.current_color[2]*255)
        self.color_btn.setStyleSheet(f"background-color: rgb({r},{g},{b}); border: 1px solid gray; border-radius: 4px;")
        
    def _width_changed(self, val):
        self.current_width = float(val)
        self.property_changed.emit("width", self.current_width)
        
    def _opacity_changed(self, val):
        self.current_opacity = val / 100.0
        self.property_changed.emit("opacity", self.current_opacity)
        
    def update_theme(self, is_dark: bool):
        self.is_dark = is_dark
        bg = "#1E2023" if is_dark else "#FFFFFF"
        border = "#383C44" if is_dark else "#E2E8F0"
        hover = "#2C3036" if is_dark else "#F1F5F9"
        accent = "#0078D4"
        text = "#D0D4DC" if is_dark else "#374151"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
            QPushButton:checked {{
                background: {accent};
            }}
            QLabel {{
                color: {text};
                border: none;
            }}
        """)
        
        for btn in self.tool_group.buttons():
            name = btn.property("tool_name")
            if name:
                btn.setIcon(get_svg_icon(name, color=text))
