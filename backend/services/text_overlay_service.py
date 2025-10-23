"""
Text overlay service for constellation images.

Adds title, technology labels, and watermark with collision avoidance.
"""

import logging
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from config import settings
from services.technology_mapper import StarTechMapping

logger = logging.getLogger(__name__)


class TextOverlayService:
    """
    Add elegant text overlays to constellation images.

    Handles title, technology labels (with collision avoidance), and watermark.

    Example:
        >>> service = TextOverlayService()
        >>> final_image = service.compose(image, mappings, title)
    """

    # Label positioning offsets (relative to star)
    LABEL_OFFSETS = [
        (30, 0),  # Right
        (-30, 0),  # Left
        (0, -30),  # Top
        (0, 30),  # Bottom
    ]

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
        """Load fonts with fallbacks."""
        try:
            # Try custom fonts
            title_font_path = self.font_dir / "Montserrat-Bold.ttf"
            if title_font_path.exists():
                self.title_font = ImageFont.truetype(str(title_font_path), 48)
            else:
                raise FileNotFoundError

            label_font_path = self.font_dir / "OpenSans-Regular.ttf"
            if label_font_path.exists():
                self.label_font = ImageFont.truetype(str(label_font_path), 16)
            else:
                raise FileNotFoundError

            logger.info("Custom fonts loaded successfully")

        except (FileNotFoundError, OSError):
            # Fallback to system fonts
            logger.warning("Custom fonts not found, using fallback")

            try:
                # Try DejaVu (common on Linux)
                self.title_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48
                )
                self.label_font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16
                )
                logger.info("DejaVu fonts loaded")
            except OSError:
                # Last resort: default font
                self.title_font = ImageFont.load_default()
                self.label_font = ImageFont.load_default()
                logger.warning("Using default PIL fonts")

        # Watermark font (smaller)
        try:
            self.watermark_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
            )
        except OSError:
            self.watermark_font = ImageFont.load_default()

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
            >>> final = service.compose(image, mappings, "L'Architecte Frontend")
        """
        # Work on a copy
        result = image.copy()

        # Add title
        result = self.add_title(result, title)

        # Add technology labels
        result = self.add_tech_labels(result, mappings)

        # Add watermark
        result = self.add_watermark(result)

        logger.info("Text composition complete")
        return result

    def add_title(self, image: Image.Image, title: str) -> Image.Image:
        """
        Add title at top center with shadow.

        Args:
            image: Base image
            title: Title text

        Returns:
            Image with title
        """
        draw = ImageDraw.Draw(image)

        # Get text bbox
        bbox = draw.textbbox((0, 0), title, font=self.title_font)
        text_width = bbox[2] - bbox[0]

        # Center horizontally, 50px from top
        x = (image.width - text_width) // 2
        y = 50

        # Draw shadow (offset)
        shadow_color = (0, 0, 0, 180)
        draw.text((x + 2, y + 2), title, font=self.title_font, fill=shadow_color)

        # Draw title (white)
        draw.text((x, y), title, font=self.title_font, fill=(255, 255, 255, 255))

        logger.debug(f"Added title: {title}")
        return image

    def add_tech_labels(
        self, image: Image.Image, mappings: list[StarTechMapping]
    ) -> Image.Image:
        """
        Add technology labels with collision avoidance.

        Args:
            image: Base image
            mappings: Star-technology mappings

        Returns:
            Image with labels
        """
        draw = ImageDraw.Draw(image)

        # Track occupied regions
        occupied_boxes: list[Tuple[int, int, int, int]] = []

        for mapping in mappings:
            star = mapping.star
            tech_name = mapping.tech.name

            # Find best position (no collision)
            position = self._find_label_position(
                draw, star.x, star.y, tech_name, occupied_boxes, image.size
            )

            if position is None:
                logger.warning(f"Could not place label for {tech_name}")
                continue

            x, y = position

            # Draw semi-transparent background
            bbox = draw.textbbox((x, y), tech_name, font=self.label_font)
            padding = 4
            bg_box = (
                bbox[0] - padding,
                bbox[1] - padding,
                bbox[2] + padding,
                bbox[3] + padding,
            )

            # Create overlay for transparency
            overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)

            # Background rectangle
            overlay_draw.rectangle(bg_box, fill=(0, 0, 0, 150))

            # Composite overlay
            image = Image.alpha_composite(image.convert("RGBA"), overlay)
            draw = ImageDraw.Draw(image)

            # Draw text (white)
            draw.text((x, y), tech_name, font=self.label_font, fill=(255, 255, 255))

            # Mark as occupied
            occupied_boxes.append(bg_box)

        logger.debug(f"Added {len(mappings)} technology labels")
        return image

    def _find_label_position(
        self,
        draw: ImageDraw.ImageDraw,
        star_x: int,
        star_y: int,
        text: str,
        occupied_boxes: list[Tuple[int, int, int, int]],
        image_size: Tuple[int, int],
    ) -> Tuple[int, int] | None:
        """
        Find best position for label avoiding collisions.

        Tries: right, left, top, bottom

        Args:
            draw: ImageDraw object
            star_x, star_y: Star coordinates
            text: Label text
            occupied_boxes: List of occupied bounding boxes
            image_size: Image dimensions

        Returns:
            (x, y) position or None if no valid position found
        """
        # Try each offset
        for offset_x, offset_y in self.LABEL_OFFSETS:
            x = star_x + offset_x
            y = star_y + offset_y

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

            # Check collision with occupied boxes
            if self._boxes_overlap(test_box, occupied_boxes):
                continue

            # Found valid position
            return (x, y)

        # No valid position found
        return None

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
        self, image: Image.Image, text: str = "constellation.tech"
    ) -> Image.Image:
        """
        Add discrete watermark bottom-right.

        Args:
            image: Base image
            text: Watermark text

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

        logger.debug("Added watermark")
        return image
