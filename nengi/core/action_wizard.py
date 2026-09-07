"""
NeNgi PDF - Action Wizard & Batch Processing Engine
Automates repetitive document tasks across batches of PDF files (compress, watermark, encrypt, convert).
"""

from __future__ import annotations
from typing import List, Dict, Any, Callable, Optional
import os
import glob
from nengi.core.pdf_document import PDFDocument
from nengi.core.pdf_optimizer import PDFOptimizer
from nengi.core.security import SecurityManager


class ActionStep:
    """Represents a single automated step in an action sequence."""

    def __init__(self, action_id: str, name: str, params: Optional[Dict[str, Any]] = None):
        self.action_id = action_id
        self.name = name
        self.params = params or {}


class ActionWizard:
    """Executes multi-step automated actions across collections of PDF documents."""

    @staticmethod
    def run_batch(
        file_paths: List[str],
        steps: List[ActionStep],
        output_dir: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[Dict[str, Any]]:
        """Executes the action steps on each PDF file and outputs to output_dir.

        Returns:
            List of results: [{"file": str, "success": bool, "message": str}, ...]
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        total_files = len(file_paths)

        for f_idx, in_path in enumerate(file_paths):
            base_name = os.path.basename(in_path)
            if progress_callback:
                progress_callback(f_idx + 1, total_files, f"İşleniyor: {base_name}")

            doc = PDFDocument()
            if not doc.open(in_path):
                results.append({
                    "file": base_name,
                    "success": False,
                    "message": "Dosya açılamadı.",
                })
                continue

            try:
                # Execute each step in sequence
                for step in steps:
                    if step.action_id == "watermark":
                        doc.add_watermark(step.params)

                    elif step.action_id == "header_footer":
                        doc.add_header_footer(step.params)

                    elif step.action_id == "encrypt":
                        pwd = step.params.get("password", "")
                        if pwd:
                            out_enc = os.path.join(output_dir, base_name)
                            SecurityManager.encrypt_document(doc, pwd, out_enc)

                # Save output
                out_path = os.path.join(output_dir, base_name)
                # If not already encrypted to out_path, save normal
                if not any(s.action_id == "encrypt" for s in steps):
                    is_compress = any(s.action_id == "compress" for s in steps)
                    if is_compress:
                        doc.doc.save(out_path, garbage=4, deflate=True, clean=True)
                    else:
                        doc.save(out_path)

                doc.close()
                results.append({
                    "file": base_name,
                    "success": True,
                    "message": "Tamamlandı",
                })
            except Exception as e:
                doc.close()
                results.append({
                    "file": base_name,
                    "success": False,
                    "message": str(e),
                })

        return results
