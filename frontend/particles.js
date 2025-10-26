/**
 * ============================================
 * PARTICLE SYSTEM - SPATIAL BACKGROUND
 * ============================================
 *
 * Effet: Étoiles en mouvement (warp speed)
 * Performance: Optimisé avec requestAnimationFrame
 * Responsive: S'adapte au resize
 */

'use strict';

class Star {
    constructor(canvas) {
        this.canvas = canvas;
        this.reset();
    }

    reset() {
        this.x = Math.random() * this.canvas.width;
        this.y = Math.random() * this.canvas.height;
        this.z = Math.random() * 1000;
        this.speed = Math.random() * 2 + 1;
        this.prevX = this.x;
        this.prevY = this.y;
    }

    update() {
        this.prevX = this.getScreenX();
        this.prevY = this.getScreenY();

        this.z -= this.speed;

        if (this.z <= 0) {
            this.reset();
            this.z = 1000;
        }
    }

    getScreenX() {
        const centerX = this.canvas.width / 2;
        return (this.x - centerX) * (1000 / this.z) + centerX;
    }

    getScreenY() {
        const centerY = this.canvas.height / 2;
        return (this.y - centerY) * (1000 / this.z) + centerY;
    }

    getRadius() {
        return Math.max(0, (1 - this.z / 1000) * 2);
    }

    getOpacity() {
        return Math.max(0, 1 - this.z / 1000);
    }

    draw(ctx) {
        const x = this.getScreenX();
        const y = this.getScreenY();
        const radius = this.getRadius();
        const opacity = this.getOpacity();

        // Skip if off-screen
        if (
            x < -10 ||
            x > this.canvas.width + 10 ||
            y < -10 ||
            y > this.canvas.height + 10
        ) {
            return;
        }

        // Draw star
        ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();

        // Draw trail (warp effect)
        if (this.speed > 1.5) {
            ctx.strokeStyle = `rgba(100, 150, 255, ${opacity * 0.3})`;
            ctx.lineWidth = radius / 2;
            ctx.beginPath();
            ctx.moveTo(this.prevX, this.prevY);
            ctx.lineTo(x, y);
            ctx.stroke();
        }
    }
}

class ParticleSystem {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.stars = [];
        this.animationId = null;
        this.isRunning = false;
    }

    init() {
        this.canvas = document.getElementById('particles-canvas');
        if (!this.canvas) {
            console.warn('[ParticleSystem] Canvas not found');
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        if (!this.ctx) {
            console.warn('[ParticleSystem] Canvas context not available');
            return;
        }

        // Set canvas size
        this.handleResize();

        // Create stars
        const starCount = CONFIG.UI_CONFIG.particlesCount || 200;
        this.stars = Array.from({ length: starCount }, () => new Star(this.canvas));

        // Start animation
        this.start();

        console.log('[ParticleSystem] Initialized with', starCount, 'stars');
    }

    handleResize() {
        if (!this.canvas) return;

        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;

        // Reset stars positions to avoid clustering
        this.stars.forEach((star) => star.reset());
    }

    start() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.animate();
    }

    stop() {
        if (!this.isRunning) return;

        this.isRunning = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    animate() {
        if (!this.isRunning) return;

        // Clear canvas with slight fade for trail effect
        this.ctx.fillStyle = 'rgba(10, 10, 20, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw stars
        this.stars.forEach((star) => {
            star.update();
            star.draw(this.ctx);
        });

        // Continue animation
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    clear() {
        if (this.ctx && this.canvas) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    destroy() {
        this.stop();
        this.clear();
        this.stars = [];
    }
}

// Auto-disable on mobile for performance
if (typeof window !== 'undefined' && window.innerWidth <= 768) {
    if (typeof CONFIG !== 'undefined') {
        CONFIG.UI_CONFIG.particlesEnabled = false;
    }
}
