"""
Exceptions personnalisées pour le service OCR.

Ces exceptions sont levées lors de l'utilisation du service OCR
avec Google Cloud Vision API.
"""


class OCRError(Exception):
    """
    Exception de base pour toutes les erreurs OCR.

    Hérite de Exception et sert de base pour toutes les erreurs
    spécifiques au service OCR.
    """

    pass


class OCRQuotaExceededError(OCRError):
    """
    Exception levée quand le quota Vision API est dépassé.

    Vision API gratuit: 1000 pages/mois
    Au-delà: ~1.50$ / 1000 pages

    Attributes:
        current_count: Nombre de pages OCR ce mois
        max_quota: Quota maximum autorisé
    """

    def __init__(self, current_count: int, max_quota: int):
        """
        Initialise l'exception avec les compteurs de quota.

        Args:
            current_count: Nombre d'appels OCR ce mois
            max_quota: Quota maximum autorisé
        """
        self.current_count = current_count
        self.max_quota = max_quota
        super().__init__(
            f"Quota Vision API dépassé: {current_count}/{max_quota} pages ce mois"
        )


class OCRTimeoutError(OCRError):
    """
    Exception levée quand l'appel Vision API timeout.

    Peut arriver avec des PDFs très longs ou connexion lente.
    """

    def __init__(self, timeout_seconds: int):
        """
        Initialise l'exception avec la durée du timeout.

        Args:
            timeout_seconds: Durée du timeout en secondes
        """
        self.timeout_seconds = timeout_seconds
        super().__init__(
            f"Timeout Vision API après {timeout_seconds}s"
        )


class OCRConversionError(OCRError):
    """
    Exception levée lors de la conversion PDF → images.

    Peut arriver si le PDF est corrompu ou mal formé.
    """

    pass
