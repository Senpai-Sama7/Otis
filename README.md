# Otis - Autonomous Cybersecurity AI Coding Agent

<div align="center">

🤖 **Production-Ready AI Agent for Cybersecurity Operations**

[![CI/CD](https://github.com/Senpai-Sama7/Otis/actions/workflows/ci.yml/badge.svg)](https://github.com/Senpai-Sama7/Otis/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

## 🎯 Overview

Otis is an autonomous cybersecurity AI coding agent built with production-grade architecture. It combines the power of DeepSeek-R1 LLM via Ollama with RAG-based threat intelligence (MITRE ATT&CK, NIST, OWASP) to provide intelligent security analysis, vulnerability detection, and automated remediation with human-in-the-loop approval.

## ✨ Features

- **🧠 AI-Powered Analysis**: DeepSeek-R1 7B model via Ollama for intelligent reasoning
- **📚 RAG Knowledge Base**: Vector search with Chroma (MITRE ATT&CK, NIST CSF, OWASP Top 10)
- **🔐 ReAct Tools**:
  - `scan_environment`: Port scanning, service detection, vulnerability assessment
  - `query_threat_intel`: Natural language threat intelligence queries
  - `propose_action`: Action proposals with risk assessment
- **🐳 Docker Sandbox**: Secure code execution in isolated containers
- **📱 Telegram Approval Gate**: Human-in-the-loop approval workflow
- **🔒 RBAC Authentication**: Role-based access control (Admin, Analyst, Viewer)
- **💾 Dual Database**: SQLite for development, PostgreSQL for production
- **📊 Structured Logging**: Production-ready logging with structlog
- **✅ Full Test Coverage**: pytest with unit and integration tests
- **🚀 CI/CD**: GitHub Actions with linting, type checking, security scanning

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Auth API   │  Agent API   │  Health API  │  WebSocket     │
├──────────────┴──────────────┴──────────────┴────────────────┤
│                      Services Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐     │
│  │  Ollama  │ │  Chroma  │ │  Docker  │ │ Telegram  │     │
│  │  Client  │ │   RAG    │ │ Sandbox  │ │    Bot    │     │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘     │
├─────────────────────────────────────────────────────────────┤
│                       ReAct Tools                            │
│  scan_environment │ query_threat_intel │ propose_action     │
├─────────────────────────────────────────────────────────────┤
│                    Database Layer                            │
│         SQLAlchemy ORM │ Repository Pattern                  │
├─────────────────────────────────────────────────────────────┤
│              SQLite (dev) / PostgreSQL (prod)                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Ollama (or use Docker Compose)
- (Optional) Telegram Bot Token for approval workflow

### One-Command Setup

```bash
# Bootstrap complete environment
bash scripts/bootstrap.sh
```

### Manual Setup

1. **Clone the repository**
```bash
git clone https://github.com/Senpai-Sama7/Otis.git
cd Otis
```

2. **Setup environment**
```bash
make setup
# or use bootstrap script: bash scripts/bootstrap.sh
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration (API keys, tokens, database URL)
```

4. **Build RAG knowledge base**
```bash
make rag  # Downloads MITRE ATT&CK, NIST CSF, OWASP Top 10
```

5. **Initialize database**
```bash
make migrate
```

6. **Create admin user**
```bash
python scripts/create_admin.py
```

### Running with Docker Compose (Recommended)

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Running Locally

```bash
# Install dependencies
make install-dev

# Run the application
make run
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## 📖 Usage

### Authentication

1. **Register a user**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst1",
    "email": "analyst@example.com",
    "password": "securepass123",
    "role": "analyst"
  }'
```

2. **Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "analyst1",
    "password": "securepass123"
  }'
```

### Environment Scanning

```bash
curl -X POST "http://localhost:8000/api/v1/agent/scan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "ports",
    "target": "localhost",
    "options": {"port_range": "1-1024"}
  }'
```

### Threat Intelligence Query

```bash
curl -X POST "http://localhost:8000/api/v1/agent/threat-intel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SQL injection attack patterns",
    "sources": ["MITRE", "OWASP"],
    "limit": 5
  }'
