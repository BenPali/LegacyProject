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

In order to view all available make commands, refer to `make help` for details.
