[![CI](https://github.com/BenPali/LegacyProject/actions/workflows/ci.yml/badge.svg)](https://github.com/BenPali/LegacyProject/actions/workflows/ci.yml) [![codecov](https://codecov.io/gh/BenPali/LegacyProject/branch/main/graph/badge.svg)](https://codecov.io/gh/BenPali/LegacyProject)

# LegacyProject - Geneweb restored from OCaml to Python

This project is a restoration of the original Geneweb, an open-source genealogy software <mcreference link="https://github.com/geneweb/geneweb" index="0"></mcreference> initially written in OCaml now re-implemented in Python. It provides a web interface and can be used offline or as a web service.

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
Quick Testing:
  make quick-test       - Run unit tests only
  make test             - Run all non-e2e tests (unit+integration+functional)
  make coverage         - Run tests with coverage report

Test Categories:
  make unit-test        - Unit tests only
  make integration-test - Integration tests only
  make functional-test  - Functional tests only
  make e2e-test         - E2E browser tests

Maintenance:
  make clean            - Remove test artifacts
  make fclean           - Deep clean
  make re               - Clean and run all tests

Daemon Management:
  make start-daemon     - Start GeneWeb daemon on port 2317
  make stop-daemon      - Stop GeneWeb daemon
  make restart-daemon   - Restart GeneWeb daemon
  make status-daemon    - Show daemon status

Docker Deployment:
  make docker-build     - Build Docker image
  make docker-run       - Run GeneWeb in Docker
  make docker-stop      - Stop Docker container
  make docker-logs      - Show Docker logs
```

## Documentation

You can find more detailed documentation in the `docs` folder:

*   [`WORKFLOW.md`](./docs/WORKFLOW.md)
*   [`DEPLOYMENT.md`](./docs/DEPLOYMENT.md)
*   [`MODULES.md`](./docs/MODULES.md)
*   [`TESTING_GUIDE.md`](./docs/TESTING_GUIDE.md)

This README is purposefully concise to improve clarity
