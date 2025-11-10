# Otis Security and Safety Policy

## Overview

Otis implements **defense-in-depth** with multiple security layers to ensure safe autonomous operation while maintaining human oversight for critical decisions.

This security policy covers both the cybersecurity AI agent and the **anti-spam AI system** with its specialized red/blue team security framework that includes:
- Proactive adversarial testing (Red Team)
- Real-time threat detection and remediation (Blue Team) 
- NIST AI Risk Management Framework compliance
- Advanced model hardening against adversarial attacks This includes both the cybersecurity agent functionality and the anti-spam AI system with comprehensive red/blue team security testing.

## Security Architecture

### Multi-Layer Defense

1. **PolicyEngine (Primary Control Layer)**
   - RBAC with 3 roles: Viewer (read-only), Analyst (active scan), Admin (full access)
   - Risk-based approval gates: Low (auto), Medium/High/Critical (human approval)
   - Target restrictions: Blocks RFC1918 private IPs, localhost, cloud metadata endpoints
   - Mode-based controls: Passive (read-only) vs Active (write operations)

2. **InputSanitizer (Input Validation Layer)**
   - Blocks command injection: `; && || | $() `` eval exec`
   - Blocks SQL injection: `' OR 1=1 UNION SELECT DROP`
   - Blocks XSS: `<script> javascript: onerror=`
   - Blocks code execution: `import os subprocess __import__`
   - Blocks sensitive files: `/etc/passwd /etc/shadow ~/.ssh`

3. **Zero-Trust Network Segmentation**
   - `frontend-net`: API, web UI (public-facing)
   - `db-net`: PostgreSQL, Redis (data layer)
   - `ai-net`: Ollama, Chroma (AI services)
   - `security-net`: C2 server, Red Team tools (isolated)
   - `obs-net`: Jaeger, Prometheus (monitoring)

4. **Docker Sandbox Hardening**
   - `security_opt: no-new-privileges`
   - `cap_drop: ALL` (no Linux capabilities)
   - Read-only root filesystem
   - No Docker socket access (API/worker isolated)
   - Memory and CPU limits enforced

5. **Audit Logging**
   - All actions logged with HMAC integrity
   - Immutable timestamps
   - Full audit trail in `data/audit.log`

## Risk Levels

### Low Risk (Auto-Approved)
- Read-only operations
- Logging and monitoring
- Database queries (read-only)
- Status checks
- Passive network scanning

**Examples:**
- `scan_environment(duration=10)` in passive mode
- `query_threat_intel("SQL injection")`
- Reading system logs

### Medium Risk (Requires Approval)
- Active network scanning
- Non-destructive configuration changes
- Network configuration updates

**Examples:**
- Active port scanning with service detection
- Updating firewall rules (non-destructive)
- Installing monitoring agents

### High Risk (Requires Approval + Enhanced Review)
- Code execution
- System patches
- Configuration modifications
- Deployment operations

**Examples:**
- Applying security patches
- Modifying application configuration
- Executing custom scripts

### Critical Risk (Requires Approval + Executive Review)
- System-level changes
- Data deletion
- Offensive operations
- Privilege escalation
- Wireless attacks

**Examples:**
- Deleting files or databases
- Kernel modifications
- Exploit attempts
- Traffic disruption

## Approval Workflow

1. **Request Generation**
   ```python
   propose_action(
       code="apt-get update && apt-get upgrade security-pkg",
       risk="high",
       rationale="Critical CVE-2024-XXXX requires immediate patching"
   )
   ```

2. **Telegram Notification**
   - Admin receives notification with:
     - Action description
     - Risk level
     - Proposed code
     - Rationale
   - Two buttons: ✅ Approve | ❌ Deny

3. **Approval Decision**
   - **Approved**: Code executes in sandbox with appropriate permissions
   - **Denied**: Action logged and rejected
   - **Timeout**: Action expires after 5 minutes

