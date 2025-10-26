/**
 * ============================================
 * CONSTELLATION TECH - MAIN SCRIPT
 * ============================================
 *
 * Architecture: Classes ES6 modulaires
 * Pattern: State Machine
 * Error Handling: Comprehensive avec retry logic
 */

'use strict';

/* ==================== CONSTANTS ==================== */
const STATES = {
    INITIAL: 'initial',
    VALIDATING: 'validating',
    UPLOADING: 'uploading',
    SUCCESS: 'success',
    ERROR: 'error',
};

/* ==================== STATE MANAGER ==================== */
class StateManager {
    constructor() {
        this.currentState = STATES.INITIAL;
        this.stateData = {};
    }

    setState(newState, data = {}) {
        console.log(`[StateManager] Transitioning: ${this.currentState} → ${newState}`);
        this.currentState = newState;
        this.stateData = data;
        UIController.updateUI(newState, data);
    }

    getState() {
        return this.currentState;
    }

    getData() {
        return this.stateData;
    }
}

/* ==================== FILE VALIDATOR ==================== */
class FileValidator {
    static validate(file) {
        if (!file) {
            return { valid: false, error: 'Aucun fichier sélectionné.' };
        }

        // Validation de l'extension
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!CONFIG.FILE_VALIDATION.allowedExtensions.includes(fileExtension)) {
            return {
                valid: false,
                error: `Format invalide. Veuillez uploader un fichier ${CONFIG.FILE_VALIDATION.allowedExtensions.join(' ou ')}.`,
            };
        }

        // Validation de la taille
        if (file.size > CONFIG.FILE_VALIDATION.maxSizeBytes) {
            const sizeMB = (file.size / 1024 / 1024).toFixed(1);
            return {
                valid: false,
                error: `Fichier trop volumineux (${sizeMB} MB). La taille maximale est de ${CONFIG.FILE_VALIDATION.maxSizeMB} MB.`,
            };
        }

        return { valid: true };
    }
}

/* ==================== API CLIENT ==================== */
class APIClient {
    static async generateConstellation(file) {
        const controller = new AbortController();
        const timeoutId = setTimeout(
            () => controller.abort(),
            CONFIG.API_SETTINGS.timeoutMs
        );

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(
                `${CONFIG.API_BASE_URL}/api/generate-constellation`,
                {
                    method: 'POST',
                    body: formData,
                    signal: controller.signal,
                }
            );

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw {
                    statusCode: response.status,
                    detail: errorData.detail || 'Une erreur est survenue.',
                };
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);

            // Timeout
            if (error.name === 'AbortError') {
                throw {
                    statusCode: 0,
                    detail: CONFIG.ERROR_MESSAGES.timeout.message,
                    type: 'timeout',
                };
            }

            // Network Error
            if (error instanceof TypeError) {
                throw {
                    statusCode: 0,
                    detail: CONFIG.ERROR_MESSAGES.network.message,
                    type: 'network',
                };
            }

