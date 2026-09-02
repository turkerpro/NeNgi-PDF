"""
NeNgi PDF - Distinctive Studio Design & Modern Windows 11 Fluent Theme
High-contrast typography, minimal chrome, intentional hierarchy, and refined micro-interactions.
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

/* Minimalist Command Bar / ToolBar with Text Under Icon */
QToolBar {
    background-color: #1E2023;
    border-bottom: 1px solid #2B2E33;
    spacing: 3px;
    padding: 3px 6px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 3px 5px;
    font-size: 10.5px;
    font-weight: 500;
    color: #9DA3AE;
    min-width: 44px;
    margin: 1px;
}

QToolButton:hover {
    background-color: #2A2D33;
    color: #FFFFFF;
    border: 1px solid #383C44;
}

QToolButton:pressed {
    background-color: #0078D4;
    color: #FFFFFF;
    border-color: #005A9E;
}

QToolButton:checked {
    background-color: #0078D4;
    color: #FFFFFF;
    border: 1px solid #005A9E;
}

QToolBar::separator {
    width: 1px;
    background-color: #2C2F36;
    margin: 6px 3px;
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

QPushButton#dangerButton:hover {
    background-color: #E81123;
}

/* Studio Tabs */
QTabWidget::pane {
    border: 1px solid #282B30;
    background-color: #17181A;
    top: -1px;
}

QTabBar::tab {
    background-color: #1E2023;
    border: 1px solid #282B30;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
    margin-right: 2px;
    color: #8C929C;
    font-size: 11.5px;
    font-weight: 500;
}

QTabBar::tab:hover {
    background-color: #25282E;
    color: #FFFFFF;
}

QTabBar::tab:selected {
    background-color: #17181A;
    color: #0078D4;
    border-top: 2px solid #0078D4;
    border-left: 1px solid #282B30;
    border-right: 1px solid #282B30;
    font-weight: 600;
}

QTabBar::close-button {
    image: none;
    subcontrol-position: right;
    margin-left: 6px;
    border-radius: 9px;
    padding: 2px;
}

QTabBar::close-button:hover {
    background-color: #D13438;
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
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #33373E;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4A505A;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Table Widget for Diff changes */
QTableWidget {
    background-color: #1C1E22;
    border: 1px solid #2B2E33;
    gridline-color: #25282E;
    color: #D0D4DC;
    border-radius: 6px;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #0078D4;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #22252A;
    color: #8C929C;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #2B2E33;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
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

/* Status Bar */
QStatusBar {
    background-color: #17181A;
    border-top: 1px solid #24272C;
    color: #727883;
    font-size: 11px;
}

/* Splitter */
QSplitter::handle {
    background-color: #22252A;
}

QSplitter::handle:hover {
    background-color: #0078D4;
}
"""

LIGHT_THEME = """
/* Global Window & Font Hierarchy */
QWidget {
    background-color: #F8F9FA;
    color: #1F2328;
    font-family: 'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif;
    font-size: 12px;
}

QMainWindow, QDialog {
    background-color: #F8F9FA;
}

/* Command Bar with Text Under Icon */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E1E4E8;
    spacing: 3px;
    padding: 3px 6px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 3px 5px;
    font-size: 10.5px;
    font-weight: 500;
    color: #57606A;
    min-width: 44px;
    margin: 1px;
}

QToolButton:hover {
    background-color: #F0F2F5;
    color: #1F2328;
    border: 1px solid #D0D7DE;
}

QToolButton:pressed, QToolButton:checked {
    background-color: #0078D4;
    color: #FFFFFF;
    border: 1px solid #005A9E;
}

QToolBar::separator {
    width: 1px;
    background-color: #E1E4E8;
    margin: 6px 3px;
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

QPushButton#dangerButton {
    background-color: #CF222E;
    border: 1px solid #A40E26;
    color: #FFFFFF;
}

QPushButton#dangerButton:hover {
    background-color: #A40E26;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #D0D7DE;
    background-color: #FFFFFF;
    top: -1px;
}

QTabBar::tab {
    background-color: #F6F8FA;
    border: 1px solid #D0D7DE;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 16px;
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
    background-color: #FFFFFF;
    color: #0078D4;
    border-top: 2px solid #0078D4;
    border-left: 1px solid #D0D7DE;
    border-right: 1px solid #D0D7DE;
    font-weight: 600;
}

/* Scroll Areas */
QScrollArea {
    background-color: #F0F2F5;
    border: none;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #F0F2F5;
    width: 10px;
}

QScrollBar::handle:vertical {
    background-color: #C0C6CF;
    min-height: 25px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #8C95A0;
}

QScrollBar:horizontal {
    border: none;
    background-color: #F0F2F5;
    height: 10px;
}

QScrollBar::handle:horizontal {
    background-color: #C0C6CF;
    min-width: 25px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #8C95A0;
}

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    gridline-color: #F0F2F5;
    color: #1F2328;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #F6F8FA;
    color: #57606A;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #D0D7DE;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Context Menu */
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #D0D7DE;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
    color: #1F2328;
}

QMenu::item:selected {
    background-color: #0078D4;
    color: #FFFFFF;
}

QMenu::separator {
    height: 1px;
    background-color: #E1E4E8;
    margin: 4px 6px;
}

/* Status Bar */
QStatusBar {
    background-color: #F8F9FA;
    border-top: 1px solid #E1E4E8;
    color: #57606A;
    font-size: 11px;
}

/* Splitter */
QSplitter::handle {
    background-color: #E1E4E8;
}

QSplitter::handle:hover {
    background-color: #0078D4;
}
"""