4. **Execution**
   - Code runs in isolated Docker container
   - Results logged and returned
   - Audit trail maintained

## Denylist Rules

The following operations are **blocked by default**:

- Wireless injection: `aircrack`, `aireplay`, `airodump`
- Traffic disruption: `ddos`, `dos attack`
- Privilege escalation: `exploit kernel`, `privilege escalation`
- Dangerous commands: `rm -rf /`, `dd if=/dev/zero`, `:(){ :|:& };:`
- Privileged Docker flags: `--privileged`, `--cap-add`

## Allowlist Rules

The following operations are **permitted** (subject to risk level):

- Port scanning: `nmap -sT`, `port scan`
- Vulnerability scanning: `vulnerability scan`
- Log analysis: `log analysis`
- Read operations: `read file`, `check status`

## Sandbox Security

### Container Constraints

```yaml
Security Settings:
  - read_only: true          # Read-only root filesystem
  - network_mode: none       # Network disabled by default
  - mem_limit: 512m          # Memory limit
  - cpu_limit: 1.0           # CPU limit
  - tmpfs: /tmp (100M)       # Temporary filesystem
  - no_new_privileges: true  # Prevent privilege escalation
  - remove: true             # Auto-remove after execution
```

### Allowed After Approval

- `network_mode: host` - Enabled only after explicit approval
- Custom resource limits - Based on action requirements

## Data Protection

### Sensitive Data Handling

1. **Secrets Management**
   - Never log secrets or tokens
   - Use environment variables for sensitive data
   - Secrets stored in `.env` (never committed)

2. **Audit Logging**
   - All actions logged to `data/audit.log`
   - HMAC integrity verification
   - Immutable timestamps
   - No PII in logs (anonymized)

### Data Storage

```
data/
├── chroma/           # Vector database (persistent)
├── logs/             # Application logs (rotating)
├── audit.log         # Audit trail (HMAC protected)
└── pending.json      # Pending approval requests
```

## Threat Intelligence

### Sources

- **MITRE ATT&CK**: Attack patterns and techniques
- **NIST CSF**: Cybersecurity framework
- **OWASP Top 10**: Web security vulnerabilities

### RAG Security

- Embeddings generated locally (all-MiniLM-L6-v2)
- Vector database persisted to `./data/chroma`
- No external API calls for embeddings
- Read-only access during queries

## Monitoring and Alerts

### Health Checks

```bash
# API Health
curl http://localhost:8000/api/v1/health

# Service Status
curl http://localhost:8000/api/v1/health | jq '.services'
```

### Alerts

- Failed approval requests → Telegram admin
- Security policy violations → Email + Telegram
- Sandbox escapes → Immediate shutdown + alert
- Audit log tampering → Integrity check failure

## Incident Response

### Security Incident Procedure

1. **Detection**
   - Monitoring alerts trigger
   - Audit log analysis identifies anomaly
   - User reports suspicious behavior

2. **Containment**
   - Automatically shutdown affected services
   - Isolate compromised containers
   - Block network access if needed

3. **Investigation**
   - Review audit logs
   - Analyze approval decisions
   - Check sandbox execution logs

4. **Recovery**
   - Restore from known-good state
   - Apply security patches
   - Update denylist rules

5. **Post-Incident**
   - Document incident
   - Update security policies
   - Improve detection rules

## Anti-Spam AI Security Controls

### Adversarial Attack Prevention

The anti-spam AI system implements multiple layers of protection against adversarial attacks:

**Red Team (Offensive Testing)**:
- **Character Obfuscation Defense**: Detection of visually similar Unicode characters (e.g., ASCII 'a' vs Cyrillic 'а')
- **Semantic Shift Detection**: Identification of paraphrased spam content
- **Prompt Injection Prevention**: Blocking system directive insertion
- **Encoding Evasion Detection**: Finding URL encoding, HTML entities, Unicode escaping
- **Multilingual Mixing Detection**: Identifying suspicious language combinations
- **Homograph Substitution Prevention**: Blocking mathematical symbol lookalikes

