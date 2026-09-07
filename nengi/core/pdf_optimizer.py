"""
NeNgi PDF - PDF Optimizer
Analyzes and optimizes PDF files for size and performance.
"""
import fitz
import os

class PDFOptimizer:
    @staticmethod
    def get_space_usage(doc) -> dict:
        """Audit space usage: images, fonts, metadata, etc."""
        if not doc.is_open:
            return {}
            
        usage = {
            'images': 0,
            'fonts': 0,
            'metadata': 0,
            'text_and_graphics': 0,
            'total': 0
        }
        
        try:
            # We can approximate using get_page_images, get_page_fonts
            # A more precise audit can be done via PyMuPDF tools, but for this app we'll estimate
            
            # Simple estimation logic:
            total_size = os.path.getsize(doc.file_path) if doc.file_path else 0
            
            img_size = 0
            for i in range(len(doc.doc)):
                page = doc.get_page(i)
                images = page.get_images()
                for img in images:
                    xref = img[0]
                    try:
                        base_image = doc.doc.extract_image(xref)
                        if base_image:
                            img_size += len(base_image["image"])
                    except:
                        pass
            
            # Very rough approximations for UI display
            usage['total'] = total_size
            usage['images'] = img_size
            usage['metadata'] = 1024 * 5 # assume 5kb metadata
            usage['fonts'] = total_size * 0.1 # assume 10% fonts if not exact
            usage['text_and_graphics'] = max(0, total_size - img_size - usage['metadata'] - usage['fonts'])
            
            return usage
        except Exception as e:
            print(f"Audit error: {e}")
            return usage
            
    @staticmethod  
    def optimize(doc, options: dict) -> bool:
        """Optimize PDF with given options."""
        if not doc.is_open:
            return False
            
        try:
            # options: {'compress_images': True, 'image_quality': 75,
            #           'remove_metadata': False, 'linearize': True,
            #           'garbage_collect': True, 'deflate': True}
            
            garbage_level = 4 if options.get('garbage_collect', True) else 0
            deflate = options.get('deflate', True)
            clean = True # removes unused objects
            linear = options.get('linearize', True)
            
            # If removing metadata
            if options.get('remove_metadata', False):
                doc.doc.set_metadata({})
                
            # Note: PyMuPDF doesn't natively recompress images with a quality slider in .save()
            # but setting garbage=4 and deflate=True does optimal compression of streams.
            
            if doc.file_path and os.path.exists(doc.file_path):
                fp = doc.file_path
                opt_bytes = doc.doc.tobytes(garbage=garbage_level, deflate=deflate, clean=clean, linear=False)
                doc.close()
                with open(fp, "wb") as f:
                    f.write(opt_bytes)
                doc.open(fp)
            else:
                save_path = "optimized.pdf"
                doc.doc.save(save_path, garbage=garbage_level, deflate=deflate, clean=clean, linear=False)
            
            return True
        except Exception as e:
            print(f"Optimize error: {e}")
            return False