```

### Propose Action

```bash
curl -X POST "http://localhost:8000/api/v1/agent/propose-action" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "patch",
    "description": "Apply security patch for CVE-2024-XXXX",
    "reasoning": "Critical vulnerability requires immediate patching",
    "risk_level": "high",
    "proposed_code": "apt-get update && apt-get upgrade package-name"
  }'
```

### ReAct Agent (New!)

Execute autonomous security assessments with the ReAct agent:

```bash
curl -X POST "http://localhost:8000/api/v1/agent/run" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Perform a passive security assessment of the localhost environment",
    "scan_duration": 10,
    "mode": "passive"
  }'
```

**Response includes:**
- `summary`: Executive summary of findings
- `steps`: Reasoning and action steps taken
- `proposals`: Any high-risk actions requiring approval
- `evidence`: Security findings and artifacts
- `confidence`: Confidence score (0.0-1.0)

### Run Demo

Try the complete workflow with the demo script:

```bash
make demo
```

This will:
1. Start all services with Docker Compose
2. Build the RAG knowledge base
3. Run health checks
4. Register a demo user
5. Execute sample agent requests
6. Query threat intelligence
7. Display results

## 🔒 Security & Safety

### Safety-First Design

Otis is built with **defense-in-depth** security:

1. **Passive-First Mode**: All operations default to passive (read-only) mode
2. **Approval Gates**: Medium/High/Critical risk actions require human approval via Telegram
3. **Sandboxed Execution**: Code runs in isolated Docker containers with:
   - Read-only root filesystem
   - Network disabled by default
   - Memory and CPU limits
   - No privileged operations
4. **Denylist Enforcement**: Blocks wireless injection, traffic disruption, privilege escalation
5. **Audit Logging**: All actions logged with HMAC integrity to `data/audit.log`

### Risk Levels

| Level | Description | Examples | Approval Required |
|-------|-------------|----------|-------------------|
| **Low** | Read-only operations | Passive scans, queries, log reading | ❌ Auto-approved |
| **Medium** | Active non-destructive | Active scanning, config queries | ✅ Yes |
| **High** | Code execution, patches | System updates, code execution | ✅ Yes + Review |
| **Critical** | Destructive operations | Data deletion, exploits, kernel mods | ✅ Yes + Executive |

### Approval Workflow

1. Agent proposes action with rationale and risk level
2. Telegram bot sends notification to admin with:
   - Action description and proposed code
   - Risk level and security context
   - Approve ✅ / Deny ❌ buttons
3. On approval:
   - Code executes in sandbox with appropriate permissions
   - Results logged and returned
4. On denial:
   - Action rejected and logged
5. Timeout: 5 minutes

**See [SECURITY_POLICY.md](docs/SECURITY_POLICY.md) for complete details.**

### Telegram Bot Setup

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
   ```bash
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_ADMIN_CHAT_ID=your-chat-id
   ```
4. Start the bot:
   ```bash
   docker-compose --profile with-bot up -d
   ```

## 🛠️ Function Signatures

### Tools

```python
# Scan environment for security issues
async def scan_environment(duration: int = 10) -> dict:
    """
    Args:
        duration: Scan duration in seconds (default: 10)
    Returns:
        dict with findings, vulnerabilities_count, risk_score
    """

# Query threat intelligence
async def query_threat_intel(query: str, k: int = 3) -> list[dict]:
    """
    Args:
        query: Natural language query
        k: Number of results (default: 3)
    Returns:
        List of threat intelligence documents
    """

# Propose action for approval
def propose_action(code: str, risk: str, rationale: str) -> dict:
    """
    Args:
        code: Code to execute
        risk: Risk level (low, medium, high, critical)
        rationale: Justification
    Returns:
        dict with action_id and status
    """
```

### Sandbox

```python
# Execute code in sandbox
def exec_in_sandbox(
    code: str,
    lang: str = "python",
    timeout: int = 20,
    net: bool = False
) -> dict:
    """
    Args:
        code: Code to execute
        lang: Language (python, node, bash)
        timeout: Timeout in seconds (default: 20)
        net: Allow network (default: False)
    Returns:
        dict with success, output, error, exit_code
    """