**Blue Team (Defensive Protection)**:
- **Pre-Inference Validation**: Text analysis before model processing
- **Post-Inference Verification**: Analysis of model confidence anomalies
- **Automated Remediation**: Tiered responses based on threat severity
- **Real-time Monitoring**: Continuous threat pattern detection

### Threat Detection Policies

**Critical Threats** (Immediate Action Required):
- Homograph characters in text (mathematical symbols, lookalikes)
- Prompt injection patterns (system directives, ignore instructions)
- Encoding anomalies (URL encoding, HTML entities in unexpected contexts)

**High Threats** (Review Required):
- Script mixing (Cyrillic + Latin combinations)
- Multiple encoding schemes in single text
- Confidence anomalies (unusually low/high model confidence)

**Medium Threats** (Monitoring):
- Semantic shifts in known spam patterns
- Multilingual content mixing
- Suspicious language patterns

### Model Hardening

**Input Validation**:
- Character normalization (Unicode to ASCII where appropriate)
- Encoding detection and decoding
- Pattern recognition for adversarial indicators

**Output Validation**:
- Confidence threshold enforcement
- Anomaly detection in prediction patterns
- Consistency checks across similar inputs

## Best Practices

### For Administrators

1. **Review Approvals Carefully**
   - Read the full proposed code
   - Verify the rationale makes sense
   - Check risk level is appropriate
   - When in doubt, deny and investigate

2. **Monitor Audit Logs**
   ```bash
   tail -f data/audit.log | jq
   ```

3. **Regular Security Updates**
   - Update Ollama models regularly
   - Keep Docker images patched
   - Review and update denylist rules
   - Update anti-spam model with new adversarial patterns

4. **Backup Critical Data**
   - Database backups (daily)
   - RAG index backups (weekly)
   - Anti-spam model checkpoints (weekly)
   - Audit logs (archived monthly)

### For Developers

1. **Follow Principle of Least Privilege**
   - Request minimum necessary permissions
   - Use passive mode when possible
   - Provide clear rationale for high-risk operations

2. **Test in Sandbox First**
   - Always test code in isolated environment
   - Verify resource limits are sufficient
   - Check for security violations
   - Run adversarial tests before deployment

3. **Document Security Decisions**
   - Explain why specific permissions needed
   - Document risk assessment
   - Include mitigation strategies

## Compliance

### Standards Alignment

- **NIST Cybersecurity Framework**: Identify, Protect, Detect, Respond, Recover
- **OWASP Top 10**: Web application security
- **MITRE ATT&CK**: Threat detection and response
- **NIST AI Risk Management Framework**: AI-specific risk management
- **SOC 2**: Security controls for service organizations

### Audit Requirements

- Audit logs retained for 90 days minimum
- HMAC integrity verification on all logs
- Regular security assessments (quarterly)
- Red team penetration testing (annually)
- Model bias and fairness audits (bi-annually)

## Emergency Contacts

### Security Team

- **Security Lead**: security@otis.local
- **Incident Response**: incident@otis.local
- **Adversarial Incident Response**: anti-spam-incident@otis.local
- **24/7 Hotline**: +1-XXX-XXX-XXXX

### Escalation

1. User → Telegram Admin
2. Admin → Security Lead  
3. Security Lead → CISO
4. CISO → Executive Team

## Updates and Revisions

This policy is reviewed and updated quarterly or after security incidents, with special attention to emerging adversarial attack techniques.

**Last Updated**: 2025-10-25  
**Version**: 1.0  
**Next Review**: 2026-01-25

## Questions and Feedback

For questions about this policy:
- Open an issue: https://github.com/Senpai-Sama7/Otis/issues
- Email: security@otis.local
- Documentation: https://github.com/Senpai-Sama7/Otis/wiki
