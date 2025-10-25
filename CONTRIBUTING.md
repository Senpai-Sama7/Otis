# Contributing to Otis

Thank you for your interest in contributing to Otis! This guide will help you get started.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow security best practices

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Otis.git
cd Otis
```

### 2. Setup Development Environment

```bash
# Install dependencies
make install-dev

# Setup pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## Development Workflow

### Running Tests

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run specific test file
pytest tests/unit/test_config.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check
```

### Running the Application

```bash
# Run locally
make run

# Run with Docker
make docker-up
make docker-logs
```

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use Black for formatting (line length: 100)
- Use type hints for all functions
- Write docstrings for public APIs

### Example

```python
from typing import Optional

def process_threat(
    threat_id: str,
    severity: str,
    mitigate: bool = False
) -> Optional[dict]:
    """Process a security threat.

    Args:
        threat_id: Unique identifier for the threat
        severity: Threat severity level (low, medium, high, critical)
        mitigate: Whether to automatically mitigate

    Returns:
        Processing result dict or None if failed

    Raises:
        ValueError: If threat_id is invalid
    """
    # Implementation
    pass
```

### Project Structure

```
src/
├── api/          # FastAPI routes
├── core/         # Core utilities (config, logging, security)
├── database/     # Database layer (models, connections)
├── models/       # Data models (SQLAlchemy, Pydantic)
├── services/     # Business logic (Ollama, Chroma, Docker, Telegram)
├── tools/        # ReAct tools
└── main.py       # Application entry point

tests/
├── unit/         # Unit tests
└── integration/  # Integration tests
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new threat detection algorithm
fix: resolve Docker sandbox timeout issue
docs: update API documentation
test: add tests for scan_environment tool
refactor: simplify Chroma service implementation
perf: optimize vector search queries
chore: update dependencies
```

### Testing Guidelines

1. **Unit Tests**: Test individual functions/classes
2. **Integration Tests**: Test API endpoints
3. **Mock External Services**: Use pytest-mock
4. **Aim for Coverage**: Target 80%+ coverage

Example:
```python
def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False
```

## Adding New Features

### 1. New API Endpoint

1. Add route in `src/api/`
2. Add Pydantic schemas in `src/models/schemas.py`
3. Update OpenAPI documentation
4. Add integration tests
5. Update API.md documentation

### 2. New ReAct Tool

1. Create tool class in `src/tools/`
2. Inherit from `BaseTool`
3. Implement `execute()` and `get_parameters()`
4. Add unit tests
5. Register in agent service

Example:
```python
class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Description of what this tool does"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "result": "..."}
```

### 3. New Service Integration

1. Create service class in `src/services/`
2. Implement health check method
3. Add to health endpoint
4. Add unit tests with mocks
5. Update documentation

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main

### Submitting PR

1. Push to your fork
2. Create PR against `main` branch
3. Fill out PR template
4. Link related issues
5. Request review

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
- [ ] Linting passes
```

## Security

### Reporting Vulnerabilities

**Do NOT** open public issues for security vulnerabilities.

Instead:
1. Email: security@otis.local
2. Include detailed description
3. Include steps to reproduce
4. Allow time for fix before disclosure

### Security Best Practices

- Never commit secrets/credentials
- Use environment variables
- Validate all input
- Sanitize output
- Use parameterized queries
- Keep dependencies updated
- Follow OWASP guidelines

## Documentation

### Update Documentation When:

- Adding new features
- Changing APIs
- Updating configuration
- Fixing bugs (if user-facing)

### Documentation Files:

- `README.md`: Overview and quick start
- `docs/API.md`: API reference
- `docs/ARCHITECTURE.md`: System design
- `docs/DEPLOYMENT.md`: Deployment guide
- `docs/CONTRIBUTING.md`: This file

## Community

### Getting Help

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and discussions
- Email: support@otis.local

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Acknowledged in documentation

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Search closed issues
3. Open a GitHub Discussion
4. Contact maintainers

Thank you for contributing to Otis! 🚀
