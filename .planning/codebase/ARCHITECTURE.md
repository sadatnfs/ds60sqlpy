---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# Architecture

**Analysis Date:** 2026-11-23

## System Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│ Browser UI: `src/ds60sqlpy/assets/classroom.html` and JS assets   │
│ `/api/lab` · `/api/classroom` · `/api/modules`                   │
└───────────────────────────────┬──────────────────────────────────┘
                                │ local HTTP; session token, Origin on mutations
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│ Application/control plane: `src/ds60sqlpy/lab.py`                │
│ `LabRequestHandler` → `LabServer.action`                         │
├───────────────────┬──────────────────┬──────────────────────────┤
│ Legacy classroom  │ Unified classroom │ Authored module service  │
│ `classroom.py`    │ `classroom_runs.py`│ `module_service.py`     │
│ coaching, SQL and │ views and receipts │ catalog, drafts, jobs    │
│ local pad runs    │                   │                          │
└─────────┬─────────┴─────────┬────────┴────────────┬─────────────┘
          │                   │                     │
          ▼                   ▼                     ▼
┌────────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│ Legacy curriculum  │ │ Local `.learning`│ │ Private profile      │
│ `curriculum/`      │ │ progress/pads/   │ │ workers              │
│ `python/`, `sql/`, │ │ receipts/modules │ │ `module_jobs.py` →   │
│ `bridge/`          │ │                 │ │ `module_worker.py`   │
└────────────────────┘ └─────────────────┘ └──────────┬───────────┘
                                                       │ fixed profile
                                                       │ operations
                                                       ▼
                                            `worker_operations.py`
                                            + Docker worker images
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

**Overall:** Local Python modular monolith/control plane with explicit profile-specific worker services; curriculum authoring and runtime implementation are separate.

**Key Characteristics:**
- `LabServer` is the single local application host; `LabRequestHandler` dispatches the three API families to catalog-bound actions (`src/ds60sqlpy/lab.py`).
- The legacy `Catalog` and authored `ModuleCatalog` are distinct loaders. `ClassroomService.index()` merges their learner-facing views without merging their registration or persistence contracts (`src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/classroom.py`).
- Modern module plans come from both the five founding plans and subject `track.json` files; the statistics tutorial book has its own authored manifest (`src/ds60sqlpy/module_plans.py`, `src/ds60sqlpy/module_extensions.py`).
- Planned subjects/lessons are not automatically executable. Authored manifests bind validated content paths to runtime profiles, while reviewed Python adapters implement execution (`src/ds60sqlpy/modules.py`, `src/ds60sqlpy/curriculum_framework.py`).
- UI JavaScript, CSS, HTML, and vendored offline rendering assets ship as package data (`src/ds60sqlpy/assets/`, `pyproject.toml`).
- The optional MCP process is a separate stdio adapter for catalog/coaching reads and explicitly gated progress, not the classroom execution API (`src/ds60sqlpy/mcp_server.py`).

## Layers

**Presentation and HTTP:**
- Purpose: Serve the browser classroom and enforce request boundary checks.
- Location: `src/ds60sqlpy/lab.py`, `src/ds60sqlpy/classroom_http.py`, `src/ds60sqlpy/http_server.py`, `src/ds60sqlpy/assets/`
- Contains: `LabRequestHandler`, shared base request handling, static assets and browser actions.
- Depends on: Application services and package resources.
- Used by: The local browser session started through `ds60 serve` or the Docker classroom.

**Application and curriculum services:**
- Purpose: Turn validated API actions into catalog, coaching, rendering, progress and execution operations.
- Location: `src/ds60sqlpy/lab.py`, `src/ds60sqlpy/classroom.py`, `src/ds60sqlpy/module_service.py`, `src/ds60sqlpy/coaching.py`
- Contains: `LabServer`, `ClassroomService`, `ModuleService`, `CoachingService`.
- Depends on: Catalog loaders, execution adapters and state stores.
- Used by: `LabRequestHandler`; the optional MCP adapter uses coaching/catalog services directly.

**Curriculum and rendering:**
- Purpose: Resolve stable lesson identities and safe repository-relative authored content.
- Location: `curriculum/`, `courses/`, `python/`, `sql/`, `bridge/`, `src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/lesson_reader.py`
- Contains: Legacy generated catalog inputs, module plans/manifests, lessons, guides, examples and renderers.
- Depends on: Validated paths and authored source files.
- Used by: Classroom APIs, static reader builders, CLI and MCP tools.

