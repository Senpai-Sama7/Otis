# Architecture Overview

## Production-Ready Security Architecture

Otis implements **defense-in-depth** with multiple security layers:

### Main Cybersecurity Platform
```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│                         (FastAPI Routes)                         │
├─────────────────────────────────────────────────────────────────┤
│                      Security Control Layer                      │
│     PolicyEngine │ InputSanitizer │ Zero-Trust Networks         │
├─────────────────────────────────────────────────────────────────┤
│                        Application Layer                         │
│         Reasoning Engine │ Memory System │ Tool Orchestration   │
├─────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                        │
│    Celery Workers │ Redis │ OpenTelemetry │ Docker Sandbox      │
├─────────────────────────────────────────────────────────────────┤
│                      External Services Layer                     │
│  Ollama │ Chroma │ PostgreSQL │ Elasticsearch │ Jaeger          │
└─────────────────────────────────────────────────────────────────┘
```

### Anti-Spam AI with Red/Blue Team Security
```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│                   (Anti-Spam API, Security API)                  │
├─────────────────────────────────────────────────────────────────┤
│                     Security Control Layer                       │
│  Red Team Engine │ Blue Team Pipeline │ Compliance Framework    │
├─────────────────────────────────────────────────────────────────┤
│                        Application Layer                         │
│    Anti-Spam Model │ Attack Vectors │ Threat Detectors │ MDP    │
├─────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                        │
│  Kubernetes │ Prometheus │ Grafana │ Auto-scaling │ Security    │
├─────────────────────────────────────────────────────────────────┤
│                      External Services Layer                     │
│  HuggingFace │ PostgreSQL │ Redis │ Model Registry │ Security    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 0. Security Control Layer (`src/security/`) **NEW**
- **Responsibilities**: Primary security enforcement, input validation, access control
- **Components**:
  - `policy_engine.py`: RBAC, risk-based approval gates, target restrictions
  - `input_sanitizer.py`: Blocks command injection, SQL injection, XSS, code execution
  - Network segmentation: 5 isolated networks (frontend, db, ai, security, obs)

### 1. API Layer (`src/api/`)
- **Responsibilities**: HTTP request handling, response formatting, authentication
- **Components**:
  - `auth.py`: User registration and authentication
  - `agent.py`: AI agent operations (scan, analyze, execute)
  - `health.py`: Health checks and status
  - `dependencies.py`: Dependency injection, auth middleware

### 2. Core Layer (`src/core/`)
- **Responsibilities**: Cross-cutting concerns, configuration
- **Components**:
  - `config.py`: Environment configuration with Pydantic
  - `security.py`: Authentication, password hashing (Argon2), JWT
  - `logging.py`: Structured logging with structlog

### 3. Tool Orchestration Layer (`src/tools/`) **UPDATED**
- **Responsibilities**: Orchestrate real security tools (not reimplemented in Python)
- **Components**:
  - `red_team_runner.py`: Orchestrates nmap, sqlmap, metasploit, gobuster, impacket
  - `blue_team_pipeline.py`: Vector → Elasticsearch → ElastAlert → Sigma rules
  - `c2_manager.py`: Integrates with existing C2 frameworks (Covenant, Sliver)
  - `scan_environment.py`: Passive/active scanning orchestration
  - `query_threat_intel.py`: RAG-based threat intelligence queries
  - `propose_action.py`: Action approval workflow with risk assessment

### 4. Services Layer (`src/services/`)
- **Responsibilities**: Business logic, external integrations
- **Components**:
  - `ollama.py`: LLM inference via Ollama (DeepSeek-R1)
  - `chroma.py`: Vector store operations for RAG
  - `docker_sandbox.py`: Secure code execution in containers
  - `telegram.py`: Bot notifications and approval workflow

### 2. Reasoning Engine (`src/reasoning/`) **RENAMED**
- **Responsibilities**: Adaptive reasoning strategy selection based on query complexity
- **Components**:
  - `direct.py`: Simple queries (formerly "zero_shot")
  - `hypothesis_evolution.py`: Moderate complexity (formerly "darwin_godel")
  - `first_principles.py`: Complex analysis (formerly "absolute_zero")
  - `query_router.py`: LLM-based semantic routing (not heuristic keyword counting)
  - `planner.py`: Multi-step task decomposition
  - `base.py`: Base tool interface
  - `scan_environment.py`: Security scanning capabilities
  - `query_threat_intel.py`: Knowledge base queries
  - `propose_action.py`: Action approval workflow

### 5. Distributed Execution Layer **NEW**
- **Responsibilities**: Horizontal scaling, task distribution, observability
- **Components**:
  - `celery_tasks.py`: Distributed task definitions (sandbox execution, scanning, threat intel)
  - `celery_config.py`: Celery + Redis configuration
  - `tracing.py`: OpenTelemetry decorators for distributed tracing
  - `metrics.py`: Prometheus metrics collection

### 6. Models Layer (`src/models/`)
- **Responsibilities**: Data structures, schemas
- **Components**:
  - `database.py`: SQLAlchemy ORM models
  - `schemas.py`: Pydantic request/response schemas

### 6. Database Layer (`src/database/`)
- **Responsibilities**: Data persistence, repository pattern
- **Components**:
  - `connection.py`: Database connection management
  - `repository.py`: Generic CRUD operations

## Data Flow

### 1. Authentication Flow
```
┌──────┐    POST /auth/login    ┌─────────┐
│Client│ ──────────────────────>│  API    │
└──────┘                         │(auth.py)│
   ▲                             └────┬────┘
   │                                  │
   │                             ┌────▼────┐
   │                             │Security │
   │      JWT Token              │(verify) │
   │◄─────────────────────────── └────┬────┘
   │                                  │
   │                             ┌────▼────┐
   │                             │Database │
   │                             │(users)  │
   │                             └─────────┘
