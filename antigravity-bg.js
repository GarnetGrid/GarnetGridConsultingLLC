/**
 * Antigravity Inspired Background Particle System
 * For Garnet Grid Consulting Home Page
 */

class AntigravityBackground {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.colors = ['#901539', '#ff2d55', '#4285f4', '#34a853', '#fbbc05', '#ea4335'];

        this.init();
        this.animate();

        window.addEventListener('resize', () => this.init());
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.x;
            this.mouse.y = e.y;
        });
    }

    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.particles = [];

        let numberOfParticles = (this.canvas.width * this.canvas.height) / 15000;
        for (let i = 0; i < numberOfParticles; i++) {
            this.particles.push(new Particle(this.canvas, this.colors));
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let i = 0; i < this.particles.length; i++) {
            this.particles[i].update(this.mouse);
            this.particles[i].draw(this.ctx);
        }

        requestAnimationFrame(() => this.animate());
    }
}

class Particle {
    constructor(canvas, colors) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.baseX = this.x;
        this.baseY = this.y;
        this.density = (Math.random() * 30) + 1;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.opacity = Math.random() * 0.5 + 0.1;
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fill();
    }

    update(mouse) {
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        let forceDirectionX = dx / distance;
        let forceDirectionY = dy / distance;
        let maxDistance = mouse.radius;
        let force = (maxDistance - distance) / maxDistance;
        let directionX = forceDirectionX * force * this.density;
        let directionY = forceDirectionY * force * this.density;

        if (distance < mouse.radius) {
            this.x -= directionX;
            this.y -= directionY;
        } else {
            if (this.x !== this.baseX) {
                let dx = this.x - this.baseX;
                this.x -= dx / 10;
            }
            if (this.y !== this.baseY) {
                let dy = this.y - this.baseY;
                this.y -= dy / 10;
            }
        }

        // Add a subtle drift
        this.baseX += Math.sin(Date.now() * 0.001 + this.density) * 0.2;
        this.baseY += Math.cos(Date.now() * 0.001 + this.density) * 0.2;
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Create canvas if it doesn't exist
    if (!document.getElementById('antigravity-canvas')) {
        const canvas = document.createElement('canvas');
        canvas.id = 'antigravity-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-3';
        canvas.style.pointerEvents = 'none';
        document.body.appendChild(canvas);
    }

    new AntigravityBackground('antigravity-canvas');
});
