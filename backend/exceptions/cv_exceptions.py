"""
Exceptions personnalisées pour le parsing de CV.
"""


class CVParserError(Exception):
    """
    Exception levée lors d'erreurs de parsing de CV.

    Utilisée pour :
    - Fichiers trop volumineux
    - Formats non supportés
    - Fichiers corrompus
    - PDF sans texte extractible (scannés)
    """
    pass