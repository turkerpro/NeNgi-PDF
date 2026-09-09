import os

filepath = 'nengi/core/pdf_document.py'
with open(filepath, 'r') as f:
    content = f.read()

old_except = "        except Exception as e:"
new_except = """        except fitz.FileDataError as e:
            print(f"FileDataError: Failed to open PDF file {file_path}: {e}")
            self.doc = None
            self.is_encrypted = False
            self.is_authenticated = False
            return False
        except Exception as e:"""

if old_except in content:
    content = content.replace(old_except, new_except)
    with open(filepath, 'w') as f:
        f.write(content)
