# Otis Desktop - Design Specification

## 🎨 Visual Identity

### Design Philosophy
**"Luxurious Minimalism with Depth"**

Inspired by:
- **Apple**: Clean, minimal, attention to detail
- **Nvidia**: Bold green accent, tech-forward
- **Clayskeuomorphism**: Subtle 3D depth, tactile feel

### Core Principles
1. **Depth over Flat**: Multi-layer shadows create hierarchy
2. **Blur over Solid**: Glassmorphism for modern feel
3. **Gradient over Single**: Smooth color transitions
4. **Animation over Static**: Fluid, purposeful motion

## 🎨 Color System

### Primary Palette
```css
--bg-primary: #0a0a0f      /* Deep space black */
--bg-secondary: #13131a    /* Midnight blue-black */
--bg-tertiary: #1a1a24     /* Charcoal blue */
```

### Accent Colors
```css
--accent: #76b900          /* Nvidia green */
--accent-glow: rgba(118, 185, 0, 0.3)
--purple: #8b5cf6          /* Tech purple */
--purple-glow: rgba(139, 92, 246, 0.3)
```

### Surface Colors
```css
--surface: rgba(255, 255, 255, 0.05)        /* Subtle overlay */
--surface-hover: rgba(255, 255, 255, 0.08)  /* Interactive state */
--border: rgba(255, 255, 255, 0.1)          /* Dividers */
```

### Text Hierarchy
```css
--text-primary: #ffffff                      /* Headings, important */
--text-secondary: rgba(255, 255, 255, 0.7)  /* Body text */
--text-tertiary: rgba(255, 255, 255, 0.5)   /* Captions, hints */
```

## 📐 Layout System

### Grid Structure
```
┌─────────────────────────────────────────┐
│           Title Bar (40px)              │
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │      Main Content            │
│ (240px)  │      (Flexible)              │
│          │                              │
│          │                              │
└──────────┴──────────────────────────────┘
```

### Spacing Scale
- **xs**: 4px
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 24px
- **2xl**: 32px

### Border Radius
- **Small**: 6px (buttons, inputs)
- **Medium**: 12px (cards, nav items)
- **Large**: 16px (panels, modals)
- **XLarge**: 20px (main containers)

## 🎭 Component Anatomy

### Navigation Item (Clayskeuomorphic)
```
┌─────────────────────────────────┐
│ ╭─────────────────────────────╮ │ ← Subtle top highlight
│ │  [Icon]  Label              │ │
│ ╰─────────────────────────────╯ │ ← Bottom shadow
└─────────────────────────────────┘

Layers:
1. Base: rgba(255, 255, 255, 0.02)
2. Border: 1px solid transparent
3. Inner shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05)
4. Outer shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
5. Gradient border (on hover)
```

### Action Card (3D Effect)
```
┌─────────────────────────────────┐
│ ╭─────────────────────────────╮ │ ← Top shine
│ │                             │ │
│ │  [Icon]  Title              │ │
│ │          Description        │ │
│ │                             │ │
│ ╰─────────────────────────────╯ │ ← Bottom depth
└─────────────────────────────────┘

Hover State:
- Lift: translateY(-4px)
- Glow: 0 0 24px accent-glow
- Border: accent color
```

### Input Field (Inset)
```
┌─────────────────────────────────┐
│ ╔═════════════════════════════╗ │ ← Inset shadow
│ ║  Placeholder text...        ║ │
│ ╚═════════════════════════════╝ │
└─────────────────────────────────┘

Effects:
- Background: rgba(0, 0, 0, 0.3)
- Inset shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2)
- Focus: border-color accent + glow
```

## ✨ Effects Library

### Glassmorphism
```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(40px) saturate(180%);
-webkit-backdrop-filter: blur(40px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.1);
```

### Clayskeuomorphic Shadow
```css
box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.2),           /* Outer depth */
    inset 0 1px 0 rgba(255, 255, 255, 0.1),  /* Top highlight */
    inset 0 -1px 0 rgba(0, 0, 0, 0.2);       /* Bottom shadow */
```

### Gradient Border
```css
.element::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.1), 
        transparent
    );
    -webkit-mask: 
        linear-gradient(#fff 0 0) content-box, 
        linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}
```

