# Actual Production Architecture

## Reality Check

**Documented**: Simple 5-layer agent
**Actual**: Complex 20+ microservice SOC-in-a-Box

This document reflects the **actual** architecture as deployed.

---

## Complete Service Inventory

### Core Services (6)
1. **api** - FastAPI application (frontend-facing)
2. **worker** - Celery workers for async tasks
3. **postgres** - PostgreSQL database
4. **redis** - Message broker and cache
5. **ollama** - LLM inference engine
6. **chroma** - Vector store for RAG

### Security Services (5)
7. **socket-proxy** - Docker socket mediator
8. **runner** - Sandbox execution service
9. **red-team-runner** - Professional Red Team tools (Kali-based)
10. **tor-proxy** - Anonymity for Red Team operations
11. **c2-server** - Command & Control framework (Havoc/Sliver)

### Blue Team Services (4)
12. **elasticsearch** - Log storage and analysis
13. **vector** - Log ingestion pipeline
14. **elastalert** - Real-time detection engine
15. **bot** - Telegram approval bot

### Observability Services (1)
16. **jaeger** - Distributed tracing

---

## Actual Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  API (FastAPI)                                           │   │
│  │  - Authentication (JWT)                                  │   │
│  │  - PolicyEngine enforcement                              │   │
│  │  - Request routing                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT BRAIN LAYER                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ ReasoningEngine  │  │    Planner       │  │ QueryRouter  │ │
│  │ - Direct         │  │ - Multi-step     │  │ - LLM-based  │ │
│  │ - Hypothesis     │  │ - Plan refinement│  │ - Complexity │ │
│  │ - First Principles│ │                  │  │   analysis   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYER                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ PolicyEngine     │  │ InputSanitizer   │  │ RBAC         │ │
│  │ - Hard-coded     │  │ - Pattern block  │  │ - Role check │ │
│  │ - Non-bypassable │  │ - Length limits  │  │ - Viewer     │ │
│  │ - PERMIT/DENY    │  │ - Validation     │  │ - Analyst    │ │
│  │ - APPROVAL       │  │                  │  │ - Admin      │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTION LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RED TEAM                    │  BLUE TEAM                 │  │
│  │  ┌────────────────┐          │  ┌────────────────┐       │  │
│  │  │ Red Team Runner│          │  │ Log Ingestion  │       │  │
│  │  │ - nmap         │          │  │ - Vector       │       │  │
│  │  │ - sqlmap       │          │  │ - Elasticsearch│       │  │
│  │  │ - metasploit   │          │  │ - ElastAlert   │       │  │
│  │  │ - gobuster     │          │  │ - Sigma rules  │       │  │
│  │  └────────────────┘          │  └────────────────┘       │  │
│  │  ┌────────────────┐          │  ┌────────────────┐       │  │
│  │  │ C2 Framework   │          │  │ Mitigation     │       │  │
│  │  │ - Havoc/Sliver │          │  │ - Auto-response│       │  │
│  │  │ - Listeners    │          │  │ - Quarantine   │       │  │
│  │  │ - Payloads     │          │  │ - Block IP     │       │  │
│  │  └────────────────┘          │  └────────────────┘       │  │
│  │  ┌────────────────┐          │                            │  │
│  │  │ Tor Proxy      │          │                            │  │
│  │  │ - Anonymity    │          │                            │  │
│  │  │ - OPSEC        │          │                            │  │
│  │  └────────────────┘          │                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  PostgreSQL  │  │    Redis     │  │   Chroma     │         │
│  │  - Users     │  │  - Celery    │  │  - RAG       │         │
│  │  - Actions   │  │  - Cache     │  │  - Vectors   │         │
│  │  - Scans     │  │  - Sessions  │  │  - MITRE     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Jaeger     │  │  Structlog   │  │  Audit Log   │         │
│  │  - Tracing   │  │  - JSON logs │  │  - HMAC      │         │
│  │  - Flame     │  │  - Structured│  │  - Integrity │         │
│  │    graphs    │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Service Dependencies

```
api → postgres, redis, ollama, chroma, jaeger
worker → postgres, redis, ollama, chroma
runner → socket-proxy
red-team-runner → tor-proxy, socket-proxy
c2-server → (standalone)
elasticsearch → (standalone)
vector → elasticsearch
elastalert → elasticsearch
bot → postgres
```

---

## Network Segmentation (Zero-Trust)

### frontend-net
- api (internet-facing)

### db-net
- postgres
- redis

### ai-net
- ollama
- chroma

### security-net (ISOLATED)
- red-team-runner
- tor-proxy
- c2-server
- socket-proxy
- runner

### obs-net
- jaeger
- elasticsearch
- vector
- elastalert

**Critical**: API has NO access to security-net. Compromised API cannot reach C2 or Red Team tools.

---

## Data Flow Examples

### Red Team Operation
```
User → API → PolicyEngine → Celery Queue → Worker → 
Red Team Runner → nmap/sqlmap → Tor Proxy → Target
```

### Blue Team Detection
```
Sysmon → /api/v1/ingest/logs → Vector → Elasticsearch → 
ElastAlert (Sigma rule match) → /api/v1/ingest/trigger_mitigation → 
Agent → PolicyEngine → Telegram Approval → Execute Mitigation
```

### Agent Reasoning
```
User Query → API → ReasoningEngine (classify complexity) → 
Planner (generate plan) → ReactAgent (execute with PolicyEngine) → 
Tools → Response
```

---

## Resource Requirements

### Minimum
- CPU: 8 cores
- RAM: 16GB
- Disk: 100GB SSD

### Recommended
- CPU: 16 cores
- RAM: 32GB
- Disk: 500GB SSD

### Per-Service Allocation
- ollama: 4-8GB RAM (model-dependent)
- elasticsearch: 2-4GB RAM
- postgres: 1-2GB RAM
- api/worker: 512MB-1GB RAM each
- red-team-runner: 2GB RAM
- Others: 256-512MB RAM each

---

## Deployment Profiles

### Development
```bash
docker-compose up -d
# Core services only
```

### Red Team
```bash
docker-compose --profile red-team up -d
# + red-team-runner, tor-proxy, c2-server
```

### Blue Team
```bash
docker-compose --profile blue-team up -d
# + elasticsearch, vector, elastalert
```

### Full Platform
```bash
docker-compose --profile red-team --profile blue-team up -d
# All 16+ services
```

---

## Scaling Strategy

### Horizontal Scaling
- **worker**: Scale to 5-10 instances
- **red-team-runner**: Scale to 2-3 instances
- **api**: Scale to 2-3 instances behind load balancer

### Vertical Scaling
- **ollama**: Increase RAM for larger models
- **elasticsearch**: Increase disk for log retention
- **postgres**: Increase RAM for query performance

---

## Maintenance

### Daily
- Monitor Jaeger for errors
- Check Elasticsearch disk usage
- Review audit logs

### Weekly
- Update Docker images
- Run security scans (Trivy)
- Review policy denials

### Monthly
- Rotate secrets
- Update Sigma rules
- Review network segmentation

---

## Known Limitations

1. **Complexity**: 20+ services require significant resources
2. **Networking**: Zero-trust segmentation adds complexity
3. **Scaling**: Ollama is single-instance (no horizontal scaling)
4. **Storage**: Elasticsearch logs can grow rapidly

---

## Future Improvements

1. **Kubernetes**: Migrate from docker-compose for production
2. **Service Mesh**: Implement Istio for advanced networking
3. **Multi-Model**: Support multiple LLM backends
4. **Distributed RAG**: Shard Chroma across multiple instances
