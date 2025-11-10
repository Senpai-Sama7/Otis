#!/bin/bash
set -e

echo "🚀 Building Otis Desktop Application..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the application
echo "🔨 Building .deb package..."
npm run build

echo "✅ Build complete!"
echo ""
echo "📦 Package location: dist/otis-desktop_1.0.0_amd64.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i dist/otis-desktop_1.0.0_amd64.deb"
echo ""
echo "To run:"
echo "  otis-desktop"
