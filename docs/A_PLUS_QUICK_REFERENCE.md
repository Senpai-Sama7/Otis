# A+ Features Quick Reference

## 🔒 PolicyEngine

### Import
```python
from src.security.policy_engine import PolicyEngine, PolicyDecision
```

### Usage
```python
# Initialize with user and request
engine = PolicyEngine(user=current_user, request=agent_request)

# Validate tool execution
decision = engine.validate(tool_name="scan_environment", tool_params={"target": "localhost"})

# Handle decision
if decision == PolicyDecision.PERMIT:
    result = await tool.execute(**params)
elif decision == PolicyDecision.REQUIRES_APPROVAL:
    await request_approval(tool_name, params)
elif decision == PolicyDecision.DENY:
    reason = engine.get_denial_reason(tool_name, params)
    return {"error": reason}
```

### Policy Decisions
- `PERMIT`: Execute immediately
- `DENY`: Block execution, log denial
- `REQUIRES_APPROVAL`: Route to approval workflow

### Sensitive Networks
```python
SENSITIVE_NETWORKS = [
    "10.0.1.",      # Production subnet
    "192.168.1.",   # Management network
    "172.16.",      # Internal services
    "prod-",        # Production hosts
    "production",   # Production systems
]
```

---

## 🤖 Query Router

### Import
```python
from src.reasoning.query_router import QueryRouter
```

### Usage
```python
# Initialize with LLM client
router = QueryRouter(ollama_client=ollama_client)

# Classify query
classification = await router.classify(query="Analyze APT attack vectors")

# Get recommended strategy
strategy = router.get_strategy_from_classification(classification)

# classification.complexity: "SIMPLE" | "MODERATE" | "COMPLEX"
# classification.recommended_strategy: "zero_shot" | "darwin_godel" | "absolute_zero"
```

### Complexity Mapping
- **SIMPLE** → Zero-shot reasoning (direct answer)
- **MODERATE** → Darwin-Gödel engine (evolutionary optimization)
- **COMPLEX** → Absolute Zero reasoner (first-principles)

---

## 📋 Planner

### Import
```python
from src.reasoning.planner import Planner
```

### Usage
```python
# Initialize with LLM client and tools
planner = Planner(ollama_client=ollama_client, available_tools=tools)

# Create plan
plan = await planner.create_plan(goal="Analyze and patch SQL injection")

# Execute plan steps
for step in plan.steps:
    tool_name = step["tool"]
    params = step["params"]
    reasoning = step["reasoning"]
    
    # Validate with PolicyEngine
    decision = policy_engine.validate(tool_name, params)
    
    # Execute if permitted
    if decision == PolicyDecision.PERMIT:
        result = await tools[tool_name].execute(**params)

# Refine plan based on observations
refined_plan = await planner.refine_plan(plan, completed_steps, observations)
```

### Plan Structure
```python
{
    "goal": "Overall objective",
    "steps": [
        {"tool": "tool_name", "params": {...}, "reasoning": "why"},
        ...
    ],
    "estimated_complexity": 0.75,
    "reasoning": "Plan explanation"
}
```

---

## 🔄 Celery Tasks

### Import
```python
from src.tasks import run_sandbox_task, scan_environment_task, query_threat_intel_task
```

### Usage
```python
# Enqueue task (non-blocking)
task = run_sandbox_task.delay(code="print('hello')", language="python", timeout=60)

# Check status
if task.ready():
    result = task.get()
    print(result)  # {"success": True, "output": "hello\n"}

# Wait for result (blocking)
result = task.get(timeout=120)

# Get task ID
task_id = task.id
```

### Available Tasks
- `run_sandbox_task(code, language, timeout)` - Execute code in sandbox
- `scan_environment_task(target, scan_type, duration)` - Run security scan
- `query_threat_intel_task(query, k)` - Query threat intelligence

### Celery CLI
```bash
# Start worker
celery -A src.tasks worker --loglevel=info --concurrency=4

# Monitor tasks
celery -A src.tasks inspect active
celery -A src.tasks inspect stats

# Purge queue
celery -A src.tasks purge
```

---

## 📊 Distributed Tracing

### Import
```python
from src.core.tracing import (
    trace_agent_execution,
    trace_tool_execution,
    trace_policy_validation,
    trace_llm_call,
)
```

### Usage
```python
# Trace agent execution
@trace_agent_execution
async def run_agent(request: AgentRequest):
    # Automatically creates parent span
    ...

# Trace tool execution
@trace_tool_execution("scan_environment")
async def execute(target: str):
    # Creates child span
    ...

# Trace policy validation
@trace_policy_validation
def validate(tool_name: str, tool_params: dict):
    # Creates child span
    ...

# Trace LLM calls
@trace_llm_call
async def generate(prompt: str):
    # Creates child span with prompt metadata
    ...
```

