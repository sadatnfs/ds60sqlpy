<!-- GSD:project-start source:PROJECT.md -->

## Project

**DS60 Classroom Overhaul**

DS60 Classroom is a local, desktop-first browser classroom for learning programming, data science, statistics, machine learning, and systems through written lessons, examples, exercises, and prepared Docker runtimes. This project will make the existing classroom and its learning content clear, reliable, and well-furnished for beginners and experienced learners across every current language and subject track. Python and SQL provide a quality reference, not a limit on the work.

**Core Value:** Learners can understand, practice, run, and keep their work in any DS60 course without installing toolchains or losing learning state.

### Constraints

- **Platform**: Design and verify for desktop browsers; do not spend scope on mobile-specific layouts.
- **Runtime**: Preserve local Docker delivery, the existing course/profile boundaries, and offline classroom assets.
- **Learner state**: Keep drafts, progress, receipts, and volumes intact across UI and runtime changes.
- **Content quality**: Preserve accurate source material and stable lesson identities; make improvements evidence-based and testable.
- **Image security**: Release images must have no unresolved CVEs in the applicable scan results; rebuild or remediate affected images before publication.
- **Release safety**: Separate ordinary code changes from pushing to `main` and publishing images. Verify all release gates and the Docker Hub target before publishing.
- **Cleanup**: Stop DS60-owned test containers at completion, but do not stop unrelated services or remove learner volumes.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.11–3.12 - classroom application, CLI, content tooling, and tests; package compatibility is `>=3.11,<3.13` in `pyproject.toml`.
- HTML, CSS, and JavaScript - static browser classroom in `src/ds60sqlpy/assets/`.
- Multiple isolated teaching runtimes - Python, C/C++, C#, Go, Java/Scala, JavaScript/TypeScript, PHP, R, Rust, Swift, Julia, SQL, and specialist data/ML workers; each is separately cataloged in `docker/classroom-images.tsv` and built from `docker/workers/`.

## Runtime

- Learner delivery uses Linux containers orchestrated by Docker Compose; Windows uses WSL 2, while macOS/Linux use a local Docker-compatible Linux engine (`README.md`).
- Main application image uses Python `3.12.16-slim-bookworm`; the TeX compilation stage uses Node `24.22.3` (`Dockerfile`).
- PostgreSQL client tools are installed in the application image as `postgresql-client-17` (`Dockerfile`).
- `uv` resolves and installs the Python project from `pyproject.toml` and the checked-in `uv.lock`; `scripts/setup.sh` also supports project-mode pip installation.
- Python package build backend: setuptools (`pyproject.toml`).
- Lockfile: `uv.lock` present; worker environments have separate locks/manifests under `docker/workers/`.

## Frameworks

- Python standard-library HTTP server, extended by `src/ds60sqlpy/classroom_http.py` and `src/ds60sqlpy/lab.py`.
- Hand-authored browser interface in `src/ds60sqlpy/assets/`; no frontend framework is declared in the root package manifest.
- Optional `mcp` extra exposes the local tutor adapter (`pyproject.toml`, `src/ds60sqlpy/mcp_server.py`).
- pytest `9.1.1` resolved in `uv.lock`; test configuration and Python 3.11/3.12 matrix are in `pyproject.toml` and `.github/workflows/ci.yml`.
- Docker Compose prepares the local app, PostgreSQL, and selected worker images (`compose.classroom.yaml`, `compose.modules.yaml`, `scripts/classroom.sh`).
- `uv` lock-based Python environment; setuptools packaging; Node is used for the container-time TeX compilation stage (`Dockerfile`).
- Ruff, mypy, pytest-cov, and pytest-xdist are declared in the `quality` extra (`pyproject.toml`).

## Key Dependencies

- `latex2mathml` `3.81.1` and `Pygments` `2.20.0` - required application dependencies for math rendering and source highlighting (`pyproject.toml`, `uv.lock`).
- `psycopg` `3.3.4` - optional bridge/SQL-notebook integration for PostgreSQL (`pyproject.toml`, `uv.lock`).
- `JupyterLab` `4.6.2`, pandas `2.3.3`, NumPy (platform-resolved versions) - optional notebook/data extras, not universal runtime requirements (`pyproject.toml`, `uv.lock`).
- The `production` optional extra declares FastAPI, Uvicorn, Pydantic, Dask, MLflow, and Prefect for selected project environments; the core classroom server itself uses the standard library (`pyproject.toml`).
- Separate container images isolate the language and scientific runtimes; profile-to-image mappings live in `docker/classroom-images.tsv`, with definitions in `docker/workers/`.
- PostgreSQL is the course SQL store; the app image includes its versioned client (`Dockerfile`, `src/ds60sqlpy/sql_runner.py`).

