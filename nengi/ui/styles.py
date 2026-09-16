"""
NeNgi PDF - Design System
"Good design is as little design as possible." — Dieter Rams

Philosophy:
  1. Only what is necessary (every pixel earns its place)
  2. Neutral palette — content is the hero, chrome disappears
  3. Consistent 4px spacing grid
  4. No decoration for decoration's sake
  5. High contrast where it matters (text, active states)
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ColorTokens:
    """Color palette tokens - semantic names, not hardcoded values."""
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str
    bg_pressed: str
    bg_overlay: str
    border_subtle: str
    border_default: str
    border_strong: str
    border_focus: str
    border_error: str
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_inverse: str
    text_accent: str
    text_error: str
    accent_primary: str
    accent_hover: str
    accent_pressed: str
    accent_subtle: str
    success_bg: str
    success_text: str
    warning_bg: str
    warning_text: str
    error_bg: str
    error_text: str
    info_bg: str
    info_text: str
    scrollbar_track: str
    scrollbar_thumb: str
    scrollbar_thumb_hover: str
    splitter_handle: str
    splitter_handle_hover: str


@dataclass(frozen=True)
class SpacingTokens:
    """Spacing scale - 4px base unit."""
    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32


@dataclass(frozen=True)
class RadiusTokens:
    """Border radius scale — kept minimal per Rams."""
    xs: int = 2
    sm: int = 4
    md: int = 6
    lg: int = 8
    xl: int = 10
    xxl: int = 12
    pill: int = 20
    circle: int = 9999


@dataclass(frozen=True)
class FontTokens:
    """Typography — system-native stack, no web fonts."""
    family: str = "'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, sans-serif"
    mono_family: str = "'JetBrains Mono', 'Consolas', 'Courier New', monospace"
    xs: int = 10
    sm: int = 11
    base: int = 12
    lg: int = 13
    xl: int = 14
    xxl: int = 16
    xxxl: int = 20
    normal: int = 400
    medium: int = 500
    semibold: int = 600
    bold: int = 700


@dataclass(frozen=True)
class IconTokens:
    """Icon size scale."""
    xs: int = 12
    sm: int = 14
    base: int = 16
    lg: int = 20
    xl: int = 24
    xxl: int = 28
    xxxl: int = 36


@dataclass(frozen=True)
class ShadowTokens:
    """Shadow/elevation tokens — used sparingly."""
    none: str = "none"
    xs: str = "0 1px 2px rgba(0,0,0,0.05)"
    sm: str = "0 1px 3px rgba(0,0,0,0.1)"
    md: str = "0 4px 6px rgba(0,0,0,0.1)"
    lg: str = "0 10px 15px rgba(0,0,0,0.1)"
    xl: str = "0 20px 25px rgba(0,0,0,0.15)"


@dataclass(frozen=True)
class ZIndexTokens:
    """Z-index layers."""
    base: int = 0
    dropdown: int = 100
    sticky: int = 200
    modal: int = 300
    popover: int = 400
    tooltip: int = 500
    toast: int = 1000


@dataclass(frozen=True)
class DesignTokens:
    """Complete design token system."""
    colors: ColorTokens
    spacing: SpacingTokens
    radius: RadiusTokens
    fonts: FontTokens
    icons: IconTokens
    shadows: ShadowTokens
    z_index: ZIndexTokens
    transition_fast: str = "120ms ease"
    transition_normal: str = "180ms ease"
    transition_slow: str = "260ms ease"
    bp_sm: int = 640
    bp_md: int = 768
    bp_lg: int = 1024
    bp_xl: int = 1280


# =============================================================================
# DARK THEME — Rams-inspired: nearly black canvas, minimal chrome
# =============================================================================
DARK_COLORS = ColorTokens(
    bg_primary="#141414",
    bg_secondary="#1A1A1A",
    bg_tertiary="#202020",
    bg_hover="#272727",
    bg_pressed="#1E1E1E",
    bg_overlay="#00000066",
    border_subtle="#252525",
    border_default="#2E2E2E",
    border_strong="#3A3A3A",
    border_focus="#0A84FF",
    border_error="#FF453A",
    text_primary="#F0F0F0",
    text_secondary="#909090",
    text_tertiary="#5A5A5A",
    text_inverse="#141414",
    text_accent="#0A84FF",
    text_error="#FF6961",
    accent_primary="#0A84FF",
    accent_hover="#1A8FFF",
    accent_pressed="#0070E0",
    accent_subtle="#102040",
    success_bg="#1A3025",
    success_text="#30D158",
    warning_bg="#2E2010",
    warning_text="#FFD60A",
    error_bg="#2E1010",
    error_text="#FF453A",
    info_bg="#101E30",
    info_text="#64D2FF",
    scrollbar_track="#141414",
    scrollbar_thumb="#2E2E2E",
    scrollbar_thumb_hover="#404040",
    splitter_handle="#1A1A1A",
    splitter_handle_hover="#0A84FF",
)

# =============================================================================
# LIGHT THEME — Pure white canvas
# =============================================================================
LIGHT_COLORS = ColorTokens(
    bg_primary="#FFFFFF",
    bg_secondary="#F7F7F7",
    bg_tertiary="#F0F0F0",
    bg_hover="#EBEBEB",
    bg_pressed="#E3E3E3",
    bg_overlay="#00000014",
    border_subtle="#E8E8E8",
    border_default="#D6D6D6",
    border_strong="#BEBEBE",
    border_focus="#007AFF",
    border_error="#FF3B30",
    text_primary="#111111",
    text_secondary="#5E5E5E",
    text_tertiary="#ABABAB",
    text_inverse="#FFFFFF",
    text_accent="#007AFF",
    text_error="#FF3B30",
    accent_primary="#007AFF",
    accent_hover="#1A85FF",
    accent_pressed="#0062D4",
    accent_subtle="#E5F0FF",
    success_bg="#F0FFF5",
    success_text="#1D7A3A",
    warning_bg="#FFFBF0",
    warning_text="#7A5900",
    error_bg="#FFF5F5",
    error_text="#CC2222",
    info_bg="#F0F8FF",
    info_text="#1A5FAB",
    scrollbar_track="#F7F7F7",
    scrollbar_thumb="#CCCCCC",
    scrollbar_thumb_hover="#AAAAAA",
    splitter_handle="#E8E8E8",
    splitter_handle_hover="#007AFF",
)


# Shared tokens (same for both themes)
SHARED_SPACING = SpacingTokens()
SHARED_RADIUS = RadiusTokens()
SHARED_FONTS = FontTokens()
SHARED_ICONS = IconTokens()
SHARED_SHADOWS = ShadowTokens()
SHARED_Z_INDEX = ZIndexTokens()


# =============================================================================
# QSS BUILDER — Dieter Rams: remove everything non-essential
# =============================================================================
def build_theme(colors: ColorTokens) -> str:
    """Build complete QSS theme from design tokens.

    Rams principles applied:
      - No gradients, no drop-shadows on UI chrome
      - Minimal border-radius — functional, not trendy
      - Single accent color used consistently
      - Scrollbars thin and unobtrusive
      - Focus ring is the ONLY ornament (accessibility matters)
    """
    c = colors
    r = SHARED_RADIUS
    s = SHARED_SPACING
    f = SHARED_FONTS

    return f"""
