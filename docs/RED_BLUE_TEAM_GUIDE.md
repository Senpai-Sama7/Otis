# Professional Red/Blue Team Operations Guide

## Overview

Otis is now a professional-grade dual-use platform for Red and Blue team operations, orchestrating battle-tested tools instead of reimplementing them.

---

## Red Team Capabilities

### Professional Tool Orchestration

Otis orchestrates real security tools in isolated containers:

- **nmap** - Network reconnaissance
- **sqlmap** - SQL injection testing
- **gobuster** - Directory/file enumeration
- **Metasploit** - Exploitation framework
- **impacket** - Windows protocol tools
- **proxychains** - Tor routing for anonymity

### Usage Examples

#### 1. Network Reconnaissance

```python
# Agent instruction
"Perform reconnaissance on target 10.0.1.50 using nmap"

# Agent execution
scan_environment(
    module="nmap",
    target="10.0.1.50",
    flags="-sV -sC -p-",
    use_proxy=True  # Route through Tor
)
```

#### 2. Web Application Testing

```python
# Agent instruction
"Test https://target.com/login for SQL injection"

# Agent execution
scan_environment(
    module="sqlmap",
    target="https://target.com/login?id=1",
    flags="--batch --level=3 --risk=2",
    use_proxy=True
)
```

#### 3. Directory Enumeration

```python
# Agent instruction
"Enumerate directories on https://target.com"

# Agent execution
scan_environment(
    module="gobuster",
    target="https://target.com",
    wordlist="/usr/share/wordlists/dirb/big.txt",
    use_proxy=True
)
```

### C2 Framework Integration

#### Create Listener

```python
c2_manager(
    operation="create_listener",
    protocol="https",
    host="0.0.0.0",
    port=443
)
```

#### Generate Payload

```python
c2_manager(
    operation="generate_payload",
    listener_id="listener-123",
    os="windows",
    arch="x64",
    format="exe"
)
```

#### Task Agent

```python
c2_manager(
    operation="task_agent",
    agent_id="agent-456",
    command="whoami /all"
)
```

### Anonymity & OPSEC

All Red Team operations can be routed through Tor:

```bash
# Start with Tor proxy
docker-compose --profile red-team up -d

# All scans with use_proxy=True are routed through Tor
# Source IP is anonymized
```

**Architecture**:
```
Red Team Tool → proxychains → Tor Proxy → Internet
```

---

## Blue Team Capabilities

### Real-Time Detection & Mitigation

#### Log Ingestion Pipeline

```
Security Tools → /api/v1/ingest/logs → Vector → Elasticsearch
                                                      ↓
                                                 ElastAlert
                                                      ↓
                                            Sigma Rule Match
                                                      ↓
                                    /api/v1/ingest/trigger_mitigation
                                                      ↓
                                                 Otis Agent
                                                      ↓
                                            Human Approval (Telegram)
                                                      ↓
                                              Mitigation Executed
```

#### Forward Logs to Otis

```bash
# Sysmon logs
curl -X POST http://otis-api:8000/api/v1/ingest/logs \
  -H "Content-Type: application/json" \
  -d @sysmon-log.json

# Zeek logs
curl -X POST http://otis-api:8000/api/v1/ingest/logs \
  -H "Content-Type: application/json" \
  -d @zeek-conn.json
```

#### Real-Time Mitigation Flow

1. **Detection**: Sigma rule matches in ElastAlert
2. **Alert**: ElastAlert calls `/trigger_mitigation` webhook
3. **Analysis**: Otis agent analyzes threat
4. **Proposal**: Agent proposes mitigation actions
5. **Approval**: Human analyst approves via Telegram
6. **Execution**: Mitigation executed (block IP, quarantine host)

### Example: Ransomware Detection

**Sigma Rule** (`config/elastalert/ransomware_detection.yaml`):
```yaml
filter:
- query:
    query_string:
      query: '(process_name:*powershell* AND command_line:*-enc*) OR (file_extension:*.encrypted)'
```

