"""
Star position dataclass for constellation mapping.

Contains only the StarPosition dataclass used across the constellation
generation pipeline. Star detection is no longer performed - positions
are now pre-calculated in constellation templates.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class StarPosition:
    """
    Position and metadata for a star in a constellation.

    Used for mapping technologies to pre-calculated constellation positions.

    Attributes:
        x: X coordinate in pixels
        y: Y coordinate in pixels
        brightness: Brightness value (0-255)
        color: RGB color tuple
        size: Size/area indicator
    """

    x: int
    y: int
    brightness: float
    color: Tuple[int, int, int]
    size: int

    def __repr__(self) -> str:
        """String representation for logging."""
        return (
            f"Star(x={self.x}, y={self.y}, brightness={self.brightness:.1f}, "
            f"size={self.size}, color={self.color})"
        )
