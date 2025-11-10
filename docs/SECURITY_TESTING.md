# Security Testing Guide

## Automated Security Scanning

Otis implements comprehensive automated security scanning in CI/CD.

### Scanning Tools

#### 1. Dependency Vulnerability Scanning
- **Safety**: Checks Python dependencies against known CVE database
- **pip-audit**: Audits Python packages for security vulnerabilities
- **Frequency**: On every push and weekly

```bash
# Run locally
pip install safety pip-audit
safety check
pip-audit
```

#### 2. Secret Scanning
- **TruffleHog**: Scans git history for leaked secrets
- **Frequency**: On every push and PR

```bash
# Run locally
docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest filesystem /repo
```

#### 3. Static Application Security Testing (SAST)
- **Bandit**: Python security linter
- **Ruff**: Security-focused linting rules
- **Frequency**: On every push

```bash
# Run locally
pip install bandit[toml] ruff
bandit -r src/
ruff check src/ --select S
```

#### 4. Docker Image Scanning
- **Trivy**: Container vulnerability scanner
- **Frequency**: On every push and weekly

```bash
# Run locally
docker build -f docker/Dockerfile.api -t otis-api:test .
trivy image otis-api:test
```

#### 5. Security Policy Validation
- **Custom checks**: Validates security architecture
- **Checks**:
  - No unauthorized Docker socket mounts
  - All Dockerfiles use non-root users
  - No hardcoded secrets

```bash
# Run locally
./scripts/security-check.sh
```

---

## Input Sanitization Testing

### Test Dangerous Patterns

```python
from src.core.sanitization import InputSanitizer
import pytest

# Test command injection
with pytest.raises(ValueError):
    InputSanitizer.sanitize_query("rm -rf /")

# Test SQL injection
with pytest.raises(ValueError):
    InputSanitizer.sanitize_query("'; DROP TABLE users; --")

# Test XSS
with pytest.raises(ValueError):
    InputSanitizer.sanitize_query("<script>alert('xss')</script>")

# Test code execution
with pytest.raises(ValueError):
    InputSanitizer.sanitize_code("import os; os.system('ls')")
```

### Sanitization Layers

```
┌─────────────────────────────────────────┐
│ Layer 1: Pydantic Schema Validation    │
├─────────────────────────────────────────┤
│ Layer 2: InputSanitizer.sanitize_*()   │
├─────────────────────────────────────────┤
│ Layer 3: PolicyEngine.validate()       │
├─────────────────────────────────────────┤
│ Layer 4: Docker Sandbox Isolation      │
└─────────────────────────────────────────┘
```

---

## Distributed Tracing for Security

### View Security Events in Jaeger

```bash
# Start Jaeger
docker-compose up -d jaeger

# Access UI
open http://localhost:16686

# Search for security events
# Service: Otis
# Tags: policy.decision=DENY, sanitizer.dangerous_pattern
```

### Trace Security Flow

```
agent.run_agent (parent span)
├── sanitizer.sanitize_query (input validation)
├── policy.validate (policy enforcement)
│   ├── policy.check_rbac
│   ├── policy.check_risk
│   └── policy.check_target
└── tool.execute (if permitted)
```

---

## Security Test Suite

### Run Security Tests

```bash
# All security tests
pytest tests/security/ -v

# Input sanitization tests
pytest tests/unit/test_sanitization.py -v

# Policy engine tests
pytest tests/unit/test_policy_engine.py -v

# Integration security tests
pytest tests/integration/test_security_flow.py -v
```

### Test Coverage

```bash
pytest --cov=src.core.sanitization --cov=src.security --cov-report=html
open htmlcov/index.html
```

---

## Manual Security Testing

### 1. Test Input Sanitization

```bash
# Test dangerous query
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"instruction": "rm -rf /"}'

# Expected: 400 Bad Request - "Invalid input: Query contains potentially dangerous content"
```

### 2. Test Policy Enforcement

```bash
# Test as viewer (should be denied)
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d '{"instruction": "Execute code: print(1)"}'

# Expected: Policy denied
```

### 3. Test Docker Socket Isolation

```bash
# API should NOT have Docker access
docker exec otis-api docker ps
# Expected: "Cannot connect to Docker daemon"

# Runner SHOULD have Docker access (via proxy)
docker exec otis-runner docker ps
# Expected: List of containers
```

### 4. Test Sandbox Hardening

```bash
# Test privilege escalation (should fail)
curl -X POST http://localhost:8000/api/v1/sandbox/execute \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"code": "import os; os.setuid(0)", "language": "python"}'

# Expected: Permission denied (no-new-privileges)
```

---

## Security Monitoring

### Metrics to Monitor

1. **Policy Denials**: Track DENY decisions
2. **Sanitization Blocks**: Track dangerous pattern detections
3. **Failed Authentication**: Track auth failures
4. **Sandbox Escapes**: Monitor for container breakouts (should be zero)

### Alerting Rules

```yaml
# Example Prometheus alerts
- alert: HighPolicyDenialRate
  expr: rate(policy_denials_total[5m]) > 10
  annotations:
    summary: "High rate of policy denials detected"

- alert: SanitizationBlockDetected
  expr: sanitizer_blocks_total > 0
  annotations:
    summary: "Dangerous input pattern detected"
```

---

## Compliance

### NIST SP 800-190 (Container Security)

- ✅ Image vulnerabilities scanned (Trivy)
- ✅ Registry security (private registry recommended)
- ✅ Orchestrator security (Docker socket proxy)
- ✅ Container runtime security (read-only, no-new-privileges)
- ✅ Host OS security (non-root users)

### OWASP Top 10

- ✅ A01: Broken Access Control (PolicyEngine + RBAC)
- ✅ A02: Cryptographic Failures (JWT, Argon2)
- ✅ A03: Injection (InputSanitizer)
- ✅ A04: Insecure Design (Defense-in-depth)
- ✅ A05: Security Misconfiguration (Hardened defaults)
- ✅ A06: Vulnerable Components (Dependency scanning)
- ✅ A07: Authentication Failures (JWT + rate limiting)
- ✅ A08: Software Integrity (Image scanning)
- ✅ A09: Logging Failures (Structured logging + tracing)
- ✅ A10: SSRF (Network isolation)

---

## Incident Response

### Security Incident Checklist

1. **Detect**: Monitor logs and traces for anomalies
2. **Contain**: Isolate affected services
3. **Investigate**: Review Jaeger traces and audit logs
4. **Remediate**: Apply patches, update policies
5. **Document**: Record incident details
6. **Review**: Update security controls

### Emergency Contacts

- Security Team: security@otis.local
- On-Call: oncall@otis.local
- Incident Response: ir@otis.local
