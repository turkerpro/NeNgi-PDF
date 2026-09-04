"""
NeNgi PDF - High-Resolution Printing & PDF Printer Engine
Provides vector/raster printing to physical printers and virtual PDF printers
with page range selection, copy count, and orientation auto-detection.
"""

from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

from nengi.core.pdf_document import PDFDocument


class PDFPrinter:
    """Handles printing documents through Qt's print subsystem."""

    @staticmethod
    def print_document(doc: PDFDocument, parent: Optional[QWidget] = None, current_page: int = 0) -> bool:
        """
        Opens Windows Print Dialog and prints the PDF document to chosen printer.
        """
        if not doc or not doc.is_open or doc.page_count == 0:
            if parent:
                QMessageBox.warning(parent, "Uyarı", "Yazdırılacak belge açık değil.")
            return False

        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            doc_name = getattr(doc, "file_name", None) or (os.path.basename(doc.file_path) if getattr(doc, "file_path", None) else "NeNgi_PDF_Yazdir")
            printer.setDocName(str(doc_name))
            printer.setFromTo(1, doc.page_count)

            dialog = QPrintDialog(printer, parent)
            dialog.setWindowTitle("🖨️ Belgeyi Yazdır - NeNgi PDF")
            if dialog.exec() != QPrintDialog.DialogCode.Accepted:
                return False

            # Determine page range
            from_page = 0
            to_page = doc.page_count - 1
            if printer.printRange() == QPrinter.PrintRange.PageRange:
                from_page = max(0, printer.fromPage() - 1)
                to_page = min(doc.page_count - 1, printer.toPage() - 1)
            elif printer.printRange() == QPrinter.PrintRange.CurrentPage:
                from_page = max(0, min(doc.page_count - 1, current_page))
                to_page = from_page

            painter = QPainter()
            if not painter.begin(printer):
                if parent:
                    QMessageBox.critical(parent, "Yazdırma Hatası", "Yazıcı başlatılamadı.")
                return False

            try:
                for idx, page_num in enumerate(range(from_page, to_page + 1)):
                    if idx > 0:
                        printer.newPage()

                    # Render page at 300 DPI high resolution for sharp print quality
                    qimg = doc.render_page_qimage(page_num, dpi=300)
                    if qimg.isNull():
                        continue

                    # Scale to fit printable page rect while preserving aspect ratio
                    page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
                    scaled_size = qimg.size().scaled(
                        int(page_rect.width()), int(page_rect.height()),
                        Qt.AspectRatioMode.KeepAspectRatio
                    )
                    x = page_rect.left() + (page_rect.width() - scaled_size.width()) / 2
                    y = page_rect.top() + (page_rect.height() - scaled_size.height()) / 2
                    dest_rect = QRectF(x, y, scaled_size.width(), scaled_size.height())

                    painter.drawImage(dest_rect, qimg)
                return True
            finally:
                if painter.isActive():
                    painter.end()

        except Exception as e:
            if parent:
                QMessageBox.critical(parent, "Yazdırma Hatası", f"Yazdırma sırasında bir hata oluştu:\n{e}")
            return False
