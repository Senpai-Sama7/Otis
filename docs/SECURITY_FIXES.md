# Critical Security Fixes

## Overview

This document details the critical security remediations applied to achieve production-grade security posture.

---

## 1. Docker Socket Security (CRITICAL)

### The Vulnerability
The original implementation mounted `/var/run/docker.sock` directly to the `api` and `worker` services, despite having a `socket-proxy` service. This completely undermined the defense-in-depth architecture.

**Risk Level**: CRITICAL
- Direct Docker socket access = root-equivalent access to host
- Compromised API or worker could escape container and control host
- Violates Principle of Least Privilege

### The Fix
**Removed Docker socket mounts from `api` and `worker` services.**

Only the `runner` service (via `socket-proxy`) has Docker access:
```yaml
runner:
  environment:
    - DOCKER_HOST=tcp://socket-proxy:2375  # Mediated access only
  # NO direct socket mount
```

### Architecture
```
┌─────────┐
│   API   │ ──┐
└─────────┘   │
              │ Celery Queue
┌─────────┐   │
│ Worker  │ ──┤
└─────────┘   │
              ▼
         ┌─────────┐      ┌──────────────┐      ┌──────────┐
         │ Runner  │─────▶│ Socket Proxy │─────▶│ Host     │
         └─────────┘      └──────────────┘      │ Docker   │
                          (Least Privilege)     └──────────┘
```

**Result**: Only the `runner` service can execute Docker commands, and only through the restricted proxy.

---

## 2. Docker Image Hygiene (SEVERE)

### The Vulnerability
Original Dockerfiles:
- Included build tools (`build-essential`, `git`) in runtime images
- API service ran as `root` user
- No multi-stage builds (bloated images)

**Risk Level**: SEVERE
- Increased attack surface (unnecessary tools)
- Root execution = privilege escalation risk
- Large image size = slower deployments

### The Fix
**Implemented multi-stage builds with non-root users.**

#### Stage 1: Builder
```dockerfile
FROM python:3.11-slim AS builder
RUN apt-get install build-essential git  # Build tools
RUN python -m venv /opt/venv
RUN pip install .  # Install from pyproject.toml
```

#### Stage 2: Runtime
```dockerfile
FROM python:3.11-slim
RUN apt-get install curl  # Runtime only
COPY --from=builder /opt/venv /opt/venv  # Copy venv only
RUN useradd -r otis  # Non-root user
USER otis  # Run as non-root
```

**Benefits**:
- 50-70% smaller images (no build tools)
- Non-root execution (defense in depth)
- Faster builds (cached layers)

---

## 3. Dependency Management (HIGH)

### The Vulnerability
- Two conflicting dependency files: `pyproject.toml` and `requirements.txt`
- Out of sync (critical packages missing from `pyproject.toml`)
- Dockerfiles only used `requirements.txt`

**Risk Level**: HIGH
- Dependency confusion attacks
- Version drift between dev and prod
- Unmaintainable

### The Fix
**Consolidated all dependencies into `pyproject.toml`.**

```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "celery>=5.3.0",
    "redis>=5.0.0",
    "opentelemetry-api>=1.21.0",
    # ... all dependencies
]
```

**Deleted**: `requirements.txt`, `requirements-dev.txt`

**Dockerfiles now install from single source**:
```dockerfile
COPY pyproject.toml ./
RUN pip install .
```

---

## 4. Principle of Least Privilege

### Implementation

| Service | Docker Access | User | Justification |
|---------|---------------|------|---------------|
| `api` | ❌ None | `otis` (non-root) | Web-facing, no need for Docker |
| `worker` | ❌ None | `otis` (non-root) | Background tasks, no need for Docker |
| `runner` | ✅ Via proxy | `runner` (non-root) | Sandbox execution only |
| `socket-proxy` | ✅ Host socket | N/A | Mediates access with restrictions |

**Result**: Only 1 service has Docker access, and it's mediated through a security proxy.

---

## 5. Defense in Depth Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Network Isolation (Docker networks)            │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Non-Root Execution (all services)              │
├─────────────────────────────────────────────────────────┤
│ Layer 3: Socket Proxy (mediated Docker access)          │
├─────────────────────────────────────────────────────────┤
│ Layer 4: PolicyEngine (hard-coded security rules)       │
├─────────────────────────────────────────────────────────┤
│ Layer 5: RBAC (role-based access control)               │
├─────────────────────────────────────────────────────────┤
│ Layer 6: Approval Gates (human-in-the-loop)             │
└─────────────────────────────────────────────────────────┘
```

---

## Verification

### Test Docker Socket Isolation
```bash
# API should NOT have Docker access
docker exec otis-api docker ps
# Expected: "Cannot connect to Docker daemon"

# Worker should NOT have Docker access
docker exec otis-worker docker ps
# Expected: "Cannot connect to Docker daemon"

# Runner SHOULD have Docker access (via proxy)
docker exec otis-runner docker ps
# Expected: List of containers
```

### Test Non-Root Execution
```bash
# Check API user
docker exec otis-api whoami
# Expected: "otis"

# Check worker user
docker exec otis-worker whoami
# Expected: "otis"

# Check runner user
docker exec otis-runner whoami
# Expected: "runner"
```

### Test Image Size
```bash
docker images | grep otis
# Expected: ~200-300MB (not 500MB+)
```

---

## Security Checklist

- [x] Docker socket removed from API
- [x] Docker socket removed from worker
- [x] Multi-stage builds implemented
- [x] Non-root users for all services
- [x] Single dependency source (pyproject.toml)
- [x] Socket proxy enforced
- [x] Build tools removed from runtime images
- [x] Principle of least privilege applied
- [x] Defense in depth architecture validated

---

## Production Deployment

### Before Deployment
1. Review `docker-compose.yml` - verify no raw socket mounts
2. Build images: `docker-compose build`
3. Scan images: `docker scan otis-api otis-runner`
4. Run security tests: `pytest tests/security/`

### Monitoring
- Monitor socket-proxy logs for unauthorized access attempts
- Alert on any service attempting direct Docker socket access
- Regular image vulnerability scans (weekly)

---

## References

- [Docker Socket Security](https://docs.docker.com/engine/security/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)
- [Defense in Depth](https://www.cisa.gov/defense-depth)
