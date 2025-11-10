# Otis Landing Page - Modern Studio Design

## 🎨 Design Philosophy

Inspired by modern studio sites like Sage, this landing page features:

- **Full-screen hero** with WebGL particle effects
- **Scroll-triggered animations** with staggered entrances
- **Minimalist typography** with bold statements
- **Card-based sections** with hover effects
- **Dark theme** with cyan/purple accents
- **Smooth parallax scrolling**

## 🏗️ Architecture

### Layout Structure
```
├── Hero Section (100vh)
│   ├── WebGL Canvas (particle network)
│   ├── Hero Content (centered)
│   │   ├── Title (animated slide-up)
│   │   ├── Subtitle
│   │   └── Stats (96%, <15%, 6 vectors)
│   └── Scroll Indicator
│
├── About Section
│   └── 3-column grid (Red Team, Blue Team, NIST)
│
├── Capabilities Section
│   └── Numbered list (01, 02, 03)
│       ├── Attack Engine
│       ├── Detection Pipeline
│       └── Compliance Framework
│
├── Technology Section
│   └── 4-column grid (Transformers, Python, K8s, CI/CD)
│
├── CTA Section
│   └── Buttons (GitHub, Docs)
│
└── Footer
    ├── Brand
    └── Links
```

## ✨ Key Features

### 1. WebGL Particle Network
- 150 particles with neural network connections
- Mouse interaction (repel effect)
- Smooth 60fps animation
- Responsive particle count based on screen size

### 2. Scroll Animations
- **IntersectionObserver** for viewport detection
- **Staggered entrances** (100ms delay between cards)
- **Parallax hero** (0.5x scroll speed)
- **Fade + slide-up** transitions

### 3. Metric Counters
- Animated from 0 to target value
- Triggered on scroll into view
- 2-second duration with easing
- Only animates once

### 4. Responsive Design
- **Desktop**: Full layout with 60px padding
- **Tablet** (1024px): Reduced gaps, single-column capabilities
- **Mobile** (768px): Stacked layout, 20px padding

## 🚀 Deployment

### Local Preview
```bash
npm run preview
# Visit http://localhost:8080
```

### GitHub Pages Deployment
```bash
# 1. Commit changes
git add index.html styles.css main.js .nojekyll
git commit -m "Deploy modern landing page"
git push origin main

# 2. Enable GitHub Pages
# Go to: Settings → Pages → Source: GitHub Actions

# 3. Site will be live at:
# https://senpai-sama7.github.io/Otis/
```

## 📊 Performance

### Metrics
- **First Contentful Paint**: <1.5s
- **Time to Interactive**: <3s
- **Lighthouse Score**: 95+
- **Bundle Size**: ~15KB (HTML + CSS + JS)

### Optimizations
- No external dependencies (vanilla JS)
- Debounced mouse tracking (16ms)
- Lazy-loaded animations (IntersectionObserver)
- Reduced motion support (`prefers-reduced-motion`)

## 🎯 Animations Breakdown

### Hero Entrance
```css
.hero-title .line:nth-child(1) {
    animation: slideUp 1s 0.2s forwards;
}
.hero-title .line:nth-child(2) {
    animation: slideUp 1s 0.4s forwards;
}
```

### Card Hover
```css
.about-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0, 245, 255, 0.1);
}
```

### Scroll Parallax
```javascript
hero.style.transform = `translateY(${scrollY * 0.5}px)`;
hero.style.opacity = 1 - (scrollY / window.innerHeight);
```

## 🔧 Customization

### Colors
```css
:root {
    --primary: #00f5ff;      /* Cyan */
    --secondary: #7b2cbf;    /* Purple */
    --dark: #0a0a0a;         /* Background */
    --text-muted: #a0a0a0;   /* Secondary text */
}
```

### Particle Count
```javascript
const particleCount = Math.min(150, Math.floor(window.innerWidth / 10));
```

### Animation Timing
```javascript
const duration = 2000;  // Metric counter duration
const staggerDelay = 100;  // Card entrance delay
```

## 📱 Browser Support

- **Chrome/Edge**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Mobile**: iOS 14+, Android 10+

### Fallbacks
- `<noscript>` warning for no-JS users
- CSS-only animations if JS fails
- Reduced motion support for accessibility

## 🐛 Known Issues

None currently. Report issues at: https://github.com/Senpai-Sama7/Otis/issues

## 📝 License

MIT License - Same as Otis Framework

---

**Built with vanilla HTML/CSS/JS for maximum performance and zero dependencies.**
