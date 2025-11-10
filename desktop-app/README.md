# Otis Desktop Application

Modern, luxurious desktop application for Otis AI Security Assistant with Apple/Nvidia aesthetic and clayskeuomorphic design.

## Features

- 🎨 **Luxurious Design**: Apple-inspired interface with Nvidia green accents
- 🪟 **Native Desktop**: True desktop application, not a web wrapper
- 🔒 **Secure**: Isolated processes with context isolation
- 📦 **Easy Install**: One-click `.deb` installation
- ⚡ **Fast**: Native performance with Electron

## Installation

### From .deb Package (Recommended)

```bash
# After building, install the .deb file
sudo dpkg -i dist/otis-desktop_1.0.0_amd64.deb

# Launch from applications menu or terminal
otis-desktop
```

### From Source

```bash
cd desktop-app

# Install dependencies
npm install

# Run in development mode
npm start

# Build .deb package
npm run build
```

## Building

```bash
# Build for Linux (.deb)
npm run build

# Build for all platforms
npm run build:all
```

The `.deb` package will be created in `dist/` directory.

## Requirements

- Node.js 18+ (for building)
- Otis API running on `http://localhost:8000`

## Usage

1. Launch the application
2. Enter your Otis credentials when prompted
3. Start chatting with the AI security assistant
4. Use quick actions for common tasks
5. Navigate between Chat, Scans, Threats, and Settings

## Architecture

- **Electron**: Cross-platform desktop framework
- **Main Process**: Window management and system integration
- **Renderer Process**: UI and user interactions
- **IPC**: Secure communication between processes
- **Context Isolation**: Enhanced security

## Design System

- **Colors**: Dark theme with Nvidia green (#76b900) and purple accents
- **Typography**: SF Pro Display / System fonts
- **Effects**: Glassmorphism, clayskeuomorphism, subtle shadows
- **Animations**: Smooth cubic-bezier transitions
- **Layout**: Responsive grid with sidebar navigation

## Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# The app will hot-reload on changes
```

## Troubleshooting

**App won't start:**
- Ensure Otis API is running on port 8000
- Check Node.js version (18+)

**Build fails:**
- Run `npm install` again
- Clear node_modules and reinstall

**Can't connect to API:**
- Verify API is accessible at http://localhost:8000
- Check firewall settings