            // API Error
            throw error;
        }
    }

    static async getQuota() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/quota`);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.warn('[APIClient] Failed to fetch quota:', error);
            return null;
        }
    }
}

/* ==================== PROGRESS SIMULATOR ==================== */
class ProgressSimulator {
    constructor() {
        this.interval = null;
        this.stepIndex = 0;
    }

    start() {
        this.stepIndex = 0;
        this.runNextStep();
    }

    runNextStep() {
        if (this.stepIndex >= CONFIG.UI_CONFIG.loadingSimulationSteps.length) {
            return;
        }

        const step = CONFIG.UI_CONFIG.loadingSimulationSteps[this.stepIndex];
        const progressBar = document.getElementById('progress-bar');
        const stepText = document.getElementById('loading-step');

        if (progressBar && stepText) {
            progressBar.style.width = `${step.progress}%`;
            stepText.textContent = step.text;
        }

        this.stepIndex++;

        this.interval = setTimeout(() => {
            this.runNextStep();
        }, step.delayMs);
    }

    stop() {
        if (this.interval) {
            clearTimeout(this.interval);
            this.interval = null;
        }

        // Compléter la barre à 100%
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = '100%';
        }
    }
}

/* ==================== UI CONTROLLER ==================== */
class UIController {
    static updateUI(state, data = {}) {
        // Masquer toutes les sections
        this.hideAllSections();

        // Afficher la bonne section
        switch (state) {
            case STATES.INITIAL:
                this.showSection('hero-section');
                break;

            case STATES.UPLOADING:
                this.showSection('loading-section');
                progressSimulator.start();
                break;

            case STATES.SUCCESS:
                this.showSection('result-section');
                this.displayResult(data);
                this.scrollToSection('result-section');
                break;

            case STATES.ERROR:
                this.showSection('error-section');
                this.displayError(data);
                break;
        }
    }

    static hideAllSections() {
        const sections = ['hero-section', 'loading-section', 'result-section', 'error-section'];
        sections.forEach((id) => {
            const section = document.getElementById(id);
            if (section) {
                section.style.display = 'none';
            }
        });
    }

    static showSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'flex';
            section.classList.add('fade-in');
        }
    }

    static scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            setTimeout(() => {
                section.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start',
                });
            }, 300);
        }
    }

    static displayResult(data) {
        progressSimulator.stop();

        // Image
        const resultImage = document.getElementById('result-image');
        if (resultImage && data.image_url) {
            resultImage.src = data.image_url;
            resultImage.alt = `Constellation: ${data.title || 'Votre profil technique'}`;
        }

        // Titre
        const resultTitle = document.getElementById('result-title');
        if (resultTitle && data.title) {
            resultTitle.textContent = data.title;
        }

        // Technologies
        const techList = document.getElementById('technologies-list');
        if (techList && data.technologies) {
            techList.innerHTML = '';
            data.technologies.forEach((tech) => {
                const badge = this.createTechBadge(tech);
                techList.appendChild(badge);
            });
        }

        // Stats
        if (data.stats) {
            const statTotal = document.getElementById('stat-total');
            const statCategory = document.getElementById('stat-category');
            const statLevel = document.getElementById('stat-level');

            if (statTotal) statTotal.textContent = data.stats.total_technologies || 0;
            if (statCategory) statCategory.textContent = data.stats.dominant_category || '-';
            if (statLevel) statLevel.textContent = data.stats.experience_level || '-';
        }
    }

    static createTechBadge(tech) {
        const badge = document.createElement('div');
        badge.className = 'tech-badge';
        badge.style.borderColor = tech.color || CONFIG.COLORS.primary;
        badge.style.setProperty('--tech-color', tech.color || CONFIG.COLORS.primary);
        badge.setAttribute('role', 'listitem');

        badge.innerHTML = `
            <span class="tech-name">${tech.name}</span>
            <span class="tech-score">${tech.raw_count}</span>
        `;

        return badge;
    }

    static displayError(errorData) {
        const titleEl = document.getElementById('error-title');
        const messageEl = document.getElementById('error-message');
        const actionsEl = document.getElementById('error-actions');

        if (!titleEl || !messageEl || !actionsEl) return;

        const { statusCode, detail, type } = errorData;

        // Clear actions
        actionsEl.innerHTML = '';

        let title = '';
        let message = '';
        let buttons = [];

        switch (statusCode) {
            case 400: // Bad Request
                title = CONFIG.ERROR_MESSAGES[400].title;
                message = `
                    ${detail}<br><br>
                    <strong>Formats acceptés :</strong> ${CONFIG.FILE_VALIDATION.allowedExtensions.join(', ')}<br>
                    <strong>Taille maximale :</strong> ${CONFIG.FILE_VALIDATION.maxSizeMB} MB
                `;
                buttons = [
                    {
                        text: 'Choisir un autre fichier',
                        className: 'btn-primary',
                        onClick: () => stateManager.setState(STATES.INITIAL),
                    },
                ];
                break;

            case 429: // Quota Exceeded
                title = CONFIG.ERROR_MESSAGES[429].title;
                const resetTime = this.calculateResetTime();
                message = `
                    Notre quota de 100 générations quotidiennes est atteint.<br>
                    Le quota se réinitialise chaque jour à minuit UTC.<br><br>
                    <strong>Prochain reset :</strong> dans ${resetTime}<br><br>
                    💡 Ce projet utilise Vertex AI Imagen, qui a un coût important.<br>
                    Revenez demain ou contactez-nous pour une instance privée.
                `;
                buttons = [
                    {
                        text: 'Me contacter',
                        className: 'btn-secondary',
                        onClick: () => window.open(CONFIG.SOCIAL_LINKS.linkedin, '_blank'),
                    },
                    {
                        text: 'Voir le code',
                        className: 'btn-secondary',
                        onClick: () => window.open(CONFIG.SOCIAL_LINKS.github, '_blank'),
                    },
                ];
                break;

            case 500: // Server Error
                title = CONFIG.ERROR_MESSAGES[500].title;
                message = `
                    Une erreur est survenue lors de la génération.<br>
                    ${detail}<br><br>
                    Nos serveurs ont peut-être du mal à suivre. Veuillez réessayer.
                `;
                buttons = [
                    {
                        text: 'Réessayer',
                        className: 'btn-primary',
                        onClick: () => stateManager.setState(STATES.INITIAL),
                    },
                    {
                        text: 'Signaler le problème',
                        className: 'btn-secondary',
                        onClick: () => window.open(`${CONFIG.SOCIAL_LINKS.github}/issues`, '_blank'),
                    },
                ];
                break;

            default: // Network or Timeout
                if (type === 'timeout') {
                    title = CONFIG.ERROR_MESSAGES.timeout.title;
                    message = CONFIG.ERROR_MESSAGES.timeout.message;
                } else {
                    title = CONFIG.ERROR_MESSAGES.network.title;
                    message = CONFIG.ERROR_MESSAGES.network.message;
                }
                buttons = [
                    {
                        text: 'Réessayer',
                        className: 'btn-primary',
                        onClick: () => stateManager.setState(STATES.INITIAL),
                    },
                ];
        }

        titleEl.textContent = title;
        messageEl.innerHTML = message;

        // Create buttons
        buttons.forEach((btn) => {
            const button = document.createElement('button');
            button.className = `btn ${btn.className}`;
            button.textContent = btn.text;
            button.addEventListener('click', btn.onClick);
            actionsEl.appendChild(button);
        });
    }

    static calculateResetTime() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setUTCHours(24, 0, 0, 0);

        const diff = tomorrow - now;
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);

        return `${hours}h ${minutes}min`;
    }
}

/* ==================== SHARE MANAGER ==================== */
class ShareManager {
    static async shareLinkedIn() {
        const imageUrl = document.getElementById('result-image')?.src;
        const title = document.getElementById('result-title')?.textContent;

        if (!imageUrl || !title) return;

        // Préparer le texte de partage
        const shareText = CONFIG.LINKEDIN_SHARE.getShareText(title);

        // Essayer de copier le texte dans le clipboard
        let copySuccess = false;
        try {
            await navigator.clipboard.writeText(shareText);
            copySuccess = true;
        } catch (err) {
            console.warn('Clipboard copy failed:', err);
        }

        // Ouvrir LinkedIn avec la modal de partage (ancienne méthode qui fonctionne)
        const encodedText = encodeURIComponent(shareText);
        const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}&summary=${encodedText}`;

        window.open(linkedInUrl, '_blank', 'width=600,height=600');

        // Afficher toast SEULEMENT si copie a réussi
        if (copySuccess) {
            ShareManager.showLinkedInToast();
        }
    }

    static showLinkedInToast() {
        const toast = document.createElement('div');
        toast.className = 'linkedin-toast';

        toast.innerHTML = `
            <button class="linkedin-toast-close" aria-label="Fermer">×</button>
            ✅ <strong>Texte copié !</strong><br><br>
            Le texte de partage est dans votre presse-papier.<br><br>
            📝 Dans la fenêtre LinkedIn :<br>
            • Collez le texte (Ctrl+V)<br>
            • Cliquez sur l'icône 📷 pour ajouter votre constellation<br>
            • Publiez ! 🚀
        `;

        document.body.appendChild(toast);

        // Bouton de fermeture
        const closeBtn = toast.querySelector('.linkedin-toast-close');
        closeBtn.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });

        // Animation d'apparition
        setTimeout(() => toast.classList.add('show'), 100);
    }

    static async copyLink() {
        const imageUrl = document.getElementById('result-image')?.src;
        if (!imageUrl) return;

        try {
            await navigator.clipboard.writeText(imageUrl);

            // Feedback visuel
            const btn = document.getElementById('btn-copy');
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Lien copié !
                `;
                btn.classList.add('success');

                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('success');
                }, 2000);
            }
        } catch (err) {
            console.error('Failed to copy:', err);
            alert('Impossible de copier le lien. Veuillez le copier manuellement.');
        }
    }

    static async downloadImage() {
        const imageUrl = document.getElementById('result-image')?.src;
        if (!imageUrl) return;

        try {
            const response = await fetch(imageUrl);
            const blob = await response.blob();

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ma-constellation.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Download failed:', err);
            // Fallback: ouvrir dans un nouvel onglet
            window.open(imageUrl, '_blank');
        }
    }
}

/* ==================== EVENT HANDLERS ==================== */
class EventHandlers {
    static init() {
        // File Upload
        const fileInput = document.getElementById('cv-upload');
        const uploadButton = document.querySelector('.upload-button');

        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileUpload.bind(this));
        }

        if (uploadButton) {
            uploadButton.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    fileInput?.click();
                }
            });
        }

        // Result Buttons
        const btnLinkedIn = document.getElementById('btn-linkedin');
        const btnCopy = document.getElementById('btn-copy');
        const btnDownload = document.getElementById('btn-download');
        const btnRestart = document.getElementById('btn-restart');

        if (btnLinkedIn) {
            btnLinkedIn.addEventListener('click', ShareManager.shareLinkedIn);
        }

        if (btnCopy) {
            btnCopy.addEventListener('click', ShareManager.copyLink);
        }

        if (btnDownload) {
            btnDownload.addEventListener('click', ShareManager.downloadImage);
        }

        if (btnRestart) {
            btnRestart.addEventListener('click', () => {
                stateManager.setState(STATES.INITIAL);
            });
        }

        // Footer Links
        const footerGithub = document.getElementById('footer-github');
        const footerLinkedIn = document.getElementById('footer-linkedin');

        if (footerGithub) {
            footerGithub.href = CONFIG.SOCIAL_LINKS.github;
        }

        if (footerLinkedIn) {
            footerLinkedIn.href = CONFIG.SOCIAL_LINKS.linkedin;
        }

        // Keyboard Navigation
        this.initKeyboardNavigation();
    }

    static async handleFileUpload(event) {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validation
        const validation = FileValidator.validate(file);
        if (!validation.valid) {
            stateManager.setState(STATES.ERROR, {
                statusCode: 400,
                detail: validation.error,
            });
            return;
        }

        // Lancer la génération
        await this.generateConstellation(file);
    }

    static async generateConstellation(file) {
        stateManager.setState(STATES.UPLOADING);

        try {
            const result = await APIClient.generateConstellation(file);
            stateManager.setState(STATES.SUCCESS, result);
        } catch (error) {
            console.error('[EventHandlers] Generation failed:', error);
            stateManager.setState(STATES.ERROR, error);
        }
    }

    static initKeyboardNavigation() {
        // Assurer que tous les boutons sont accessibles au clavier
        document.querySelectorAll('.btn').forEach((btn) => {
            if (!btn.hasAttribute('tabindex')) {
                btn.setAttribute('tabindex', '0');
            }
        });
    }
}

/* ==================== PARALLAX EFFECT ==================== */
class ParallaxEffect {
    static init() {
        // Désactiver sur mobile pour performance
        if (window.innerWidth <= 768) return;

        window.addEventListener('scroll', this.handleScroll.bind(this));
    }

    static handleScroll() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');

        if (hero && scrolled < window.innerHeight) {
            hero.style.transform = `translateY(${scrolled * 0.3}px)`;
        }
    }
}

/* ==================== INITIALIZATION ==================== */

// Global instances
let stateManager;
let progressSimulator;
let particleSystem;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[App] Initializing Constellation Tech...');

    // Initialize managers
    stateManager = new StateManager();
    progressSimulator = new ProgressSimulator();

    // Initialize event handlers
    EventHandlers.init();

    // Initialize parallax
    ParallaxEffect.init();

    // Initialize particle system (separate file)
    if (CONFIG.UI_CONFIG.particlesEnabled) {
        if (typeof ParticleSystem !== 'undefined') {
            particleSystem = new ParticleSystem();
            particleSystem.init();
        }
    }

    // Set initial state
    stateManager.setState(STATES.INITIAL);

    console.log('[App] Initialization complete ✓');
});

// Handle window resize
window.addEventListener('resize', () => {
    if (particleSystem && typeof particleSystem.handleResize === 'function') {
        particleSystem.handleResize();
    }
});
