# Makefile for SendApi Project
# Security and development commands

.PHONY: help install install-dev security-scan security-install test lint format clean build

# Default target
help:
	@echo "SendApi Project - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo "  security-install - Install security tools"
	@echo ""
	@echo "Security:"
	@echo "  security-scan  - Run all security checks"
	@echo "  safety         - Run Safety dependency check"
	@echo "  bandit         - Run Bandit security linter"
	@echo "  semgrep        - Run Semgrep static analysis"
	@echo "  pip-audit      - Run pip-audit"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run all linting tools"
	@echo "  format         - Format code with Black and isort"
	@echo "  type-check     - Run MyPy type checking"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run tests with coverage"
	@echo "  test-fast      - Run tests without coverage"
	@echo ""
	@echo "Development:"
	@echo "  pre-commit     - Install pre-commit hooks"
	@echo "  clean          - Clean build artifacts"
	@echo "  build          - Build package"
	@echo "  run            - Run the application"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-security.txt

security-install:
	pip install safety bandit semgrep pip-audit

# Security scanning
security-scan:
	@echo "🔒 Running comprehensive security scan..."
	python scripts/security_scan.py --check all

safety:
	@echo "🔍 Running Safety dependency check..."
	safety check --full-report

bandit:
	@echo "🔍 Running Bandit security linter..."
	bandit -r src/ -f txt

semgrep:
	@echo "🔍 Running Semgrep static analysis..."
	semgrep ci --config auto

pip-audit:
	@echo "🔍 Running pip-audit..."
	pip-audit

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 src/ tests/ main.py --max-line-length=88 --extend-ignore=E203,W503
	pylint src/ --disable=C0114,C0116 --max-line-length=88

format:
	@echo "🎨 Formatting code..."
	black src/ tests/ main.py
	isort src/ tests/ main.py

type-check:
	@echo "🔍 Running type checking..."
	mypy src/ --ignore-missing-imports --disallow-untyped-defs

# Testing
test:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v

test-fast:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Development
pre-commit:
	@echo "🔧 Installing pre-commit hooks..."
	pre-commit install
	pre-commit install --hook-type commit-msg

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf security-reports/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	@echo "🔨 Building package..."
	python setup.py sdist bdist_wheel

run:
	@echo "🚀 Running SendApi application..."
	python main.py

# CI/CD helpers
ci-security:
	@echo "🔒 Running CI security checks..."
	safety check --json --output safety-report.json || true
	bandit -r src/ -f json -o bandit-report.json || true
	semgrep ci --config auto --json --output semgrep-report.json || true
	pip-audit --format json --output pip-audit-report.json || true

ci-quality:
	@echo "🔍 Running CI quality checks..."
	black --check --diff src/ tests/ main.py
	isort --check-only --diff src/ tests/ main.py
	flake8 src/ tests/ main.py --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports --disallow-untyped-defs

ci-test:
	@echo "🧪 Running CI tests..."
	pytest tests/ --cov=src --cov-report=xml --cov-report=html

# Docker helpers (if needed)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t sendapi .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -it sendapi

# Documentation
docs:
	@echo "📚 Generating documentation..."
	pydoc -w src/
	@echo "Documentation generated in current directory"

# Dependencies
update-deps:
	@echo "📦 Updating dependencies..."
	pip install --upgrade -r requirements.txt
	pip install --upgrade -r requirements-security.txt

check-deps:
	@echo "📦 Checking for outdated dependencies..."
	pip list --outdated

# Security reports
security-report:
	@echo "📊 Generating security report..."
	@if [ -f "security-reports/security-summary.json" ]; then \
		echo "Security report found:"; \
		cat security-reports/security-summary.json | python -m json.tool; \
	else \
		echo "No security report found. Run 'make security-scan' first."; \
	fi 