```

### 2. Threat Intelligence Query Flow
```
┌──────┐  POST /agent/threat-intel  ┌────────┐
│Client│ ─────────────────────────> │API     │
└──────┘                             │(agent) │
   ▲                                 └───┬────┘
   │                                     │
   │                                ┌────▼───────┐
   │                                │QueryThreat │
   │                                │IntelTool   │
   │                                └────┬───────┘
   │                                     │
   │                                ┌────▼────┐
   │         Results                │ Chroma  │
   │◄────────────────────────────── │ Vector  │
                                    │  Store  │
                                    └────┬────┘
                                         │
                                    ┌────▼────┐
                                    │  MITRE  │
                                    │  NIST   │
                                    │  OWASP  │
                                    └─────────┘
```

### 3. Code Execution Flow with Approval
```
┌──────┐  POST /agent/propose-action  ┌────────┐
│Client│ ─────────────────────────────>│API     │
└──────┘                               │(agent) │
                                       └───┬────┘
                                           │
                                      ┌────▼────────┐
                                      │ProposeAction│
                                      │    Tool     │
                                      └────┬────────┘
                                           │
                           ┌───────────────┴─────────────┐
                           │                             │
                      ┌────▼────┐                   ┌────▼────┐
                      │Database │                   │Telegram │
                      │(actions)│                   │ Service │
                      └─────────┘                   └────┬────┘
                                                         │
                                                    ┌────▼────┐
                                                    │  Admin  │
                                                    │Approval │
                                                    └────┬────┘
                                                         │
                                        Approved?        │
                                        ┌────────────────┘
                                        │
                                   ┌────▼───────┐
                                   │   Docker   │
                                   │  Sandbox   │
                                   └────────────┘
