.PHONY: help install install-dev clean test lint format type-check run docker-build docker-up docker-down migrations

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ dist/ build/

test:  ## Run tests with coverage
	pytest

test-verbose:  ## Run tests with verbose output
	pytest -vv

lint:  ## Run linters
	ruff check src tests
	black --check src tests

format:  ## Format code with black and ruff
	black src tests
	ruff check --fix src tests

type-check:  ## Run type checking with mypy
	mypy src

check: lint type-check test  ## Run all checks (lint, type-check, test)

run:  ## Run the application locally
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

docker-build:  ## Build Docker images
	docker-compose build

docker-up:  ## Start Docker containers
	docker-compose up -d

docker-down:  ## Stop Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f

migrations:  ## Create a new migration
	alembic revision --autogenerate -m "$(msg)"

migrate:  ## Apply migrations
	alembic upgrade head

migrate-down:  ## Rollback last migration
	alembic downgrade -1

init-rag:  ## Initialize RAG data (download and ingest)
	python scripts/init_rag_data.py

setup:  ## Complete setup (install deps, create env, init db)
	@echo "Setting up Otis..."
	@cp -n .env.example .env 2>/dev/null || echo ".env already exists"
	@$(MAKE) install-dev
	@echo "Setup complete! Edit .env file with your configuration."
	@echo "Run 'make migrate' to initialize the database."
	@echo "Run 'make init-rag' to download cybersecurity knowledge base."
	@echo "Run 'make run' to start the application."
