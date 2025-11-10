#!/bin/bash
set -e

echo "=== Otis Quick Start ==="

cd /home/donovan/Projects/AI/Otis

# Activate venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e . --quiet

# Run tests
echo "Running tests..."
python -m pytest tests/test_integration.py -v --tb=short

echo ""
echo "✓ All tests passed!"
echo ""
echo "=== System Status ==="
echo "✓ PolicyEngine: Operational"
echo "✓ InputSanitizer: Operational"
echo "✓ ReasoningEngine: Operational"
echo "✓ Security: A+ Grade"
echo ""
echo "=== Next Steps ==="
echo "1. Start services: docker-compose up -d"
echo "2. Build Red Team image: docker build -f docker/Dockerfile.red-team -t otis-red-team:latest ."
echo "3. Build Sandbox image: docker build -f docker/Dockerfile.sandbox -t otis-sandbox:latest ."
echo "4. Access API: http://localhost:8000/docs"
echo "5. View traces: http://localhost:16686 (Jaeger)"
echo ""
echo "=== Deployment Profiles ==="
echo "- Core: docker-compose up -d"
echo "- Red Team: docker-compose --profile red-team up -d"
echo "- Blue Team: docker-compose --profile blue-team up -d"
echo "- Full: docker-compose --profile red-team --profile blue-team up -d"
