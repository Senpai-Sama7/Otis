# Zero-Trust Network Architecture

## Critical Security Fix

**Problem**: Flat network (`otis-network`) allows any compromised service to access all others, including C2 server, databases, and Red Team tools.

**Solution**: Network segmentation with least-privilege access.

---

## Network Segments

### 1. frontend-net (Internet-Facing)
**Purpose**: Public-facing services
**Services**: `api`
**Access**: Internet → API only

### 2. db-net (Data Layer)
**Purpose**: Database and cache services
**Services**: `postgres`, `redis`
**Access**: Internal only, no internet

### 3. ai-net (AI Services)
**Purpose**: LLM and vector store
**Services**: `ollama`, `chroma`
**Access**: Internal only, no internet

### 4. security-net (Red Team Operations)
**Purpose**: Isolated security tools
**Services**: `red-team-runner`, `tor-proxy`, `c2-server`, `socket-proxy`, `runner`
**Access**: Completely isolated from API

### 5. obs-net (Observability)
**Purpose**: Monitoring and logging
**Services**: `jaeger`, `elasticsearch`, `vector`, `elastalert`
**Access**: Internal only

---

## Service Network Assignments

| Service | frontend-net | db-net | ai-net | security-net | obs-net |
|---------|--------------|--------|--------|--------------|---------|
| **api** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **worker** | ❌ | ✅ | ✅ | ❌ | ✅ |
| **postgres** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **redis** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **ollama** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **chroma** | ❌ | ❌ | ✅ | ❌ | ❌ |
| **runner** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **socket-proxy** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **red-team-runner** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **tor-proxy** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **c2-server** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **jaeger** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **elasticsearch** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **vector** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **elastalert** | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Security Benefits

### 1. API Compromise Containment
**Before**: API compromise → access to C2 server, Red Team tools, databases
**After**: API compromise → NO access to security-net (C2, Red Team tools isolated)

### 2. Database Isolation
**Before**: Any service can access postgres
**After**: Only services on db-net can access postgres

### 3. Red Team Isolation
**Before**: Compromised API can control Red Team tools
**After**: Red Team tools completely isolated in security-net

### 4. Defense in Depth
Multiple network boundaries must be breached to reach critical assets.

---

## Attack Surface Reduction

```
BEFORE (Flat Network):
┌─────────────────────────────────────────┐
│         otis-network (flat)             │
│  ┌─────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐  │
│  │ API │─│ DB │─│ C2 │─│Red │─│Tor │  │
│  └─────┘ └────┘ └────┘ └────┘ └────┘  │
│    ALL services can talk to ALL others  │
└─────────────────────────────────────────┘

AFTER (Segmented):
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ frontend-net │  │  db-net  │  │ security-net │
│   ┌─────┐    │  │ ┌────┐   │  │ ┌────┐ ┌───┐ │
│   │ API │────┼──┼─│ DB │   │  │ │ C2 │ │Red│ │
│   └─────┘    │  │ └────┘   │  │ └────┘ └───┘ │
└──────────────┘  └──────────┘  └──────────────┘
     ↓                ↓                ↓
  Internet      Internal Only    Isolated
```

---

## Implementation

### Update docker-compose.yml

```yaml
networks:
  frontend-net:
    driver: bridge
    internal: false
  
  db-net:
    driver: bridge
    internal: true
  
  ai-net:
    driver: bridge
    internal: true
  
  security-net:
    driver: bridge
    internal: true
  
  obs-net:
    driver: bridge
    internal: true

services:
  api:
    networks:
      - frontend-net
      - db-net
      - ai-net
      - obs-net
      # NO security-net access
  
  red-team-runner:
    networks:
      - security-net
      - obs-net
      # NO frontend-net, db-net, or ai-net access
```

### Verification

```bash
# API should NOT reach C2 server
docker exec otis-api ping c2-server
# Expected: Network unreachable

# API SHOULD reach postgres
docker exec otis-api ping postgres
# Expected: Success

# Red Team runner should NOT reach API
docker exec otis-red-team-runner ping api
# Expected: Network unreachable
```

---

## Compliance

- ✅ NIST SP 800-207 (Zero Trust Architecture)
- ✅ PCI DSS Requirement 1.3 (Network Segmentation)
- ✅ CIS Controls 12 (Network Infrastructure Management)
- ✅ Defense in Depth principle

---

## Migration Guide

1. **Backup**: Export all data before migration
2. **Update**: Apply network changes to docker-compose.yml
3. **Test**: Verify service connectivity
4. **Deploy**: Restart all services
5. **Validate**: Run security tests

```bash
# Apply changes
docker-compose down
docker-compose up -d

# Verify segmentation
./scripts/verify-network-segmentation.sh
```
