"""
NeNgi PDF - Form Designer Engine
Creates, modifies, and manages interactive AcroForm fields (text, checkbox,
radio, dropdown, listbox, button, signature) using PyMuPDF Widget API.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
import fitz
from .pdf_document import PDFDocument


# PyMuPDF widget type constants (safe fallbacks for all PyMuPDF versions)
FIELD_TEXT = getattr(fitz, "PDF_WIDGET_TYPE_TEXT", 4)
FIELD_CHECKBOX = getattr(fitz, "PDF_WIDGET_TYPE_CHECKBOX", 2)
FIELD_RADIO = getattr(fitz, "PDF_WIDGET_TYPE_RADIOBUTTON", 3)
FIELD_COMBO = getattr(fitz, "PDF_WIDGET_TYPE_COMBOBOX", 6)
FIELD_LISTBOX = getattr(fitz, "PDF_WIDGET_TYPE_LISTBOX", 5)
FIELD_BUTTON = getattr(fitz, "PDF_WIDGET_TYPE_BUTTON", getattr(fitz, "PDF_WIDGET_TYPE_PUSHBUTTON", 1))
FIELD_SIGNATURE = getattr(fitz, "PDF_WIDGET_TYPE_SIGNATURE", 7)

# Field flags
PDF_FIELD_IS_READ_ONLY = getattr(fitz, "PDF_FIELD_IS_READ_ONLY", 1)
PDF_FIELD_IS_REQUIRED = getattr(fitz, "PDF_FIELD_IS_REQUIRED", 2)
PDF_TX_FIELD_IS_MULTILINE = getattr(fitz, "PDF_TX_FIELD_IS_MULTILINE", 1 << 12)
PDF_TX_FIELD_IS_PASSWORD = getattr(fitz, "PDF_TX_FIELD_IS_PASSWORD", 1 << 13)
PDF_TX_FIELD_IS_COMB = getattr(fitz, "PDF_TX_FIELD_IS_COMB", 1 << 24)

# Turkish display names for field types
FIELD_TYPE_LABELS = {
    FIELD_TEXT: "Metin Alanı",
    FIELD_CHECKBOX: "Onay Kutusu",
    FIELD_RADIO: "Radyo Düğmesi",
    FIELD_COMBO: "Açılır Liste",
    FIELD_LISTBOX: "Liste Kutusu",
    FIELD_BUTTON: "Düğme",
    FIELD_SIGNATURE: "İmza Alanı",
}


class FormFieldConfig:
    """Configuration for a form field to be created."""

    def __init__(
        self,
        field_type: int = FIELD_TEXT,
        name: str = "",
        rect: Optional[fitz.Rect] = None,
        tooltip: str = "",
        value: str = "",
        default_value: str = "",
        options: Optional[List[str]] = None,
        is_readonly: bool = False,
        is_required: bool = False,
        is_multiline: bool = False,
        is_password: bool = False,
        max_length: int = 0,
        comb_chars: int = 0,
        font_name: str = "helv",
        font_size: float = 11.0,
        text_color: Tuple[float, float, float] = (0, 0, 0),
        fill_color: Optional[Tuple[float, float, float]] = (1, 1, 1),
        border_color: Optional[Tuple[float, float, float]] = (0.6, 0.6, 0.6),
        border_width: float = 1.0,
        border_style: str = "solid",
        alignment: int = 0,  # 0=left, 1=center, 2=right
        check_style: str = "check",
        export_value: str = "Yes",
    ):
        self.field_type = field_type
        self.name = name
        self.rect = rect or fitz.Rect(0, 0, 200, 25)
        self.tooltip = tooltip
        self.value = value
        self.default_value = default_value
        self.options = options or []
        self.is_readonly = is_readonly
        self.is_required = is_required
        self.is_multiline = is_multiline
        self.is_password = is_password
        self.max_length = max_length
        self.comb_chars = comb_chars
        self.font_name = font_name
        self.font_size = font_size
        self.text_color = text_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_style = border_style
        self.alignment = alignment
        self.check_style = check_style
        self.export_value = export_value


class FormDesigner:
    """Creates, inspects, and manages interactive AcroForm fields on PDF pages."""

    @staticmethod
    def create_field(
        doc: PDFDocument, page_num: int, config: FormFieldConfig
    ) -> Optional[fitz.Widget]:
        """Creates a new form field on the specified page."""
        if not doc.is_open or page_num < 0 or page_num >= doc.page_count:
            return None

        doc.save_state_for_undo()
        page = doc.get_page(page_num)

        widget = fitz.Widget()
        widget.field_type = config.field_type
        widget.field_name = config.name or f"field_{page_num}_{id(widget)}"
        widget.rect = config.rect

        if config.tooltip:
            widget.field_label = config.tooltip

        widget.text_fontsize = config.font_size
        widget.text_color = config.text_color
        widget.fill_color = config.fill_color
        widget.border_color = config.border_color
        widget.border_width = config.border_width

        border_style_map = {
            "solid": "S", "dashed": "D", "beveled": "B",
            "inset": "I", "underline": "U",
        }
        widget.border_style = border_style_map.get(config.border_style, "S")

        field_flags = 0
        if config.is_readonly:
            field_flags |= PDF_FIELD_IS_READ_ONLY
        if config.is_required:
            field_flags |= PDF_FIELD_IS_REQUIRED
        widget.field_flags = field_flags

        if config.field_type == FIELD_TEXT:
            widget.text_maxlen = config.max_length if config.max_length > 0 else 0
            if config.is_multiline:
                widget.field_flags |= PDF_TX_FIELD_IS_MULTILINE
            if config.is_password:
                widget.field_flags |= PDF_TX_FIELD_IS_PASSWORD
            if config.comb_chars > 0:
                widget.field_flags |= PDF_TX_FIELD_IS_COMB
                widget.text_maxlen = config.comb_chars
            if config.value:
                widget.field_value = config.value
            if config.default_value:
                widget.field_value = config.default_value

        elif config.field_type == FIELD_CHECKBOX:
            widget.field_value = config.value or "Off"

        elif config.field_type == FIELD_RADIO:
            widget.field_value = config.value or "Off"

        elif config.field_type in (FIELD_COMBO, FIELD_LISTBOX):
            if config.options:
                widget.choice_values = config.options
            if config.value:
                widget.field_value = config.value

        elif config.field_type == FIELD_BUTTON:
            if config.value:
                widget.button_caption = config.value

        page.add_widget(widget)
        doc.is_modified = True
        return widget

    @staticmethod
    def update_field(
        doc: PDFDocument, page_num: int, widget: fitz.Widget, config: FormFieldConfig
    ) -> bool:
        """Updates an existing form field's properties."""
        if not doc.is_open:
            return False

        doc.save_state_for_undo()
        widget.field_name = config.name
        widget.rect = config.rect
        widget.text_fontsize = config.font_size
        widget.text_color = config.text_color
        widget.fill_color = config.fill_color
        widget.border_color = config.border_color
        widget.border_width = config.border_width

        if config.field_type == FIELD_TEXT and config.value:
            widget.field_value = config.value
        elif config.field_type in (FIELD_COMBO, FIELD_LISTBOX):
            if config.options:
                widget.choice_values = config.options
            if config.value:
                widget.field_value = config.value

        widget.update()
        doc.is_modified = True
        return True

    @staticmethod
    def delete_field(doc: PDFDocument, page_num: int, widget: fitz.Widget) -> bool:
        """Removes a form field from the page."""
        if not doc.is_open:
            return False

        doc.save_state_for_undo()
        page = doc.get_page(page_num)

        for w in page.widgets():
            if w.field_name == widget.field_name and w.rect == widget.rect:
                page.delete_widget(w)
                doc.is_modified = True
                return True
        return False

    @staticmethod
    def get_fields_on_page(doc: PDFDocument, page_num: int) -> List[Dict[str, Any]]:
        """Returns all form fields on a specific page with their properties."""
        if not doc.is_open or page_num < 0 or page_num >= doc.page_count:
            return []

        page = doc.get_page(page_num)
        fields = []
        for widget in page.widgets():
            field_info = {
                "name": widget.field_name,
                "type": widget.field_type,
                "type_label": FIELD_TYPE_LABELS.get(widget.field_type, "Bilinmeyen"),
                "value": widget.field_value,
                "rect": widget.rect,
                "page": page_num,
                "readonly": bool(widget.field_flags & PDF_FIELD_IS_READ_ONLY),
                "required": bool(widget.field_flags & PDF_FIELD_IS_REQUIRED),
                "tooltip": getattr(widget, "field_label", ""),
                "font_size": widget.text_fontsize,
                "text_color": widget.text_color,
                "fill_color": widget.fill_color,
                "border_color": widget.border_color,
                "widget": widget,
            }
            if widget.field_type in (FIELD_COMBO, FIELD_LISTBOX):
                field_info["options"] = getattr(widget, "choice_values", [])
            fields.append(field_info)
        return fields

    @staticmethod
    def get_all_field_names(doc: PDFDocument) -> List[str]:
        """Returns unique names of all form fields in the document."""
        if not doc.is_open:
            return []
        names = set()
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                if widget.field_name:
                    names.add(widget.field_name)
        return sorted(names)

    @staticmethod
    def clear_all_fields(doc: PDFDocument) -> int:
        """Resets all form field values to empty/default. Returns count."""
        if not doc.is_open:
            return 0
        doc.save_state_for_undo()
        count = 0
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                if widget.field_type in (FIELD_CHECKBOX, FIELD_RADIO):
                    widget.field_value = "Off"
                else:
                    widget.field_value = ""
                widget.update()
                count += 1
        doc.is_modified = True
        return count

    @staticmethod
    def export_form_data(doc: PDFDocument, output_path: str, fmt: str = "csv") -> bool:
        """Exports form field data to file (csv, xml, or json)."""
        if not doc.is_open:
            return False

        fields = []
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                fields.append({
                    "name": widget.field_name or "",
                    "type": widget.field_type_string,
                    "value": widget.field_value or "",
                    "page": page_idx + 1,
                })
        if not fields:
            return False

        if fmt == "csv":
            import csv
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "type", "value", "page"])
                writer.writeheader()
                writer.writerows(fields)
        elif fmt == "xml":
            import xml.etree.ElementTree as ET
            root = ET.Element("form_data")
            for field in fields:
                elem = ET.SubElement(root, "field")
                for key, val in field.items():
                    elem.set(key, str(val))
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding="unicode", xml_declaration=True)
        elif fmt == "json":
            import json
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(fields, f, ensure_ascii=False, indent=2)
        return True

    @staticmethod
    def import_form_data(doc: PDFDocument, input_path: str, fmt: str = "csv") -> int:
        """Imports form field data from file. Returns count of updated fields."""
        if not doc.is_open:
            return 0

        doc.save_state_for_undo()
        data = {}

        if fmt == "csv":
            import csv
            with open(input_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    data[row["name"]] = row["value"]
        elif fmt == "xml":
            import xml.etree.ElementTree as ET
            for elem in ET.parse(input_path).findall("field"):
                data[elem.get("name", "")] = elem.get("value", "")
        elif fmt == "json":
            import json
            with open(input_path, "r", encoding="utf-8") as f:
                for entry in json.load(f):
                    data[entry["name"]] = entry["value"]

        count = 0
        for page_idx in range(doc.page_count):
            page = doc.get_page(page_idx)
            for widget in page.widgets():
                if widget.field_name in data:
                    widget.field_value = str(data[widget.field_name])
                    widget.update()
                    count += 1
        doc.is_modified = True
        return count

    @staticmethod
    def auto_detect_fields(doc: PDFDocument, page_num: int) -> List[FormFieldConfig]:
        """Auto-detect potential form field locations on a page by analyzing
        horizontal lines, text labels ending with ':', and rectangular shapes."""
        if not doc.is_open or page_num < 0 or page_num >= doc.page_count:
            return []

        page = doc.get_page(page_num)
        suggestions = []

        # Strategy 1: Find horizontal lines that could be text input underlines
        paths = page.get_drawings()
        horizontal_lines = []
        for path in paths:
            for item in path.get("items", []):
                if item[0] == "l":
                    p1, p2 = item[1], item[2]
                    if abs(p1.y - p2.y) < 2 and abs(p1.x - p2.x) > 50:
                        horizontal_lines.append(
                            fitz.Rect(min(p1.x, p2.x), p1.y - 18,
                                      max(p1.x, p2.x), p1.y + 2)
                        )

        # Strategy 2: Labels ending with ':' → text field to the right
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                line_text = line_text.strip()
                if line_text.endswith(":") or line_text.endswith(": "):
                    bbox = line.get("bbox", (0, 0, 0, 0))
                    field_rect = fitz.Rect(bbox[2] + 10, bbox[1] - 2,
                                           bbox[2] + 200, bbox[3] + 2)
                    label = line_text.rstrip(": ")
                    suggestions.append(FormFieldConfig(
                        field_type=FIELD_TEXT,
                        name=label.lower().replace(" ", "_"),
                        rect=field_rect,
                        tooltip=label,
                    ))

        # Strategy 3: Small squares → checkboxes
        for path in paths:
            rect = fitz.Rect(path.get("rect", (0, 0, 0, 0)))
            w, h = rect.width, rect.height
            if 8 < w < 20 and 8 < h < 20 and abs(w - h) < 3:
                suggestions.append(FormFieldConfig(
                    field_type=FIELD_CHECKBOX,
                    name=f"check_{int(rect.x0)}_{int(rect.y0)}",
                    rect=rect,
                ))

        for rect in horizontal_lines:
            suggestions.append(FormFieldConfig(
                field_type=FIELD_TEXT,
                name=f"text_{int(rect.x0)}_{int(rect.y0)}",
                rect=rect,
            ))

        return suggestions
