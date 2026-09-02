"""
NeNgi PDF - External Image Roundtrip Editing Handler
Launches external image editors (MS Paint, Photoshop, etc.), monitors
file changes via QFileSystemWatcher, and automatically updates the PDF
in-place when the user saves the image.
"""

from __future__ import annotations
import os
import sys
import subprocess
import tempfile
import time
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QFileSystemWatcher, QTimer
import pymupdf as fitz
from .pdf_document import PDFDocument


class ImageRoundtripHandler(QObject):
    """Manages editing images/pages in external editors with auto-reload."""

    # Emitted when an edited image was saved and applied to the PDF document
    image_updated = pyqtSignal(int, int)  # (page_num, xref)
    status_message = pyqtSignal(str)      # User-friendly status message

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self._on_file_changed)
        
        # Maps temp_filepath -> session_info
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Debounce timer to avoid multiple reloads while external app writes
        self._pending_files: Dict[str, float] = {}
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setInterval(400)
        self._debounce_timer.timeout.connect(self._process_pending_reloads)

        # Temporary workspace
        self.temp_dir = os.path.join(tempfile.gettempdir(), "nengi_pdf_edits")
        os.makedirs(self.temp_dir, exist_ok=True)

    def edit_embedded_image(self, doc: PDFDocument, page_num: int, xref: int) -> Optional[str]:
        """
        Extracts an embedded image to a temp file, watches it, and launches
        the external editor.
        """
        if not doc.is_open:
            return None

        try:
            image_bytes, ext = doc.extract_image_bytes(xref)
            temp_filename = f"edit_img_p{page_num + 1}_xref{xref}_{int(time.time())}.{ext}"
            temp_path = os.path.join(self.temp_dir, temp_filename)

            with open(temp_path, "wb") as f:
                f.write(image_bytes)

            session = {
                "doc": doc,
                "page_num": page_num,
                "xref": xref,
                "type": "embedded",
                "temp_path": temp_path
            }
            self.sessions[temp_path] = session
            self.watcher.addPath(temp_path)

            self._launch_editor(temp_path)
            self.status_message.emit(
                f"Resim harici düzenleyicide açıldı. Düzenleyip kaydettiğinizde (Ctrl+S) PDF otomatik güncellenecek."
            )
            return temp_path
        except Exception as e:
            self.status_message.emit(f"Resim dışa aktarılırken hata: {e}")
            return None

    def edit_scanned_page(self, doc: PDFDocument, page_num: int, dpi: int = 300) -> Optional[str]:
        """
        Renders an entire scanned page to high-res PNG, watches it, and opens
        in external editor to clean pen marks, handwriting, or stains.
        """
        if not doc.is_open:
            return None

        try:
            page = doc.get_page(page_num)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            temp_filename = f"scanned_page_{page_num + 1}_{int(time.time())}.png"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            pix.save(temp_path)

            session = {
                "doc": doc,
                "page_num": page_num,
                "xref": -1,
                "type": "scanned_page",
                "temp_path": temp_path
            }
            self.sessions[temp_path] = session
            self.watcher.addPath(temp_path)

            self._launch_editor(temp_path)
            self.status_message.emit(
                f"Sayfa {page_num + 1} resim editöründe açıldı. Temizleyip kaydettiğinizde PDF otomatik güncellenecektir."
            )
            return temp_path
        except Exception as e:
            self.status_message.emit(f"Sayfa resim editörüne gönderilirken hata: {e}")
            return None

    def _launch_editor(self, file_path: str):
        """Launches the platform-appropriate image editor."""
        try:
            if sys.platform == "win32":
                # On Windows: try mspaint first for instant pen/eraser editing, or default viewer
                try:
                    subprocess.Popen(["mspaint", file_path])
                except FileNotFoundError:
                    os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                # Linux / Unix
                subprocess.Popen(["xdg-open", file_path])
        except Exception as e:
            print(f"Could not launch image editor: {e}")

    def _on_file_changed(self, file_path: str):
        """Called by QFileSystemWatcher when the watched temp file is modified."""
        # Re-add path because some editors rewrite files by replacing them
        if os.path.exists(file_path):
            self.watcher.addPath(file_path)
        self._pending_files[file_path] = time.time()
        self._debounce_timer.start()

    def _process_pending_reloads(self):
        """Applies updates after debounce timer completes."""
        self._debounce_timer.stop()
        now = time.time()
        reloaded_files = []

        for file_path, ts in list(self._pending_files.items()):
            if now - ts >= 0.3:
                session = self.sessions.get(file_path)
                if session and os.path.exists(file_path):
                    self._apply_file_update(session)
                reloaded_files.append(file_path)

        for rf in reloaded_files:
            self._pending_files.pop(rf, None)

    def _apply_file_update(self, session: Dict[str, Any]):
        """Applies edited image back to PDF document."""
        doc: PDFDocument = session["doc"]
        page_num: int = session["page_num"]
        xref: int = session["xref"]
        temp_path: str = session["temp_path"]
        sess_type: str = session["type"]

        success = False
        if sess_type == "embedded" and xref > 0:
            success = doc.replace_image(xref, temp_path)
        elif sess_type == "scanned_page":
            success = doc.replace_page_with_scanned_image(page_num, temp_path)

        if success:
            self.status_message.emit(f"Sayfa {page_num + 1} düzenlenen görselle başarıyla güncellendi!")
            self.image_updated.emit(page_num, xref)
        else:
            self.status_message.emit("Görsel güncellenirken bir sorun oluştu.")