## Configuration

- Local Compose defaults and supported overrides are documented by variable name in `.env.example`; relevant names include `DS60_POSTGRES_PORT`, `DS60_LAB_PORT`, `DS60_COURSE_USER`, `DS60_COURSE_PASSWORD`, and `DS60_DOCKER_PROFILES`. No values are repeated here.
- `DS60_DATABASE_URL` selects the contributor/host SQL target; `DS60_LAB_DATABASE_URL` is an internal-container override (`src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/container_runtime.py`).
- A local `.env` file is present; its contents were not read.
- Python package and pinned image inputs: `pyproject.toml`, `uv.lock`, `Dockerfile`, and `docker/classroom-images.tsv`.
- Container composition and optional overlays: `compose.classroom.yaml`, `compose.modules.yaml`, and `compose.classroom.kubernetes.yaml`.
- CI and image publication definitions: `.github/workflows/`.

## Platform Requirements

- Python 3.11 or 3.12 and `uv` for the locked contributor environment; Docker/Compose and Bash are needed for container-based classroom workflows (`scripts/setup.sh`, `README.md`).
- Docker Compose 2.28.0 or newer for the supported learner launcher (`README.md`).
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

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Use `snake_case.py` for Python implementation and script modules; use `test_<area>.py` for pytest modules. Examples: `src/ds60sqlpy/classroom_http.py`, `scripts/check_modules.py`, and `tests/test_classroom_http.py`.
- Course artifact filenames are owned by the curriculum and may include subject or lesson IDs; do not rename them to match Python module conventions. The formatter policy treats generated lesson artifacts separately in `scripts/format-policy.json`.
- Use `snake_case` for Python functions and methods, including test functions named `test_<behavior>`. Examples: `Catalog.load` and `find_repo_root` in `src/ds60sqlpy/catalog.py`, and `test_catalog_prerequisite_graph_is_acyclic` in `tests/test_catalog.py`.
- Prefix implementation helpers that are not public with `_` where appropriate, as in `_derived_outcome` imported by `tests/test_catalog.py`.
- Use `snake_case` for Python variables and parameters; use uppercase names for module-level constants such as `TRACK_ORDER` in `src/ds60sqlpy/catalog.py`.
- Use `PascalCase` for classes, protocols, and data types. The immutable `Lesson` dataclass in `src/ds60sqlpy/catalog.py` and test contracts in `tests/test_sql_json_transport.py` are representative.
- Add parameter and return annotations to maintained Python APIs and tests; examples include `Catalog.find_repo_root` in `src/ds60sqlpy/catalog.py` and fixtures in `tests/conftest.py`.

## Code Style

- Use `./scripts/format-repo` to format maintained sources and `./scripts/format-repo --check` to verify without editing. `make format` and `make format-check` are equivalent entrypoints in `Makefile`.
- Formatting is coordinated by `scripts/format_repo.py` and `scripts/format-policy.json`, with isolated toolchains for Python and the repository's other maintained languages. Preserve generated and historically qualified files according to the policy rather than formatting them independently.
- Follow `.editorconfig`: UTF-8, LF, final newline, trailing-space cleanup (except Markdown), four-space Python indentation, and two-space indentation for JSON/YAML and SQL.
- Run `./scripts/lint-repo` or `make lint`; the wrappers in `scripts/lint-repo` and `scripts/format-repo` provide read-only checks through the prepared toolchains.
- Python lint settings live in `pyproject.toml`: Ruff targets Python 3.11 with a 100-character line length and selects `E`, `F`, `I`, `UP`, `B`, `SIM`, `C4`, and `PTH`. Mypy is configured with `strict = true`, `explicit_package_bases = true`, and paths for `src` and `packages/spark-likelihood/src`.
- Python tests relax the `S101` Ruff rule via the `tests/*` per-file setting in `pyproject.toml`; do not generalize that exception to production code.
- The pre-commit hooks in `.pre-commit-config.yaml` run the sensitive-content scan, `scripts/lint-repo`, and `scripts/format-repo --check`.

## Import Organization

- Not detected for Python imports. Package imports use `ds60sqlpy...`; `pyproject.toml` configures `src` as the package source and mypy search path.
- Prefer imports from the defining module for tests and internal callers, as in `tests/test_catalog.py` importing from `ds60sqlpy.catalog`. No broad Python barrel-export convention is configured.

## Error Handling

