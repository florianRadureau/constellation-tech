"""
Exceptions personnalisées du projet Constellation Tech.
"""

from .cv_exceptions import CVParserError
from .ocr_exceptions import (
    OCRError,
    OCRQuotaExceededError,
    OCRTimeoutError,
    OCRConversionError,
)

__all__ = [
    "CVParserError",
    "OCRError",
    "OCRQuotaExceededError",
    "OCRTimeoutError",
    "OCRConversionError",
]