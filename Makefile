.PHONY: help install install-dev test test-cov test-unit test-integration lint format clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install minimal dependencies"
	@echo "  make install-dev   - Install all development dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make lint         - Run linters (flake8, mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make clean        - Remove build artifacts and cache"

install:
	pip install -r requirements-minimal.txt

install-dev:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest -v --cov=. --cov-report=term-missing --cov-report=html

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

lint:
	flake8 . --exclude=venv,tests
	mypy . --exclude=venv

format:
	black . --exclude=venv

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info