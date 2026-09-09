import os

filepath = 'nengi/ui/pdf_view.py'
with open(filepath, 'r') as f:
    content = f.read()

old_set_tool_mode = """    def set_tool_mode(self, mode: str, stamp_path: Optional[str] = None):
        \"\"\"Switches active tool: 'view', 'whiteout', 'text', 'stamp'.\"\"\"
        self.current_mode = mode
        self.stamp_image_path = stamp_path
        
        cursor_map = {
            "view": Qt.CursorShape.ArrowCursor,
            "whiteout": Qt.CursorShape.CrossCursor,
            "text": Qt.CursorShape.IBeamCursor,
            "stamp": Qt.CursorShape.PointingHandCursor
        }
        cursor = cursor_map.get(mode, Qt.CursorShape.ArrowCursor)
        self.setCursor(cursor)

        for pw in self.page_widgets:
            pw.mode = mode
            pw.stamp_image_path = stamp_path"""

new_set_tool_mode = """    def set_tool_mode(self, mode: str, stamp_path: Optional[str] = None):
        \"\"\"Switches active tool.\"\"\"
        self.current_mode = mode
        self.stamp_image_path = stamp_path
        
        cross_cursors = ["whiteout", "line", "arrow", "rect", "oval", "polygon", "cloud", "draw"]
        text_cursors = ["text", "highlight", "underline", "strikethrough"]
        
        if mode in cross_cursors:
            cursor = Qt.CursorShape.CrossCursor
        elif mode in text_cursors:
            cursor = Qt.CursorShape.IBeamCursor
        elif mode in ["stamp", "sticky_note"]:
            cursor = Qt.CursorShape.PointingHandCursor
        else:
            cursor = Qt.CursorShape.ArrowCursor
            
        self.setCursor(cursor)

        for pw in self.page_widgets:
            pw.mode = mode
            pw.stamp_image_path = stamp_path"""

if old_set_tool_mode in content:
    content = content.replace(old_set_tool_mode, new_set_tool_mode)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find set_tool_mode")
