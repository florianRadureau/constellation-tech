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
from services.image_composer import ImageComposer
from services.image_generator import ImageGenerator
from services.prompt_generator import PromptGenerator
from services.storage_service import StorageService
from services.tech_analyzer import TechAnalyzer
from services.technology_mapper import TechnologyMapper
from services.text_overlay_service import TextOverlayService
from services.title_generator import TitleGenerator
from utils.constellation_templates import get_constellation_template

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
        self.image_composer = ImageComposer()
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
            total_techs = analysis.get("total_techs_found", len(technologies))
            logger.info(
                f"✓ Detected {total_techs} technologies "
                f"(dominant: {stats.get('dominant_category', 'N/A')})"
            )

            # Step 3: Generate title
            logger.info("[3/10] Generating title...")
            title = self.title_generator.generate(stats)
            logger.info(f"✓ Title: {title}")

            # Step 4: Generate background-only prompt
            logger.info("[4/11] Generating nebula background prompt...")
            dominant_category = stats.get("dominant_category", "Other")
            background_prompt = self.prompt_generator.generate_background_only(
                dominant_category
            )
            logger.info(f"✓ Background prompt generated for category '{dominant_category}'")

            # Step 5: Generate nebula background with Vertex AI
            logger.info("[5/11] Generating nebula background (Vertex AI)...")
            logger.info("⏳ This may take 15-30 seconds...")
            background_image = await self.image_generator.generate(background_prompt)
            logger.info(f"✓ Nebula background generated: {background_image.size}")

            # Step 6: Select constellation template
            logger.info("[6/11] Selecting constellation template...")
            # Use hash of CV text for deterministic template selection
            template_index = hash(text) % 3  # Cycles through 3 available templates
            template = get_constellation_template(template_index)
            logger.info(f"✓ Selected template: {template['name']} ({len(template['stars'])} stars)")

            # Step 7: Map technologies to constellation positions
            logger.info("[7/11] Mapping technologies to constellation positions...")
            total_techs = len(technologies)
            available_positions = len(template["stars"])

            # Use only as many positions as we have technologies (up to template max)
            num_mappings = min(total_techs, available_positions)

            mappings = []
            for i in range(num_mappings):
                tech = technologies[i]
                star_x, star_y = template["stars"][i]

                # Create StarPosition at template position
                from services.star_detector import StarPosition
                star = StarPosition(
                    x=star_x,
                    y=star_y,
                    brightness=255,
                    color=(255, 255, 255),
                    size=20
                )

                # Create TechData
                from services.technology_mapper import TechData, StarTechMapping
                tech_data = TechData(
                    name=tech["name"],
                    category=tech["category"],
                    color=tech.get("color", "#FFFFFF"),
                    score=tech["score"],
                    size=tech.get("size", "medium")
                )

                # Create mapping
                mapping = StarTechMapping(star=star, tech=tech_data)
                mappings.append(mapping)

            logger.info(f"✓ Created {len(mappings)} position mappings")

            # Step 8: Compose image with layers
            logger.info("[8/11] Composing constellation layers...")
            composed_image = self.image_composer.compose(
                background=background_image,
                star_positions=template["stars"][:num_mappings],
                connections=template["connections"]
            )
            logger.info("✓ Constellation composed (background + lines + stars)")

            # Step 9: Add text overlays (title + labels)
            logger.info("[9/11] Adding text overlays...")
            final_image = self.text_overlay.compose(
                composed_image,
                mappings,
                title
            )
            logger.info("✓ Text overlays added")

            # Step 10: Upload to Cloud Storage
            logger.info("[10/11] Uploading to Cloud Storage...")
            image_url = await self.storage.upload(final_image)
            logger.info(f"✓ Uploaded: {image_url[:60]}...")

            # Step 11: Build result
            generation_time = time.time() - start_time
            logger.info(f"[11/11] Generation complete in {generation_time:.2f}s")

            result = ConstellationResult(
                image_url=image_url,
                title=title,
                technologies=technologies,
                stats=stats,
                generation_time=generation_time,
                stars_detected=num_mappings,
            )

            logger.info(f"=" * 80)
            logger.info("✅ CONSTELLATION GENERATION SUCCESSFUL")
            logger.info(f"   Title: {title}")
            logger.info(f"   Template: {template['name']}")
            logger.info(f"   Technologies: {len(technologies)}")
            logger.info(f"   Stars: {num_mappings}")
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
