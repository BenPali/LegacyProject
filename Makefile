.PHONY: all test test-modern coverage clean fclean re help

help:
	@echo "Available targets:"
	@echo "  all           - Default target, runs tests"
	@echo "  test          - Run all modernProject tests"
	@echo "  test-modern   - Run all modernProject tests"
	@echo "  coverage      - Run tests with coverage report"
	@echo "  clean         - Remove test artifacts"
	@echo "  fclean        - Remove all generated files"
	@echo "  re            - Clean and run all tests"

all: test

test: test-modern coverage

test-modern:
	@echo "Running modernProject tests..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/ -v

coverage:
	@if ! python3 -c "import pytest_cov" 2>/dev/null; then \
		echo "ERROR: pytest-cov not installed"; \
		echo "Install: sudo pacman -S python-pytest-cov"; \
		exit 1; \
	fi
	@echo "Running tests with coverage..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/ -q --cov=modernProject/lib --cov=modernProject/bin --cov-report=html:modernProject/htmlcov --cov-report=xml:coverage.xml --cov-report=term | grep -E "^(modernProject/lib/|modernProject/bin/|TOTAL|passed|skipped|failed)"
	@echo ""
	@echo "HTML report: modernProject/htmlcov/index.html"

clean:
	@echo "Cleaning test artifacts..."
	-find . -type d -name __pycache__ -exec rm -rf {} +
	-find . -type f -name "*.pyc" -delete
	-rm -f modernProject/coverage.xml modernProject/.coverage
	-rm -rf modernProject/htmlcov/

fclean: clean
	@echo "Deep cleaning..."
	-find . -type d -name "*.egg-info" -exec rm -rf {} +
	-find . -type d -name ".pytest_cache" -exec rm -rf {} +
	-rm -rf htmlcov/

re: fclean all