```

### Agent

```python
# Run ReAct agent
async def run_agent(req: AgentRequest) -> AgentResponse:
    """
    Args:
        req: AgentRequest with instruction, scan_duration, mode
    Returns:
        AgentResponse with summary, steps, proposals, evidence, confidence
    """

# Ollama inference
async def infer(
    prompt: str,
    temperature: float = 0.1,
    top_p: float = 0.9,
    num_ctx: int = 1536
) -> str:
    """Deterministic inference with DeepSeek-R1"""
```

## 📚 Documentation

- **[Security Policy](docs/SECURITY_POLICY.md)**: Complete security and safety guidelines
- **[Architecture](docs/ARCHITECTURE.md)**: System architecture and design
- **[API Documentation](docs/API.md)**: API endpoints and schemas
- **[Deployment](docs/DEPLOYMENT.md)**: Production deployment guide
- **[Troubleshooting](#troubleshooting)**: Common issues and solutions
```

### LLM Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/agent/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze this log for security issues: ...",
    "context": "System: Ubuntu 22.04, Role: Web Server"
  }'
```

## 🧪 Development

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check
```

### Testing

```bash
# Run tests
make test

# Run with verbose output
make test-verbose
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
make install-dev

# Manually run on all files
pre-commit run --all-files
```

## 📁 Project Structure

```
Otis/
├── src/                      # Application source code
│   ├── api/                  # FastAPI routes
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── agent.py         # Agent operations endpoints
│   │   └── health.py        # Health check endpoints
│   ├── core/                 # Core utilities
│   │   ├── config.py        # Configuration management
│   │   ├── logging.py       # Logging setup
│   │   └── security.py      # Security utilities
│   ├── database/             # Database layer
│   │   ├── connection.py    # DB connection management
│   │   └── repository.py    # Repository pattern
│   ├── models/               # Data models
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── services/             # Business logic services
│   │   ├── ollama.py        # Ollama LLM client
│   │   ├── chroma.py        # Chroma vector store
│   │   ├── docker_sandbox.py # Docker sandbox
│   │   └── telegram.py      # Telegram bot
│   ├── tools/                # ReAct tools
│   │   ├── scan_environment.py
│   │   ├── query_threat_intel.py
│   │   └── propose_action.py
│   └── main.py               # Application entry point
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── conftest.py           # Test configuration
├── scripts/                  # Utility scripts
│   ├── init_rag_data.py     # Initialize RAG data
│   └── create_admin.py      # Create admin user
├── docs/                     # Documentation
├── .github/workflows/        # GitHub Actions
│   └── ci.yml               # CI/CD pipeline
├── docker-compose.yml        # Docker Compose config
├── Dockerfile               # Docker image
├── Makefile                 # Development commands
├── pyproject.toml           # Python project config
└── requirements.txt         # Dependencies
```

## 🔒 Security

- **RBAC**: Role-based access control with three levels (Admin, Analyst, Viewer)
- **JWT Authentication**: Secure token-based authentication
- **Docker Sandbox**: Isolated code execution environment
- **Approval Gate**: Human-in-the-loop via Telegram for critical actions
- **Security Scanning**: Automated vulnerability scanning in CI/CD
- **Input Validation**: Pydantic schemas for request validation
- **Rate Limiting**: (Recommended to add in production)

## 📊 Monitoring & Logging

- **Structured Logging**: Using structlog for JSON logging
- **Health Checks**: `/api/v1/health` endpoint for monitoring
- **Service Status**: Real-time status of all dependencies
- **Audit Trail**: All actions logged with user context

## 🛠️ Configuration

Key environment variables in `.env`:

```bash
# Application
APP_NAME=Otis Cybersecurity AI Agent
DEBUG=false
LOG_LEVEL=INFO

# Database
# Development: Use SQLite for local development
DATABASE_URL=sqlite:///./data/app.db
# Production: Use PostgreSQL for production deployments
# DATABASE_URL=postgresql://user:pass@localhost:5432/otis

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:7b

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id

# Feature Flags
ENABLE_APPROVAL_GATE=true
ENABLE_CODE_EXECUTION=true

# Security Policy
DEFAULT_MODE=passive
MAX_ITERATIONS=2
MAX_EXEC_TIME=45
```

