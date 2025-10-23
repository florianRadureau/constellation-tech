"""
Constellation generation orchestrator.

Coordinates the full pipeline from CV to final constellation image.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict

from PIL import Image

from services.cv_parser import CVParser
from services.image_generator import ImageGenerator
from services.prompt_generator import PromptGenerator
from services.star_detector import StarDetector
from services.storage_service import StorageService
from services.tech_analyzer import TechAnalyzer
from services.technology_mapper import TechnologyMapper
from services.text_overlay_service import TextOverlayService
from services.title_generator import TitleGenerator

logger = logging.getLogger(__name__)


@dataclass
class ConstellationResult:
    """
    Result of constellation generation.

    Attributes:
        image_url: Public URL to generated image
        title: Generated title
        technologies: List of detected technologies
        stats: Technology statistics
        generation_time: Time taken in seconds
        stars_detected: Number of stars detected
    """

    image_url: str
    title: str
    technologies: list[Dict[str, Any]]
    stats: Dict[str, Any]
    generation_time: float
    stars_detected: int


class ConstellationOrchestrator:
    """
    Orchestrate full constellation generation pipeline.

    Coordinates all services to transform a CV into a beautiful constellation.

    Pipeline:
    1. Parse CV → text
    2. Analyze → technologies
    3. Generate title
    4. Generate prompt
    5. Generate image (Vertex AI)
    6. Detect stars
    7. Map stars → technologies
    8. Add text overlays
    9. Upload to GCS
    10. Return result

    Example:
        >>> orchestrator = ConstellationOrchestrator()
        >>> result = await orchestrator.generate(cv_bytes, "cv.pdf")
        >>> print(result.image_url)
    """

    def __init__(self) -> None:
        """Initialize all services."""
        logger.info("Initializing ConstellationOrchestrator...")

        self.cv_parser = CVParser()
        self.tech_analyzer = TechAnalyzer()
        self.title_generator = TitleGenerator()
        self.prompt_generator = PromptGenerator()
        self.image_generator = ImageGenerator()
        self.star_detector = StarDetector()
        self.tech_mapper = TechnologyMapper()
        self.text_overlay = TextOverlayService()
        self.storage = StorageService()

        logger.info("ConstellationOrchestrator initialized successfully")

    async def generate(
        self, cv_content: bytes, cv_filename: str
    ) -> ConstellationResult:
        """
        Generate constellation from CV.

        Full pipeline with error handling and logging at each step.

        Args:
            cv_content: CV file bytes
            cv_filename: CV filename (for format detection)

        Returns:
            ConstellationResult with image URL and metadata

        Raises:
            Various exceptions from individual services

        Example:
            >>> with open("cv.pdf", "rb") as f:
            ...     result = await orchestrator.generate(f.read(), "cv.pdf")
        """
        start_time = time.time()

        logger.info(f"=" * 80)
        logger.info(f"Starting constellation generation for: {cv_filename}")
        logger.info(f"=" * 80)

        try:
            # Step 1: Parse CV
            logger.info("[1/10] Parsing CV...")
            text = CVParser.extract_text(cv_content, cv_filename)
            logger.info(f"✓ Extracted {len(text)} characters")

            # Step 2: Analyze technologies
            logger.info("[2/10] Analyzing technologies...")
            analysis = self.tech_analyzer.analyze(text)
            technologies = analysis["technologies"]
            stats = analysis["stats"]
            logger.info(
                f"✓ Detected {stats['total_techs_found']} technologies "
                f"(dominant: {stats['dominant_category']})"
            )

            # Step 3: Generate title
            logger.info("[3/10] Generating title...")
            title = self.title_generator.generate(stats)
            logger.info(f"✓ Title: {title}")

            # Step 4: Generate prompt
            logger.info("[4/10] Generating prompt...")
            tech_count = min(len(technologies), 15)  # Limit for Imagen
            prompt = self.prompt_generator.generate_from_stats(stats, tech_count)
            logger.info(f"✓ Prompt generated ({tech_count} stars)")

            # Step 5: Generate image with Vertex AI
            logger.info("[5/10] Generating constellation image (Vertex AI)...")
            logger.info("⏳ This may take 15-30 seconds...")
            raw_image = await self.image_generator.generate(prompt)
            logger.info(f"✓ Image generated: {raw_image.size}")

            # Step 6: Detect stars
            logger.info("[6/10] Detecting stars...")
            stars = self.star_detector.detect_with_adjustable_threshold(
                raw_image, target_count=tech_count
            )
            logger.info(f"✓ Detected {len(stars)} stars")

            # Step 7: Map stars to technologies
            logger.info("[7/10] Mapping stars to technologies...")
            mappings = self.tech_mapper.map(stars, technologies)
            logger.info(f"✓ Created {len(mappings)} mappings")

            # Step 8: Add text overlays
            logger.info("[8/10] Adding text overlays...")
            final_image = self.text_overlay.compose(raw_image, mappings, title)
            logger.info("✓ Text overlays added")

            # Step 9: Upload to Cloud Storage
            logger.info("[9/10] Uploading to Cloud Storage...")
            image_url = await self.storage.upload(final_image)
            logger.info(f"✓ Uploaded: {image_url[:60]}...")

            # Step 10: Build result
            generation_time = time.time() - start_time
            logger.info(f"[10/10] Generation complete in {generation_time:.2f}s")

            result = ConstellationResult(
                image_url=image_url,
                title=title,
                technologies=technologies,
                stats=stats,
                generation_time=generation_time,
                stars_detected=len(stars),
            )

            logger.info(f"=" * 80)
            logger.info("✅ CONSTELLATION GENERATION SUCCESSFUL")
            logger.info(f"   Title: {title}")
            logger.info(f"   Technologies: {len(technologies)}")
            logger.info(f"   Stars: {len(stars)}")
            logger.info(f"   Time: {generation_time:.2f}s")
            logger.info(f"=" * 80)

            return result

        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"=" * 80)
            logger.error(f"❌ GENERATION FAILED after {generation_time:.2f}s")
            logger.error(f"   Error: {e}")
            logger.error(f"=" * 80)
            raise

    def get_quota_status(self) -> Dict[str, Any]:
        """
        Get current quota status from ImageGenerator.

        Returns:
            Quota information dict

        Example:
            >>> status = orchestrator.get_quota_status()
            >>> print(status["remaining"])
        """
        return self.image_generator.get_quota_status()