/* =========================================================================
   NeNgi PDF — Design System
   "Less, but better." — Dieter Rams
   ========================================================================= */

* {{ outline: none; }}

QWidget {{
    background-color: {c.bg_primary};
    color: {c.text_primary};
    font-family: {f.family};
    font-size: {f.base}px;
    selection-background-color: {c.accent_primary};
    selection-color: {c.text_inverse};
}}

QMainWindow, QDialog {{
    background-color: {c.bg_primary};
}}

/* =========================================================================
   Layout Panels
   ========================================================================= */
QWidget#navigationRail {{
    background-color: {c.bg_secondary};
    border-right: 1px solid {c.border_subtle};
}}

QWidget#copilotPanel {{
    background-color: {c.bg_primary};
    border-left: 1px solid {c.border_subtle};
}}

QFrame#topHeader {{
    background-color: {c.bg_primary};
    border-bottom: 1px solid {c.border_subtle};
    min-height: 48px;
    max-height: 48px;
}}

QFrame#bottomFooter {{
    background-color: {c.bg_primary};
    border-top: 1px solid {c.border_subtle};
    min-height: 36px;
    max-height: 36px;
    color: {c.text_tertiary};
    font-size: {f.sm}px;
}}

QFrame#floatingPill {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {r.pill}px;
}}

/* =========================================================================
   Search Input
   ========================================================================= */
QLineEdit#searchBox {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {r.lg}px;
    padding: {s.xs}px {s.md}px;
    color: {c.text_primary};
    font-size: {f.base}px;
    min-height: 28px;
}}

QLineEdit#searchBox:focus {{
    border-color: {c.border_focus};
    background-color: {c.bg_primary};
}}

/* =========================================================================
   Buttons — functional, not decorative
   ========================================================================= */
QPushButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: {r.sm}px;
    padding: {s.xs}px {s.sm}px;
    color: {c.text_primary};
    font-weight: {f.medium};
    font-size: {f.base}px;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {c.bg_hover};
    border-color: {c.border_subtle};
}}

QPushButton:pressed {{
    background-color: {c.bg_pressed};
}}

QPushButton:focus {{
    border-color: {c.border_focus};
}}

