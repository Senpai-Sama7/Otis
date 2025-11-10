#!/bin/bash
set -e

echo "=== Otis Installation and Testing ==="

# Install dependencies
echo "Installing dependencies..."
cd /home/donovan/Projects/AI/Otis
pip install -e . --quiet

# Test imports
echo "Testing core imports..."
python3 -c "
from src.security.policy_engine import PolicyEngine
from src.core.sanitization import InputSanitizer
from src.core.config import get_settings
print('✓ Core modules imported successfully')
"

# Test PolicyEngine
echo "Testing PolicyEngine..."
python3 -c "
from src.security.policy_engine import PolicyEngine, PolicyDecision
from src.models.schemas import AgentRequest

class MockUser:
    def __init__(self, role):
        self.role = role

user = MockUser('admin')
request = AgentRequest(instruction='test', mode='passive')
engine = PolicyEngine(user, request)

# Test RBAC
decision = engine.validate('query_threat_intel', {})
assert decision == PolicyDecision.PERMIT, 'Admin should be able to query'

# Test high-risk tool
decision = engine.validate('exec_in_sandbox', {'code': 'test'})
assert decision == PolicyDecision.REQUIRES_APPROVAL, 'Code execution should require approval'

print('✓ PolicyEngine tests passed')
"

# Test InputSanitizer
echo "Testing InputSanitizer..."
python3 -c "
from src.core.sanitization import InputSanitizer

# Test valid input
result = InputSanitizer.sanitize_query('What is SQL injection?')
assert result == 'What is SQL injection?', 'Valid query should pass'

# Test dangerous pattern
try:
    InputSanitizer.sanitize_query('rm -rf /')
    assert False, 'Should have blocked dangerous command'
except ValueError:
    pass

print('✓ InputSanitizer tests passed')
"

echo "=== All tests passed! ==="
