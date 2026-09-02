"""
NeNgi PDF - NextGen Studio Design & Windows 11 Fluent Theme
Features navigation rail, floating pill island toolbar, copilot side panel,
and high-contrast typography.
"""

DARK_THEME = """
/* Global Window & Font Hierarchy */
QWidget {
    background-color: #17181A;
    color: #EDEDED;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 12px;
}

QMainWindow, QDialog {
    background-color: #17181A;
}

/* Left Navigation Rail */
QWidget#navigationRail {
    background-color: #1A1C1E;
    border-right: 1px solid #26292E;
}

/* Right Copilot Panel */
QWidget#copilotPanel {
    background-color: #17181A;
    border-left: 1px solid #26292E;
}

/* Top Global Header */
QFrame#topHeader {
    background-color: #17181A;
    border-bottom: 1px solid #26292E;
}

/* Search Bar Pill */
QLineEdit#searchBox {
    background-color: #202226;
    border: 1px solid #30333A;
    border-radius: 16px;
    padding: 6px 14px;
    color: #FFFFFF;
    font-size: 12px;
}

QLineEdit#searchBox:focus {
    border-color: #0078D4;
    background-color: #24272D;
}

/* Floating Bottom Capsule / Island Toolbar */
QFrame#floatingPill {
    background-color: #1E2024;
    border: 1px solid #33373F;
    border-radius: 24px;
}

/* Bottom Pagination & Zoom Footer */
QFrame#bottomFooter {
    background-color: #17181A;
    border-top: 1px solid #26292E;
    color: #8C929C;
    font-size: 11.5px;
}

/* Buttons */
QPushButton {
    background-color: #24272D;
    border: 1px solid #353942;
    border-radius: 6px;
    padding: 6px 14px;
    color: #EDEDED;
    font-weight: 500;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #2E333B;
    border-color: #464C56;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #1B1E22;
}

QPushButton#accentButton {
    background-color: #0078D4;
    border: 1px solid #005A9E;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #1084D9;
    border-color: #0078D4;
}

QPushButton#dangerButton {
    background-color: #D13438;
    border: 1px solid #A80000;
    color: #FFFFFF;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #26292E;
    background-color: #17181A;
    top: -1px;
}

QTabBar::tab {
    background-color: #1C1E22;
    border: 1px solid #26292E;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 18px;
    margin-right: 2px;
    color: #8C929C;
    font-size: 11.5px;
    font-weight: 500;
}

QTabBar::tab:hover {
    background-color: #24272D;
    color: #FFFFFF;
}

QTabBar::tab:selected {
    background-color: #17181A;
    color: #0078D4;
    border-top: 2px solid #0078D4;
    border-left: 1px solid #26292E;
    border-right: 1px solid #26292E;
    font-weight: 600;
}

/* Scroll Areas */
QScrollArea {
    background-color: #17181A;
    border: none;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #17181A;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #33373E;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4A505A;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #17181A;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #33373E;
    min-width: 25px;
    border-radius: 5px;
}

/* Context Menu */
QMenu {
    background-color: #22252A;
    border: 1px solid #33373E;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    color: #EDEDED;
}

QMenu::item:selected {
    background-color: #0078D4;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background-color: #2E3238;
    margin: 4px 6px;
}

/* Splitter */
QSplitter::handle {
    background-color: #202226;
}

QSplitter::handle:hover {
    background-color: #0078D4;
}
"""

LIGHT_THEME = """
/* Global Window & Font Hierarchy */
QWidget {
    background-color: #FFFFFF;
    color: #1F2328;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 12px;
}

QMainWindow, QDialog {
    background-color: #FFFFFF;
}

/* Left Navigation Rail */
QWidget#navigationRail {
    background-color: #F8F9FA;
    border-right: 1px solid #E1E4E8;
}

/* Right Copilot Panel */
QWidget#copilotPanel {
    background-color: #FFFFFF;
    border-left: 1px solid #E1E4E8;
}

/* Top Global Header */
QFrame#topHeader {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E1E4E8;
}

/* Search Bar Pill */
QLineEdit#searchBox {
    background-color: #F1F3F5;
    border: 1px solid #D0D7DE;
    border-radius: 16px;
    padding: 6px 14px;
    color: #1F2328;
    font-size: 12px;
}

QLineEdit#searchBox:focus {
    border-color: #0078D4;
    background-color: #FFFFFF;
}

/* Floating Bottom Capsule / Island Toolbar */
QFrame#floatingPill {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 24px;
}

/* Bottom Pagination & Zoom Footer */
QFrame#bottomFooter {
    background-color: #FFFFFF;
    border-top: 1px solid #E1E4E8;
    color: #57606A;
    font-size: 11.5px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 6px;
    padding: 6px 14px;
    color: #1F2328;
    font-weight: 500;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #F3F4F6;
    border-color: #AFB8C1;
}

QPushButton:pressed {
    background-color: #EBECF0;
}

QPushButton#accentButton {
    background-color: #0078D4;
    border: 1px solid #005A9E;
    color: #FFFFFF;
    font-weight: 600;
}

QPushButton#accentButton:hover {
    background-color: #1084D9;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #E1E4E8;
    background-color: #F5F7FA;
    top: -1px;
}

QTabBar::tab {
    background-color: #F6F8FA;
    border: 1px solid #E1E4E8;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 7px 18px;
    margin-right: 2px;
    color: #57606A;
    font-size: 11.5px;
    font-weight: 500;
}

QTabBar::tab:hover {
    background-color: #FFFFFF;
    color: #1F2328;
}

QTabBar::tab:selected {
    background-color: #F5F7FA;
    color: #0078D4;
    border-top: 2px solid #0078D4;
    border-left: 1px solid #E1E4E8;
    border-right: 1px solid #E1E4E8;
    font-weight: 600;
}

/* Scroll Areas */
QScrollArea {
    background-color: #F5F7FA;
    border: none;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #F5F7FA;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #C0C6CF;
    min-height: 25px;
    border-radius: 5px;
}

/* Splitter */
QSplitter::handle {
    background-color: #E1E4E8;
}

QSplitter::handle:hover {
    background-color: #0078D4;
}
"""
