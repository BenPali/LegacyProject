.PHONY: all help test quick-test unit-test integration-test functional-test e2e-test coverage clean fclean re start-daemon stop-daemon restart-daemon status-daemon docker-build docker-run docker-stop docker-logs

help:
	@echo "=== GeneWeb Python Make Rules ==="
	@echo ""
	@echo "Quick Testing:"
	@echo "  make quick-test       - Run unit tests only"
	@echo "  make test             - Run all non-e2e tests (unit+integration+functional)"
	@echo "  make coverage         - Run tests with coverage report"
	@echo ""
	@echo "Test Categories:"
	@echo "  make unit-test        - Unit tests only"
	@echo "  make integration-test - Integration tests only"
	@echo "  make functional-test  - Functional tests only"
	@echo "  make e2e-test         - E2E browser tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            - Remove test artifacts"
	@echo "  make fclean           - Deep clean"
	@echo "  make re               - Clean and run all tests"
	@echo ""
	@echo "Daemon Management:"
	@echo "  make start-daemon     - Start GeneWeb daemon on port 2317"
	@echo "  make stop-daemon      - Stop GeneWeb daemon"
	@echo "  make restart-daemon   - Restart GeneWeb daemon"
	@echo "  make status-daemon    - Show daemon status"
	@echo ""
	@echo "Docker Deployment:"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run GeneWeb in Docker"
	@echo "  make docker-stop      - Stop Docker container"
	@echo "  make docker-logs      - Show Docker logs"

all: test

test: unit-test integration-test functional-test
	@echo ""
	@echo "✓ All non-e2e tests passed"
	@echo "  Run 'make e2e-test' for browser tests"
	@echo "  Run 'make coverage' for coverage report"

quick-test: unit-test

unit-test:
	@echo "Running unit tests..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/unit/ -v

integration-test:
	@echo "Running integration tests..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/integration/ -v

functional-test:
	@echo "Running functional tests..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/functional/ -v

e2e-test:
	@echo "Running e2e tests..."
	@echo ""
	@echo "⚠  Requirements:"
	@echo "   - Selenium (pip install selenium)"
	@echo "   - Chrome or Firefox webdriver"
	@echo ""
	@echo "💡 To see browser window:"
	@echo "   SELENIUM_HEADLESS=false PYTHONPATH=modernProject python -m pytest modernProject/tests/e2e/ -v -s"
	@echo ""
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/e2e/ -v

coverage:
	@if ! python3 -c "import pytest_cov" 2>/dev/null; then \
		echo "ERROR: pytest-cov not installed"; \
		echo "Install: sudo pacman -S python-pytest-cov"; \
		exit 1; \
	fi
	@echo "Running tests with coverage (excludes e2e)..."
	@PYTHONPATH=modernProject python -m pytest modernProject/tests/unit/ modernProject/tests/integration/ modernProject/tests/functional/ -q --cov=modernProject/lib --cov=modernProject/bin --cov-report=html:modernProject/htmlcov --cov-report=xml:coverage.xml --cov-report=term | grep -E "^(modernProject/lib/|modernProject/bin/|TOTAL|passed|skipped|failed)"
	@echo ""
	@echo "HTML report: modernProject/htmlcov/index.html"

clean:
	@echo "Cleaning test artifacts..."
	-find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	-find . -type f -name "*.pyc" -delete
	-rm -f modernProject/coverage.xml modernProject/.coverage
	-rm -rf modernProject/htmlcov/
	@echo "✓ Clean complete"

fclean: clean
	@echo "Deep cleaning..."
	-find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
	-find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
	-rm -rf htmlcov/ coverage.xml .coverage
	@echo "✓ Deep clean complete"

re: fclean all

start-daemon:
	@echo "Starting GeneWeb daemon on port 2317..."
	@if lsof -Pi :2317 -sTCP:LISTEN -t >/dev/null 2>&1; then \
		echo "Error: Port 2317 is already in use"; \
		echo "Run 'make stop-daemon' first or check with 'make status-daemon'"; \
		exit 1; \
	fi
	@mkdir -p geneweb_databases
	@cd modernProject && nohup python -m bin.gwd -p 2317 -wd ../geneweb_databases > /tmp/geneweb-daemon.log 2>&1 & echo $$! > /tmp/geneweb-daemon.pid
	@sleep 2
	@if [ -f /tmp/geneweb-daemon.pid ] && kill -0 $$(cat /tmp/geneweb-daemon.pid) 2>/dev/null; then \
		echo "✓ Daemon started successfully (PID: $$(cat /tmp/geneweb-daemon.pid))"; \
		echo "  Access at: http://localhost:2317/"; \
		echo "  Logs: /tmp/geneweb-daemon.log"; \
	else \
		echo "✗ Failed to start daemon. Check logs at /tmp/geneweb-daemon.log"; \
		exit 1; \
	fi

stop-daemon:
	@echo "Stopping GeneWeb daemon..."
	@STOPPED=0; \
	if [ -f /tmp/geneweb-daemon.pid ]; then \
		PID=$$(cat /tmp/geneweb-daemon.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			pkill -P $$PID 2>/dev/null || true; \
			kill $$PID 2>/dev/null && STOPPED=1; \
			sleep 1; \
			if kill -0 $$PID 2>/dev/null; then \
				kill -9 $$PID 2>/dev/null; \
			fi; \
			echo "✓ Main daemon stopped (PID: $$PID)"; \
		fi; \
		rm -f /tmp/geneweb-daemon.pid; \
	fi; \
	PIDS=$$(lsof -ti :2317 2>/dev/null || true); \
	if [ -n "$$PIDS" ]; then \
		echo "  Killing processes on port 2317: $$PIDS"; \
		echo $$PIDS | xargs -r kill -9 2>/dev/null || true; \
		STOPPED=1; \
	fi; \
	PIDS=$$(pgrep -f "bin\.gwd" 2>/dev/null || true); \
	if [ -n "$$PIDS" ]; then \
		echo "  Killing GeneWeb processes: $$PIDS"; \
		echo $$PIDS | xargs -r kill -9 2>/dev/null || true; \
		STOPPED=1; \
	fi; \
	if [ $$STOPPED -eq 1 ]; then \
		echo "✓ All GeneWeb processes stopped"; \
	else \
		echo "  No GeneWeb daemon was running"; \
	fi

restart-daemon: stop-daemon
	@sleep 1
	@$(MAKE) start-daemon

status-daemon:
	@if [ -f /tmp/geneweb-daemon.pid ]; then \
		PID=$$(cat /tmp/geneweb-daemon.pid); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "✓ GeneWeb daemon is running (PID: $$PID)"; \
			echo "  Listening on: http://localhost:2317/"; \
			echo "  Logs: /tmp/geneweb-daemon.log"; \
		else \
			echo "✗ GeneWeb daemon is not running (stale PID file found)"; \
			rm -f /tmp/geneweb-daemon.pid; \
		fi \
	else \
		echo "  GeneWeb daemon is not running (no PID file)"; \
		if lsof -Pi :2317 -sTCP:LISTEN -t >/dev/null 2>&1; then \
			echo "⚠  Warning: Port 2317 is in use by another process"; \
		fi \
	fi

docker-build:
	@echo "Building Docker image..."
	docker build -t geneweb-python:latest .

docker-run:
	@echo "Starting GeneWeb in Docker..."
	docker compose up -d
	@echo "✓ GeneWeb is running at http://localhost:2317/"

docker-stop:
	@echo "Stopping Docker containers..."
	docker compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker compose logs -f geneweb
