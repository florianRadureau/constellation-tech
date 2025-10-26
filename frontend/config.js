/**
 * ============================================
 * CONSTELLATION TECH - CONFIGURATION
 * ============================================
 *
 * Fichier de configuration centralisé.
 * Modifiez ces valeurs avant le déploiement.
 */

const CONFIG = {
    /**
     * URL de l'API Backend (Cloud Run)
     *
     * DÉVELOPPEMENT : 'http://localhost:8000'
     * PRODUCTION : 'https://constellation-tech-backend-330986367561.europe-west1.run.app/'
     */
    API_BASE_URL: 'https://constellation-tech-backend-330986367561.europe-west1.run.app/',

    /**
     * Liens Sociaux
     *
     * TODO: Remplacer par vos URLs personnelles
     */
    SOCIAL_LINKS: {
        github: 'https://github.com/florianRadureau/constellation-tech',
        linkedin: 'https://linkedin.com/in/florianradureau',
    },

    /**
     * Paramètres de Validation Fichier
     */
    FILE_VALIDATION: {
        maxSizeMB: 5,
        maxSizeBytes: 5 * 1024 * 1024,
        allowedExtensions: ['.pdf', '.docx'],
        allowedMimeTypes: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    },

    /**
     * Paramètres API
     */
    API_SETTINGS: {
        timeoutMs: 60000, // 60 secondes (1 minute)
        retryAttempts: 1,
    },

    /**
     * Animation & UI
     */
    UI_CONFIG: {
        loadingSimulationSteps: [
            { progress: 20, text: 'Analyse des technologies...', delayMs: 3000 },
            { progress: 40, text: 'Génération du titre poétique...', delayMs: 3000 },
            { progress: 60, text: 'Création de la constellation avec Imagen...', delayMs: 3000 },
            { progress: 80, text: 'Détection des étoiles...', delayMs: 3000 },
            { progress: 95, text: 'Finalisation...', delayMs: 3000 },
        ],
        particlesEnabled: true, // Désactiver sur mobile pour performance
        particlesCount: 200,
    },

    /**
     * Textes de l'Interface
     */
    TEXTS: {
        hero: {
            title: 'Votre CV Tech devient une Constellation Spatiale',
            subtitle: 'L\'IA analyse vos compétences et génère une visualisation cosmique unique en 15 secondes. Gratuit, confidentiel, spectaculaire.',
        },
        privacy: '🔒 Nous ne conservons aucun CV. Votre fichier est analysé temporairement puis supprimé.',
        footer: {
            credit: 'Made with ❤️ and AI • Powered by Google Vertex AI Imagen',
        },
    },

    /**
     * Messages d'Erreur
     */
    ERROR_MESSAGES: {
        400: {
            title: 'Fichier invalide',
            getCTA: () => 'Choisir un autre fichier',
        },
        429: {
            title: 'Quota quotidien atteint',
            getCTA: () => 'Me contacter',
        },
        500: {
            title: 'Erreur serveur',
            getCTA: () => 'Réessayer',
        },
        network: {
            title: 'Erreur de connexion',
            message: 'Impossible de contacter le serveur. Vérifiez votre connexion internet et réessayez.',
            getCTA: () => 'Recharger la page',
        },
        timeout: {
            title: 'Requête expirée',
            message: 'La génération a pris trop de temps (> 30 secondes). Veuillez réessayer.',
            getCTA: () => 'Réessayer',
        },
    },

    /**
     * Partage LinkedIn
     */
    LINKEDIN_SHARE: {
        getShareText: (title) =>
            `J'ai transformé mon CV tech en constellation spatiale avec l'IA ! 🌟\n\n` +
            `"${title}"\n\n` +
            `Généré par Constellation Tech - un projet open-source qui visualise ` +
            `les compétences techniques comme une carte stellaire.\n\n` +
            `#TechVisualization #AI #OpenSource`,
    },
};

// Export pour utilisation dans les modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
