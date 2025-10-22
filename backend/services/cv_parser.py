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