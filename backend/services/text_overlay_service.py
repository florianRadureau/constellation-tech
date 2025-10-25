"""
Text overlay service for constellation images.

Adds title, technology labels, and watermark with smart collision avoidance.
Uses intelligent angle calculation to place labels in clear zones away from other stars.
"""

import logging
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import settings
from services.star_detector import StarPosition
from services.technology_mapper import StarTechMapping

logger = logging.getLogger(__name__)


class TextOverlayService:
    """
    Add elegant text overlays to constellation images.

    Handles title, technology labels (with smart collision avoidance), and watermark.
    Uses intelligent angle calculation to place labels in zones away from other stars.

    Example:
        >>> service = TextOverlayService()
        >>> final_image = service.compose(image, mappings, title)
    """

    # Smart positioning constants
    MIN_DISTANCE_FROM_STAR = 60  # Minimum distance from star center to label (px)
    MIN_DISTANCE_FROM_OTHER_STARS = 40  # Minimum distance to other stars (px)
    STAR_INFLUENCE_RADIUS = 150  # Radius in which other stars affect placement (px)
    NUM_RADIAL_ATTEMPTS = 8  # Number of radial positions to try around optimal angle

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
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
    ) -> Image.Image:
        """
        Add all text overlays to image.

        Args:
            image: Base constellation image
            mappings: Star-technology mappings
            title: Constellation title
            connections: List of (star_idx1, star_idx2) defining constellation lines
            star_positions: List of (x, y) positions for each star

        Returns:
            Image with text overlays

        Example:
            >>> final = service.compose(image, mappings, "La Constellation", connections, positions)
        """
        # Work on a copy
        result = image.copy()

        # Add title
        result = self.add_title(result, title)

        # Add technology labels with topology-aware positioning
        result = self.add_tech_labels(result, mappings, connections, star_positions)

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
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
    ) -> Image.Image:
        """
        Add technology labels with topology-aware positioning.

        Uses constellation topology (connection lines) to place labels in optimal positions
        away from the constellation structure.

        Args:
            image: Base image
            mappings: Star-technology mappings
            connections: List of (star_idx1, star_idx2) defining constellation lines
            star_positions: List of (x, y) positions for each star

        Returns:
            Image with labels
        """
        draw = ImageDraw.Draw(image)

        # Extract all star positions for collision checking
        all_star_positions = [mapping.star for mapping in mappings]

        # Track occupied regions by labels
        occupied_boxes: list[Tuple[int, int, int, int]] = []

        for idx, mapping in enumerate(mappings):
            star = mapping.star
            tech_name = mapping.tech.name

            # Find best position using topology-aware angle calculation
            position = self._find_label_position(
                draw,
                star.x,
                star.y,
                tech_name,
                occupied_boxes,
                image.size,
                all_star_positions,
                idx,  # Star index for connection lookup
                connections,
                star_positions,
            )

            if position is None:
                logger.warning(
                    f"Could not place label for {tech_name} at star ({star.x}, {star.y})"
                )
                continue

            x, y = position

            # Draw premium label with glow effect and colored border
            category = mapping.tech.category
            image, label_box = self._draw_premium_label(
                image, x, y, tech_name, category
            )

            # Update draw object after image modification
            draw = ImageDraw.Draw(image)

            # Mark as occupied
            occupied_boxes.append(label_box)

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
        occupied_boxes: list[Tuple[int, int, int, int]],
        image_size: Tuple[int, int],
        all_stars: list[StarPosition],
        star_idx: int,
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
    ) -> Tuple[int, int] | None:
        """
        Find best position for label using topology-aware angle calculation.

        Algorithm:
        1. Calculate optimal angle based on constellation connections
        2. Adjust position based on label width (align end at MIN_DISTANCE_FROM_STAR)
        3. Try position, checking collisions with labels and other stars
        4. If collision, try alternative positions with angular offsets
        5. Return first valid position or None

        Args:
            draw: ImageDraw object
            star_x, star_y: Star coordinates
            text: Label text
            occupied_boxes: List of occupied bounding boxes
            image_size: Image dimensions
            all_stars: All star positions in constellation
            star_idx: Index of this star for connection lookup
            connections: List of constellation connections
            star_positions: List of all star positions

        Returns:
            (x, y) position or None if no valid position found
        """
        # Calculate optimal angle based on constellation topology
        optimal_angle = self._calculate_angle_from_connections(
            star_idx, star_x, star_y, connections, star_positions
        )

        # Calculate label width
        bbox = draw.textbbox((0, 0), text, font=self.label_font)
        label_width = bbox[2] - bbox[0]

        # Adjust distance based on angle to align label end at MIN_DISTANCE_FROM_STAR
        # If angle in quadrants 3-4 (180° to 360°), label extends left
        if math.pi < optimal_angle < 2 * math.pi:
            # Label goes left, so add label width to ensure end is at 60px
            distance_from_star = self.MIN_DISTANCE_FROM_STAR + label_width
        else:
            # Label goes right, normal distance
            distance_from_star = self.MIN_DISTANCE_FROM_STAR

        # Calculate primary position
        primary_x = star_x + int(distance_from_star * math.cos(optimal_angle))
        primary_y = star_y + int(distance_from_star * math.sin(optimal_angle))

        # Try primary position first, then alternatives with angular offsets
        angle_offsets = [0, 15, -15, 30, -30, 45, -45, 60]  # In degrees
        candidate_positions = []
        for offset_deg in angle_offsets:
            offset_rad = math.radians(offset_deg)
            angle = optimal_angle + offset_rad
            x = star_x + int(distance_from_star * math.cos(angle))
            y = star_y + int(distance_from_star * math.sin(angle))
            candidate_positions.append((x, y))

        # Try each candidate position
        for x, y in candidate_positions:
            # Get text bounding box
            bbox = draw.textbbox((x, y), text, font=self.label_font)
            padding = 4
            test_box = (
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding,
            )

            # Check if within image bounds
            if (
                test_box[0] < 0
                or test_box[1] < 0
                or test_box[2] > image_size[0]
                or test_box[3] > image_size[1]
            ):
                continue

            # Check collision with occupied label boxes
            if self._boxes_overlap(test_box, occupied_boxes):
                continue

            # Check proximity to other stars (avoid placing between stars)
            if self._too_close_to_other_stars(
                test_box, star_x, star_y, all_stars
            ):
                continue

            # Found valid position
            logger.debug(
                f"Label placed at angle {math.degrees(optimal_angle):.0f}° "
                f"from star ({star_x}, {star_y})"
            )
            return (x, y)

        # No valid position found
        return None

    def _calculate_angle_from_connections(
        self,
        star_idx: int,
        star_x: int,
        star_y: int,
        connections: list[Tuple[int, int]],
        star_positions: list[Tuple[int, int]],
    ) -> float:
        """
        Calculate optimal angle for label based on constellation topology.

        Analyzes the connection lines from this star and finds the optimal position
        by placing the label opposite to the arc center of connected lines.

        Algorithm:
        1. Find all connections for this star
        2. Calculate angle of each connected line
        3. Find center of arc formed by these angles
        4. Return opposite angle (+180°)

        Args:
            star_idx: Index of current star in star_positions list
            star_x, star_y: Star coordinates
            connections: List of (star_idx1, star_idx2) tuples
            star_positions: List of all star (x, y) positions

        Returns:
            Optimal angle in radians (opposite to connection arc center)

        Example:
            If star has connections at 90° and 180°:
            - Arc center = 135°
            - Optimal angle = 135° + 180° = 315°
        """
        # Find all connections for this star
        star_connections = [
            conn for conn in connections if star_idx in conn
        ]

        if not star_connections:
            # No connections - this shouldn't happen based on user requirements
            # But as safety fallback, place label to the right
            logger.warning(
                f"Star {star_idx} has no connections, using fallback angle 0°"
            )
            return 0.0

        # Calculate angles for each connected line
        connected_angles: list[float] = []
        for conn in star_connections:
            # Get the OTHER star in the connection
            other_idx = conn[1] if conn[0] == star_idx else conn[0]
            other_x, other_y = star_positions[other_idx]

            # Calculate angle from current star to connected star
            angle = math.atan2(other_y - star_y, other_x - star_x)
            connected_angles.append(angle)

        # Calculate center of arc (average of all connection angles)
        arc_center = sum(connected_angles) / len(connected_angles)

        # Return opposite angle (+180° or +π radians)
        optimal_angle = (arc_center + math.pi) % (2 * math.pi)

        logger.debug(
            f"Star {star_idx}: {len(connected_angles)} connections, "
            f"arc center={math.degrees(arc_center):.0f}°, "
            f"optimal={math.degrees(optimal_angle):.0f}°"
        )

        return optimal_angle

    def _calculate_smart_angle(
        self, star_x: int, star_y: int, all_stars: list[StarPosition]
    ) -> float:
        """
        Calculate optimal angle for label placement.

        Finds the angle (direction) with the least density of nearby stars,
        creating a "clear zone" for the label.

        Args:
            star_x, star_y: Star coordinates
            all_stars: All star positions in constellation

        Returns:
            Optimal angle in radians (0 = right, π/2 = down, π = left, 3π/2 = up)
        """
        # Collect angles to nearby stars (within influence radius)
        nearby_angles: list[float] = []

        for other_star in all_stars:
            # Skip self
            if other_star.x == star_x and other_star.y == star_y:
                continue

            # Calculate distance
            dx = other_star.x - star_x
            dy = other_star.y - star_y
            distance = math.hypot(dx, dy)

            # Only consider stars within influence radius
            if distance < self.STAR_INFLUENCE_RADIUS:
                angle = math.atan2(dy, dx)  # Angle from current star to other star
                nearby_angles.append(angle)

        # If no nearby stars, default to right (0 radians)
        if not nearby_angles:
            return 0.0

        # Sort angles
        nearby_angles.sort()

        # Find largest gap between consecutive angles
        max_gap = 0.0
        optimal_angle = 0.0

        for i in range(len(nearby_angles)):
            # Calculate gap between this angle and next (wrapping around)
            current = nearby_angles[i]
            next_angle = nearby_angles[(i + 1) % len(nearby_angles)]

            # Handle wraparound from π to -π
            if i == len(nearby_angles) - 1:
                gap = (2 * math.pi - current) + (next_angle + math.pi)
            else:
                gap = next_angle - current

            if gap > max_gap:
                max_gap = gap
                # Place label in middle of gap
                optimal_angle = current + gap / 2

        # Normalize to [0, 2π)
        optimal_angle = optimal_angle % (2 * math.pi)

        logger.debug(
            f"Optimal angle: {math.degrees(optimal_angle):.0f}° "
            f"(gap: {math.degrees(max_gap):.0f}°, nearby stars: {len(nearby_angles)})"
        )

        return optimal_angle

    def _generate_radial_positions(
        self, star_x: int, star_y: int, center_angle: float, num_positions: int
    ) -> list[Tuple[int, int]]:
        """
        Generate radial positions around a center angle.

        Creates positions at MIN_DISTANCE_FROM_STAR, spreading ±45° around center angle.

        Args:
            star_x, star_y: Star coordinates
            center_angle: Center angle in radians
            num_positions: Number of positions to generate

        Returns:
            List of (x, y) positions
        """
        positions: list[Tuple[int, int]] = []

        # Generate positions spreading ±45° around center angle
        angle_spread = math.pi / 4  # 45 degrees in radians

        for i in range(num_positions):
            # Distribute angles evenly in ±45° range
            if num_positions == 1:
                angle_offset = 0
            else:
                angle_offset = (i / (num_positions - 1) - 0.5) * 2 * angle_spread

            angle = center_angle + angle_offset

            # Calculate position at MIN_DISTANCE_FROM_STAR
            x = star_x + int(self.MIN_DISTANCE_FROM_STAR * math.cos(angle))
            y = star_y + int(self.MIN_DISTANCE_FROM_STAR * math.sin(angle))

            positions.append((x, y))

        return positions

    def _too_close_to_other_stars(
        self,
        label_box: Tuple[int, int, int, int],
        current_star_x: int,
        current_star_y: int,
        all_stars: list[StarPosition],
    ) -> bool:
        """
        Check if label box is too close to other stars.

        Prevents labels from being placed between or near other stars.

        Args:
            label_box: Label bounding box (x1, y1, x2, y2)
            current_star_x, current_star_y: Current star coordinates (to exclude)
            all_stars: All star positions

        Returns:
            True if label is too close to another star
        """
        # Calculate label center
        label_center_x = (label_box[0] + label_box[2]) / 2
        label_center_y = (label_box[1] + label_box[3]) / 2

        for star in all_stars:
            # Skip current star
            if star.x == current_star_x and star.y == current_star_y:
                continue

            # Calculate distance from label center to other star
            distance = math.hypot(
                star.x - label_center_x, star.y - label_center_y
            )

            if distance < self.MIN_DISTANCE_FROM_OTHER_STARS:
                logger.debug(
                    f"Label too close to star at ({star.x}, {star.y}): "
                    f"distance={distance:.1f}px < {self.MIN_DISTANCE_FROM_OTHER_STARS}px"
                )
                return True

        return False

    def _boxes_overlap(
        self, box: Tuple[int, int, int, int], boxes: list[Tuple[int, int, int, int]]
    ) -> bool:
        """
        Check if box overlaps with any box in list.

        Args:
            box: (x1, y1, x2, y2) to test
            boxes: List of boxes to check against

        Returns:
            True if overlap detected
        """
        x1, y1, x2, y2 = box

        for bx1, by1, bx2, by2 in boxes:
            # Check overlap
            if not (x2 < bx1 or x1 > bx2 or y2 < by1 or y1 > by2):
                return True

        return False

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