QPushButton:disabled {{
    color: {c.text_tertiary};
}}

QPushButton#accentButton {{
    background-color: {c.accent_primary};
    border: 1px solid {c.accent_pressed};
    border-radius: {r.sm}px;
    color: {c.text_inverse};
    font-weight: {f.semibold};
    padding: {s.xs}px {s.md}px;
}}

QPushButton#accentButton:hover {{
    background-color: {c.accent_hover};
}}

QPushButton#accentButton:pressed {{
    background-color: {c.accent_pressed};
}}

QPushButton#dangerButton {{
    background-color: transparent;
    border: 1px solid {c.border_error};
    border-radius: {r.sm}px;
    color: {c.error_text};
}}

QPushButton#dangerButton:hover {{
    background-color: {c.error_bg};
}}

/* =========================================================================
   Tabs
   ========================================================================= */
QTabWidget::pane {{
    border: none;
    border-top: 1px solid {c.border_subtle};
    background-color: {c.bg_primary};
}}

QTabBar {{
    background-color: {c.bg_secondary};
}}

QTabBar::tab {{
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: {s.sm}px {s.lg}px;
    margin-right: 1px;
    color: {c.text_secondary};
    font-size: {f.sm}px;
    font-weight: {f.normal};
    min-width: 80px;
}}

QTabBar::tab:hover {{
    color: {c.text_primary};
    background-color: {c.bg_hover};
}}

QTabBar::tab:selected {{
    color: {c.text_accent};
    border-bottom: 2px solid {c.accent_primary};
    font-weight: {f.semibold};
    background-color: {c.bg_primary};
}}

/* =========================================================================
   Scroll Bars — thin, unobtrusive
   ========================================================================= */
QScrollArea {{
    background-color: {c.bg_primary};
    border: none;
}}

QScrollBar:vertical {{
    border: none;
    background-color: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {c.scrollbar_thumb};
    min-height: 32px;
    border-radius: 4px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c.scrollbar_thumb_hover};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    border: none;
    background-color: transparent;
    height: 8px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {c.scrollbar_thumb};
    min-width: 32px;
    border-radius: 4px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c.scrollbar_thumb_hover};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* =========================================================================
   Inputs & Form Controls
   ========================================================================= */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {r.sm}px;
    padding: {s.xs}px {s.sm}px;
    color: {c.text_primary};
    font-size: {f.base}px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {c.border_focus};
    background-color: {c.bg_primary};
}}

QLineEdit:disabled, QTextEdit:disabled {{
    color: {c.text_tertiary};
    background-color: {c.bg_secondary};
}}

QComboBox {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {r.sm}px;
    padding: {s.xs}px {s.sm}px;
    color: {c.text_primary};
    font-size: {f.base}px;
    min-height: 28px;
}}

QComboBox:focus {{
    border-color: {c.border_focus};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {r.md}px;
    selection-background-color: {c.accent_primary};
    selection-color: {c.text_inverse};
    padding: {s.xs}px;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {r.sm}px;
    padding: {s.xs}px {s.sm}px;
    color: {c.text_primary};
    font-size: {f.base}px;
    min-height: 28px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {c.border_focus};
}}

QCheckBox {{
    color: {c.text_primary};
    font-size: {f.base}px;
    spacing: {s.sm}px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {c.border_strong};
    border-radius: {r.xs}px;
    background-color: {c.bg_tertiary};
}}

QCheckBox::indicator:checked {{
    background-color: {c.accent_primary};
    border-color: {c.accent_primary};
}}

QCheckBox::indicator:hover {{
    border-color: {c.border_focus};
}}

QRadioButton {{
    color: {c.text_primary};
    font-size: {f.base}px;
    spacing: {s.sm}px;
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {c.border_strong};
    border-radius: 8px;
    background-color: {c.bg_tertiary};
}}

QRadioButton::indicator:checked {{
    background-color: {c.accent_primary};
    border-color: {c.accent_primary};
}}

QSlider::groove:horizontal {{
    height: 4px;
    background-color: {c.border_default};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    background-color: {c.accent_primary};
    border-radius: 7px;
    margin: -5px 0;
}}

QSlider::sub-page:horizontal {{
    background-color: {c.accent_primary};
    border-radius: 2px;
}}

/* =========================================================================
   Context Menus
   ========================================================================= */
QMenu {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {r.lg}px;
    padding: {s.xs}px;
}}

QMenu::item {{
    padding: 5px {s.md}px 5px {s.sm}px;
    border-radius: {r.xs}px;
    color: {c.text_primary};
    font-size: {f.base}px;
}}

QMenu::item:selected {{
    background-color: {c.accent_primary};
    color: {c.text_inverse};
}}

QMenu::item:disabled {{
    color: {c.text_tertiary};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c.border_subtle};
    margin: {s.xs}px {s.sm}px;
}}

