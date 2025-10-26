"""
Tests unitaires pour OCRService.

Mock Vision API pour éviter d'appeler l'API réelle.
"""

import io
from unittest.mock import MagicMock, Mock, patch

import pytest
from google.cloud import vision

from exceptions.ocr_exceptions import OCRConversionError, OCRError, OCRTimeoutError
from services.ocr_service import OCRService


class TestOCRService:
    """Tests pour OCRService."""

    @pytest.fixture
    def mock_vision_client(self):
        """Mock Vision API client."""
        with patch("services.ocr_service.vision.ImageAnnotatorClient") as mock:
            yield mock

    @pytest.fixture
    def ocr_service(self, mock_vision_client):
        """Crée une instance OCRService avec Vision API mockée."""
        with patch("services.ocr_service.OCRService._initialize_vision_client"):
            service = OCRService()
            service.client = mock_vision_client.return_value
            return service

    def test_clean_text(self, ocr_service):
        """Test nettoyage du texte."""
        # Texte avec espaces multiples et sauts de ligne multiples
        dirty_text = "Hello   World\n\n\n\nTest   Text\n  \n  "

        clean = ocr_service._clean_text(dirty_text)

        assert "   " not in clean  # Pas d'espaces multiples
        assert "\n\n\n" not in clean  # Max 2 \n consécutifs
        assert clean.strip() == clean  # Pas d'espaces début/fin

    def test_pdf_to_images_success(self, ocr_service):
        """Test conversion PDF → images."""
        # Créer un PDF simple avec une page blanche
        import fitz

        pdf_doc = fitz.open()
        page = pdf_doc.new_page(width=595, height=842)  # A4
        page.insert_text((50, 50), "Test Text")
        pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

        # Convertir
        images = ocr_service._pdf_to_images(pdf_bytes)

        assert len(images) == 1
        assert isinstance(images[0], bytes)
        assert len(images[0]) > 0

    def test_pdf_to_images_corrupted_pdf(self, ocr_service):
        """Test conversion avec PDF corrompu."""
        corrupted_pdf = b"not a valid pdf"

        with pytest.raises(OCRConversionError):
            ocr_service._pdf_to_images(corrupted_pdf)

    def test_ocr_image_with_text(self, ocr_service):
        """Test OCR d'une image contenant du texte."""
        # Mock la réponse Vision API
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.full_text_annotation.text = "Extracted Text From Image"

        ocr_service.client.document_text_detection.return_value = mock_response

        # Image factice (peu importe le contenu pour le mock)
        fake_image_bytes = b"fake image data"

        text = ocr_service._ocr_image(fake_image_bytes)

        assert text == "Extracted Text From Image"
        ocr_service.client.document_text_detection.assert_called_once()

    def test_ocr_image_no_text(self, ocr_service):
        """Test OCR d'une image sans texte."""
        # Mock réponse sans texte
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.full_text_annotation = None

        ocr_service.client.document_text_detection.return_value = mock_response

        fake_image_bytes = b"fake image"

        text = ocr_service._ocr_image(fake_image_bytes)

        assert text == ""  # Pas de texte détecté

    def test_ocr_image_api_error(self, ocr_service):
        """Test OCR avec erreur Vision API."""
        # Mock erreur API
        mock_response = Mock()
        mock_response.error.message = "API Rate Limit Exceeded"

        ocr_service.client.document_text_detection.return_value = mock_response

        fake_image_bytes = b"fake image"

        with pytest.raises(OCRError) as exc_info:
            ocr_service._ocr_image(fake_image_bytes)

        assert "API Rate Limit Exceeded" in str(exc_info.value)

    def test_ocr_image_timeout(self, ocr_service):
        """Test OCR avec timeout."""
        import google.api_core.exceptions

        # Mock timeout exception
        ocr_service.client.document_text_detection.side_effect = (
            google.api_core.exceptions.DeadlineExceeded("Timeout")
        )

        fake_image_bytes = b"fake image"

        with pytest.raises(OCRTimeoutError):
            ocr_service._ocr_image(fake_image_bytes)

    @patch("services.ocr_service.OCRService._pdf_to_images")
    @patch("services.ocr_service.OCRService._ocr_image")
    def test_extract_text_from_pdf_success(
        self, mock_ocr_image, mock_pdf_to_images, ocr_service
    ):
        """Test extraction complète d'un PDF scanné."""
        # Mock conversion PDF → images (2 pages)
        mock_pdf_to_images.return_value = [b"image1", b"image2"]

        # Mock OCR de chaque page
        mock_ocr_image.side_effect = ["Page 1 text", "Page 2 text"]

        fake_pdf = b"fake pdf bytes"

        text = ocr_service.extract_text_from_pdf(fake_pdf)

        assert "Page 1 text" in text
        assert "Page 2 text" in text
        assert mock_pdf_to_images.called
        assert mock_ocr_image.call_count == 2

    @patch("services.ocr_service.OCRService._pdf_to_images")
    @patch("services.ocr_service.OCRService._ocr_image")
    def test_extract_text_from_pdf_no_text_detected(
        self, mock_ocr_image, mock_pdf_to_images, ocr_service
    ):
        """Test extraction d'un PDF sans texte détectable."""
        mock_pdf_to_images.return_value = [b"image1"]
        mock_ocr_image.return_value = ""  # Pas de texte

        fake_pdf = b"fake pdf"

        with pytest.raises(OCRError) as exc_info:
            ocr_service.extract_text_from_pdf(fake_pdf)

        assert "Aucun texte détecté" in str(exc_info.value)

    @patch("services.ocr_service.OCRService._pdf_to_images")
    def test_extract_text_from_pdf_conversion_error(
        self, mock_pdf_to_images, ocr_service
    ):
        """Test extraction avec erreur de conversion."""
        mock_pdf_to_images.side_effect = OCRConversionError("Conversion failed")

        fake_pdf = b"bad pdf"

        with pytest.raises(OCRError):
            ocr_service.extract_text_from_pdf(fake_pdf)
