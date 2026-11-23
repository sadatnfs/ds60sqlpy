---
last_mapped_commit: a7b9bee89d73119a71319d41d2bf7ec2fefffc8e
last_mapped_at: 2026-11-23
---
<!-- refreshed: 2026-11-23 -->
# Codebase Structure

**Analysis Date:** 2026-11-23

## Directory Layout

```text
ds60sqlpy/
├── src/ds60sqlpy/             # Python application, curriculum adapters and bundled UI
│   ├── assets/                # Classroom HTML/CSS/JS and vendored offline assets
│   └── spark_likelihood/      # App-distributed likelihood implementation
├── courses/<subject>/         # Subject guides, source, manifests, tests and authoring
├── curriculum/                # Generated legacy catalog and extension/quality metadata
├── docs/                      # Contributor, setup, design and subject-plan documentation
├── python/                    # Original Python curriculum and professional route
├── sql/                       # Original PostgreSQL curriculum and professional route
├── bridge/                    # Python/PostgreSQL integrated curriculum
├── packages/                  # Separately installable scientific packages
├── docker/                    # App, database and profile-worker image/build assets
├── scripts/                   # Catalog/content generators, launcher and validation tools
├── tests/                     # Application tests and shared fixtures
├── lesson-pages/              # Generated static lesson readers
├── reference-pages/           # Generated static reference readers
├── START_HERE.html            # Generated standalone course dashboard
└── pyproject.toml             # Python package, CLI, tooling and test configuration
```

## Directory Purposes

**`src/ds60sqlpy/`:**
- Purpose: Maintained Python application and adapters.
- Contains: CLI, HTTP server, catalog loaders, rendering, coaching, execution, persistence, SQL/module runtimes.
- Key files: `src/ds60sqlpy/cli.py`, `src/ds60sqlpy/lab.py`, `src/ds60sqlpy/catalog.py`, `src/ds60sqlpy/modules.py`.

**`src/ds60sqlpy/assets/`:**
- Purpose: Browser classroom and offline rendering assets shipped with the Python package.
- Contains: Classroom HTML/JS/CSS, isolated browser/plot preview documents, bundled CodeMirror/D3/Plotly/KaTeX and fonts.
- Key files: `src/ds60sqlpy/assets/classroom.html`, `src/ds60sqlpy/assets/classroom.js`, `src/ds60sqlpy/assets/classroom-editor.js`.

**`courses/`:**
- Purpose: Modern subject-based curriculum and authored module content.
- Contains: Kebab-case subject directories with `track.json`/`lessons.json` where used, guides, examples, source, tests and local authoring guidance.
- Key files: `courses/<subject>/README.md`, `courses/<subject>/AGENTS.md`, `courses/<subject>/lessons.json`; the module loader is `src/ds60sqlpy/modules.py`.
- Placement: Add a new subject lesson to its subject tree and register it using the existing plan/manifest contract; do not put runtime commands in JSON.

**`curriculum/`:**
- Purpose: Legacy catalog and extension/validation metadata.
- Contains: `catalog.json` and JSON extension/audit files; `extensions/` holds catalog additions.
- Key files: `curriculum/catalog.json`, `curriculum/extensions/`, `src/ds60sqlpy/catalog_builder.py`.
- Placement: Update source metadata/builder inputs and regenerate the catalog with `scripts/build_catalog.py`; do not hand-edit generated catalog output (`docs/content-authoring.md`).

**`python/`, `sql/`, and `bridge/`:**
- Purpose: Original course roots for Python, PostgreSQL, and combined Python/PostgreSQL lessons.
- Contains: Day-based curricula, professional lessons, guides, solutions, notebooks, fixtures and course-local tests.
- Key files: `python/ds-60day/`, `python/professional/`, `sql/postgres-60day/`, `sql/professional/`, `bridge/lessons/`, `bridge/professional/`.
- Placement: Extend the matching root for legacy tracks; add track metadata through the catalog builder and curriculum extension system.

**`docs/`:**
- Purpose: Product, setup, content-authoring, implementation and research documentation.
- Contains: General docs plus `docs/implementation/`, `docs/learning/`, `docs/setup/`, `docs/research/`, and active plans in `docs/expansion/plans/`.
- Key files: `docs/README.md`, `docs/content-authoring.md`, `docs/implementation/ADDING_A_MODULE.md`, `docs/expansion/plans/`.

**`packages/`:**
- Purpose: Scientific packages with distinct distribution and integration boundaries.
- Contains: `packages/spark-likelihood/` and `packages/spark-tmbad/`, each with package-specific README, source, tests, tooling and integrations.
- Key files: `packages/spark-likelihood/pyproject.toml`, `packages/spark-likelihood/README.md`, `packages/spark-tmbad/README.md`.
- Placement: Keep package dependencies, build tooling and source in the relevant package tree rather than coupling them to the classroom application.

**`docker/`:**
- Purpose: Container definitions and worker/runtime preparation.
- Contains: App entrypoint and health check, database initialization, profile-specific Dockerfiles, native/GPU locks and Kubernetes fixtures.
- Key files: `docker/entrypoint.py`, `docker/start_lab.py`, `docker/workers/`, `docker/init/`, `docker/classroom-images.tsv`.

**`scripts/`:**
- Purpose: Maintainer commands for generation, launch, validation, packaging and CI qualification.
- Contains: Catalog/reader builders, classroom scripts, source tools, checks, release and profile workflows.
- Key files: `scripts/course.py`, `scripts/build_catalog.py`, `scripts/build_lesson_readers.py`, `scripts/classroom.sh`, `scripts/lint-repo`.