**Execution and runtime:**
- Purpose: Execute legacy Python/SQL pads locally in the app environment, and route authored profile jobs to prepared worker services.
- Location: `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/sql_runner.py`, `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`, `src/ds60sqlpy/worker_operations.py`, `docker/workers/`
- Contains: Bounded pad runners, a profile-to-service map, private HTTP worker client/server, and fixed operation adapters.
- Depends on: Python/database runtime for legacy pads, or selected Docker worker profiles for module jobs.
- Used by: `LabServer.action()` through `src/ds60sqlpy/lab.py` and `ModuleService`.

**Persistence:**
- Purpose: Keep learner progress and work separate from authored files and worker images.
- Location: `.learning/` at runtime; persistence implementation in `src/ds60sqlpy/state_files.py`, `src/ds60sqlpy/progress.py`, `src/ds60sqlpy/modules.py`, `src/ds60sqlpy/classroom_runs.py`, `src/ds60sqlpy/module_jobs.py`
- Contains: Progress, pads/history, append-only execution receipts, module drafts and job receipts.
- Depends on: Local filesystem, file locks and atomic replacement.
- Used by: Classroom and module services.

## Data Flow

### Browser Classroom Action

1. `serve_lab()` constructs `LabServer`, initializes legacy services and serves the UI (`src/ds60sqlpy/lab.py:47`, `src/ds60sqlpy/lab.py:542`).
2. `LabRequestHandler.do_GET()` returns package UI assets and injects the per-session token into the classroom page (`src/ds60sqlpy/lab.py:419`).
3. The browser posts JSON to `/api/lab`, `/api/classroom`, or `/api/modules`; the handler applies token/Origin checks and selects an action family (`src/ds60sqlpy/lab.py:511`).
4. `LabServer.action()` routes classroom actions to `ClassroomService`, module actions to a lazily created `ModuleService`, and legacy actions to coaching/pad/SQL services (`src/ds60sqlpy/lab.py:136`).
5. Services resolve lesson IDs against the relevant catalog, render registered files, run an explicit operation, and return a JSON result (`src/ds60sqlpy/classroom.py:145`, `src/ds60sqlpy/module_service.py:225`).

### Authored Module Worker Job

1. `ModuleService.action()` resolves an authored lesson and calls `ModuleJobs.start()` for `module-run`; draft-only and browser-only profiles are rejected from worker execution (`src/ds60sqlpy/module_service.py:225`).
2. `ModuleJobs` saves a practice draft, checks profile readiness, writes a job record, and submits the fixed profile/source/language contract through `WorkerClient` (`src/ds60sqlpy/module_jobs.py:341`).
3. `WorkerClient` calls the explicit private endpoint with the worker token; `WorkerHandler` validates and submits to `WorkerState` (`src/ds60sqlpy/module_jobs.py:79`, `src/ds60sqlpy/module_worker.py:381`).
4. `worker_operations.py` chooses the registered `WorkerProfile`/adapter, bounds execution, then worker status is polled and persisted as a module job receipt (`src/ds60sqlpy/worker_operations.py:25`, `src/ds60sqlpy/module_jobs.py:448`).

### Catalog and Static Reader Generation

1. `scripts/build_catalog.py` invokes the catalog builder to assemble legacy lessons and curriculum extensions into `curriculum/catalog.json` (`src/ds60sqlpy/catalog_builder.py:1323`, `src/ds60sqlpy/catalog_builder.py:1409`).
2. `ModuleCatalog` separately loads founding plans from `docs/expansion/plans/`, additive subject plans from `courses/*/track.json`, and authored manifests/content from subject trees; `courses/statistics-ml/manifest.json` registers its tutorial book (`src/ds60sqlpy/module_plans.py:63`, `src/ds60sqlpy/module_extensions.py:285`, `src/ds60sqlpy/modules.py:105`).
3. Reader-generation scripts use the catalog and `lesson_reader.py` to generate checked-in static outputs (`Makefile:21`, `src/ds60sqlpy/lesson_reader.py:34`).

**State Management:**
- Legacy progress is maintained by `ProgressStore`; legacy pads and classroom receipts have separate stores (`src/ds60sqlpy/progress.py`, `src/ds60sqlpy/execution.py`, `src/ds60sqlpy/classroom_runs.py`).
- Module drafts are a separate sidecar in `.learning/modules/`; worker job receipts live below the module state directory (`src/ds60sqlpy/modules.py:360`, `src/ds60sqlpy/module_jobs.py:172`).
- `locked_update()` serializes mutations across threads/processes; `atomic_json_write()` replaces a complete JSON document rather than exposing partial writes (`src/ds60sqlpy/state_files.py:78`, `src/ds60sqlpy/state_files.py:96`).
- Browser preview and offline DAX lesson modes are distinct from server worker jobs (`src/ds60sqlpy/module_service.py:225`, `src/ds60sqlpy/browser_runs.py`, `src/ds60sqlpy/module_drafts.py`).

