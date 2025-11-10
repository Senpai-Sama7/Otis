# Otis - Autonomous Cybersecurity AI Coding Agent

<div align="center">

🤖 **Production-Ready AI Agent for Cybersecurity Operations**

[![CI/CD](https://github.com/Senpai-Sama7/Otis/actions/workflows/ci.yml/badge.svg)](https://github.com/Senpai-Sama7/Otis/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

## 🎯 Overview

Otis is an autonomous cybersecurity AI coding agent built with production-grade architecture and enhanced with advanced reasoning capabilities from Project-C0Di3. It combines the power of DeepSeek-R1 LLM via Ollama with RAG-based threat intelligence (MITRE ATT&CK, NIST, OWASP), multi-layered reasoning, and comprehensive memory systems to provide intelligent security analysis, vulnerability detection, and automated remediation with human-in-the-loop approval.

**NEW**: Enhanced with advanced features synthesized from Project-C0Di3 for superior performance and intelligence.

## ✨ Features

### 🧠 **Advanced Multi-Layered Reasoning** 🆕
- **Absolute Zero Reasoner**: First-principles reasoning from fundamental axioms
- **Darwin-Gödel Engine**: Evolutionary optimization with formal verification
- **Zero-Shot Intelligence**: Direct responses for simple queries
- **Adaptive Strategy Selection**: Automatically selects optimal reasoning approach based on query complexity
- **Complexity Analysis**: Intelligent assessment of query difficulty

### 🧠 **Comprehensive Memory Systems** 🆕
- **Episodic Memory**: Stores specific interaction history and experiences with temporal context
- **Semantic Memory**: Conceptual cybersecurity knowledge with vector-based retrieval
- **Procedural Memory**: Step-by-step methodologies and best practices
- **Working Memory**: Short-term active context with LRU eviction
- **Persistent Storage**: Automatic save/load with JSON serialization

### ⚡ **Cache-Augmented Generation (CAG)** 🆕
- **10x Faster Responses**: Intelligent caching reduces response time from seconds to milliseconds
- **Semantic Similarity Matching**: Cache hits for similar queries, not just exact matches
- **Multi-Level Caching**: Exact match, similar query, and embedding-based retrieval
- **Performance Metrics**: Real-time hit rate, average response time, and cache statistics
- **Cache Management**: LRU eviction, TTL expiration, pre-warming, import/export

### 🔐 **Core Security Features**
- **AI-Powered Analysis**: DeepSeek-R1 7B model via Ollama for intelligent reasoning
- **RAG Knowledge Base**: Vector search with Chroma (MITRE ATT&CK, NIST CSF, OWASP Top 10)
- **ReAct Tools**:
  - `scan_environment`: Port scanning, service detection, vulnerability assessment
  - `query_threat_intel`: Natural language threat intelligence queries
  - `propose_action`: Action proposals with risk assessment
- **🐳 Docker Sandbox**: Secure code execution in isolated containers
- **📱 Telegram Approval Gate**: Human-in-the-loop approval workflow
- **🔒 RBAC Authentication**: Role-based access control (Admin, Analyst, Viewer)
- **💾 Dual Database**: SQLite for development, PostgreSQL for production
- **📊 Structured Logging**: Production-ready logging with structlog
- **✅ Full Test Coverage**: 47+ tests with pytest (reasoning, memory, CAG, integration)
- **🚀 CI/CD**: GitHub Actions with linting, type checking, security scanning

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                              │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│   Auth API   │  Agent API   │  Health API  │  WebSocket   │  Memory API │
├──────────────┴──────────────┴──────────────┴──────────────┴─────────────┤
│                           Services Layer                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐    │
│  │  Ollama  │ │  Chroma  │ │  Docker  │ │ Telegram  │ │   CAG    │    │
│  │  Client  │ │   RAG    │ │ Sandbox  │ │    Bot    │ │ Service  │    │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│                    Advanced Reasoning Engine 🆕                          │
│  ┌────────────────┐ ┌───────────────┐ ┌──────────────────────┐        │
│  │  Zero-Shot     │ │ Darwin-Gödel  │ │  Absolute Zero       │        │
│  │  Reasoning     │ │   Engine      │ │  Reasoner            │        │
│  └────────────────┘ └───────────────┘ └──────────────────────┘        │
├─────────────────────────────────────────────────────────────────────────┤
│                    Comprehensive Memory Systems 🆕                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐          │
│  │ Episodic   │ │ Semantic   │ │ Procedural │ │  Working   │          │
│  │  Memory    │ │  Memory    │ │  Memory    │ │  Memory    │          │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘          │
├─────────────────────────────────────────────────────────────────────────┤
│                          ReAct Tools                                     │
│     scan_environment │ query_threat_intel │ propose_action              │
├─────────────────────────────────────────────────────────────────────────┤
│                         Database Layer                                   │
│            SQLAlchemy ORM │ Repository Pattern                           │
├─────────────────────────────────────────────────────────────────────────┤
│                  SQLite (dev) / PostgreSQL (prod)                        │
└─────────────────────────────────────────────────────────────────────────┘
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

### Production-Grade Security Architecture

Otis implements **defense-in-depth** with multiple security layers:

#### Critical Security Fixes (Production-Ready)

1. **Docker Socket Isolation** ✅
   - API and worker services have NO Docker access
   - Only `runner` service can execute Docker commands
   - Access mediated through `socket-proxy` (least privilege)
   - Prevents container escape and privilege escalation

2. **Multi-Stage Docker Builds** ✅
   - Build tools removed from runtime images
   - 50-70% smaller attack surface
   - All services run as non-root users (`otis`, `runner`)

3. **Single Dependency Source** ✅
   - All dependencies in `pyproject.toml` (PEP 621)
   - No version drift or dependency confusion
   - Reproducible builds

See [SECURITY_FIXES.md](docs/SECURITY_FIXES.md) for complete details.

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

## 🆕 Advanced Features

### Multi-Layered Reasoning Engine

The reasoning engine automatically selects the optimal strategy based on query complexity:

```python
from src.reasoning import ReasoningEngine, ReasoningContext

# Initialize reasoning engine
reasoning_engine = ReasoningEngine(
    ollama_client=ollama_client,
    memory_system=memory_system
)

# Execute reasoning (strategy auto-selected)
context = ReasoningContext(
    query="Analyze advanced persistent threat attack vectors involving lateral movement",
    user_context={"role": "analyst"},
    relevant_memories=[...]
)

result = await reasoning_engine.reason(context)
# Returns: ReasoningResult with strategy_used, response, steps, confidence
```

**Reasoning Strategies:**

| Complexity | Strategy | Use Case | Features |
|-----------|----------|----------|----------|
| < 0.3 | **Zero-Shot** | Simple queries | Direct generation with context |
| 0.3 - 0.7 | **Darwin-Gödel** | Moderate complexity | Evolutionary optimization with formal verification |
| ≥ 0.7 | **Absolute Zero** | Complex analysis | First-principles reasoning from fundamental axioms |

**Darwin-Gödel Engine Process:**
1. Extract foundational axioms from context
2. Generate initial hypothesis population
3. Evolve through mutation and crossover
4. Verify logical consistency
5. Extract optimized solution

**Absolute Zero Reasoner Process:**
1. Extract fundamental cybersecurity principles
2. Decompose complex concepts into base elements
3. Establish ground truth statements
4. Build logical inferences
5. Validate reasoning through verification
6. Synthesize verified solution

### Comprehensive Memory Systems

Store and retrieve knowledge across multiple memory types:

```python
from src.memory import MemorySystem

# Initialize memory system
memory = MemorySystem(
    vector_store=chroma_client,
    persistence_path="./data/memory",
    working_memory_capacity=10
)
await memory.initialize()

# Add interaction to episodic memory
await memory.add_interaction(
    query="What is SQL injection?",
    response="SQL injection is a code injection technique...",
    context={"severity": "high"},
    metadata={"user": "analyst1", "session": "abc123"}
)

# Recall similar past interactions
similar = await memory.recall_similar_interactions(
    "SQL injection attack",
    k=5
)

# Add concept to semantic memory
await memory.add_concept(
    "SQL injection exploits database vulnerabilities",
    metadata={"category": "red-team", "source": "OWASP"}
)

# Query knowledge base
knowledge = await memory.query_knowledge("SQL injection", k=5)

# Add procedure to procedural memory
await memory.add_procedure(
    name="SQL Injection Testing",
    steps=[
        "Identify input fields",
        "Test for SQL syntax errors",
        "Attempt boolean-based blind injection",
        "Extract database schema",
        "Document findings"
    ],
    category="red-team"
)

# Get procedure
procedure = await memory.get_procedure("SQL Injection Testing")

# Working memory (short-term context)
memory.add_to_working_memory("current_task", "Analyze logs")
task = memory.get_from_working_memory("current_task")

# Get comprehensive context for reasoning
context = await memory.get_context_for_reasoning(
    "SQL injection analysis",
    max_items=10
)
```

### Cache-Augmented Generation (CAG)

Achieve 10x faster responses with intelligent caching:

```python
from src.cag import CAGService, CAGQuery

# Initialize CAG service
cag = CAGService(
    llm_client=ollama_client,
    max_cache_size=2000,
    similarity_threshold=0.92,
    default_ttl=7200  # 2 hours
)

# Query with caching (10-200ms for cache hits vs 2-5s for generation)
query = CAGQuery(
    query="What is SQL injection?",
    category="vulnerability",
    use_cache=True
)

result = await cag.query(query)
# result.cached = True (if cache hit)
# result.cache_hit_type = "exact" | "similar" | "none"
# result.processing_time < 0.2s for cache hits

# Pre-warm cache with common queries
common_queries = [
    CAGQuery(query="What is SQL injection?"),
    CAGQuery(query="What is XSS?"),
    CAGQuery(query="What is CSRF?"),
]
await cag.prewarm_cache(common_queries)

# Get performance metrics
metrics = cag.get_metrics()
print(f"Hit rate: {metrics.hit_rate:.2%}")
print(f"Average response time: {metrics.average_response_time:.3f}s")
print(f"Cache size: {metrics.cache_size}")

# Export/import cache for persistence
await cag.export_cache(Path("cache.json"))
await cag.import_cache(Path("cache.json"))
```

**CAG Performance Comparison:**

| Metric | Without CAG | With CAG (Cache Hit) |
|--------|-------------|----------------------|
| Response Time | 2-5 seconds | 50-200ms (10-100x faster) |
| Resource Usage | High (per query) | Low (cached) |
| Consistency | Variable | High (cached) |
| Throughput | ~0.2-0.5 QPS | ~5-20 QPS |

### Integrated Example: Advanced Security Analysis

```python
from src.reasoning import ReasoningEngine, ReasoningContext
from src.memory import MemorySystem
from src.cag import CAGService, CAGQuery

# Initialize systems
memory = MemorySystem(vector_store=chroma, persistence_path="./data/memory")
await memory.initialize()

reasoning = ReasoningEngine(ollama_client, memory_system=memory)

cag = CAGService(llm_client=ollama_client)

# Perform advanced analysis
query = "Analyze potential SQL injection vulnerability in login form"

# Check CAG cache first (fast path)
cag_query = CAGQuery(query=query, category="vulnerability")
cag_result = await cag.query(cag_query)

if not cag_result.cached:
    # Cache miss - use advanced reasoning
    
    # Get context from memory
    context = await memory.get_context_for_reasoning(query)
    
    # Reason about the query (auto-selects strategy)
    reasoning_context = ReasoningContext(
        query=query,
        relevant_memories=context["relevant_knowledge"]
    )
    
    reasoning_result = await reasoning.reason(reasoning_context)
    
    # Store interaction in episodic memory
    await memory.add_interaction(
        query=query,
        response=reasoning_result.response,
        context={"strategy": reasoning_result.strategy_used.value}
    )
    
    response = reasoning_result.response
else:
    # Cache hit - instant response
    response = cag_result.response

print(f"Response: {response}")
print(f"Cached: {cag_result.cached}")
print(f"Processing time: {cag_result.processing_time:.3f}s")
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
# Run all tests (47+ tests covering reasoning, memory, CAG, and core features)
make test

# Run with verbose output
make test-verbose

# Run specific test suites
pytest tests/unit/test_reasoning.py -v  # Reasoning engine tests (12 tests)
pytest tests/unit/test_memory.py -v     # Memory systems tests (21 tests)
pytest tests/unit/test_cag.py -v        # CAG service tests (14 tests)

# Run with coverage report
pytest --cov=src --cov-report=html
```

**Test Coverage:**
- ✅ Reasoning Engine: 12 tests (zero-shot, Darwin-Gödel, Absolute Zero)
- ✅ Memory Systems: 21 tests (episodic, semantic, procedural, working)
- ✅ CAG Service: 14 tests (caching, similarity, metrics, persistence)
- ✅ Core Features: Integration tests for agent, API, security

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