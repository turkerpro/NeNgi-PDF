"""
NeNgi PDF - Windows 11 Fluent Design Stylesheet & Color Palette
Provides Dark and Light themes adhering to Windows 11 design guidelines.
"""

DARK_THEME = """
QWidget {
    background-color: #202020;
    color: #FFFFFF;
    font-family: 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #202020;
}

/* Command Bar / ToolBar */
QToolBar {
    background-color: #2C2C2C;
    border-bottom: 1px solid #383838;
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 5px 8px;
    font-weight: 500;
    color: #E0E0E0;
}

QToolButton:hover {
    background-color: #383838;
    border: 1px solid #484848;
}

QToolButton:pressed, QToolButton:checked {
    background-color: #0078D4;
    color: #FFFFFF;
    border: 1px solid #005A9E;
}

/* Buttons */
QPushButton {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 5px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #383838;
    border-color: #505050;
}

QPushButton:pressed {
    background-color: #1F1F1F;
}

QPushButton#accentButton {
    background-color: #0078D4;
    border: 1px solid #005A9E;
    color: #FFFFFF;
}

QPushButton#accentButton:hover {
    background-color: #1084D9;
}

QPushButton#dangerButton {
    background-color: #C42B1C;
    border: 1px solid #A12619;
    color: #FFFFFF;
}

QPushButton#dangerButton:hover {
    background-color: #D83B01;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #202020;
    top: -1px;
}

QTabBar::tab {
    background-color: #272727;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 16px;
    margin-right: 2px;
    color: #A0A0A0;
}

QTabBar::tab:selected {
    background-color: #202020;
    border-color: #0078D4;
    border-bottom: 2px solid #0078D4;
    color: #FFFFFF;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #323232;
    color: #E0E0E0;
}

/* Scroll Areas */
QScrollArea {
    border: 1px solid #2D2D2D;
    background-color: #181818;
}

QScrollBar:vertical {
    border: none;
    background: #202020;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #404040;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #555555;
}

QScrollBar:horizontal {
    border: none;
    background: #202020;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #404040;
    min-width: 25px;
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #1F1F1F;
    border-top: 1px solid #2B2B2B;
    color: #999999;
    font-size: 12px;
}

/* Inputs & ComboBox */
QLineEdit, QSpinBox, QComboBox {
    background-color: #2B2B2B;
    border: 1px solid #3E3E3E;
    border-radius: 4px;
    padding: 5px 8px;
    color: #FFFFFF;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #0078D4;
}

/* Table and List views */
QListWidget, QTableWidget {
    background-color: #242424;
    border: 1px solid #333333;
    border-radius: 6px;
    gridline-color: #303030;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #0078D4;
    color: #FFFFFF;
}

QListWidget::item:hover:!selected, QTableWidget::item:hover:!selected {
    background-color: #303030;
}

/* Splitter */
QSplitter::handle {
    background-color: #2D2D2D;
}

QSplitter::handle:hover {
    background-color: #0078D4;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #F3F3F3;
    color: #1A1A1A;
    font-family: 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #F3F3F3;
}

QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E5E5;
    spacing: 6px;
    padding: 6px 10px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 5px;
    padding: 5px 8px;
    font-weight: 500;
    color: #2D2D2D;
}

QToolButton:hover {
    background-color: #EAEAEA;
    border: 1px solid #D0D0D0;
}

QToolButton:pressed, QToolButton:checked {
    background-color: #0078D4;
    color: #FFFFFF;
}

QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 5px;
    padding: 6px 14px;
    color: #1A1A1A;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #F7F7F7;
    border-color: #B0B0B0;
}

QPushButton#accentButton {
    background-color: #0078D4;
    border: 1px solid #005A9E;
    color: #FFFFFF;
}

QPushButton#accentButton:hover {
    background-color: #1084D9;
}

QScrollArea {
    border: 1px solid #E0E0E0;
    background-color: #E8E8E8;
}

QScrollBar:vertical {
    border: none;
    background: #F0F0F0;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #C0C0C0;
    border-radius: 5px;
}

QStatusBar {
    background-color: #F8F8F8;
    border-top: 1px solid #E5E5E5;
    color: #555555;
    font-size: 12px;
}
"""