**When Triggered**:
1. ElastAlert detects ransomware indicators
2. Calls `/trigger_mitigation` with alert data
3. Otis agent receives instruction:
   ```
   URGENT: Mitigate detected threat.
   Alert: Potential Ransomware Activity
   Source IP: 10.0.1.50
   ```
4. Agent proposes:
   ```
   Action: Block host 10.0.1.50 at firewall
   Risk: High
   Rationale: Ransomware activity detected
   ```
5. Analyst approves via Telegram
6. Firewall rule applied

---

## Deployment

### Red Team Deployment

```bash
# Build Red Team image
docker build -f docker/Dockerfile.red-team -t otis-red-team:latest .

# Start Red Team services
docker-compose --profile red-team up -d

# Verify
docker exec otis-red-team-runner nmap --version
```

### Blue Team Deployment

```bash
# Start Blue Team services
docker-compose --profile blue-team up -d

# Verify Elasticsearch
curl http://localhost:9200

# Verify Vector
docker logs otis-vector

# Verify ElastAlert
docker logs otis-elastalert
```

### Full Platform

```bash
# Start everything
docker-compose --profile red-team --profile blue-team up -d
```

---

## Security & Safety

### Red Team Safety

1. **PolicyEngine Enforcement**: All operations require policy approval
2. **Approval Gates**: High-risk operations require human approval
3. **Audit Logging**: All actions logged with distributed tracing
4. **Tor Routing**: Anonymity for operators
5. **Isolated Execution**: Tools run in dedicated containers

### Blue Team Safety

1. **Human-in-the-Loop**: Mitigation requires analyst approval
2. **Risk Assessment**: Agent evaluates mitigation risk
3. **Audit Trail**: All mitigations logged
4. **Rollback**: Failed mitigations can be reverted

---

## Professional Workflows

### Red Team: Penetration Test

```
1. Reconnaissance
   → scan_environment(module="nmap", target="10.0.1.0/24", use_proxy=True)

2. Vulnerability Scanning
   → scan_environment(module="sqlmap", target="https://target.com/login")

3. Exploitation
   → c2_manager(operation="create_listener")
   → c2_manager(operation="generate_payload")
   → [Manual delivery of payload]

4. Post-Exploitation
   → c2_manager(operation="list_agents")
   → c2_manager(operation="task_agent", command="whoami")

5. Reporting
   → Agent generates report from artifacts
```

### Blue Team: Incident Response

```
1. Detection
   → Sigma rule matches in ElastAlert
   → /trigger_mitigation called

2. Analysis
   → Agent analyzes alert data
   → Queries threat intelligence
   → Assesses risk

3. Containment
   → Agent proposes: "Block source IP"
   → Analyst approves via Telegram
   → Firewall rule applied

4. Eradication
   → Agent proposes: "Quarantine host"
   → Analyst approves
   → Host isolated

5. Recovery
   → Agent proposes: "Restore from backup"
   → Analyst approves
   → System restored

6. Lessons Learned
   → Agent generates incident report
   → Updates detection rules
```

---

## Configuration

### Red Team Config

```bash
# .env
C2_API_URL=http://c2-server:40056
C2_API_TOKEN=your-c2-token
TOR_PROXY_HOST=tor-proxy
TOR_PROXY_PORT=9050
```

### Blue Team Config

```bash
# .env
ELASTICSEARCH_URL=http://elasticsearch:9200
VECTOR_CONFIG=/config/vector.toml
ELASTALERT_CONFIG=/config/elastalert.yaml
```

---

## Compliance

### Red Team

- ✅ Authorization required before operations
- ✅ Scope limitations enforced by PolicyEngine
- ✅ Audit trail for all actions
- ✅ Anonymity for operators (Tor)

### Blue Team

- ✅ NIST Cybersecurity Framework alignment
- ✅ MITRE ATT&CK mapping
- ✅ Sigma rule library
- ✅ Human-in-the-loop for critical actions

---

## Support

- Red Team Operations: redteam@otis.local
- Blue Team Operations: blueteam@otis.local
- Security Incidents: ir@otis.local
