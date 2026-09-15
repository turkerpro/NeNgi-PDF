"""
NeNgi PDF - NextGen Studio Design & Windows 11 Fluent Theme
Design token system for consistent, maintainable theming.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ColorTokens:
    """Color palette tokens - semantic names, not hardcoded values."""
    # Background hierarchy
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_hover: str
    bg_pressed: str
    bg_overlay: str
    
    # Border hierarchy
    border_subtle: str
    border_default: str
    border_strong: str
    border_focus: str
    border_error: str
    
    # Text hierarchy
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_inverse: str
    text_accent: str
    text_error: str
    
    # Accent / Brand
    accent_primary: str
    accent_hover: str
    accent_pressed: str
    accent_subtle: str
    
    # Semantic states
    success_bg: str
    success_text: str
    warning_bg: str
    warning_text: str
    error_bg: str
    error_text: str
    info_bg: str
    info_text: str
    
    # Scrollbar
    scrollbar_track: str
    scrollbar_thumb: str
    scrollbar_thumb_hover: str
    
    # Splitter
    splitter_handle: str
    splitter_handle_hover: str


@dataclass(frozen=True)
class SpacingTokens:
    """Spacing scale - 4px base unit."""
    xs: int = 4   # 4px
    sm: int = 8   # 8px
    md: int = 12  # 12px
    lg: int = 16  # 16px
    xl: int = 24  # 24px
    xxl: int = 32 # 32px


@dataclass(frozen=True)
class RadiusTokens:
    """Border radius scale."""
    xs: int = 3   # 3px - small chips, badges
    sm: int = 4   # 4px - buttons, inputs
    md: int = 6   # 6px - standard cards, buttons
    lg: int = 8   # 8px - panels, menus
    xl: int = 12  # 12px - large cards
    xxl: int = 16 # 16px - large panels
    pill: int = 24 # 24px - pill/capsule shapes
    circle: int = 9999 # 9999px - fully rounded


@dataclass(frozen=True)
class FontTokens:
    """Typography scale."""
    family: str = "'Segoe UI Variable Text', 'Segoe UI', system-ui, sans-serif"
    mono_family: str = "'JetBrains Mono', 'Consolas', monospace"
    
    # Sizes (px)
    xs: int = 10
    sm: int = 11
    base: int = 12
    lg: int = 13
    xl: int = 14
    xxl: int = 16
    xxxl: int = 20
    
    # Weights
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
    """Shadow/elevation tokens."""
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
    
    # Animation
    transition_fast: str = "150ms ease"
    transition_normal: str = "200ms ease"
    transition_slow: str = "300ms ease"
    
    # Breakpoints (for responsive if needed)
    bp_sm: int = 640
    bp_md: int = 768
    bp_lg: int = 1024
    bp_xl: int = 1280


# =============================================================================
# DARK THEME TOKENS
# =============================================================================
DARK_COLORS = ColorTokens(
    bg_primary="#17181A",
    bg_secondary="#1A1C1E",
    bg_tertiary="#1E2024",
    bg_hover="#24272D",
    bg_pressed="#1B1E22",
    bg_overlay="#00000080",
    
    border_subtle="#26292E",
    border_default="#2E3238",
    border_strong="#353942",
    border_focus="#0078D4",
    border_error="#D13438",
    
    text_primary="#EDEDED",
    text_secondary="#A0A0A0",
    text_tertiary="#6A6A6A",
    text_inverse="#17181A",
    text_accent="#0078D4",
    text_error="#FF6B6B",
    
    accent_primary="#0078D4",
    accent_hover="#1084D9",
    accent_pressed="#005A9E",
    accent_subtle="#1A3C5E",
    
    success_bg="#166534",
    success_text="#BBF7D0",
    warning_bg="#854D0E",
    warning_text="#FDE68A",
    error_bg="#991B1B",
    error_text="#FECACA",
    info_bg="#1E3A8A",
    info_text="#BFDBFE",
    
    scrollbar_track="#17181A",
    scrollbar_thumb="#33373E",
    scrollbar_thumb_hover="#4A505A",
    
    splitter_handle="#202226",
    splitter_handle_hover="#0078D4",
)


LIGHT_COLORS = ColorTokens(
    bg_primary="#FFFFFF",
    bg_secondary="#F8F9FA",
    bg_tertiary="#F1F3F5",
    bg_hover="#F3F4F6",
    bg_pressed="#EBECF0",
    bg_overlay="#0000001A",
    
    border_subtle="#E1E4E8",
    border_default="#D0D7DE",
    border_strong="#AFB8C1",
    border_focus="#0078D4",
    border_error="#D13438",
    
    text_primary="#1F2328",
    text_secondary="#57606A",
    text_tertiary="#8C929C",
    text_inverse="#FFFFFF",
    text_accent="#0078D4",
    text_error="#CF222E",
    
    accent_primary="#0078D4",
    accent_hover="#1084D9",
    accent_pressed="#005A9E",
    accent_subtle="#DBEAFE",
    
    success_bg="#F0FDF4",
    success_text="#166534",
    warning_bg="#FFFBEB",
    warning_text="#854D0E",
    error_bg="#FEF2F2",
    error_text="#DC2626",
    info_bg="#EFF6FF",
    info_text="#1E40AF",
    
    scrollbar_track="#F5F7FA",
    scrollbar_thumb="#C0C6CF",
    scrollbar_thumb_hover="#9CA3AF",
    
    splitter_handle="#E1E4E8",
    splitter_handle_hover="#0078D4",
)


# Shared tokens (same for both themes)
SHARED_SPACING = SpacingTokens()
SHARED_RADIUS = RadiusTokens()
SHARED_FONTS = FontTokens()
SHARED_ICONS = IconTokens()
SHARED_SHADOWS = ShadowTokens()
SHARED_Z_INDEX = ZIndexTokens()


# =============================================================================
# THEME STRING BUILDERS
# =============================================================================
def build_theme(colors: ColorTokens) -> str:
    """Build complete QSS theme string from color tokens."""
    c = colors
    r = SHARED_RADIUS
    s = SHARED_SPACING
    f = SHARED_FONTS
    i = SHARED_ICONS
    
    return f"""