## 🐛 Troubleshooting

### Common Issues

#### Ollama Connection Errors

**Problem**: `Connection refused to http://localhost:11434`

**Solutions**:
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/version
   ```
2. Start Ollama if not running:
   ```bash
   ollama serve
   ```
3. Pull the DeepSeek-R1 model:
   ```bash
   ollama pull deepseek-r1:7b
   ```
4. Update `OLLAMA_BASE_URL` in `.env` if using Docker Compose

#### RAG Knowledge Base Not Found

**Problem**: `Collection not found: cybersecurity_knowledge`

**Solutions**:
1. Build the RAG index:
   ```bash
   make rag
   ```
2. Verify Chroma directory exists:
   ```bash
   ls -la data/chroma/
   ```
3. Check Chroma service is running (if using Docker):
   ```bash
   docker-compose logs chroma
   ```

#### Docker Sandbox Permission Denied

**Problem**: `Cannot connect to Docker socket`

**Solutions**:
1. Ensure Docker is running:
   ```bash
   docker ps
   ```
2. Add user to docker group (Linux):
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```
3. Verify Docker socket permissions:
   ```bash
   ls -l /var/run/docker.sock
   ```

#### Telegram Bot Not Responding

**Problem**: Bot doesn't send approval requests

**Solutions**:
1. Verify token and chat ID in `.env`:
   ```bash
   grep TELEGRAM .env
   ```
2. Test bot is accessible:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```
3. Start bot service:
   ```bash
   docker-compose --profile with-bot up -d
   ```
4. Check bot logs:
   ```bash
   docker-compose logs bot
   ```

#### Agent Returns Low Confidence

**Problem**: Agent confidence score is consistently low (<0.3)

**Solutions**:
1. Check Ollama model is loaded:
   ```bash
   ollama list
   ```
2. Verify RAG data is indexed:
   ```bash
   python -c "from src.rag.index import query; print(query('test', k=1))"
   ```
3. Increase scan duration:
   ```json
   {"scan_duration": 30, "mode": "passive"}
   ```
4. Check agent logs for errors:
   ```bash
   tail -f data/logs/agent.log
   ```

#### Tests Failing

**Problem**: `pytest` tests fail

**Solutions**:
1. Install dev dependencies:
   ```bash
   make install-dev
   ```
2. Clean cached files:
   ```bash
   make clean
   ```
3. Run specific test:
   ```bash
   pytest tests/unit/test_agent.py -v
   ```
4. Check coverage report:
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

#### Memory/Resource Issues

**Problem**: Container OOM or high CPU usage

**Solutions**:
1. Adjust resource limits in `docker-compose.yml`:
   ```yaml
   services:
     api:
       deploy:
         resources:
           limits:
             memory: 1G
             cpus: '2.0'
   ```
2. Reduce concurrent operations
3. Increase Docker Desktop resources (Mac/Windows)

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Restart services
make down && make up
```

View detailed logs:

```bash
# All services
make docker-logs

# Specific service
docker-compose logs -f api

# Audit logs
tail -f data/audit.log | jq

# Application logs
tail -f data/logs/*.log
```

### Getting Help

1. **Check Documentation**: Review [docs/](docs/) directory
2. **Search Issues**: [GitHub Issues](https://github.com/Senpai-Sama7/Otis/issues)
3. **Create Issue**: Include:
   - Error messages and logs
   - Steps to reproduce
   - Environment details (OS, Python version, Docker version)
   - Configuration (redact secrets!)
4. **Security Issues**: Email security@otis.local

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MITRE ATT&CK** for threat intelligence framework
- **NIST** for cybersecurity framework
- **OWASP** for security best practices
- **FastAPI** for the excellent web framework
- **DeepSeek** for the powerful LLM model

## 📞 Support

- 📧 Email: support@otis.local
- 💬 GitHub Issues: [Create an issue](https://github.com/Senpai-Sama7/Otis/issues)
- 📖 Documentation: [Wiki](https://github.com/Senpai-Sama7/Otis/wiki)

---

**Built with ❤️ for the cybersecurity community**