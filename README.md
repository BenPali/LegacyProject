# LegacyProject
[![CI](https://github.com/BenPali/LegacyProject/actions/workflows/ci.yml/badge.svg)](https://github.com/BenPali/LegacyProject/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/BenPali/LegacyProject/branch/main/graph/badge.svg)](https://codecov.io/gh/BenPali/LegacyProject)
# Geneweb - A Cobol Project Restored in Python

This project is a restoration of the original Geneweb, an open-source genealogy software <mcreference link="https://github.com/geneweb/geneweb" index="0"></mcreference> initially written in OCaml (not Cobol as previously stated), now re-implemented in Python. It provides a web interface and can be used offline or as a web service.

## How to launch the project

To launch the project, you have several options:

```bash
make docker-build
make docker-run
```

Alternatively, you can use Docker Compose:

```bash
docker compose up --build -d
```

For a lighter run, you can start Geneweb through the daemon with:

```bash
make start-daemon
```

In order to view all available make commands, refer to `make help` for details:

```bash
Available targets:
  all              - Default target, runs tests
  test             - Run all modernProject tests
  test-modern      - Run all modernProject tests
  coverage         - Run tests with coverage report
  clean            - Remove test artifacts
  fclean           - Remove all generated files
  re               - Clean and run all tests

Daemon management:
  start-daemon     - Start GeneWeb daemon on port 2317
  stop-daemon      - Stop GeneWeb daemon
  restart-daemon   - Restart GeneWeb daemon
  status-daemon    - Show daemon status

Docker deployment:
  docker-build     - Build Docker image
  docker-run       - Run GeneWeb in Docker
  docker-stop      - Stop Docker container
  docker-logs      - Show Docker logs
  ```