```

## Security Architecture

### Defense in Depth

1. **Network Layer**
   - HTTPS/TLS encryption
   - Reverse proxy (Nginx)
   - Rate limiting

2. **Authentication Layer**
   - JWT with expiration
   - Argon2 password hashing (memory-hard)
   - Role-based access control (RBAC)

3. **Authorization Layer**
   - Role hierarchy: Admin > Analyst > Viewer
   - Endpoint-level permissions
   - Resource-level access control

4. **Application Layer**
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS prevention (FastAPI auto-escaping)

5. **Execution Layer**
   - Docker container isolation
   - Resource limits (CPU, memory)
   - Network disabled
   - No privileged access

6. **Approval Layer**
   - Human-in-the-loop for critical actions
   - Risk level assessment
   - Audit logging

## Scalability

### Horizontal Scaling
```
┌─────────┐
│  Load   │
│Balancer │
└────┬────┘
     │
     ├─────────┬─────────┬─────────┐
     │         │         │         │
┌────▼────┐┌────▼────┐┌────▼────┐│
│ Otis    ││ Otis    ││ Otis    ││
│Instance ││Instance ││Instance ││
│   1     ││   2     ││   3     ││
└────┬────┘└────┬────┘└────┬────┘│
     │          │          │      │
     └──────────┴──────────┴──────┘
                │
        ┌───────┴────────┐
        │                │
   ┌────▼────┐      ┌────▼────┐
   │Postgres │      │  Chroma │
   │(Primary)│      │ (Shared)│
   └─────────┘      └─────────┘
```

### Caching Strategy
- Redis for session storage
- Chroma vector cache for frequent queries
- HTTP response caching for static content

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **ASGI Server**: Uvicorn

### AI & ML
- **LLM**: DeepSeek-R1 7B via Ollama
- **Vector Store**: ChromaDB
- **RAG**: LangChain integration

### Database
- **Development**: SQLite
- **Production**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic

### Authentication
- **Password Hashing**: Argon2 (via Passlib)
- **JWT**: python-jose
- **Tokens**: HS256 algorithm

### External Integrations
- **Telegram**: python-telegram-bot
- **Docker**: docker-py
- **HTTP**: httpx (async)

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Structlog + aggregation tools

## Design Patterns

### 1. Repository Pattern
Abstracts data access logic:
```python
class BaseRepository(Generic[ModelType]):
    def get(self, id: int) -> Optional[ModelType]: ...
    def create(self, **kwargs) -> ModelType: ...
    def update(self, id: int, **kwargs) -> ModelType: ...
```

### 2. Dependency Injection
FastAPI's built-in DI for services:
```python
@router.post("/agent/scan")
async def scan(db: Session = Depends(get_db)): ...
```

### 3. Strategy Pattern
Interchangeable tool implementations:
```python
class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> dict: ...
```

### 4. Factory Pattern
Service instantiation:
```python
def get_settings() -> Settings:
    return Settings()  # Cached singleton
```

### 5. Adapter Pattern
External service wrappers:
- `OllamaService` adapts Ollama HTTP API
- `ChromaService` adapts ChromaDB client
- `DockerSandboxService` adapts Docker SDK

## Best Practices

### Code Organization
- ✅ Separation of concerns
- ✅ Single responsibility principle
- ✅ Dependency inversion
- ✅ Interface segregation

### Testing
- ✅ Unit tests for business logic
- ✅ Integration tests for APIs
- ✅ Mocked external dependencies
- ✅ Test fixtures and factories

### Security
- ✅ Input validation
- ✅ Output encoding
- ✅ Least privilege principle
- ✅ Defense in depth

### Performance
- ✅ Async/await throughout
- ✅ Connection pooling
- ✅ Efficient queries
- ✅ Resource limits

### Observability
- ✅ Structured logging
- ✅ Health checks
- ✅ Metrics endpoints
- ✅ Error tracking

## Future Enhancements

### Short Term
- [ ] WebSocket support for streaming
- [ ] Redis caching layer
- [ ] Enhanced metrics (Prometheus)
- [ ] GraphQL API option

### Medium Term
- [ ] Multi-model LLM support
- [ ] Advanced RAG techniques
- [ ] Plugin architecture
- [ ] Web UI dashboard

### Long Term
- [ ] Distributed tracing
- [ ] ML model fine-tuning
- [ ] Custom tool marketplace
- [ ] Multi-tenant support
