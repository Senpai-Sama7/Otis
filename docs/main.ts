// main.ts - Immersive Interactions for Otis Landing Page

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
}

class OtisAnimations {
  private canvas: HTMLCanvasElement | null = null;
  private ctx: CanvasRenderingContext2D | null = null;
  private particles: Particle[] = [];
  private animationId: number | null = null;

  constructor() {
    this.initCanvas();
    this.initParticles(100); // 100 particles for neural net simulation
    this.initScrollAnimations();
    this.initMetrics();
    this.initNav();
  }

  private initCanvas(): void {
    this.canvas = document.getElementById('particles-canvas') as HTMLCanvasElement;
    if (this.canvas) {
      this.ctx = this.canvas.getContext('2d');
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
      window.addEventListener('resize', () => this.resizeCanvas());
    }
  }

  private resizeCanvas(): void {
    if (this.canvas) {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }
  }

  private initParticles(count: number): void {
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        size: Math.random() * 3 + 1,
        color: Math.random() > 0.5 ? '#00f5ff' : '#7b2cbf'
      });
    }
    this.animateParticles();
  }

  private animateParticles(): void {
    if (!this.ctx) return;
    this.ctx.clearRect(0, 0, this.canvas!.width, this.canvas!.height);

    this.particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      // Bounce off edges (neural net "containment")
      if (p.x < 0 || p.x > window.innerWidth) p.vx *= -1;
      if (p.y < 0 || p.y > window.innerHeight) p.vy *= -1;

      // Draw particle with glow
      this.ctx!.beginPath();
      this.ctx!.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      this.ctx!.fillStyle = p.color;
      this.ctx!.shadowBlur = 10;
      this.ctx!.shadowColor = p.color;
      this.ctx!.fill();
    });

    // Connect nearby particles (neural links)
    for (let i = 0; i < this.particles.length; i++) {
      for (let j = i + 1; j < this.particles.length; j++) {
        const dx = this.particles[i].x - this.particles[j].x;
        const dy = this.particles[i].y - this.particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 100) {
          this.ctx!.beginPath();
          this.ctx!.moveTo(this.particles[i].x, this.particles[i].y);
          this.ctx!.lineTo(this.particles[j].x, this.particles[j].y);
          this.ctx!.strokeStyle = `rgba(0, 245, 255, ${1 - dist / 100})`;
          this.ctx!.lineWidth = 1;
          this.ctx!.stroke();
        }
      }
    }

    this.animationId = requestAnimationFrame(() => this.animateParticles());
  }

  private initScrollAnimations(): void {
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -50px 0px' };
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          (entry.target as HTMLElement).style.animation = 'slideUp 0.8s ease-out forwards';
        }
      });
    }, observerOptions);

    document.querySelectorAll('.section, .card, .step, .audience-card').forEach(el => {
      observer.observe(el as HTMLElement);
    });

    // Parallax effect
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const parallax = document.querySelector('.parallax') as HTMLElement;
      if (parallax) {
        parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
      }
    });
  }

  private initMetrics(): void {
    const numbers = document.querySelectorAll('.metric-number') as NodeListOf<HTMLElement>;
    const animateNumber = (el: HTMLElement, target: number) => {
      let start = 0;
      const increment = target / 100;
      const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
          start = target;
          clearInterval(timer);
        }
        el.textContent = Math.floor(start).toString();
      }, 20);
    };

    // Trigger on scroll into view
    const metricsObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target as HTMLElement;
          const target = parseInt(el.getAttribute('data-target') || '0');
          animateNumber(el, target);
          metricsObserver.unobserve(el);
        }
      });
    });

    numbers.forEach(num => metricsObserver.observe(num));
  }

  private initNav(): void {
    const hamburger = document.querySelector('.hamburger') as HTMLElement;
    const navLinks = document.querySelector('.nav-links') as HTMLElement;

    hamburger?.addEventListener('click', () => {
      navLinks?.classList.toggle('active');
    });

    // Smooth scroll for links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href')!) as HTMLElement;
        target?.scrollIntoView({ behavior: 'smooth' });
      });
    });

    // Header background on scroll
    window.addEventListener('scroll', () => {
      const header = document.getElementById('header');
      if (header) {
        if (window.scrollY > 100) {
          header.style.background = 'rgba(0,0,0,0.95)';
        } else {
          header.style.background = 'rgba(0,0,0,0.9)';
        }
      }
    });
  }

  destroy(): void {
    if (this.animationId) cancelAnimationFrame(this.animationId);
  }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  const animations = new OtisAnimations();

  // Cleanup on unload
  window.addEventListener('beforeunload', () => animations.destroy());
});