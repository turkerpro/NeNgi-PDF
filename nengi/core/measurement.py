"""
NeNgi PDF - Precision Measurement Engine
Calculates real-world distances, perimeters, and polygon areas from PDF vector points
using customizable scale ratios and unit conversion (mm, cm, m, inch, pt).
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Any, Optional
import math
import pymupdf as fitz
from nengi.core.pdf_document import PDFDocument


# Standard PDF points per unit (1 inch = 72 points)
POINTS_PER_INCH = 72.0
POINTS_PER_MM = 72.0 / 25.4
POINTS_PER_CM = 72.0 / 2.54
POINTS_PER_M = (72.0 / 2.54) * 100.0


class ScaleRatio:
    """Represents real-world scale ratio (e.g., 1 cm on page = 5 meters in real world)."""

    def __init__(
        self,
        page_value: float = 1.0,
        page_unit: str = "cm",
        real_value: float = 1.0,
        real_unit: str = "m",
    ):
        self.page_value = max(0.001, page_value)
        self.page_unit = page_unit.lower()
        self.real_value = max(0.001, real_value)
        self.real_unit = real_unit.lower()

    def get_points_per_real_unit(self) -> float:
        """Returns how many PDF points correspond to 1 real unit."""
        if self.page_unit == "mm":
            pts_on_page = self.page_value * POINTS_PER_MM
        elif self.page_unit == "cm":
            pts_on_page = self.page_value * POINTS_PER_CM
        elif self.page_unit == "inch":
            pts_on_page = self.page_value * POINTS_PER_INCH
        else:  # "pt"
            pts_on_page = self.page_value

        return pts_on_page / self.real_value

    def points_to_real_distance(self, pts: float) -> float:
        """Converts points distance to real unit distance."""
        pts_per_unit = self.get_points_per_real_unit()
        if pts_per_unit <= 0:
            return 0.0
        return pts / pts_per_unit

    def points_sq_to_real_area(self, pts_sq: float) -> float:
        """Converts square points to real square units."""
        pts_per_unit = self.get_points_per_real_unit()
        if pts_per_unit <= 0:
            return 0.0
        return pts_sq / (pts_per_unit ** 2)

    def format_distance(self, pts: float) -> str:
        dist = self.points_to_real_distance(pts)
        return f"{dist:.2f} {self.real_unit}"

    def format_area(self, pts_sq: float) -> str:
        area = self.points_sq_to_real_area(pts_sq)
        return f"{area:.2f} {self.real_unit}²"


class MeasurementEngine:
    """Performs geometric measurement on PDF points and polygons."""

    @staticmethod
    def calculate_distance(p1: fitz.Point, p2: fitz.Point) -> float:
        """Calculates euclidean distance between two PDF points in points."""
        return math.hypot(p2.x - p1.x, p2.y - p1.y)

    @staticmethod
    def calculate_perimeter(points: List[fitz.Point], closed: bool = False) -> float:
        """Calculates cumulative perimeter length along a sequence of points."""
        if len(points) < 2:
            return 0.0

        total = 0.0
        for i in range(len(points) - 1):
            total += MeasurementEngine.calculate_distance(points[i], points[i + 1])

        if closed and len(points) > 2:
            total += MeasurementEngine.calculate_distance(points[-1], points[0])

        return total

    @staticmethod
    def calculate_polygon_area(points: List[fitz.Point]) -> float:
        """Calculates enclosed polygon area using the Shoelace formula (Gauss's area formula)."""
        n = len(points)
        if n < 3:
            return 0.0

        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i].x * points[j].y
            area -= points[j].x * points[i].y

        return abs(area) / 2.0

    @staticmethod
    def add_measurement_annotation(
        doc: PDFDocument,
        page_num: int,
        measure_type: str,  # "distance", "perimeter", "area"
        points: List[fitz.Point],
        scale: ScaleRatio,
        color: Tuple[float, float, float] = (0.9, 0.2, 0.2),
    ) -> Optional[fitz.Annot]:
        """Creates a permanent measurement dimension line or polygon annotation with text callout."""
        if not doc.is_open or page_num < 0 or page_num >= doc.page_count:
            return None

        doc.save_state_for_undo()
        page = doc.get_page(page_num)

        if measure_type == "distance" and len(points) >= 2:
            p1, p2 = points[0], points[1]
            dist_pts = MeasurementEngine.calculate_distance(p1, p2)
            label = f"Mesafe: {scale.format_distance(dist_pts)}"

            annot = page.add_line_annot(p1, p2)
            annot.set_colors(stroke=color)
            annot.set_border(width=1.5)
            # Add tick line ends
            annot.set_line_ends(fitz.PDF_ANNOT_LE_SLASH, fitz.PDF_ANNOT_LE_SLASH)
            annot.set_info(title="Ölçüm", content=label)
            annot.update()

            # Place small dimension text label at midpoint
            mid = fitz.Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2 - 4)
            page.insert_text(mid, label, fontsize=9, color=color)
            doc.is_modified = True
            return annot

        elif measure_type == "area" and len(points) >= 3:
            area_pts = MeasurementEngine.calculate_polygon_area(points)
            perim_pts = MeasurementEngine.calculate_perimeter(points, closed=True)
            label = f"Alan: {scale.format_area(area_pts)}\nÇevre: {scale.format_distance(perim_pts)}"

            annot = page.add_polygon_annot(points)
            annot.set_colors(stroke=color, fill=(color[0], color[1], color[2]))
            annot.set_opacity(0.25)
            annot.set_border(width=1.5)
            annot.set_info(title="Alan Ölçümü", content=label)
            annot.update()

            centroid_x = sum(p.x for p in points) / len(points)
            centroid_y = sum(p.y for p in points) / len(points)
            page.insert_text(fitz.Point(centroid_x - 30, centroid_y), scale.format_area(area_pts), fontsize=9, color=color)
            doc.is_modified = True
            return annot

        return None
