#!/bin/bash
# Bootstrap script for Otis cybersecurity agent setup

set -e  # Exit on error

echo "🚀 Bootstrapping Otis Cybersecurity Agent..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

echo "Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.11+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q
pip install -r requirements-dev.txt -q
echo "✅ Dependencies installed"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/chroma
mkdir -p data/logs
mkdir -p data/pending
touch data/.gitkeep
echo "✅ Directories created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please update with your configuration"
else
    echo "✅ .env file already exists"
fi

# Check for Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    if docker ps &> /dev/null; then
        echo "✅ Docker is running"
    else
        echo "⚠️  Docker is installed but not running. Please start Docker."
    fi
else
    echo "⚠️  Docker is not installed. Some features may not work."
fi

# Check for Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
else
    echo "⚠️  Ollama is not installed. Please install from https://ollama.ai"
fi

echo ""
echo "🎉 Bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration (API keys, tokens, etc.)"
echo "2. Run 'make init-rag' to build the RAG knowledge base"
echo "3. Run 'make migrate' to initialize the database"
echo "4. Run 'make run' to start the application locally"
echo "   OR"
echo "5. Run 'make docker-up' to start all services with Docker Compose"
echo ""
echo "For more information, see README.md"
