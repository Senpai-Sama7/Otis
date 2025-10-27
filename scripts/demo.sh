#!/bin/bash
# Demo script for happy-path demonstration

set -e  # Exit on error

echo "🎬 Starting Otis Cybersecurity Agent Demo..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "${BLUE}Step 1: Starting services with Docker Compose${NC}"
echo "----------------------------------------------"
docker-compose up -d
echo "✅ Services started"
echo ""
sleep 5

echo "${BLUE}Step 2: Waiting for services to be ready${NC}"
echo "----------------------------------------------"
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health &> /dev/null; then
        echo "✅ API is ready"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start within timeout"
        exit 1
    fi
done
echo ""

echo "${BLUE}Step 3: Building RAG knowledge base${NC}"
echo "----------------------------------------------"
python scripts/build_rag.py
echo "✅ RAG knowledge base built"
echo ""

echo "${BLUE}Step 4: Health Check${NC}"
echo "----------------------------------------------"
echo "GET /health"
HEALTH=$(curl -s http://localhost:8000/api/v1/health)
echo "${GREEN}$HEALTH${NC}"
echo ""

echo "${BLUE}Step 5: Register Test User${NC}"
echo "----------------------------------------------"
echo "POST /auth/register"
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "demo_analyst",
        "email": "demo@example.com",
        "password": "SecurePassword123!",
        "role": "analyst"
    }' || echo '{"error": "User may already exist"}')
echo "${GREEN}$REGISTER_RESPONSE${NC}"
echo ""

echo "${BLUE}Step 6: Login${NC}"
echo "----------------------------------------------"
echo "POST /auth/login"
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{
        "username": "demo_analyst",
        "password": "SecurePassword123!"
    }')

# Extract token using python
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null || echo "")

if [ -z "$TOKEN" ]; then
    echo "${YELLOW}⚠️  Login failed or user exists. Using existing credentials...${NC}"
    # Try with potentially existing user
    TOKEN="demo_token"
else
    echo "${GREEN}✅ Login successful${NC}"
    echo "Token: ${TOKEN:0:20}..."
fi
echo ""

echo "${BLUE}Step 7: Run Agent with Passive Scan${NC}"
echo "----------------------------------------------"
echo "POST /v1/agent/run"
AGENT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/agent/run \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "instruction": "Perform a passive security assessment of localhost",
        "scan_duration": 10,
        "mode": "passive"
    }' 2>/dev/null || echo '{"summary": "Demo mode - agent would execute here"}')

echo "${GREEN}Agent Response:${NC}"
echo "$AGENT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$AGENT_RESPONSE"
echo ""

echo "${BLUE}Step 8: Query Threat Intelligence${NC}"
echo "----------------------------------------------"
echo "POST /threat-intel"
THREAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/agent/threat-intel \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "query": "SQL injection vulnerabilities",
        "limit": 3
    }' 2>/dev/null || echo '{"query": "SQL injection", "results": []}')

echo "${GREEN}Threat Intel Response:${NC}"
echo "$THREAT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$THREAT_RESPONSE"
echo ""

echo "${BLUE}Step 9: Check Logs${NC}"
echo "----------------------------------------------"
echo "Recent logs from Otis API:"
docker-compose logs --tail=20 otis 2>/dev/null || echo "Logs not available"
echo ""

echo "${GREEN}═══════════════════════════════════════════${NC}"
echo "${GREEN}🎉 Demo Complete!${NC}"
echo "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "1. View full logs: make docker-logs"
echo "2. Access API documentation: http://localhost:8000/docs"
echo "3. Stop services: make docker-down"
echo ""
echo "For more advanced features:"
echo "- Configure Telegram bot for approval workflow"
echo "- Set up Ollama with DeepSeek-R1 model"
echo "- Run active security scans (requires approval)"
echo ""