/* =========================================================================
   Labels & Groups
   ========================================================================= */
QLabel {{
    color: {c.text_primary};
    font-size: {f.base}px;
    background-color: transparent;
}}

QGroupBox {{
    border: 1px solid {c.border_subtle};
    border-radius: {r.md}px;
    margin-top: 16px;
    padding-top: 8px;
    color: {c.text_secondary};
    font-size: {f.sm}px;
    font-weight: {f.semibold};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 {s.xs}px;
    left: {s.sm}px;
    color: {c.text_secondary};
}}

/* =========================================================================
   List, Tree & Table Views
   ========================================================================= */
QListWidget, QListView, QTreeWidget, QTreeView {{
    background-color: {c.bg_primary};
    border: 1px solid {c.border_subtle};
    border-radius: {r.md}px;
    color: {c.text_primary};
    font-size: {f.base}px;
    outline: none;
}}

QListWidget::item, QListView::item,
QTreeWidget::item, QTreeView::item {{
    padding: {s.xs}px {s.sm}px;
    border-radius: {r.xs}px;
}}

QListWidget::item:selected, QListView::item:selected,
QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {c.accent_subtle};
    color: {c.text_accent};
}}

QListWidget::item:hover, QListView::item:hover,
QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: {c.bg_hover};
}}

QTableWidget, QTableView {{
    background-color: {c.bg_primary};
    border: 1px solid {c.border_subtle};
    border-radius: {r.md}px;
    gridline-color: {c.border_subtle};
    color: {c.text_primary};
    font-size: {f.base}px;
}}

QHeaderView::section {{
    background-color: {c.bg_secondary};
    border: none;
    border-bottom: 1px solid {c.border_default};
    padding: {s.xs}px {s.sm}px;
    color: {c.text_secondary};
    font-size: {f.sm}px;
    font-weight: {f.semibold};
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {c.accent_subtle};
    color: {c.text_accent};
}}

/* =========================================================================
   Progress Bar
   ========================================================================= */
QProgressBar {{
    background-color: {c.bg_tertiary};
    border: none;
    border-radius: {r.xs}px;
    height: 6px;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: {c.accent_primary};
    border-radius: {r.xs}px;
}}

/* =========================================================================
   Splitter — invisible at rest
   ========================================================================= */
QSplitter::handle {{
    background-color: {c.splitter_handle};
}}

QSplitter::handle:hover {{
    background-color: {c.splitter_handle_hover};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

/* =========================================================================
   Tooltip
   ========================================================================= */
QToolTip {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {r.sm}px;
    padding: {s.xs}px {s.sm}px;
    color: {c.text_primary};
    font-size: {f.sm}px;
}}

/* =========================================================================
   Status Bar & Misc
   ========================================================================= */
QStatusBar {{
    background-color: {c.bg_secondary};
    color: {c.text_tertiary};
    font-size: {f.sm}px;
    border-top: 1px solid {c.border_subtle};
}}

QMessageBox {{
    background-color: {c.bg_primary};
}}

QMessageBox QLabel {{
    color: {c.text_primary};
    font-size: {f.base}px;
}}

QDialog {{
    background-color: {c.bg_primary};
}}

QDialogButtonBox QPushButton {{
    min-width: 72px;
    padding: {s.xs}px {s.md}px;
}}
"""


# =============================================================================
# THEME INSTANCES
# =============================================================================
DARK_THEME = build_theme(DARK_COLORS)
LIGHT_THEME = build_theme(LIGHT_COLORS)


# =============================================================================
# TOKEN ACCESS HELPERS
# =============================================================================
def get_dark_tokens() -> DesignTokens:
    """Returns DesignTokens instance for dark theme."""
    return DesignTokens(
        colors=DARK_COLORS,
        spacing=SHARED_SPACING,
        radius=SHARED_RADIUS,
        fonts=SHARED_FONTS,
        icons=SHARED_ICONS,
        shadows=SHARED_SHADOWS,
        z_index=ZIndexTokens(),
    )


def get_light_tokens() -> DesignTokens:
    """Returns DesignTokens instance for light theme."""
    return DesignTokens(
        colors=LIGHT_COLORS,
        spacing=SHARED_SPACING,
        radius=SHARED_RADIUS,
        fonts=SHARED_FONTS,
        icons=SHARED_ICONS,
        shadows=SHARED_SHADOWS,
        z_index=ZIndexTokens(),
    )


__all__ = [
    "DARK_THEME",
    "LIGHT_THEME",
    "DesignTokens",
    "ColorTokens",
    "SpacingTokens",
    "RadiusTokens",
    "FontTokens",
    "IconTokens",
    "ShadowTokens",
    "ZIndexTokens",
    "get_dark_tokens",
    "get_light_tokens",
]