## Key Abstractions

**Legacy `Catalog` and `Lesson`:**
- Purpose: Immutable in-memory view of `curriculum/catalog.json` and stable legacy identities.
- Examples: `src/ds60sqlpy/catalog.py`, `curriculum/catalog.json`.
- Pattern: Repository-root-aware loader with validated relative content paths.

**`ModuleCatalog` and `ModuleLesson`:**
- Purpose: Separate planned/authored module metadata from legacy lessons; variants are expanded as aliases.
- Examples: `src/ds60sqlpy/modules.py`, `docs/expansion/plans/`, `courses/*/track.json`, `courses/*/lessons.json`.
- Pattern: Declarative plans plus authored manifests; implementation adapters, not manifest commands, define execution.

**`ModuleJobs` / `WorkerClient`:**
- Purpose: Own lifecycle and persisted records for one active or unresolved module job, and call only registered private workers.
- Examples: `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`.
- Pattern: Controller/worker boundary over authenticated HTTP with polling and explicit cancellation/recovery.

**`ReaderTarget`:**
- Purpose: Map authored content files to their generated reader destinations and rewritten links.
- Examples: `src/ds60sqlpy/lesson_reader.py`.
- Pattern: Build-time mapping with escaped/validated content instead of rendering arbitrary saved HTML.

## Entry Points

**`ds60` command:**
- Location: `src/ds60sqlpy/cli.py`, `src/ds60sqlpy/__main__.py`, registered in `pyproject.toml`.
- Triggers: Installed `ds60` console script or `python -m ds60sqlpy`.
- Responsibilities: Catalog, validation, doctor, planning, progress, SQL and local serving commands.

**Docker classroom launcher:**
- Location: `classroom`, `scripts/classroom.sh`, `scripts/classroom_images.sh`.
- Triggers: `./classroom` or its documented subcommands.
- Responsibilities: Select/build/start/stop classroom and profile containers; Python app starts through `docker/start_lab.py`.

**Optional MCP tutor:**
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

**What happens:** A planned lesson is used as if it has authored guide/source files and an admitted runtime.
**Why it's wrong:** Plans deliberately hold identities/progression separately; `ModuleCatalog.get()` accepts only authored lessons (`src/ds60sqlpy/modules.py:317`).
**Do this instead:** Add/validate the authored manifest and content under `courses/<subject>/`, with a registered profile contract in `src/ds60sqlpy/modules.py` and `src/ds60sqlpy/worker_operations.py`.

### Putting Runtime Commands in Curriculum Manifests

**What happens:** A course manifest is expanded to choose arbitrary commands or shell arguments.
**Why it's wrong:** The curriculum framework explicitly states manifests register teaching content; executable adapters are reviewed application code (`src/ds60sqlpy/curriculum_framework.py:1`).
**Do this instead:** Bind authored lessons to an existing runtime profile; implement new fixed execution behavior in `src/ds60sqlpy/worker_operations.py` and matching worker/deployment files under `docker/workers/`.

## Error Handling

**Strategy:** Validate request/catalog/runtime contracts at boundaries and convert expected failures to bounded learner-facing HTTP or CLI errors.

**Patterns:**
- `LabRequestHandler` catches input, I/O and value errors and returns JSON errors (`src/ds60sqlpy/lab.py:511`).
- Worker requests use `WorkerRequestError` with explicit HTTP status; the worker rejects unknown routes and invalid payloads (`src/ds60sqlpy/module_worker.py:50`, `src/ds60sqlpy/module_worker.py:381`).
- Module jobs persist `interrupted`/terminal status and poll existing worker jobs rather than replaying source after uncertain submission (`src/ds60sqlpy/module_jobs.py:341`, `src/ds60sqlpy/module_jobs.py:448`).
- State writes use validation, locks and atomic replacement (`src/ds60sqlpy/state_files.py`).

## Cross-Cutting Concerns

**Logging:** Local app request logs are concise; worker access logs omit request content, tokens and learner paths (`src/ds60sqlpy/classroom_http.py:151`, `src/ds60sqlpy/module_worker.py:420`).
**Validation:** Stable lesson/profile allowlists and repository-contained content paths are checked in `src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/curriculum_framework.py`, and `src/ds60sqlpy/modules.py`.
**Authentication:** Local API calls require the session token and exact Host; mutating API calls also require the expected Origin (`src/ds60sqlpy/classroom_http.py:158`). Worker calls use a distinct private worker token (`src/ds60sqlpy/module_jobs.py:106`, `src/ds60sqlpy/module_worker.py:440`).

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

---

*Architecture analysis: 2026-11-23*
