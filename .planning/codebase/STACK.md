---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# Technology Stack

**Analysis Date:** 2026-11-23

## Languages

**Primary:**
- Python 3.11–3.12 - classroom application, CLI, content tooling, and tests; package compatibility is `>=3.11,<3.13` in `pyproject.toml`.

**Secondary:**
- HTML, CSS, and JavaScript - static browser classroom in `src/ds60sqlpy/assets/`.
- Multiple isolated teaching runtimes - Python, C/C++, C#, Go, Java/Scala, JavaScript/TypeScript, PHP, R, Rust, Swift, Julia, SQL, and specialist data/ML workers; each is separately cataloged in `docker/classroom-images.tsv` and built from `docker/workers/`.

## Runtime

**Environment:**
- Learner delivery uses Linux containers orchestrated by Docker Compose; Windows uses WSL 2, while macOS/Linux use a local Docker-compatible Linux engine (`README.md`).
- Main application image uses Python `3.12.16-slim-bookworm`; the TeX compilation stage uses Node `24.22.3` (`Dockerfile`).
- PostgreSQL client tools are installed in the application image as `postgresql-client-17` (`Dockerfile`).

**Package Manager:**
- `uv` resolves and installs the Python project from `pyproject.toml` and the checked-in `uv.lock`; `scripts/setup.sh` also supports project-mode pip installation.
- Python package build backend: setuptools (`pyproject.toml`).
- Lockfile: `uv.lock` present; worker environments have separate locks/manifests under `docker/workers/`.

## Frameworks

**Core:**
- Python standard-library HTTP server, extended by `src/ds60sqlpy/classroom_http.py` and `src/ds60sqlpy/lab.py`.
- Hand-authored browser interface in `src/ds60sqlpy/assets/`; no frontend framework is declared in the root package manifest.
- Optional `mcp` extra exposes the local tutor adapter (`pyproject.toml`, `src/ds60sqlpy/mcp_server.py`).

**Testing:**
- pytest `9.1.1` resolved in `uv.lock`; test configuration and Python 3.11/3.12 matrix are in `pyproject.toml` and `.github/workflows/ci.yml`.

**Build/Dev:**
- Docker Compose prepares the local app, PostgreSQL, and selected worker images (`compose.classroom.yaml`, `compose.modules.yaml`, `scripts/classroom.sh`).
- `uv` lock-based Python environment; setuptools packaging; Node is used for the container-time TeX compilation stage (`Dockerfile`).
- Ruff, mypy, pytest-cov, and pytest-xdist are declared in the `quality` extra (`pyproject.toml`).

## Key Dependencies

**Critical:**
- `latex2mathml` `3.81.1` and `Pygments` `2.20.0` - required application dependencies for math rendering and source highlighting (`pyproject.toml`, `uv.lock`).
- `psycopg` `3.3.4` - optional bridge/SQL-notebook integration for PostgreSQL (`pyproject.toml`, `uv.lock`).
- `JupyterLab` `4.6.2`, pandas `2.3.3`, NumPy (platform-resolved versions) - optional notebook/data extras, not universal runtime requirements (`pyproject.toml`, `uv.lock`).
- The `production` optional extra declares FastAPI, Uvicorn, Pydantic, Dask, MLflow, and Prefect for selected project environments; the core classroom server itself uses the standard library (`pyproject.toml`).

**Infrastructure:**
- Separate container images isolate the language and scientific runtimes; profile-to-image mappings live in `docker/classroom-images.tsv`, with definitions in `docker/workers/`.
- PostgreSQL is the course SQL store; the app image includes its versioned client (`Dockerfile`, `src/ds60sqlpy/sql_runner.py`).

## Configuration

**Environment:**
- Local Compose defaults and supported overrides are documented by variable name in `.env.example`; relevant names include `DS60_POSTGRES_PORT`, `DS60_LAB_PORT`, `DS60_COURSE_USER`, `DS60_COURSE_PASSWORD`, and `DS60_DOCKER_PROFILES`. No values are repeated here.
- `DS60_DATABASE_URL` selects the contributor/host SQL target; `DS60_LAB_DATABASE_URL` is an internal-container override (`src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/container_runtime.py`).
- A local `.env` file is present; its contents were not read.

**Build:**
- Python package and pinned image inputs: `pyproject.toml`, `uv.lock`, `Dockerfile`, and `docker/classroom-images.tsv`.
- Container composition and optional overlays: `compose.classroom.yaml`, `compose.modules.yaml`, and `compose.classroom.kubernetes.yaml`.
- CI and image publication definitions: `.github/workflows/`.

## Platform Requirements

**Development:**
- Python 3.11 or 3.12 and `uv` for the locked contributor environment; Docker/Compose and Bash are needed for container-based classroom workflows (`scripts/setup.sh`, `README.md`).
- Docker Compose 2.28.0 or newer for the supported learner launcher (`README.md`).

**Production:**
- The product is delivered as a local Docker classroom, not a hosted web service. Optional versioned multi-platform images are built and distributed through the Docker Hub workflow (`README.md`, `.github/workflows/publish-images.yml`).

## Evidence

- `pyproject.toml`
- `uv.lock`
- `Dockerfile`
- `docker/classroom-images.tsv`
- `docker/workers/`
- `.env.example`
- `compose.classroom.yaml`
- `.github/workflows/ci.yml`

---

*Stack analysis: 2026-11-23*
