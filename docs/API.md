# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require authentication via JWT Bearer token.

### Register a New User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "analyst1",
  "email": "analyst@example.com",
  "password": "securepass123",
  "role": "analyst"
}
```

**Response (201)**:
```json
{
  "id": 1,
  "username": "analyst1",
  "email": "analyst@example.com",
  "role": "analyst",
  "is_active": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "analyst1",
  "password": "securepass123"
}
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Health & Status

### Health Check
```http
GET /health
```

**Response (200)**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-20T10:00:00Z",
  "services": {
    "ollama": "healthy",
    "chroma": "healthy",
    "docker": "healthy",
    "telegram": "not_configured",
    "database": "healthy"
  }
}
```

### Root Endpoint
```http
GET /
```

**Response (200)**:
```json
{
  "name": "Otis Cybersecurity AI Agent",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs"
}
```

## Agent Operations

All agent endpoints require authentication. Use `Authorization: Bearer <token>` header.

### Environment Scan
Scan a target for security issues.

**Requires**: Analyst role or higher

```http
POST /agent/scan
Authorization: Bearer <token>
Content-Type: application/json

{
  "scan_type": "ports",
  "target": "localhost",
  "options": {
    "port_range": "1-1024"
  }
}
```

**Scan Types**:
- `ports`: Port scanning
- `services`: Service detection
- `vulnerabilities`: Vulnerability scanning
- `config`: Configuration audit

**Response (200)**:
```json
{
  "id": 1,
  "scan_type": "ports",
  "target": "localhost",
  "findings": "[{\"port\": 80, \"status\": \"open\"}, ...]",
  "vulnerabilities_count": 3,
  "risk_score": 0.3,
  "created_at": "2024-01-20T10:05:00Z"
}
```

### Query Threat Intelligence
Query the cybersecurity knowledge base using natural language.

**Requires**: Any authenticated user

```http
POST /agent/threat-intel
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "SQL injection attack patterns",
  "sources": ["MITRE", "OWASP"],
  "limit": 5
}
```

**Sources** (optional):
- `MITRE`: MITRE ATT&CK framework
- `NIST`: NIST Cybersecurity Framework
- `OWASP`: OWASP Top 10

**Response (200)**:
```json
{
  "query": "SQL injection attack patterns",
  "results": [
    {
      "content": "Injection: Application is vulnerable to injection attacks...",
      "source": "OWASP",
      "category": "vulnerability",
      "relevance_score": 0.92,
      "external_id": "A03:2021",
      "name": "Injection"
    }
  ],
  "sources_searched": ["MITRE", "OWASP"]
}
```

### Propose Action
Propose a security action for approval.

**Requires**: Analyst role or higher

```http
POST /agent/propose-action
Authorization: Bearer <token>
Content-Type: application/json

{
  "action_type": "patch",
  "description": "Apply security patch for CVE-2024-XXXX",
  "reasoning": "Critical vulnerability requires immediate patching to prevent exploitation",
  "risk_level": "high",
  "proposed_code": "apt-get update && apt-get upgrade package-name"
}
```

**Risk Levels**:
- `low`: Minimal impact
- `medium`: Moderate impact
- `high`: Significant impact
- `critical`: Business-critical action

**Response (200)**:
```json
{
  "id": 1,
  "action_type": "patch",
  "description": "Apply security patch for CVE-2024-XXXX",
  "reasoning": "Critical vulnerability requires immediate patching...",
  "risk_level": "high",
  "status": "pending",
  "created_at": "2024-01-20T10:10:00Z",
  "execution_result": null
}
```

### Execute Code
Execute code in a sandboxed Docker container.

**Requires**: Analyst role or higher

```http
POST /agent/execute-code
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "print('Hello from sandbox')",
  "language": "python"
}
```

**Languages**:
- `python`: Python 3.11
- `bash`: Bash shell

**Response (200)**:
```json
{
  "success": true,
  "output": "Hello from sandbox\n"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "error": "Execution timeout after 60 seconds"
}
```

### LLM Analysis
Analyze security issues using the AI model.

**Requires**: Any authenticated user

```http
POST /agent/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Analyze this log entry for security issues: [ERROR] Unauthorized access attempt from 192.168.1.100",
  "context": "System: Ubuntu 22.04, Service: Apache Web Server"
}
```

**Response (200)**:
```json
{
  "analysis": "The log entry indicates a potential security incident...\n\nThought: This appears to be an unauthorized access attempt.\n\nAction: I should check if this IP is part of a known threat database.\n\nObservation: The IP 192.168.1.100 is a private network address...\n\nAnswer: This is likely an internal probing attempt. Recommend:\n1. Review firewall rules\n2. Check authentication logs\n3. Verify the source system..."
}
```

## Error Responses

### 400 Bad Request
Invalid request parameters.
```json
{
  "detail": "Invalid scan type"
}
```

### 401 Unauthorized
Missing or invalid authentication token.
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
Insufficient permissions.
```json
{
  "detail": "Required role: analyst"
}
```

### 404 Not Found
Resource not found.
```json
{
  "detail": "Not Found"
}
```

### 500 Internal Server Error
Server error.
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently not implemented. Consider adding rate limiting in production:
- 100 requests per minute per user
- 1000 requests per hour per user

## Pagination

List endpoints support pagination (when applicable):
```http
GET /endpoint?page=1&per_page=20
```

**Parameters**:
- `page`: Page number (starts at 1)
- `per_page`: Items per page (max 100)

## Filtering

Some endpoints support filtering:
```http
GET /endpoint?status=pending&risk_level=high
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Code Examples

### Python
```python
import httpx

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = httpx.post(
    f"{BASE_URL}/auth/login",
    json={"username": "analyst1", "password": "securepass123"}
)
token = response.json()["access_token"]

# Query threat intel
headers = {"Authorization": f"Bearer {token}"}
response = httpx.post(
    f"{BASE_URL}/agent/threat-intel",
    headers=headers,
    json={
        "query": "ransomware defense strategies",
        "limit": 5
    }
)
results = response.json()
```

### cURL
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst1","password":"securepass123"}' \
  | jq -r '.access_token')

# Scan environment
curl -X POST http://localhost:8000/api/v1/agent/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_type": "ports",
    "target": "localhost",
    "options": {"port_range": "1-1024"}
  }'
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function main() {
  // Login
  const loginResponse = await axios.post(`${BASE_URL}/auth/login`, {
    username: 'analyst1',
    password: 'securepass123'
  });
  const token = loginResponse.data.access_token;

  // Analyze with LLM
  const analysisResponse = await axios.post(
    `${BASE_URL}/agent/analyze`,
    {
      prompt: 'What are common indicators of a SQL injection attack?',
      context: 'Web application security audit'
    },
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  console.log(analysisResponse.data.analysis);
}

main();
```

## WebSocket Support

Coming soon: Real-time streaming of LLM responses and scan results.

## Versioning

API is currently at version v1. Future versions will be available at:
- `/api/v2`
- `/api/v3`

Legacy versions will be maintained for backward compatibility.
