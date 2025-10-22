"""
Tests unitaires pour le service CVParser.
"""
import pytest
from services.cv_parser import CVParser
from exceptions import CVParserError


class TestValidateFile:
    """Tests de la méthode validate_file."""

    def test_valid_pdf(self):
        """Test avec un PDF valide."""
        fake_pdf = b"fake pdf content"
        # Si aucune exception levée = test réussi
        CVParser.validate_file(fake_pdf, "mon_cv.pdf")

    def test_valid_docx(self):
        """Test avec un DOCX valide."""
        fake_docx = b"fake docx content"
        CVParser.validate_file(fake_docx, "cv.docx")

    def test_invalid_extension_txt(self):
        """Test avec extension .txt (invalide)."""
        with pytest.raises(CVParserError) as exc_info:
            CVParser.validate_file(b"content", "document.txt")

        # Vérifie que le message contient l'extension
        assert "txt" in str(exc_info.value).lower()
        assert "supporté" in str(exc_info.value).lower()

    def test_invalid_extension_jpg(self):
        """Test avec extension .jpg (invalide)."""
        with pytest.raises(CVParserError) as exc_info:
            CVParser.validate_file(b"content", "image.jpg")

        assert "jpg" in str(exc_info.value).lower()

    def test_file_too_large(self):
        """Test avec fichier trop volumineux (6 MB)."""
        big_file = b"a" * (6 * 1024 * 1024)  # 6 MB

        with pytest.raises(CVParserError) as exc_info:
            CVParser.validate_file(big_file, "gros_cv.pdf")

        # Vérifie que le message parle de taille
        error_message = str(exc_info.value).lower()
        assert "volumineux" in error_message or "mb" in error_message

    def test_exact_max_size(self):
        """Test avec fichier exactement à la limite (5 MB)."""
        max_file = b"a" * (5 * 1024 * 1024)  # Exactement 5 MB

        # Devrait passer (limite inclusive)
        CVParser.validate_file(max_file, "limite.pdf")

    def test_case_insensitive_extension(self):
        """Test que l'extension est case-insensitive."""
        # PDF, Pdf, pdf doivent tous fonctionner
        CVParser.validate_file(b"content", "cv.PDF")
        CVParser.validate_file(b"content", "cv.Pdf")
        CVParser.validate_file(b"content", "cv.DOCX")

class TestCleanText:
    """Tests de la méthode _clean_text (TDD)."""

    def test_multiple_consecutive_newlines(self):
        """Test que les newlines consécutifs deviennent un seul."""
        dirty = "Ligne1\n\n\nLigne2"
        expected = "Ligne1\nLigne2"
        assert CVParser._clean_text(dirty) == expected

    def test_multiple_spaces(self):
        """Test que les espaces multiples deviennent un seul."""
        dirty = "Mot1    Mot2"
        expected = "Mot1 Mot2"
        assert CVParser._clean_text(dirty) == expected

    def test_tabs_become_single_space(self):
        """Test que les tabs deviennent un espace."""
        dirty = "Mot1\t\tMot2"
        expected = "Mot1 Mot2"
        assert CVParser._clean_text(dirty) == expected

    def test_strip_each_line(self):
        """Test que chaque ligne est strippée."""
        dirty = "  Ligne1  \n  Ligne2  "
        expected = "Ligne1\nLigne2"
        assert CVParser._clean_text(dirty) == expected

    def test_global_strip(self):
        """Test strip global du texte."""
        dirty = "\n\n  Texte  \n\n"
        expected = "Texte"
        assert CVParser._clean_text(dirty) == expected

class TestExtractTextFromPdf:
    """Tests de la méthode extract_text_from_pdf."""

    def test_extract_from_valid_pdf(self):
        """Test extraction depuis un PDF valide."""
        # Charge le PDF de test
        with open("tests/fixtures/sample_cv.pdf", "rb") as f:
            pdf_content = f.read()

        # Extrait le texte
        text = CVParser.extract_text_from_pdf(pdf_content)

        # Vérifie que le texte contient des éléments attendus
        assert "Python" in text or "python" in text.lower()
        assert len(text) > 10  # Au moins quelques caractères

    def test_extract_corrupted_pdf_raises_error(self):
        """Test avec un PDF corrompu."""
        corrupted = b"This is not a PDF file"

        with pytest.raises(CVParserError):
            CVParser.extract_text_from_pdf(corrupted)