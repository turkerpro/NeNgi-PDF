import os

filepath = 'nengi/ui/main_window.py'
with open(filepath, 'r') as f:
    content = f.read()

old_tool_handling = """    def _on_floating_tool_changed(self, tool_id: str):
        if tool_id in ["view", "text", "whiteout"]:
            self._set_viewer_tool(tool_id)
        elif tool_id == "edit_text":
            self._edit_selected_text_trigger()
        elif tool_id == "signature":
            self._open_signature_dialog()
        elif tool_id == "rotate":
            self._rotate_current_page()
        elif tool_id == "pages":
            self._open_page_manager()
        elif tool_id == "undo":
            self.undo_current()
        elif tool_id == "redo":
            self.redo_current()"""

new_tool_handling = """    def _on_floating_tool_changed(self, tool_id: str):
        if tool_id in ["view", "text", "whiteout", "highlight", "underline", "strikethrough", 
                       "line", "arrow", "rect", "oval", "polygon", "cloud", "draw", "sticky_note", "stamp"]:
            self._set_viewer_tool(tool_id)
        elif tool_id == "edit_text":
            self._edit_selected_text_trigger()
        elif tool_id == "signature":
            self._open_signature_dialog()
        elif tool_id == "rotate":
            self._rotate_current_page()
        elif tool_id == "pages":
            self._open_page_manager()
        elif tool_id == "undo":
            self.undo_current()
        elif tool_id == "redo":
            self.redo_current()"""

if old_tool_handling in content:
    content = content.replace(old_tool_handling, new_tool_handling)
    with open(filepath, 'w') as f:
        f.write(content)
else:
    print("Could not find old_tool_handling")
