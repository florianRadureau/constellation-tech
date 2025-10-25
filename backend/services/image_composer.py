"""
Image composition service for constellation layers.

Composes constellation images with 4 layers:
1. Background nebula (from Imagen)
2. Connection lines between stars
3. Star sprites at each position
4. Labels (handled separately by TextOverlayService)
"""

import glob
import logging
import random
from typing import Tuple

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class ImageComposer:
    """
    Compose constellation images with multiple layers.

    Uses layer composition to create professional constellation visualizations
    with precise control over each element.

    Example:
        >>> composer = ImageComposer()
        >>> result = composer.compose(
        ...     background=nebula_image,
        ...     star_positions=[(300, 200), (500, 400)],
        ...     connections=[(0, 1)],
        ... )
    """

    def __init__(self, canvas_size: Tuple[int, int] = (1024, 1024)):
        """
        Initialize image composer.

        Args:
            canvas_size: Size of canvas (width, height) in pixels
        """
        self.canvas_size = canvas_size
        self.star_sprites = self._load_star_sprites()

        logger.info(
            f"ImageComposer initialized (canvas: {canvas_size}, "
            f"{len(self.star_sprites)} star sprites loaded)"
        )

    def _load_star_sprites(self) -> list[Image.Image]:
        """
        Load all star sprites from assets folder.

        Loads all PNG files from assets/images/star_sprites/ directory.
        Falls back to creating a single procedural sprite if folder is empty.

        Returns:
            List of RGBA Image sprites (at least 1 sprite guaranteed)
        """
        sprites = []
        sprite_pattern = "assets/images/star_sprites/*.png"

        try:
            sprite_files = sorted(glob.glob(sprite_pattern))

            if not sprite_files:
                logger.warning(
                    f"No sprites found at {sprite_pattern}, using procedural fallback"
                )
                return [self._create_procedural_sprite()]

            for sprite_path in sprite_files:
                try:
                    sprite = Image.open(sprite_path).convert("RGBA")
                    sprites.append(sprite)
                    logger.debug(f"Loaded sprite: {sprite_path}")
                except Exception as e:
                    logger.warning(f"Failed to load {sprite_path}: {e}")

            if not sprites:
                logger.warning("No valid sprites loaded, using procedural fallback")
                return [self._create_procedural_sprite()]

            logger.info(f"✓ Loaded {len(sprites)} star sprites")
            return sprites

        except Exception as e:
            logger.error(f"Error loading sprites: {e}, using procedural fallback")
            return [self._create_procedural_sprite()]

    def _create_procedural_sprite(self, size: int = 60) -> Image.Image:
        """
        Create procedural star sprite with glow effect (fallback).

        Args:
            size: Size of sprite in pixels

        Returns:
            RGBA Image with transparent background
        """
        logger.debug(f"Creating procedural star sprite ({size}x{size})")

        star = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(star)

        center = size // 2

        # Outer glow (concentric circles with decreasing alpha)
        for i in range(6, 0, -1):
            radius = i * 4
            alpha = int(255 * (i / 6) * 0.2)  # Fade from 20% to 0%
            draw.ellipse(
                [
                    center - radius,
                    center - radius,
                    center + radius,
                    center + radius,
                ],
                fill=(255, 255, 255, alpha),
            )

        # Bright center
        draw.ellipse(
            [center - 10, center - 10, center + 10, center + 10],
            fill=(255, 255, 255, 255),
        )

        # Small inner glow
        draw.ellipse(
            [center - 14, center - 14, center + 14, center + 14],
            fill=(255, 255, 255, 200),
        )

        return star

    def _draw_glowing_line(
        self,
        draw: ImageDraw.Draw,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color_base: Tuple[int, int, int] = (255, 220, 150),
    ) -> None:
        """
        Draw line with multi-layer glow effect.

        Creates a luminous halo by drawing 5 progressively thinner lines
        with increasing opacity, from widest/transparent to thinnest/opaque.

        Args:
            draw: ImageDraw object to draw on
            start: Starting point (x1, y1)
            end: Ending point (x2, y2)
            color_base: Base RGB color (default: golden)

        Layers (drawn from external to center):
            Layer 5: 8px width, 40 alpha  - Wide, very transparent halo
            Layer 4: 6px width, 70 alpha  - Intermediate diffusion
            Layer 3: 4px width, 110 alpha - Transition
            Layer 2: 3px width, 150 alpha - Near center
            Layer 1: 2px width, 190 alpha - Sharp, luminous center
        """
        # Layer configuration: (width, alpha) from external to center
        layers = [
            (8, 40),   # External halo
            (6, 70),   # Diffusion
            (4, 110),  # Transition
            (3, 150),  # Near center
            (2, 190),  # Center line
        ]

        # Draw each layer from widest to thinnest
        for width, alpha in layers:
            color = (*color_base, alpha)
            draw.line([start, end], fill=color, width=width)

    def compose(
        self,
        background: Image.Image,
        star_positions: list[Tuple[int, int]],
        connections: list[Tuple[int, int]],
    ) -> Image.Image:
        """
        Compose constellation with multiple layers.

        Layers are composited in order:
        1. Background (nebula from Imagen)
        2. Connection lines (semi-transparent golden lines)
        3. Stars (sprites with glow effect)

        Args:
            background: Nebula background image from Imagen
            star_positions: List of (x, y) positions for stars
            connections: List of (idx1, idx2) tuples for lines between stars

        Returns:
            Composed RGBA image ready for label overlay

        Example:
            >>> result = composer.compose(
            ...     background=nebula,
            ...     star_positions=[(300, 200), (500, 400), (700, 350)],
            ...     connections=[(0, 1), (1, 2)],
            ... )
        """
        logger.info(
            f"Composing constellation: {len(star_positions)} stars, "
            f"{len(connections)} connections"
        )

        # Layer 1: Background (convert to RGBA for alpha compositing)
        result = background.convert("RGBA")
        logger.debug("Layer 1: Background converted to RGBA")

        # Layer 2: Connection lines
        line_layer = Image.new("RGBA", self.canvas_size, (0, 0, 0, 0))
        line_draw = ImageDraw.Draw(line_layer)

        for idx1, idx2 in connections:
            if idx1 >= len(star_positions) or idx2 >= len(star_positions):
                logger.warning(
                    f"Invalid connection ({idx1}, {idx2}), "
                    f"skipping (only {len(star_positions)} stars)"
                )
                continue

            x1, y1 = star_positions[idx1]
            x2, y2 = star_positions[idx2]

            # Draw glowing line with multi-layer effect (5 layers)
            self._draw_glowing_line(
                draw=line_draw,
                start=(x1, y1),
                end=(x2, y2),
            )

        result = Image.alpha_composite(result, line_layer)
        logger.debug(f"Layer 2: Drew {len(connections)} glowing connection lines")

        # Layer 3: Stars (random sprite per star)
        star_layer = Image.new("RGBA", self.canvas_size, (0, 0, 0, 0))

        for i, (x, y) in enumerate(star_positions):
            # Choose random sprite for this star
            sprite = random.choice(self.star_sprites)

            # Center sprite on position
            offset_x = x - sprite.width // 2
            offset_y = y - sprite.height // 2

            # Paste star with alpha channel
            star_layer.paste(sprite, (offset_x, offset_y), sprite)

        result = Image.alpha_composite(result, star_layer)
        logger.debug(f"Layer 3: Placed {len(star_positions)} stars (random sprites)")

        logger.info("✓ Constellation composition complete")

        return result

    def create_debug_visualization(
        self,
        background: Image.Image,
        star_positions: list[Tuple[int, int]],
        connections: list[Tuple[int, int]],
        output_path: str,
    ) -> None:
        """
        Create debug visualization showing composition structure.

        Draws star positions as numbered circles and connection lines
        for debugging and validation.

        Args:
            background: Background image
            star_positions: Star positions
            connections: Line connections
            output_path: Path to save debug image

        Example:
            >>> composer.create_debug_visualization(
            ...     background=nebula,
            ...     star_positions=positions,
            ...     connections=connections,
            ...     output_path="debug_composition.png"
            ... )
        """
        debug_image = background.copy().convert("RGBA")
        draw = ImageDraw.Draw(debug_image)

        # Draw connections in green
        for idx1, idx2 in connections:
            x1, y1 = star_positions[idx1]
            x2, y2 = star_positions[idx2]
            draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 0, 255), width=2)

        # Draw star positions as numbered circles
        for i, (x, y) in enumerate(star_positions):
            # Red circle
            draw.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(255, 0, 0, 255))

            # White number
            draw.text((x - 5, y - 10), str(i), fill=(255, 255, 255, 255))

        debug_image.save(output_path)
        logger.info(f"✓ Saved debug visualization to {output_path}")