### Glow Effect
```css
box-shadow: 
    0 4px 16px var(--accent-glow),
    0 0 24px var(--accent-glow);
```

## 🎬 Animation System

### Timing Functions
```css
--ease-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.6, 1);
```

### Durations
- **Fast**: 150ms (hover states)
- **Normal**: 300ms (transitions)
- **Slow**: 500ms (page changes)

### Key Animations

**Fade In**
```css
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(8px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}
```

**Pulse (Status Indicator)**
```css
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

**Slide In**
```css
@keyframes slideIn {
    from { 
        transform: translateX(-100%); 
        opacity: 0; 
    }
    to { 
        transform: translateX(0); 
        opacity: 1; 
    }
}
```

## 🖼️ Iconography

### Style
- **Line weight**: 1.5px
- **Corner radius**: Rounded
- **Fill**: None (stroke only)
- **Color**: Inherits from parent

### Sizes
- **Small**: 16x16px (inline icons)
- **Medium**: 20x20px (navigation)
- **Large**: 24x24px (headers)
- **XLarge**: 32x32px (quick actions)

## 📱 Responsive Behavior

### Breakpoints
- **Minimum**: 1200x700px
- **Comfortable**: 1400x900px
- **Large**: 1920x1080px

### Scaling
- Sidebar: Fixed 240px
- Content: Flexible with max-width constraints
- Cards: Grid adapts to available space

## 🎯 Interactive States

### Button States
```css
/* Default */
background: gradient;
box-shadow: 0 4px 16px glow;

/* Hover */
transform: translateY(-2px);
box-shadow: 0 6px 24px glow;

/* Active */
transform: translateY(0);
box-shadow: 0 2px 8px glow;

/* Disabled */
opacity: 0.5;
cursor: not-allowed;
```

### Card States
```css
/* Default */
background: subtle gradient;
border: 1px solid border;

/* Hover */
transform: translateY(-4px);
border-color: accent;
box-shadow: enhanced + glow;

/* Active */
background: accent gradient;
border-color: accent;
```

## 🔤 Typography Scale

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 
             'SF Pro Display', 'Segoe UI', sans-serif;
```

### Scale
- **Display**: 32px / 700 / -0.5px (Page titles)
- **Heading**: 24px / 600 / -0.3px (Section headers)
- **Subheading**: 18px / 600 / 0px (Card titles)
- **Body**: 14px / 400 / 0px (Main text)
- **Caption**: 12px / 400 / 0px (Hints, labels)

### Line Heights
- **Tight**: 1.2 (headings)
- **Normal**: 1.5 (body)
- **Relaxed**: 1.7 (long-form)

## 🎨 Theme Variations

### Dark (Default)
- Background: Deep blacks and blues
- Text: White with opacity
- Accents: Nvidia green + purple

### Light (Future)
- Background: Off-white gradients
- Text: Dark grays
- Accents: Same (adjusted saturation)

## 📐 Accessibility

### Contrast Ratios
- **Text Primary**: 21:1 (AAA)
- **Text Secondary**: 7:1 (AA)
- **Text Tertiary**: 4.5:1 (AA)

### Focus States
- Visible outline: 2px solid accent
- Glow: 0 0 0 3px accent-glow

### Motion
- Respects `prefers-reduced-motion`
- Animations can be disabled

## 🎯 Design Tokens

```css
:root {
    /* Spacing */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 12px;
    --space-lg: 16px;
    --space-xl: 24px;
    --space-2xl: 32px;
    
    /* Radius */
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    
    /* Shadows */
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

## 🎨 Implementation Notes

1. **Use CSS Variables**: All colors and spacing use CSS custom properties
2. **Layer Shadows**: Multiple box-shadows create depth
3. **Backdrop Filters**: Enable for glassmorphism (requires GPU)
4. **Transform Animations**: Use transform for smooth 60fps animations
5. **Will-Change**: Apply to animated elements for performance
6. **Contain**: Use CSS containment for layout optimization

## 🚀 Performance Targets

- **First Paint**: < 100ms
- **Interactive**: < 500ms
- **Smooth Animations**: 60fps
- **Memory**: < 200MB
- **CPU (Idle)**: < 1%