### Jaeger UI
```bash
# Access Jaeger UI
open http://localhost:16686

# Search for traces
# - Service: "Otis"
# - Operation: "agent.run_agent"
# - Tags: tool.name, policy.decision, llm.prompt_length
```

---

## 🧪 Testing

### PolicyEngine Tests
```bash
pytest tests/unit/test_policy_engine.py -v

# Specific test classes
pytest tests/unit/test_policy_engine.py::TestRBAC -v
pytest tests/unit/test_policy_engine.py::TestPromptInjectionImmunity -v
```

### Planner Tests
```bash
pytest tests/unit/test_planner.py -v
```

### Query Router Tests
```bash
pytest tests/unit/test_query_router.py -v
```

### Celery Task Tests
```bash
# Start Redis first
docker-compose up -d redis

# Run tests
pytest tests/integration/test_celery_tasks.py -v
```

---

## 🐳 Docker Compose

### Start Services
```bash
# All services
docker-compose up -d

# With workers
docker-compose --profile with-worker up -d

# With Telegram bot
docker-compose --profile with-bot up -d

# Scale workers
docker-compose up -d --scale worker=5
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f jaeger
```

### Service Ports
- **API**: 8000
- **Postgres**: 5432
- **Redis**: 6379
- **Ollama**: 11434
- **Chroma**: 8001
- **Jaeger UI**: 16686
- **Jaeger Agent**: 6831

---

## 🔧 Configuration

### Environment Variables
```bash
# Security
SECRET_KEY=your-secret-key
ENABLE_APPROVAL_GATE=true

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Jaeger
JAEGER_HOST=localhost
JAEGER_PORT=6831
ENABLE_TRACING=true

# Database
DATABASE_URL=postgresql://otis:password@localhost:5432/otis

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:7b
```

---

## 📝 API Examples

### Run Agent with PolicyEngine
```bash
curl -X POST http://localhost:8000/api/v1/agent/run \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Scan localhost for vulnerabilities",
    "mode": "passive",
    "scan_duration": 10
  }'
```

### Response with Policy Decisions
```json
{
  "summary": "Completed 3 reasoning steps",
  "steps": [
    {
      "iteration": 1,
      "thought": "Start with passive scan",
      "action": "scan_environment",
      "action_input": {"target": "localhost"},
      "policy_decision": "PERMIT",
      "observation": {"success": true, "findings": [...]}
    },
    {
      "iteration": 2,
      "thought": "Query threat intel for findings",
      "action": "query_threat_intel",
      "action_input": {"query": "vulnerability analysis"},
      "policy_decision": "PERMIT",
      "observation": {"success": true, "results": [...]}
    },
    {
      "iteration": 3,
      "thought": "Propose remediation",
      "action": "propose_action",
      "action_input": {"code": "patch_system()", "risk": "high"},
      "policy_decision": "REQUIRES_APPROVAL",
      "observation": "Action requires human approval. Proposal sent."
    }
  ],
  "proposals": [
    {
      "action_id": "abc123",
      "status": "pending",
      "risk_level": "high"
    }
  ],
  "evidence": [...],
  "confidence": 0.85
}
```

---

## 🚨 Common Issues

### PolicyEngine Denials
```python
# Check user role
print(f"User role: {current_user.role}")

# Check denial reason
reason = policy_engine.get_denial_reason(tool_name, params)
print(f"Denial reason: {reason}")

# Verify mode
print(f"Request mode: {request.mode}")
```

### Celery Connection Issues
```bash
# Check Redis
redis-cli ping

# Check Celery workers
celery -A src.tasks inspect ping

# Restart workers
docker-compose restart worker
```

### Jaeger Not Showing Traces
```bash
# Check Jaeger is running
curl http://localhost:16686

# Verify tracing is enabled
echo $ENABLE_TRACING  # Should be "true"

# Check Jaeger agent port
netstat -an | grep 6831
```

---

## 📚 Additional Resources

- **Full Documentation**: [A_PLUS_UPGRADES.md](./A_PLUS_UPGRADES.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Security Policy**: [SECURITY_POLICY.md](./SECURITY_POLICY.md)
- **API Reference**: [API.md](./API.md)

---

## 🎯 Key Takeaways

1. **PolicyEngine** = Hard-coded security (no prompt injection)
2. **Query Router** = LLM-based complexity classification
3. **Planner** = Multi-step autonomous plans
4. **Celery** = Distributed task execution
5. **Jaeger** = Distributed tracing and debugging

**Otis is now A+ production-ready!** 🏆