/* =========================================================================
   NeNgi PDF - NextGen Studio Design System
   Generated from DesignTokens
   ========================================================================= */

/* =========================================================================
   Global Window & Font Hierarchy
   ========================================================================= */
QWidget {{
    background-color: {c.bg_primary};
    color: {c.text_primary};
    font-family: {SHARED_FONTS.family};
    font-size: {SHARED_FONTS.base}px;
}}

QMainWindow, QDialog {{
    background-color: {c.bg_primary};
}}

/* =========================================================================
   Left Navigation Rail
   ========================================================================= */
QWidget#navigationRail {{
    background-color: {c.bg_secondary};
    border-right: 1px solid {c.border_subtle};
}}

/* Right Copilot Panel */
QWidget#copilotPanel {{
    background-color: {c.bg_primary};
    border-left: 1px solid {c.border_subtle};
}}

/* Top Global Header */
QFrame#topHeader {{
    background-color: {c.bg_primary};
    border-bottom: 1px solid {c.border_subtle};
}}

/* Search Bar Pill */
QLineEdit#searchBox {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {SHARED_RADIUS.xl}px;
    padding: {SHARED_SPACING.sm}px {SHARED_SPACING.md}px;
    color: {c.text_primary};
    font-size: {SHARED_FONTS.base}px;
}}

QLineEdit#searchBox:focus {{
    border-color: {c.border_focus};
    background-color: {c.bg_hover};
}}

/* Floating Bottom Capsule / Island Toolbar */
QFrame#floatingPill {{
    background-color: {c.bg_tertiary};
    border: 1px solid {c.border_default};
    border-radius: {SHARED_RADIUS.pill}px;
}}

/* Bottom Pagination & Zoom Footer */
QFrame#bottomFooter {{
    background-color: {c.bg_primary};
    border-top: 1px solid {c.border_subtle};
    color: {c.text_tertiary};
    font-size: {SHARED_FONTS.sm}px;
}}

/* =========================================================================
   Buttons
   ========================================================================= */
QPushButton {{
    background-color: {c.bg_hover};
    border: 1px solid {c.border_default};
    border-radius: {SHARED_RADIUS.md}px;
    padding: {SHARED_SPACING.sm}px {SHARED_SPACING.md}px;
    color: {c.text_primary};
    font-weight: {SHARED_FONTS.medium};
    font-size: {SHARED_FONTS.base}px;
}}

