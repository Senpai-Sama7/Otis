# Otis Desktop - Quick Start Card

## 🚀 5-Minute Setup

```bash
# 1. Navigate to desktop app
cd /home/donovan/Otis/desktop-app

# 2. Install dependencies (first time only)
npm install

# 3. Run in development mode
npm start

# OR build .deb package
npm run build
sudo dpkg -i dist/otis-desktop_1.0.0_amd64.deb
otis-desktop
```

## 📁 Project Structure

```
desktop-app/
├── package.json          # Dependencies & build config
├── build.sh             # Automated build script
├── src/
│   ├── main/
│   │   ├── main.js      # Electron main process
│   │   └── preload.js   # Secure IPC bridge
│   └── renderer/
│       ├── index.html   # UI structure
│       ├── styles.css   # Luxurious styling
│       └── app.js       # Application logic
└── docs/
    ├── README.md        # Installation guide
    ├── DESIGN.md        # Design specification
    ├── SUMMARY.md       # Complete overview
    └── VISUAL_MOCKUP.md # Visual reference
```

## 🎨 Design at a Glance

**Colors:**
- Background: `#0a0a0f` → `#1a1a24` (gradient)
- Accent: `#76b900` (Nvidia green)
- Purple: `#8b5cf6`
- Surface: `rgba(255,255,255,0.05)`

**Effects:**
- Glassmorphism: `backdrop-filter: blur(40px)`
- Shadows: Multi-layer depth
- Animations: 300ms cubic-bezier

**Typography:**
- Font: SF Pro Display / System
- Sizes: 12px → 32px
- Weights: 400, 500, 600, 700

## 🔧 Common Commands

```bash
# Development
npm start                 # Run dev mode
npm run build            # Build .deb
npm run build:all        # Build all platforms

# Installation
sudo dpkg -i dist/*.deb  # Install package
otis-desktop             # Launch app

# Cleanup
rm -rf node_modules dist # Clean build
npm install              # Reinstall
```

## 🎯 Key Features

✅ Native desktop app (not web)
✅ Luxurious Apple/Nvidia design
✅ Clayskeuomorphic effects
✅ One-click .deb install
✅ Custom frameless window
✅ Secure IPC communication
✅ Chat with AI assistant
✅ Quick action buttons
✅ Scans & threats views
✅ Settings panel

## 📦 Requirements

- **Node.js**: 18+ (for building)
- **Otis API**: Running on port 8000
- **RAM**: 512MB minimum
- **Disk**: 200MB for app

## 🐛 Troubleshooting

**App won't start:**
```bash
curl http://localhost:8000/api/v1/health
```

**Build fails:**
```bash
rm -rf node_modules
npm install
```

**Can't connect:**
```bash
docker ps  # Check containers
```

## 📚 Documentation

- `README.md` - Installation & usage
- `DESIGN.md` - Design system
- `SUMMARY.md` - Complete overview
- `VISUAL_MOCKUP.md` - Visual reference

## 🎨 Customization

Edit these files to customize:
- `styles.css` - Colors, spacing, effects
- `index.html` - UI structure
- `app.js` - Application logic

## 🚀 Next Steps

1. ✅ Install Node.js 18+
2. ✅ Run `npm install`
3. ✅ Test with `npm start`
4. ✅ Build with `npm run build`
5. ✅ Install .deb package
6. ✅ Launch and enjoy!

---

**Need help?** Check the full documentation in the `desktop-app/` directory.
