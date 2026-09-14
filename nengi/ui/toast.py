"""
Toast notification widget for NeNgi PDF.
Shows temporary error/warning/info messages with optional detail hint.
"""
from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtGui import QColor, QPainter, QBrush, QFont, QPainterPath


class Toast(QWidget):
    """A toast notification that appears at the bottom-right of its parent."""
    
    def __init__(
        self,
        parent: Optional["ToastManager"] = None,
        message: str = "",
        hint: Optional[str] = None,
        duration: int = 4000,
        level: str = "error"  # "error", "warning", "info", "success"
    ):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self._level = level
        self._duration = duration
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content container with rounded corners
        container = QWidget()
        container.setObjectName("toastContainer")
        
        # Color by level
        colors = {
            "error": ("#DC2626", "#FEF2F2"),      # red
            "warning": ("#D97706", "#FFFBEB"),    # amber
            "info": ("#2563EB", "#EFF6FF"),       # blue
            "success": ("#16A34A", "#F0FDF4"),    # green
        }
        bg_color, text_color = colors.get(level, colors["error"])
        
        container.setStyleSheet(f"""
            QWidget#toastContainer {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 8px;
                padding: 12px 16px;
                min-width: 280px;
                max-width: 420px;
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 12, 16, 12)
        container_layout.setSpacing(6)
        
        # Title row (icon + message)
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        icons = {
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ",
            "success": "✓"
        }
        icon_label = QLabel(icons.get(level, "ℹ"))
        icon_label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: bold;")
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {text_color}; font-size: 13px;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(msg_label, 1)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {text_color};
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background: rgba(0,0,0,0.1); }}
        """)
        close_btn.clicked.connect(self._dismiss)
        title_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignTop)
        
        container_layout.addLayout(title_layout)
        
        # Hint (detail)
        if hint:
            hint_label = QLabel(hint)
            hint_label.setWordWrap(True)
            hint_label.setStyleSheet(f"color: {text_color}; font-size: 11px; opacity: 0.85;")
            container_layout.addWidget(hint_label)
        
        layout.addWidget(container)
        
        # Animation
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Auto-dismiss timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)
        self._timer.start(duration)
        
        # Position at parent's bottom-right
        if parent:
            parent.toast_added(self)
    
    def _dismiss(self):
        """Fade out and delete."""
        if self._timer.isActive():
            self._timer.stop()
        
        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(200)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(self.deleteLater)
        fade.start()
    
    def paintEvent(self, event):
        """Custom paint for rounded corners with shadow."""
        super().paintEvent(event)


class ToastManager(QWidget):
    """Manages toast queue and positioning for a parent window."""
    
    def __init__(self, parent: Optional["MainWindow"] = None):
        super().__init__(parent)
        self._toasts = []
        self._parent = parent
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def toast_added(self, toast: Toast):
        """Called when a new toast is created."""
        # Remove oldest if too many
        while len(self._toasts) >= 5:
            oldest = self._toasts.pop(0)
            oldest._dismiss()
        
        self._toasts.append(toast)
        self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Stack toasts vertically at bottom-right."""
        if not self._parent:
            return
        
        margin = 16
        spacing = 8
        y = self._parent.height() - margin
        
        for toast in reversed(self._toasts):
            toast_width = toast.sizeHint().width()
            toast.move(
                self._parent.width() - toast_width - margin,
                y - toast.height()
            )
            y -= toast.height() + spacing
            toast.show()


def show_error_toast(parent: Optional["MainWindow"], message: str, hint: Optional[str] = None):
    """Convenience function to show an error toast."""
    if parent and hasattr(parent, '_toast_manager'):
        toast = Toast(parent._toast_manager, message, hint, level="error")
    else:
        # Fallback to simple message box
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(parent, "Hata", f"{message}\n\n{hint}" if hint else message)


def show_warning_toast(parent: Optional["MainWindow"], message: str, hint: Optional[str] = None):
    if parent and hasattr(parent, '_toast_manager'):
        Toast(parent._toast_manager, message, hint, level="warning")


def show_info_toast(parent: Optional["MainWindow"], message: str, hint: Optional[str] = None):
    if parent and hasattr(parent, '_toast_manager'):
        Toast(parent._toast_manager, message, hint, level="info")


def show_success_toast(parent: Optional["MainWindow"], message: str, hint: Optional[str] = None):
    if parent and hasattr(parent, '_toast_manager'):
        Toast(parent._toast_manager, message, hint, level="success")