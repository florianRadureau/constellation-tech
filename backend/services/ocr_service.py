"""
Service OCR pour extraire le texte des PDFs scannés.

Utilise Google Cloud Vision API pour la reconnaissance optique de caractères (OCR).
Ce service est automatiquement utilisé en fallback quand un PDF n'a pas de texte extractible.
"""

import io
import logging
from typing import List

import fitz  # PyMuPDF
import google.auth
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image

from config import settings
from exceptions.ocr_exceptions import (
    OCRConversionError,
    OCRError,
    OCRTimeoutError,
)

logger = logging.getLogger(__name__)


class OCRService:
    """
    Service d'extraction de texte via OCR (Google Cloud Vision API).

    Utilisé automatiquement en fallback quand un PDF scanné est détecté
    (pas de texte extractible avec pypdf).

    Example:
        >>> ocr = OCRService()
        >>> text = ocr.extract_text_from_pdf(pdf_bytes)
        >>> print(text)  # Texte extrait via OCR
    """

    # Paramètres Vision API
    TIMEOUT_SECONDS = 60  # Timeout par page
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB max par image

    def __init__(self) -> None:
        """
        Initialise le service OCR avec Vision API credentials.

        Utilise service account file en développement ou default credentials en production.
        """
        self._initialize_vision_client()
        logger.info("OCRService initialized successfully")

    def _initialize_vision_client(self) -> None:
        """
        Initialise le client Google Cloud Vision API.

        Uses service account file in development or default credentials in production (Cloud Run).
        """
        import os

        credentials_path = settings.google_application_credentials

        # Check if credentials file exists (local development)
        if os.path.exists(credentials_path):
            logger.info(f"Using service account file: {credentials_path}")
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        else:
            # Production (Cloud Run) - use default credentials
            logger.info("Using default environment credentials (Cloud Run)")
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )

        self.client = vision.ImageAnnotatorClient(credentials=credentials)

        logger.info("Vision API client initialized")

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extrait le texte d'un PDF scanné via OCR.

        Process:
        1. Convertir chaque page PDF → image PNG
        2. Envoyer chaque image à Vision API (document_text_detection)
        3. Assembler le texte de toutes les pages
        4. Nettoyer le texte (espaces, sauts de ligne)

        Args:
            pdf_bytes: Contenu binaire du PDF

        Returns:
            Texte extrait via OCR (nettoyé)

        Raises:
            OCRConversionError: Si conversion PDF → images échoue
            OCRError: Si extraction OCR échoue
            OCRTimeoutError: Si timeout Vision API

        Example:
            >>> ocr = OCRService()
            >>> text = ocr.extract_text_from_pdf(pdf_bytes)
        """
        logger.info("Starting OCR extraction from PDF")

        try:
            # 1. Convertir PDF → images (une par page)
            images = self._pdf_to_images(pdf_bytes)
            logger.info(f"Converted PDF to {len(images)} images")

            # 2. Extraire texte de chaque image via Vision API
            text_parts: List[str] = []
            for page_num, image_bytes in enumerate(images, start=1):
                logger.debug(f"OCR page {page_num}/{len(images)}")
                page_text = self._ocr_image(image_bytes)
                if page_text.strip():
                    text_parts.append(page_text)

            # 3. Vérifier qu'on a du texte
            if not text_parts:
                raise OCRError("Aucun texte détecté via OCR dans le PDF")

            # 4. Assembler et nettoyer
            full_text = "\n\n".join(text_parts)  # Double \n entre pages
            clean_text = self._clean_text(full_text)

            logger.info(
                f"OCR extraction successful: {len(images)} pages, "
                f"{len(clean_text)} chars"
            )

            return clean_text

        except OCRError:
            # Re-raise nos propres erreurs
            raise
        except Exception as e:
            # Capture les autres erreurs
            logger.error(f"OCR extraction failed: {e}", exc_info=True)
            raise OCRError(f"Erreur lors de l'extraction OCR: {str(e)}") from e

    def _pdf_to_images(self, pdf_bytes: bytes) -> List[bytes]:
        """
        Convertit un PDF en liste d'images PNG (une par page).

        Utilise PyMuPDF (fitz) pour le rendu des pages en images haute qualité.

        Args:
            pdf_bytes: Contenu binaire du PDF

        Returns:
            Liste des images (bytes PNG) pour chaque page

        Raises:
            OCRConversionError: Si conversion échoue
        """
        try:
            # Ouvrir le PDF avec PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

            images: List[bytes] = []

            # Convertir chaque page en image
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Rendre la page en image (haute résolution: 300 DPI)
                # zoom = 2.0 → 144 DPI, zoom = 3.0 → 216 DPI, zoom = 4.0 → 288 DPI
                zoom = 3.0  # Bon compromis qualité/taille
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)

                # Convertir pixmap → bytes PNG
                image_bytes = pix.tobytes("png")

                # Vérifier taille image
                if len(image_bytes) > self.MAX_IMAGE_SIZE:
                    logger.warning(
                        f"Page {page_num + 1} image too large "
                        f"({len(image_bytes) / 1024 / 1024:.1f} MB), "
                        "reducing quality"
                    )
                    # Réessayer avec résolution réduite
                    mat = fitz.Matrix(2.0, 2.0)  # 144 DPI
                    pix = page.get_pixmap(matrix=mat)
                    image_bytes = pix.tobytes("png")

                images.append(image_bytes)

            pdf_document.close()

            return images

        except Exception as e:
            logger.error(f"PDF to images conversion failed: {e}", exc_info=True)
            raise OCRConversionError(
                f"Impossible de convertir le PDF en images: {str(e)}"
            ) from e

    def _ocr_image(self, image_bytes: bytes) -> str:
        """
        Extrait le texte d'une image via Vision API.

        Utilise document_text_detection qui est optimisé pour les documents
        (vs text_detection qui est général).

        Args:
            image_bytes: Image en bytes (PNG/JPEG)

        Returns:
            Texte détecté dans l'image

        Raises:
            OCRTimeoutError: Si timeout
            OCRError: Si échec Vision API
        """
        try:
            # Créer l'objet Image pour Vision API
            image = vision.Image(content=image_bytes)

            # Appel Vision API avec timeout
            response = self.client.document_text_detection(
                image=image, timeout=self.TIMEOUT_SECONDS
            )

            # Vérifier erreurs API
            if response.error.message:
                raise OCRError(
                    f"Vision API error: {response.error.message}"
                )

            # Extraire le texte
            if response.full_text_annotation:
                return response.full_text_annotation.text
            else:
                # Pas de texte détecté (page vide ou image non-textuelle)
                return ""

        except google.api_core.exceptions.DeadlineExceeded:
            raise OCRTimeoutError(self.TIMEOUT_SECONDS)
        except OCRError:
            raise
        except Exception as e:
            logger.error(f"Vision API call failed: {e}", exc_info=True)
            raise OCRError(f"Erreur Vision API: {str(e)}") from e

    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte extrait par OCR.

        Opérations:
        - Remplace sauts de ligne multiples par un seul
        - Remplace espaces/tabs multiples par un seul espace
        - Enlève espaces début/fin de chaque ligne
        - Trim général

        Args:
            text: Texte brut extrait

        Returns:
            Texte nettoyé
        """
        import re

        # Remplacer sauts de ligne multiples
        text = re.sub(r"\n\n+", "\n\n", text)  # Max 2 \n consécutifs

        # Remplacer espaces/tabs multiples
        text = re.sub(r"[ \t]+", " ", text)

        # Nettoyer chaque ligne
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        text = "\n".join(lines)

        # Trim général
        text = text.strip()

        return text