- Validate invalid inputs at the owning boundary and raise a suitable exception; production examples include `ValueError` for unsupported lesson tracks and runners in `src/ds60sqlpy/catalog.py`.
- Keep error behavior explicit in tests with `pytest.raises`, including message checks where the contract requires them; see `tests/test_sql_json_transport.py` and `bridge/tests/test_days01_04.py`.
- Domain-specific exceptions are used where they clarify a contract, for example `ObjectiveError` in `packages/spark-likelihood/tests/test_dataframe.py`. There is no single repository-wide result/error type.

## Logging

- Use the relevant module's logger and avoid logging credentials or other sensitive values. The test in `bridge/tests/test_days01_04.py` checks that a customer name is absent from log output; `scripts/scan_secrets.py` is also wired into `.pre-commit-config.yaml`.
- Logging APIs and message conventions vary by runtime and component; no single structured logging schema is configured across the repository.

## Comments

- Explain non-obvious safety, isolation, compatibility, or ownership constraints; examples include the scheduler safeguards in `tests/conftest.py` and generated-file preservation notes in `scripts/format-policy.json`.
- Use docstrings for public classes/functions and complex helper behavior, as in `src/ds60sqlpy/catalog.py` and `scripts/format_repo.py`.
- Not detected as a repository-wide convention; use the language-appropriate documentation style for the file being changed.

## Function Design

## Module Design

## Evidence

- `pyproject.toml`
- `.editorconfig`
- `.pre-commit-config.yaml`
- `scripts/format_repo.py`
- `scripts/format-policy.json`
- `src/ds60sqlpy/catalog.py`
- `src/ds60sqlpy/reader_tex.py`
- `tests/test_catalog.py`
- `tests/test_classroom_http.py`
- `tests/test_sql_json_transport.py`
- `tests/conftest.py`
- `bridge/tests/test_days01_04.py`

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## System Overview

```text

```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI and startup | Exposes `ds60` commands and starts the contributor classroom | `src/ds60sqlpy/cli.py`, `src/ds60sqlpy/lab.py` |
| HTTP boundary | Serves UI/content and validates local API requests | `src/ds60sqlpy/classroom_http.py`, `src/ds60sqlpy/lab.py` |
| Legacy curriculum | Loads the checked-in Python/SQL/bridge catalog and resolves lesson content | `src/ds60sqlpy/catalog.py`, `curriculum/catalog.json` |
| Catalog generation | Builds the legacy catalog from lesson roots and extension metadata | `src/ds60sqlpy/catalog_builder.py`, `scripts/build_catalog.py` |
| Module catalog | Combines founding plans and authored course manifests; variants are expanded here | `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/module_plans.py`, `src/ds60sqlpy/module_extensions.py` |
| Rendering | Converts authored Markdown/source to safe classroom and static reader HTML | `src/ds60sqlpy/lesson_reader.py`, `src/ds60sqlpy/reader_content.py`, `src/ds60sqlpy/reader_tex.py` |
| Legacy application services | Coordinates lesson views, coaching, SQL/Python runs and classroom receipts | `src/ds60sqlpy/classroom.py`, `src/ds60sqlpy/coaching.py`, `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/sql_lesson.py` |
| Module application | Coordinates authored lessons, saved drafts, browser receipts and worker jobs | `src/ds60sqlpy/module_service.py`, `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/modules.py` |
| Worker runtime | Exposes authenticated profile jobs and executes only registered operations | `src/ds60sqlpy/module_worker.py`, `src/ds60sqlpy/worker_operations.py`, `docker/workers/` |
| Local state | Stores progress, drafts, job records and run receipts using validated paths and atomic writes | `src/ds60sqlpy/progress.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/classroom_runs.py`, `src/ds60sqlpy/state_files.py` |

## Pattern Overview

- `LabServer` is the single local application host; `LabRequestHandler` dispatches the three API families to catalog-bound actions (`src/ds60sqlpy/lab.py`).
- The legacy `Catalog` and authored `ModuleCatalog` are distinct loaders. `ClassroomService.index()` merges their learner-facing views without merging their registration or persistence contracts (`src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/classroom.py`).
- Modern module plans come from both the five founding plans and subject `track.json` files; the statistics tutorial book has its own authored manifest (`src/ds60sqlpy/module_plans.py`, `src/ds60sqlpy/module_extensions.py`).
- Planned subjects/lessons are not automatically executable. Authored manifests bind validated content paths to runtime profiles, while reviewed Python adapters implement execution (`src/ds60sqlpy/modules.py`, `src/ds60sqlpy/curriculum_framework.py`).
- UI JavaScript, CSS, HTML, and vendored offline rendering assets ship as package data (`src/ds60sqlpy/assets/`, `pyproject.toml`).
- The optional MCP process is a separate stdio adapter for catalog/coaching reads and explicitly gated progress, not the classroom execution API (`src/ds60sqlpy/mcp_server.py`).

