import os

for filepath in ['nengi/ui/main_window.py', 'installer.nsi', '.github/workflows/build-windows.yml']:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new = content.replace('1.8.1', '1.8.2').replace('v1.8.1', 'v1.8.2')
    if new != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new)
        print(f"Updated {filepath}")
