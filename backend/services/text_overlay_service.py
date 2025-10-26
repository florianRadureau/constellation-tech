"""
Text overlay service for constellation images.

Adds title, technology labels, and watermark with simple fixed positioning.
"""

import logging
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import settings
from services.technology_mapper import StarTechMapping

logger = logging.getLogger(__name__)


class TextOverlayService:
    """
    Add elegant text overlays to constellation images.

    Handles title, technology labels (simple fixed positioning), and watermark.

    Example:
        >>> service = TextOverlayService()
        >>> final_image = service.compose(image, mappings, title)
    """

    def __init__(self, font_dir: Path | None = None) -> None:
        """
        Initialize text overlay service.

        Args:
            font_dir: Directory containing fonts (defaults to assets/fonts)
        """
        self.font_dir = font_dir or settings.fonts_dir
        self._load_fonts()

        logger.info("TextOverlayService initialized")

    def _load_fonts(self) -> None:
        """Load custom SpaceMono fonts from assets."""
        # Title font: SpaceMono-Bold 34px
        title_path = self.font_dir / "SpaceMono-Bold.ttf"
        self.title_font = ImageFont.truetype(str(title_path), 34)

        # Label font: SpaceMono-Regular 18px
        label_path = self.font_dir / "SpaceMono-Regular.ttf"
        self.label_font = ImageFont.truetype(str(label_path), 18)

        # Watermark font: SpaceMono-Regular 16px
        watermark_path = self.font_dir / "SpaceMono-Regular.ttf"
        self.watermark_font = ImageFont.truetype(str(watermark_path), 16)

        logger.info("SpaceMono fonts loaded (Bold 34px, Regular 18px/16px)")

    def compose(
        self,
        image: Image.Image,
        mappings: list[StarTechMapping],
        title: str,
    ) -> Image.Image:
        """
        Add all text overlays to image.

        Args:
            image: Base constellation image
            mappings: Star-technology mappings
            title: Constellation title

        Returns:
            Image with text overlays

        Example:
            >>> final = service.compose(image, mappings, "La Constellation")
        """
        # Work on a copy
        result = image.copy()

        # Add title
        result = self.add_title(result, title)

        # Add technology labels with fixed positioning
        result = self.add_tech_labels(result, mappings)

        # Add watermark
        result = self.add_watermark(result)

        logger.info("Text composition complete")
        return result

    def add_title(self, image: Image.Image, title: str) -> Image.Image:
        """
        Add title at top center with premium glow effect.

        Features:
        - Large elegant font (56-60px)
        - Cyan/white glow effect
        - Text stroke for depth
        - Centered positioning

        Args:
            image: Base image
            title: Title text

        Returns:
            Image with title
        """
        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Use SpaceMono-Bold 34px for title
        title_font = self.title_font

        # Create temporary draw to measure text
        temp_draw = ImageDraw.Draw(image)
        bbox = temp_draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Center horizontally, position lower (80px from top)
        x = (image.width - text_width) // 2
        y = 60

        # Create overlay for effects
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

        # 1. Draw cyan glow (outer layer)
        glow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)

        # Multiple layers of glow (subtle for elegance)
        glow_colors = [
            ((100, 200, 255, 20), 4),  # Outer cyan glow
            ((150, 220, 255, 30), 2),  # Inner glow
        ]

        for color, offset in glow_colors:
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    if dx * dx + dy * dy <= offset * offset:
                        glow_draw.text(
                            (x + dx, y + dy),
                            title,
                            font=title_font,
                            fill=color,
                        )

        # Apply blur to glow
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=4))
        overlay = Image.alpha_composite(overlay, glow_layer)

        # 2. Draw text stroke (outline)
        overlay_draw = ImageDraw.Draw(overlay)
        stroke_offset = 2
        for dx in range(-stroke_offset, stroke_offset + 1):
            for dy in range(-stroke_offset, stroke_offset + 1):
                if dx != 0 or dy != 0:
                    overlay_draw.text(
                        (x + dx, y + dy),
                        title,
                        font=title_font,
                        fill=(0, 0, 0, 200),
                    )

        # 3. Draw main title text (bright white)
        overlay_draw.text((x, y), title, font=title_font, fill=(255, 255, 255, 255))

        # Composite all effects
        result = Image.alpha_composite(image, overlay)

        logger.debug(f"Added title with glow: {title}")
        return result

    def add_tech_labels(
        self,
        image: Image.Image,
        mappings: list[StarTechMapping],
    ) -> Image.Image:
        """
        Add technology labels with fixed positioning (30px below stars).

        Args:
            image: Base image
            mappings: Star-technology mappings

        Returns:
            Image with labels
        """
        draw = ImageDraw.Draw(image)

        for mapping in mappings:
            star = mapping.star
            tech_name = mapping.tech.name
            category = mapping.tech.category

            # Find position (30px below star)
            position = self._find_label_position(
                draw,
                star.x,
                star.y,
                tech_name,
                image.size,
            )

            if position is None:
                logger.warning(
                    f"Could not place label for {tech_name} at ({star.x}, {star.y})"
                )
                continue

            x, y = position

            # Draw premium label
            image, label_box = self._draw_premium_label(
                image, x, y, tech_name, category
            )

            # Update draw object after image modification
            draw = ImageDraw.Draw(image)

        logger.debug(f"Added {len(mappings)} technology labels")
        return image

    def _draw_premium_label(
        self,
        image: Image.Image,
        x: int,
        y: int,
        text: str,
        category: str,
    ) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        """
        Draw minimal elegant label.

        Features:
        - Simple rounded rectangle background (dark gray)
        - No colored borders (too amateur)
        - Subtle text shadow
        - Clean Space Mono typography

        Args:
            image: Base image
            x, y: Label position (top-left)
            text: Label text
            category: Technology category (unused, kept for compatibility)

        Returns:
            Tuple of (modified image, label bounding box)
        """
        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Calculate text dimensions
        draw = ImageDraw.Draw(image)
        bbox = draw.textbbox((x, y), text, font=self.label_font)
        padding = 8  # Generous padding
        corner_radius = 6

        label_box = (
            bbox[0] - padding,
            bbox[1] - padding,
            bbox[2] + padding,
            bbox[3] + padding,
        )

        # Create overlay
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # 1. Simple rounded background (dark, semi-transparent)
        overlay_draw.rounded_rectangle(
            label_box, radius=corner_radius, fill=(20, 20, 30, 180)  # Dark gray, 70% opacity
        )

        # 2. Text shadow (subtle)
        overlay_draw.text(
            (x + 1, y + 1), text, font=self.label_font, fill=(0, 0, 0, 150)
        )

        # 3. Main text (white)
        overlay_draw.text((x, y), text, font=self.label_font, fill=(255, 255, 255, 255))

        # Composite
        result = Image.alpha_composite(image, overlay)

        return result, label_box

    def _find_label_position(
        self,
        draw: ImageDraw.ImageDraw,
        star_x: int,
        star_y: int,
        text: str,
        image_size: tuple[int, int],
    ) -> tuple[int, int] | None:
        """
        Place label 30px below star (simple fixed placement).

        Args:
            draw: ImageDraw object
            star_x, star_y: Star coordinates
            text: Label text
            image_size: Image dimensions (width, height)

        Returns:
            (x, y) position or None if out of bounds
        """
        # Calculate label dimensions
        bbox = draw.textbbox((0, 0), text, font=self.label_font)
        label_width = bbox[2] - bbox[0]
        label_height = bbox[3] - bbox[1]

        # Place label 30px below star (center of label at 30px below star center)
        center_x = star_x
        center_y = star_y + 30

        # Convert center to top-left corner (Pillow anchor)
        x = int(center_x - label_width / 2)
        y = int(center_y - label_height / 2)

        # Check if within image bounds
        bbox = draw.textbbox((x, y), text, font=self.label_font)
        padding = 4
        test_box = (
            bbox[0] - padding,
            bbox[1] - padding,
            bbox[2] + padding,
            bbox[3] + padding,
        )

        if (
            test_box[0] < 0
            or test_box[1] < 0
            or test_box[2] > image_size[0]
            or test_box[3] > image_size[1]
        ):
            logger.warning(f"Label '{text}' at ({star_x}, {star_y}) out of bounds")
            return None

        logger.debug(f"Label '{text}' placed 30px below star at ({star_x}, {star_y})")
        return (x, y)

    def add_watermark(
        self, image: Image.Image, text: str = "Made with <3 by Florian RADUREAU"
    ) -> Image.Image:
        """
        Add visible watermark bottom-right with semi-transparent background.

        Features:
        - 16px SpaceMono font
        - Rounded rectangle background
        - 100% opacity - fully visible
        - <3 heart symbol

        Args:
            image: Base image
            text: Watermark text (default: custom signature with star)

        Returns:
            Image with watermark
        """
        # Convert to RGBA if needed
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Calculate text dimensions
        temp_draw = ImageDraw.Draw(image)
        bbox = temp_draw.textbbox((0, 0), text, font=self.watermark_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position bottom-right with margins
        padding = 8
        margin = 20
        x = image.width - text_width - padding * 2 - margin
        y = image.height - text_height - padding * 2 - margin

        # Background box
        bg_box = (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding,
        )

        # Create overlay for semi-transparent background
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Draw rounded rectangle background (dark gray, 78% opacity)
        overlay_draw.rounded_rectangle(
            bg_box,
            radius=6,
            fill=(20, 20, 30, 200),  # Dark background
        )

        # Draw text (white, 100% opacity - fully visible)
        overlay_draw.text(
            (x, y),
            text,
            font=self.watermark_font,
            fill=(255, 255, 255, 255),  # Pure white, 100% opaque
        )

        # Composite overlay onto image
        result = Image.alpha_composite(image, overlay)

        logger.debug(f"Added visible watermark: {text}")
        return result

    def _get_title_zone(
        self, image_size: Tuple[int, int], title: str
    ) -> Tuple[int, int, int, int]:
        """
        Calculate forbidden zone for title (top center).

        Uses same positioning logic as add_title() to compute the title bounding box.

        Args:
            image_size: Image dimensions (width, height)
            title: Title text

        Returns:
            Tuple (x1, y1, x2, y2) representing title zone with padding
        """
        # Create temporary image to measure text
        temp_img = Image.new("RGBA", image_size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), title, font=self.title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Same positioning as add_title() (line 138-139)
        x = (image_size[0] - text_width) // 2
        y = 60

        # Add padding for glow effects and stroke (from add_title: glow offset=4, stroke=2)
        padding = 15  # Extra safety margin for glow + stroke effects

        return (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding,
        )

    def _get_watermark_zone(
        self, image_size: Tuple[int, int]
    ) -> Tuple[int, int, int, int]:
        """
        Calculate forbidden zone for watermark (bottom-right).

        Uses same positioning logic as add_watermark() to compute watermark bounding box.

        Args:
            image_size: Image dimensions (width, height)

        Returns:
            Tuple (x1, y1, x2, y2) representing watermark zone with padding
        """
        # Fixed text from add_watermark default
        text = "Made with <3 by Florian RADUREAU"

        # Create temporary image to measure text
        temp_img = Image.new("RGBA", image_size, (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=self.watermark_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Same positioning as add_watermark() (line 713-716)
        padding = 8
        margin = 20
        x = image_size[0] - text_width - padding * 2 - margin
        y = image_size[1] - text_height - padding * 2 - margin

        # Background box with padding (line 719-724)
        bg_box = (
            x - padding,
            y - padding,
            x + text_width + padding,
            y + text_height + padding,
        )

        return bg_box

    def _line_rectangle_intersect(
        self,
        line_p1: Tuple[float, float],
        line_p2: Tuple[float, float],
        rect: Tuple[int, int, int, int],
    ) -> bool:
        """
        Check if line segment intersects with rectangle.

        Uses Cohen-Sutherland algorithm for line-rectangle intersection.

        Args:
            line_p1: Line start point (x1, y1)
            line_p2: Line end point (x2, y2)
            rect: Rectangle (x_min, y_min, x_max, y_max)

        Returns:
            True if line segment intersects rectangle

        Reference:
            https://en.wikipedia.org/wiki/Cohen%E2%80%93Sutherland_algorithm
        """
        x1, y1 = line_p1
        x2, y2 = line_p2
        x_min, y_min, x_max, y_max = rect

        # Cohen-Sutherland outcodes
        INSIDE = 0  # 0000
        LEFT = 1    # 0001
        RIGHT = 2   # 0010
        BOTTOM = 4  # 0100
        TOP = 8     # 1000

        def compute_outcode(x: float, y: float) -> int:
            """Compute outcode for point relative to rectangle."""
            code = INSIDE
            if x < x_min:
                code |= LEFT
            elif x > x_max:
                code |= RIGHT
            if y < y_min:
                code |= BOTTOM
            elif y > y_max:
                code |= TOP
            return code

        # Compute outcodes for both endpoints
        outcode1 = compute_outcode(x1, y1)
        outcode2 = compute_outcode(x2, y2)

        while True:
            if outcode1 == 0 and outcode2 == 0:
                # Both points inside rectangle
                return True
            elif (outcode1 & outcode2) != 0:
                # Both points on same side outside rectangle
                return False
            else:
                # Line segment needs clipping
                # Pick point outside rectangle
                outcode_out = outcode1 if outcode1 != 0 else outcode2

                # Find intersection point
                if outcode_out & TOP:
                    x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                    y = y_max
                elif outcode_out & BOTTOM:
                    x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                    y = y_min
                elif outcode_out & RIGHT:
                    y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                    x = x_max
                elif outcode_out & LEFT:
                    y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                    x = x_min

                # Update point and outcode
                if outcode_out == outcode1:
                    x1, y1 = x, y
                    outcode1 = compute_outcode(x1, y1)
                else:
                    x2, y2 = x, y
                    outcode2 = compute_outcode(x2, y2)

    def _intersects_constellation_lines(
        self,
        label_box: Tuple[int, int, int, int],
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
    ) -> bool:
        """
        Check if label box intersects any constellation connection lines.

        Args:
            label_box: Label bounding box (x1, y1, x2, y2)
            connections: List of (star_idx1, star_idx2) tuples
            star_positions: List of (x, y) positions for each star

        Returns:
            True if label intersects any connection line
        """
        for conn in connections:
            idx1, idx2 = conn

            # Get star positions
            p1 = star_positions[idx1]
            p2 = star_positions[idx2]

            # Check if line segment intersects label box
            if self._line_rectangle_intersect(p1, p2, label_box):
                return True

        return False

    def _min_angular_distance(self, angle1: float, angle2: float) -> float:
        """
        Calculate minimum angular distance between two angles.

        Args:
            angle1: First angle in radians
            angle2: Second angle in radians

        Returns:
            Minimum angular distance (0 to π radians)

        Example:
            >>> service._min_angular_distance(0, math.pi)
            3.14159...  # π radians (180°)
            >>> service._min_angular_distance(0, 2*math.pi - 0.1)
            0.1  # Wraps around
        """
        diff = abs(angle1 - angle2)
        return min(diff, 2 * math.pi - diff)

    def _point_in_box(
        self, point: Tuple[float, float], box: Tuple[int, int, int, int]
    ) -> bool:
        """
        Check if a point is inside a rectangle.

        Args:
            point: (x, y) coordinates
            box: Rectangle (x_min, y_min, x_max, y_max)

        Returns:
            True if point is inside box
        """
        x, y = point
        return box[0] <= x <= box[2] and box[1] <= y <= box[3]

    def _point_to_line_distance(
        self,
        point: Tuple[float, float],
        line_p1: Tuple[int, int],
        line_p2: Tuple[int, int],
    ) -> float:
        """
        Calculate perpendicular distance from point to line segment.

        Uses point-to-line formula:
        distance = |((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)| / sqrt((y2-y1)² + (x2-x1)²)

        Args:
            point: (px, py) coordinates
            line_p1: Line start point (x1, y1)
            line_p2: Line end point (x2, y2)

        Returns:
            Perpendicular distance in pixels

        Example:
            >>> service._point_to_line_distance((50, 50), (0, 0), (100, 0))
            50.0  # Point is 50px above horizontal line
        """
        px, py = point
        x1, y1 = line_p1
        x2, y2 = line_p2

        # Handle degenerate case (line is a point)
        if x1 == x2 and y1 == y2:
            return math.hypot(px - x1, py - y1)

        # Calculate perpendicular distance
        numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
        denominator = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

        return numerator / denominator

    def _calculate_sector_scores(
        self,
        star_idx: int,
        star_x: int,
        star_y: int,
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
        occupied_boxes: list[Tuple[int, int, int, int]],
        image_size: Tuple[int, int],
        title: str,
        num_sectors: int = 12,
    ) -> list[Tuple[float, float]]:
        """
        Calculate score for each angular sector around the star.

        Divides the space around the star into num_sectors sectors (default: 12 sectors of 30°).
        For each sector, calculates a score based on:
        - Distance to connections (penalty if < 30°)
        - Presence of other labels (penalty)
        - Forbidden zones: title, watermark, lines (strong penalty)

        Args:
            star_idx: Index of current star
            star_x, star_y: Star coordinates
            connections: List of constellation connections
            star_positions: List of all star positions
            occupied_boxes: List of already placed label boxes
            image_size: Image dimensions
            title: Constellation title (for forbidden zone)
            num_sectors: Number of sectors to divide circle (default: 12)

        Returns:
            List of (sector_angle, score) tuples sorted by score (best first)

        Example:
            >>> scores = service._calculate_sector_scores(0, 300, 200, ...)
            >>> best_angle, best_score = scores[0]
            >>> print(f"Best sector: {math.degrees(best_angle):.0f}° (score: {best_score:.1f})")
        """
        sector_size = 2 * math.pi / num_sectors  # e.g., 30° in radians
        scores = []

        # 1. Calculate angles of all connections for this star
        connection_angles = []
        for conn in connections:
            if star_idx in conn:
                other_idx = conn[1] if conn[0] == star_idx else conn[0]
                other_x, other_y = star_positions[other_idx]
                angle = math.atan2(other_y - star_y, other_x - star_x)
                connection_angles.append(angle)

        # 2. For each sector, calculate score
        for i in range(num_sectors):
            sector_angle = i * sector_size  # Center of sector
            score = 100.0  # Initial score

            # PENALTY 1: Proximity to connections
            for conn_angle in connection_angles:
                angular_distance = self._min_angular_distance(sector_angle, conn_angle)
                if angular_distance < math.radians(30):  # < 30°
                    # Progressive penalty: closer = stronger
                    penalty = 50 * (1 - angular_distance / math.radians(30))
                    score -= penalty

            # PENALTY 2: Proximity to other already placed labels
            # Calculate hypothetical label position in this sector
            test_x = star_x + self.MIN_DISTANCE_FROM_STAR * math.cos(sector_angle)
            test_y = star_y + self.MIN_DISTANCE_FROM_STAR * math.sin(sector_angle)

            # Count labels within 100px radius
            nearby_labels = 0
            for box in occupied_boxes:
                box_center_x = (box[0] + box[2]) / 2
                box_center_y = (box[1] + box[3]) / 2
                distance = math.hypot(test_x - box_center_x, test_y - box_center_y)
                if distance < 100:
                    nearby_labels += 1

            score -= nearby_labels * 20  # -20 points per nearby label

            # PENALTY 3: Title zone (forbidden)
            title_zone = self._get_title_zone(image_size, title)
            if self._point_in_box((test_x, test_y), title_zone):
                score -= 200  # Strong penalty

            # PENALTY 4: Watermark zone (forbidden)
            watermark_zone = self._get_watermark_zone(image_size)
            if self._point_in_box((test_x, test_y), watermark_zone):
                score -= 200  # Strong penalty

            # PENALTY 5: Proximity to connection lines
            # Check if position is within 30px of any line
            for conn in connections:
                p1 = star_positions[conn[0]]
                p2 = star_positions[conn[1]]
                distance_to_line = self._point_to_line_distance((test_x, test_y), p1, p2)
                if distance_to_line < 30:
                    # Progressive penalty
                    penalty = 30 * (1 - distance_to_line / 30)
                    score -= penalty

            scores.append((sector_angle, score))

        # Log all sector scores for debugging
        logger.info(f"Star {star_idx} at ({star_x}, {star_y}) - Sector scores:")
        logger.info(f"  Connections: {len(connection_angles)} at angles {[f'{math.degrees(a):.0f}°' for a in connection_angles]}")

        # Display all sectors with their scores
        for sector_angle, score in scores:
            logger.info(f"    Sector {math.degrees(sector_angle):6.0f}°: score = {score:6.1f}")

        # Sort by score (best first)
        scores.sort(key=lambda x: x[1], reverse=True)

        logger.info(f"  → Best sector: {math.degrees(scores[0][0]):.0f}° (score: {scores[0][1]:.1f})")

        return scores