## Layers

- Purpose: Serve the browser classroom and enforce request boundary checks.
- Location: `src/ds60sqlpy/lab.py`, `src/ds60sqlpy/classroom_http.py`, `src/ds60sqlpy/http_server.py`, `src/ds60sqlpy/assets/`
- Contains: `LabRequestHandler`, shared base request handling, static assets and browser actions.
- Depends on: Application services and package resources.
- Used by: The local browser session started through `ds60 serve` or the Docker classroom.
- Purpose: Turn validated API actions into catalog, coaching, rendering, progress and execution operations.
- Location: `src/ds60sqlpy/lab.py`, `src/ds60sqlpy/classroom.py`, `src/ds60sqlpy/module_service.py`, `src/ds60sqlpy/coaching.py`
- Contains: `LabServer`, `ClassroomService`, `ModuleService`, `CoachingService`.
- Depends on: Catalog loaders, execution adapters and state stores.
- Used by: `LabRequestHandler`; the optional MCP adapter uses coaching/catalog services directly.
- Purpose: Resolve stable lesson identities and safe repository-relative authored content.
- Location: `curriculum/`, `courses/`, `python/`, `sql/`, `bridge/`, `src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/lesson_reader.py`
- Contains: Legacy generated catalog inputs, module plans/manifests, lessons, guides, examples and renderers.
- Depends on: Validated paths and authored source files.
- Used by: Classroom APIs, static reader builders, CLI and MCP tools.
- Purpose: Execute legacy Python/SQL pads locally in the app environment, and route authored profile jobs to prepared worker services.
- Location: `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`, `src/ds60sqlpy/worker_operations.py`, `docker/workers/`
- Contains: Bounded pad runners, a profile-to-service map, private HTTP worker client/server, and fixed operation adapters.
- Depends on: Python/database runtime for legacy pads, or selected Docker worker profiles for module jobs.
- Used by: `LabServer.action()` through `src/ds60sqlpy/lab.py` and `ModuleService`.
- Purpose: Keep learner progress and work separate from authored files and worker images.
- Location: `.learning/` at runtime; persistence implementation in `src/ds60sqlpy/state_files.py`, `src/ds60sqlpy/progress.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/classroom_runs.py`, `src/ds60sqlpy/module_jobs.py`
- Contains: Progress, pads/history, append-only execution receipts, module drafts and job receipts.
- Depends on: Local filesystem, file locks and atomic replacement.
- Used by: Classroom and module services.

## Data Flow

### Browser Classroom Action

### Authored Module Worker Job

### Catalog and Static Reader Generation

- Legacy progress is maintained by `ProgressStore`; legacy pads and classroom receipts have separate stores (`src/ds60sqlpy/progress.py`, `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/classroom_runs.py`).
- Module drafts are a separate sidecar in `.learning/modules/`; worker job receipts live below the module state directory (`src/ds60sqlpy/modules.py:360`, `src/ds60sqlpy/module_jobs.py:172`).
- `locked_update()` serializes mutations across threads/processes; `atomic_json_write()` replaces a complete JSON document rather than exposing partial writes (`src/ds60sqlpy/state_files.py:78`, `src/ds60sqlpy/state_files.py:96`).
- Browser preview and offline DAX lesson modes are distinct from server worker jobs (`src/ds60sqlpy/module_service.py:225`, `src/ds60sqlpy/browser_runs.py`, `src/ds60sqlpy/module_drafts.py`).

## Key Abstractions

- Purpose: Immutable in-memory view of `curriculum/catalog.json` and stable legacy identities.
- Examples: `src/ds60sqlpy/catalog.py`, `curriculum/catalog.json`.
- Pattern: Repository-root-aware loader with validated relative content paths.
- Purpose: Separate planned/authored module metadata from legacy lessons; variants are expanded as aliases.
- Examples: `src/ds60sqlpy/modules.py`, `docs/expansion/plans/`, `courses/*/track.json`, `courses/*/lessons.json`.
- Pattern: Declarative plans plus authored manifests; implementation adapters, not manifest commands, define execution.
- Purpose: Own lifecycle and persisted records for one active or unresolved module job, and call only registered private workers.
- Examples: `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`.
- Pattern: Controller/worker boundary over authenticated HTTP with polling and explicit cancellation/recovery.
- Purpose: Map authored content files to their generated reader destinations and rewritten links.
- Examples: `src/ds60sqlpy/lesson_reader.py`.
- Pattern: Build-time mapping with escaped/validated content instead of rendering arbitrary saved HTML.

