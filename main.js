// Otis Landing Page - Modern Interactive Experience
class OtisExperience {
    constructor() {
        this.canvas = document.getElementById('webgl-canvas');
        this.ctx = this.canvas?.getContext('2d');
        this.particles = [];
        this.mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
        this.scrollY = 0;
        
        if (this.canvas) {
            this.init();
        }
    }

    init() {
        this.resizeCanvas();
        this.createParticles();
        this.animate();
        this.initScrollAnimations();
        this.initMouseTracking();
        this.initMetricCounters();
        this.initNavScroll();
        
        window.addEventListener('resize', () => this.resizeCanvas());
        window.addEventListener('scroll', () => this.handleScroll());
    }

    resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const particleCount = Math.min(150, Math.floor(window.innerWidth / 10));
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2,
                color: Math.random() > 0.5 ? '0, 245, 255' : '123, 44, 191'
            });
        }
    }

    animate() {
        if (!this.ctx) return;

        // Clear with fade effect
        this.ctx.fillStyle = 'rgba(10, 10, 10, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw particles
        this.particles.forEach(p => {
            // Move particle
            p.x += p.vx;
            p.y += p.vy;

            // Bounce off edges
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            // Mouse interaction (repel)
            const dx = this.mouse.x - p.x;
            const dy = this.mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            
            if (dist < 150) {
                const force = (150 - dist) / 150;
                p.x -= dx * force * 0.02;
                p.y -= dy * force * 0.02;
            }

            // Draw particle with glow
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(${p.color}, ${p.opacity})`;
            this.ctx.shadowBlur = 15;
            this.ctx.shadowColor = `rgba(${p.color}, ${p.opacity})`;
            this.ctx.fill();
            this.ctx.shadowBlur = 0;
        });

        // Draw connections (neural network effect)
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 120) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    const opacity = 0.15 * (1 - dist / 120);
                    this.ctx.strokeStyle = `rgba(0, 245, 255, ${opacity})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.stroke();
                }
            }
        }

        requestAnimationFrame(() => this.animate());
    }

    initMouseTracking() {
        let timeout;
        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
            
            // Debounce for performance
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                this.mouse.x = e.clientX;
                this.mouse.y = e.clientY;
            }, 16);
        });
    }

    initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                }
            });
        }, observerOptions);

        // Observe cards with stagger
        const cards = document.querySelectorAll('.about-card, .tech-card');
        cards.forEach((card, index) => {
            observer.observe(card);
        });

        // Observe capability items
        const capabilities = document.querySelectorAll('.capability-item');
        capabilities.forEach((item, index) => {
            observer.observe(item);
        });

        // Smooth scroll for nav links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    const offset = 80;
                    const targetPosition = target.offsetTop - offset;
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    initMetricCounters() {
        const counters = document.querySelectorAll('.stat-number');
        let hasAnimated = false;

        const animateCounter = (el) => {
            const target = parseInt(el.getAttribute('data-target'));
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    el.textContent = Math.floor(current);
                    requestAnimationFrame(updateCounter);
                } else {
                    el.textContent = target;
                }
            };

            updateCounter();
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !hasAnimated) {
                    hasAnimated = true;
                    counters.forEach((counter, index) => {
                        setTimeout(() => animateCounter(counter), index * 200);
                    });
                }
            });
        });

        const heroStats = document.querySelector('.hero-stats');
        if (heroStats) observer.observe(heroStats);
    }

    initNavScroll() {
        const nav = document.querySelector('.nav');
        let lastScroll = 0;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 100) {
                nav.style.background = 'rgba(10, 10, 10, 0.95)';
                nav.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.5)';
            } else {
                nav.style.background = 'rgba(10, 10, 10, 0.8)';
                nav.style.boxShadow = 'none';
            }

            lastScroll = currentScroll;
        });
    }

    handleScroll() {
        this.scrollY = window.pageYOffset;
        
        // Parallax effect for hero
        const hero = document.querySelector('.hero-content');
        if (hero && this.scrollY < window.innerHeight) {
            hero.style.transform = `translateY(${this.scrollY * 0.5}px)`;
            hero.style.opacity = 1 - (this.scrollY / window.innerHeight);
        }
    }
}

// Initialize on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new OtisExperience();
    });
} else {
    new OtisExperience();
}

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});
