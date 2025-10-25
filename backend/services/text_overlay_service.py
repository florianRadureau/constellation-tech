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

        # Watermark font: SpaceMono-Regular 12px
        watermark_path = self.font_dir / "SpaceMono-Regular.ttf"
        self.watermark_font = ImageFont.truetype(str(watermark_path), 12)

        logger.info("SpaceMono fonts loaded (Bold 34px, Regular 18px/12px)")

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
            >>> final = service.compose(image, mappings, "La Constellation du Pixel Parfait")
        """
        # Work on a copy
        result = image.copy()

        # Add title
        result = self.add_title(result, title)

        # Add technology labels with smart positioning
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
        self, image: Image.Image, mappings: list[StarTechMapping]
    ) -> Image.Image:
        """
        Add technology labels with smart collision avoidance.

        Uses intelligent angle calculation to place labels in zones away from other stars.

        Args:
            image: Base image
            mappings: Star-technology mappings

        Returns:
            Image with labels
        """
        draw = ImageDraw.Draw(image)

        # Extract all star positions for smart placement
        all_star_positions = [mapping.star for mapping in mappings]

        # Track occupied regions by labels
        occupied_boxes: list[Tuple[int, int, int, int]] = []

        for mapping in mappings:
            star = mapping.star
            tech_name = mapping.tech.name

            # Find best position using smart angle calculation
            position = self._find_label_position(
                draw,
                star.x,
                star.y,
                tech_name,
                occupied_boxes,
                image.size,
                all_star_positions,
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
    ) -> Tuple[int, int] | None:
        """
        Find best position for label using smart angle calculation.

        Algorithm:
        1. Calculate optimal angle (clearest zone away from other stars)
        2. Generate 8 radial positions around optimal angle
        3. Try each position, checking collisions with labels AND other stars
        4. Return first valid position or None

        Args:
            draw: ImageDraw object
            star_x, star_y: Star coordinates
            text: Label text
            occupied_boxes: List of occupied bounding boxes
            image_size: Image dimensions
            all_stars: All star positions in constellation

        Returns:
            (x, y) position or None if no valid position found
        """
        # Calculate optimal angle (away from other stars)
        optimal_angle = self._calculate_smart_angle(
            star_x, star_y, all_stars
        )

        # Generate radial positions around optimal angle
        candidate_positions = self._generate_radial_positions(
            star_x, star_y, optimal_angle, self.NUM_RADIAL_ATTEMPTS
        )

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
        self, image: Image.Image, text: str = "Made with ⭐ by Florian RADUREAU"
    ) -> Image.Image:
        """
        Add discrete watermark bottom-right.

        Args:
            image: Base image
            text: Watermark text (default: custom signature)

        Returns:
            Image with watermark
        """
        draw = ImageDraw.Draw(image)

        # Get text size
        bbox = draw.textbbox((0, 0), text, font=self.watermark_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position bottom-right
        x = image.width - text_width - 20
        y = image.height - text_height - 20

        # Draw with low opacity
        draw.text((x, y), text, font=self.watermark_font, fill=(255, 255, 255, 100))

        logger.debug(f"Added watermark: {text}")
        return image