## Entry Points

- Location: `src/ds60sqlpy/cli.py`, `src/ds60sqlpy/__main__.py`, registered in `pyproject.toml`.
- Triggers: Installed `ds60` console script or `python -m ds60sqlpy`.
- Responsibilities: Catalog, validation, doctor, planning, progress, SQL and local serving commands.
- Location: `classroom`, `scripts/classroom.sh`, `scripts/classroom_images.sh`.
- Triggers: `./classroom` or its documented subcommands.
- Responsibilities: Select/build/start/stop classroom and profile containers; Python app starts through `docker/start_lab.py`.
- Location: `src/ds60sqlpy/mcp_server.py`, registered as `ds60-mcp` in `pyproject.toml`.
- Triggers: Local stdio MCP host.
- Responsibilities: Expose catalog-bounded learning and tutoring tools; it does not run lesson source.

## Architectural Constraints

- **Threading:** The local classroom uses `ThreadingMixIn`; `LabServer` keeps request threads joinable on shutdown and uses an execution lock to serialize direct pad/SQL operations (`src/ds60sqlpy/http_server.py`, `src/ds60sqlpy/lab.py:35`). Worker jobs run through their own controller threads and a worker-side execution thread (`src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`).
- **Global state:** `state_files.py` has a process-local lock registry; `LabServer` lazily holds one `ModuleService` behind a lock (`src/ds60sqlpy/state_files.py:26`, `src/ds60sqlpy/lab.py:74`).
- **Catalog separation:** Do not merge planning placeholders with published legacy lessons or treat planned lessons as authored; the module loader explicitly tracks `planned` versus `authored` (`src/ds60sqlpy/modules.py:322`).
- **Runtime boundary:** Do not encode shell commands in curriculum JSON. Runtime profiles and fixed operation handlers are registered in application code (`src/ds60sqlpy/curriculum_framework.py:1`, `src/ds60sqlpy/worker_operations.py:25`).
- **Persistence boundary:** Keep progress, draft source, and run evidence in their separate stores; receipt reads do not replay work (`src/ds60sqlpy/progress.py`, `src/ds60sqlpy/classroom_runs.py`, `src/ds60sqlpy/modules.py`).
- **Circular imports:** No circular import chain was established in the inspected application import edges; modules use package-qualified imports under `src/ds60sqlpy/`.

## Anti-Patterns

### Treating Planned Lessons as Runtime-Ready

### Putting Runtime Commands in Curriculum Manifests

## Error Handling

- `LabRequestHandler` catches input, I/O and value errors and returns JSON errors (`src/ds60sqlpy/lab.py:511`).
- Worker requests use `WorkerRequestError` with explicit HTTP status; the worker rejects unknown routes and invalid payloads (`src/ds60sqlpy/module_worker.py:50`, `src/ds60sqlpy/module_worker.py:381`).
- Module jobs persist `interrupted`/terminal status and poll existing worker jobs rather than replaying source after uncertain submission (`src/ds60sqlpy/module_jobs.py:341`, `src/ds60sqlpy/module_jobs.py:448`).
- State writes use validation, locks and atomic replacement (`src/ds60sqlpy/state_files.py`).

## Cross-Cutting Concerns

## Evidence

- `src/ds60sqlpy/lab.py`
- `src/ds60sqlpy/classroom_http.py`
- `src/ds60sqlpy/catalog.py`
- `src/ds60sqlpy/modules.py`
- `src/ds60sqlpy/module_jobs.py`
- `src/ds60sqlpy/module_worker.py`
- `src/ds60sqlpy/worker_operations.py`
- `src/ds60sqlpy/state_files.py`
- `curriculum/catalog.json`
- `docs/expansion/plans/`
- `courses/`

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| add-learning-path | Add or extend DS60 lessons, learning paths or execution languages with prerequisite-aware teaching, maintained authoring sources and verified classroom integration. Use for curriculum implementation, not ordinary learner tutoring. | `.agents/skills/add-learning-path/SKILL.md` |
| guide-ds60sqlpy-learning | Help a learner start, resume, understand, practice or review registered DS60 lessons using prerequisites, their actual attempt and progressive hints. Use for course tutoring; use add-learning-path for curriculum changes. | `.agents/skills/guide-ds60sqlpy-learning/SKILL.md` |
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-fast` for a trivial task inline, with no subagents and no PLAN.md
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