**`tests/`:**
- Purpose: Main application and cross-cutting behavior tests.
- Contains: `test_*.py` modules and `tests/fixtures/`; course-specific tests also live under `bridge/` and some subject trees.
- Key files: `tests/`, `bridge/tests/`, `python/professional/tests/`, `sql/professional/tests/`.

## Key File Locations

**Entry Points:**
- `src/ds60sqlpy/cli.py`: Main Python console CLI, including `serve`.
- `src/ds60sqlpy/__main__.py`: `python -m ds60sqlpy` wrapper.
- `src/ds60sqlpy/mcp_server.py`: Optional stdio MCP tutor.
- `classroom`: Docker classroom launcher.
- `scripts/course.py`: Repository contributor command wrapper.

**Configuration:**
- `pyproject.toml`: Package metadata, console scripts, package data and test/tool settings.
- `uv.lock`: Root Python dependency lock.
- `compose.yaml`, `compose.classroom.yaml`, `compose.modules.yaml`: Docker Compose service definitions.
- `docker/classroom-images.tsv`: Profile-to-image inventory.
- `.github/workflows/`: CI and release workflows.

**Core Logic:**
- `src/ds60sqlpy/lab.py`: Unified HTTP application, API action dispatch and legacy execution coordination.
- `src/ds60sqlpy/catalog.py`: Legacy curriculum loader.
- `src/ds60sqlpy/modules.py`: Authored module loader and module draft state.
- `src/ds60sqlpy/module_service.py`: Module application service.
- `src/ds60sqlpy/module_jobs.py`, `src/ds60sqlpy/module_worker.py`, `src/ds60sqlpy/worker_operations.py`: Worker job boundary and runtime.
- `src/ds60sqlpy/lesson_reader.py`: Static and classroom content rendering.

**Curriculum and data:**
- `curriculum/catalog.json`: Checked-in generated legacy catalog.
- `docs/expansion/plans/`: Planned founding subject identities and progression.
- `courses/<subject>/lessons.json`: Authored lesson manifests where the subject uses module manifests.
- `python/`, `sql/`, `bridge/`: Original curriculum sources.

**Testing:**
- `tests/`: Main pytest suite.
- `bridge/tests/`: Bridge-specific tests.
- `python/professional/tests/`, `sql/professional/tests/`: Professional curriculum tests.
- `pyproject.toml`: Pytest roots include `tests`, bridge tests, and professional course tests.

## Naming Conventions

**Files:**
- Python modules use lowercase `snake_case.py`, for example `src/ds60sqlpy/module_service.py`.
- Subject/course directories use kebab-case, for example `courses/data-ml-engineering/`.
- Tests use `test_*.py`, for example `tests/test_module_jobs.py`.
- Runtime manifests use descriptive JSON names such as `lessons.json` and `track.json` under `courses/<subject>/`.

**Directories:**
- Application code is grouped primarily by module/responsibility under `src/ds60sqlpy/`.
- Curriculum is organized by subject under `courses/`, with legacy route roots separated into `python/`, `sql/`, and `bridge/`.
- Deployment and runtime assets are grouped under `docker/` and `docker/workers/`.

## Where to Add New Code

**New Feature:**
- Application implementation: `src/ds60sqlpy/`; place browser UI in `src/ds60sqlpy/assets/`.
- Tests: `tests/`, with a targeted course-local test directory only when it belongs to that curriculum package/root.
- Keep HTTP dispatch in `src/ds60sqlpy/lab.py` and delegate domain behavior to a service/store module.

**New Subject or Lesson:**
- Authored materials: `courses/<subject>/`.
- Subject plan: `docs/expansion/plans/<subject>.json` for a founding-plan workflow; authored registration belongs in the subject manifest.
- Read `docs/implementation/ADDING_A_MODULE.md` and the nearest `courses/<subject>/AGENTS.md` before changing curriculum contracts.

**Legacy Course Extension:**
- Lesson/source files: the matching subtree under `python/`, `sql/`, or `bridge/`.
- Registration/generation: `src/ds60sqlpy/catalog_builder.py`, `curriculum/extensions/`, and `scripts/build_catalog.py`.

**New Standalone Package:**
- Implementation and package-specific tests/tooling: `packages/<package-name>/`.
- Keep its package contract, dependencies and integration docs local to that directory, following `packages/spark-likelihood/` or `packages/spark-tmbad/`.

**Utilities and Generated Readers:**
- Shared application utilities: `src/ds60sqlpy/`.
- Build/validation helpers: `scripts/`.
- Change reader sources/generators, not generated outputs in `START_HERE.html`, `lesson-pages/`, or `reference-pages/` (`docs/content-authoring.md`).

## Special Directories

**`lesson-pages/`, `reference-pages/`, and `START_HERE.html`:**
- Purpose: Checked-in deterministic static readers generated from curriculum sources.
- Generated: Yes; generation is documented in `docs/content-authoring.md` and wired through `Makefile`.
- Committed: Yes; these generated learner-facing artifacts are tracked.

**`src/ds60sqlpy/assets/vendor/`:**
- Purpose: Vendored browser/rendering dependencies and provenance/license metadata.
- Generated: Third-party bundles are vendored; update only through the documented dependency/provenance process.
- Committed: Yes; package data includes assets from this tree (`pyproject.toml`).

**`.learning/` and `.classroom/`:**
- Purpose: Local learner work/progress and per-project launcher settings, respectively.
- Generated: Yes, at runtime.
- Committed: No; `.learning/` and `.classroom/` are local state, not curriculum sources.

**`.agents/skills/`:**
- Purpose: Repository-specific learner tutoring and curriculum authoring guidance.
- Generated: No.
- Committed: Yes.

---

*Structure analysis: 2026-11-23*
