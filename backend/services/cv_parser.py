"""
Service d'extraction de texte depuis CV (PDF et DOCX).
"""
import io
import re
from pypdf import PdfReader
from docx import Document
from exceptions import CVParserError


class CVParser:
    """Parse les CV pour en extraire le texte brut."""

    # Constantes de classe
    SUPPORTED_EXTENSIONS = ['pdf', 'docx', 'doc']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB en bytes

    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> str:
        """
        Point d'entrée principal : extrait le texte d'un CV.

        Args:
            file_content: Contenu binaire du fichier
            filename: Nom du fichier (pour détecter l'extension)

        Returns:
            Texte extrait du CV

        Raises:
            CVParserError: Si l'extraction échoue
        """
        # TODO: À implémenter
        pass

    @staticmethod
    def validate_file(file_content: bytes, filename: str) -> None:
        """
        Valide qu'un fichier peut être traité.

        Args:
            file_content: Contenu du fichier
            filename: Nom du fichier

        Raises:
            CVParserError: Si la validation échoue
        """
        # Validation 1 : Extension
        extension = filename.lower().split(".")[-1]
        if extension not in CVParser.SUPPORTED_EXTENSIONS:
            raise CVParserError(
                f"Format de fichier non supporté : .{extension}. "
                f"Formats acceptés : {', '.join(CVParser.SUPPORTED_EXTENSIONS).upper()}"
            )

        # Validation 2 : Taille
        file_size = len(file_content)
        if file_size > CVParser.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = CVParser.MAX_FILE_SIZE / (1024 * 1024)
            raise CVParserError(
                f"Fichier trop volumineux ({size_mb:.1f} MB). "
                f"Taille maximale : {max_mb:.0f} MB"
            )

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Nettoie le texte extrait.

        Opérations :
        - Remplace sauts de ligne multiples par un seul
        - Remplace espaces/tabs multiples par un seul espace
        - Enlève espaces début/fin de chaque ligne
        - Trim général

        Args:
            text: Texte brut extrait

        Returns:
            Texte nettoyé
        """
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)

        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        text = text.strip()

        return text

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extrait le texte d'un PDF.

        Args:
            file_content: Contenu binaire du fichier PDF

        Returns:
            Texte extrait (nettoyé)

        Raises:
            CVParserError: Si l'extraction échoue
        """
        try:
            # 1. BytesIO
            with io.BytesIO(file_content) as pdf_file:
                # 2. PdfReader
                reader = PdfReader(pdf_file)

            # 3. Vérifier qu'il y a des pages
                if len(reader.pages) == 0:
                    raise CVParserError("...")

                # 4. Extraire le texte de chaque page
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                # 5. Vérifier qu'on a du texte
                if not text_parts:
                    raise CVParserError("Aucun texte extractible...")

                # 6. Joindre et nettoyer
                full_text = "\n".join(text_parts)
                return CVParser._clean_text(full_text)

        except CVParserError:
            # Re-raise nos propres erreurs
            raise
        except Exception as e:
            # Capture les autres erreurs
            raise CVParserError(f"Erreur lecture PDF: {str(e)}")