QPushButton:hover {{
    background-color: {c.bg_pressed};
    border-color: {c.border_strong};
    color: {c.text_primary};
}}

QPushButton:pressed {{
    background-color: {c.bg_secondary};
}}

QPushButton#accentButton {{
    background-color: {c.accent_primary};
    border: 1px solid {c.accent_pressed};
    color: {c.text_inverse};
    font-weight: {SHARED_FONTS.semibold};
}}

QPushButton#accentButton:hover {{
    background-color: {c.accent_hover};
    border-color: {c.accent_primary};
}}

QPushButton#accentButton:pressed {{
    background-color: {c.accent_pressed};
}}

QPushButton#dangerButton {{
    background-color: {c.error_bg};
    border: 1px solid {c.border_error};
    color: {c.error_text};
}}

QPushButton#dangerButton:hover {{
    background-color: #B91C1C;
    border-color: #991B1B;
}}

/* =========================================================================
   Tabs
   ========================================================================= */
QTabWidget::pane {{
    border: 1px solid {c.border_subtle};
    background-color: {c.bg_primary};
    top: -1px;
}}

QTabBar::tab {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_subtle};
    border-bottom: none;
    border-top-left-radius: {SHARED_RADIUS.md}px;
    border-top-right-radius: {SHARED_RADIUS.md}px;
    padding: 7px 18px;
    margin-right: 2px;
    color: {c.text_tertiary};
    font-size: {SHARED_FONTS.sm}px;
    font-weight: {SHARED_FONTS.medium};
}}

QTabBar::tab:hover {{
    background-color: {c.bg_hover};
    color: {c.text_primary};
}}

QTabBar::tab:selected {{
    background-color: {c.bg_primary};
    color: {c.text_accent};
    border-top: 2px solid {c.accent_primary};
    border-left: 1px solid {c.border_subtle};
    border-right: 1px solid {c.border_subtle};
    font-weight: {SHARED_FONTS.semibold};
}}

/* =========================================================================
   Scroll Areas
   ========================================================================= */
QScrollArea {{
    background-color: {c.bg_primary};
    border: none;
}}

QScrollBar:vertical {{
    border: none;
    background-color: {c.scrollbar_track};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {c.scrollbar_thumb};
    min-height: 25px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c.scrollbar_thumb_hover};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    border: none;
    background-color: {c.scrollbar_track};
    height: 10px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c.scrollbar_thumb};
    min-width: 25px;
    border-radius: 5px;
}}

/* =========================================================================
   Context Menu
   ========================================================================= */
QMenu {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {SHARED_RADIUS.lg}px;
    padding: {SHARED_SPACING.xs}px;
}}

QMenu::item {{
    padding: {SHARED_SPACING.xs}px {SHARED_SPACING.md}px {SHARED_SPACING.xs}px {SHARED_SPACING.sm}px;
    border-radius: {SHARED_RADIUS.sm}px;
    color: {c.text_primary};
}}

QMenu::item:selected {{
    background-color: {c.accent_primary};
    color: {c.text_inverse};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c.border_subtle};
    margin: {SHARED_SPACING.xs}px {SHARED_SPACING.sm}px;
}}

/* =========================================================================
   Splitter
   ========================================================================= */
QSplitter::handle {{
    background-color: {c.splitter_handle};
}}

QSplitter::handle:hover {{
    background-color: {c.splitter_handle_hover};
}}

/* =========================================================================
   Tooltip
   ========================================================================= */
QToolTip {{
    background-color: {c.bg_secondary};
    border: 1px solid {c.border_default};
    border-radius: {SHARED_RADIUS.md}px;
    padding: {SHARED_SPACING.sm}px {SHARED_SPACING.md}px;
    color: {c.text_primary};
    font-size: {SHARED_FONTS.sm}px;
}}
"""


# =============================================================================
# THEME INSTANCES
# =============================================================================
DARK_THEME = build_theme(DARK_COLORS)
LIGHT_THEME = build_theme(LIGHT_COLORS)


# =============================================================================
# TOKEN ACCESS HELPERS (for Python-side usage)
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


# Re-export for backward compatibility
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