# Technology Stack

**Project:** DS60 Classroom Overhaul; brownfield milestone
**Researched:** 2026-11-23

## Recommended Stack

**Recommendation:** Keep the established stack intact. The all-language content work is a curriculum, renderer, and verification effort - not a reason to introduce another web framework, frontend toolchain, database, or content platform. The only stack evolution recommended is to extend the current pytest-based quality gates across all registered language and subject tracks, using Python’s standard library where small offline content checks are needed.

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11-3.12 (`requires-python = ">=3.11,<3.13"`); classroom image currently uses 3.12.16 | Application, CLI, content tooling, tests | Established runtime with a locked contributor environment and working classroom services. Preserve the supported range; do not broaden or upgrade it as part of content improvement without a concrete compatibility need. |
| Python standard-library HTTP server | Existing implementation | Local classroom control plane and API | Already matches local/offline delivery and existing request-boundary design. Keep `LabServer`/`LabRequestHandler`; no framework migration is warranted. |
| HTML, CSS, vanilla JavaScript | Existing static assets | Desktop browser classroom | Assets are packaged and work without a frontend build or remote asset service. Improve the current UI in place; do not introduce a framework or bundler. |

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL | Existing Compose-managed service; use the repository’s pinned image/configuration | SQL course runtime and learner exercises | It is part of the current SQL learning model. Preserve its current runtime and existing integration boundaries; this content-focused milestone does not justify a database change. |
| `psycopg` | Existing optional `bridge` extra; lock currently resolves 3.3.4 | Python/PostgreSQL integration | Keep it optional and scoped to bridge/SQL integration rather than adding a database driver to the base classroom dependency set. |

### Infrastructure

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Docker Compose | Existing delivery; documented minimum 2.28.0 | Local classroom, database, and selected worker profiles | It is the product’s established offline-capable delivery path. Keep the current Compose files, launch flow, and profiles. |
| Profile-specific Docker workers | Existing worker images and per-worker manifests/locks | Isolated language and specialist runtimes | This is how the classroom offers many languages without installing every toolchain into the app image. Keep the controller/worker boundary and fixed operations; do not consolidate workers or put arbitrary commands in course data. |
| `uv` + `uv.lock` | Existing locked project environment | Contributor dependency resolution | The lockfile and worker-local dependency inputs make builds reproducible. Change them only when a necessary dependency or supported-runtime update is approved. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | Existing quality extra; lock currently resolves 9.1.1 | Automated tests and content-quality gates | Extend existing tests with explicit parametrized cases across the current track/manifest inventory. Avoid introducing a plugin or test framework solely for content coverage. |
| Python `html.parser` | Standard library in supported Python versions | Lightweight offline inspection of generated HTML fragments | Use only for checks such as required headings, links, or code blocks when such checks are useful. It accepts invalid markup and does not check matching start/end tags, so it is **not** a standards-compliance validator or sanitizer. |
| Pygments | Existing core dependency, `>=2.19,<3` | Source-code highlighting | Continue using the packaged implementation for rendered examples; no replacement or new theme pipeline is needed. |
| `latex2mathml` | Existing core dependency, `>=3.81.1,<4` | Offline math rendering | Retain because it supports existing lesson rendering without depending on remote services. |
| Ruff, mypy, pytest-cov, pytest-xdist | Existing `quality` extra | Linting, typing, coverage, and test execution | Continue the repository’s current checks. Add coverage assertions only where they produce useful, actionable all-track feedback. |

**Content-check guidance:** Favor existing catalog/manifest validation and focused pytest checks over introducing a separate CMS, Markdown toolchain, or runtime dependency. A useful next increment is a data-driven test matrix that exercises currently registered tracks and verifies authored lesson paths, required content/metadata, and representative renderer output. Keep checks aligned with authored-versus-planned lesson semantics. Use browser review for actual browser behavior; stdlib parsing alone cannot establish visual or accessibility correctness.

**Optional dependency policy:** Keep notebook, data/ML, production, bridge, and other specialized packages in their existing extras or isolated worker images. They are not prerequisites for reading lessons or starting the core offline classroom.

## What Not to Change

- Do **not** replace the Python standard-library HTTP server with FastAPI, Flask, or another web framework.
- Do **not** replace the hand-authored HTML/CSS/JavaScript UI or add a frontend framework, bundler, package manager, or remote runtime assets.
- Do **not** replace Docker Compose delivery, merge isolated workers into the app image, or move language toolchains into the base install.
- Do **not** change PostgreSQL or the current persistence model as a side effect of curriculum work.
- Do **not** add dependencies for validation that can be handled by the existing pytest suite and standard library. If strict HTML conformance or broad browser automation later becomes an explicit release requirement, evaluate a narrowly scoped, reproducible tool then; do not imply `html.parser` provides either.
- Do **not** move existing optional teaching packages into core dependencies; preserve offline installation size and the separation between classroom control plane and course runtimes.

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Local HTTP server | Keep standard-library server | Adopt FastAPI/Flask | Adds framework surface and migration risk without solving the current all-language content-quality need. |
| Browser UI | Keep vanilla HTML/CSS/JS | Adopt React/Vue/Svelte plus a build chain | No evidence that this milestone needs a second runtime/toolchain; it complicates offline packaging and broadens change scope. |
| Content quality checks | pytest + current validators + targeted stdlib checks | Add a new content framework or plugin stack | Existing tests and catalog/content infrastructure are already in the repository. Prefer expanding them before acquiring new dependencies. |
| Language execution | Keep isolated Docker worker profiles | Install all runtimes in one image or execute manifest commands | Increases image size and weakens the established runtime boundary and fixed-operation model. |
| Specialized packages | Keep optional extras and worker-local dependencies | Make every course library a core dependency | Forces large, platform-sensitive scientific stacks on learners who only need the base classroom. |

## Installation

No new package installation is recommended for this milestone. Use existing project workflows:

```bash
# Contributor quality environment (existing project extra)
uv sync --extra quality

# Learner classroom (existing Docker Compose launcher)
./classroom
```

Do not install the optional teaching extras unless working on those specific lessons or worker profiles.

## Dependencies and Implications

- **Content quality gates:** Add or extend parametrized pytest checks to represent every currently registered language/subject track. Keep fixtures and expected coverage grounded in the catalogs/manifests; distinguish planned material from authored lessons.
- **Rendering:** Validate representative generated output through current renderer tests and desktop browser review. HTML token parsing can support narrow structural assertions but is permissive and not a conformance/security check.
- **Reproducibility:** Retain `uv.lock`, per-worker manifests/locks, Python 3.11/3.12 CI, pinned image inputs, and Compose profiles. Any dependency change should update the correct lock/input and pass existing build/test/release gates.
- **Offline behavior:** Continue packaging UI/vendor assets locally. Avoid newly introduced runtime downloads, external content APIs, CDNs, or hosted build dependencies for the classroom experience.
- **Scope:** The active project requirements call for complete content and classroom improvements across existing tracks. This stack recommendation deliberately leaves application architecture unchanged while enabling quality checks to cover the full catalog.

## Confidence

| Area | Confidence | Notes |
|------|------------|-------|
| Existing stack and constraints | HIGH | Directly grounded in the requested project, stack, and architecture documents and the checked-in `pyproject.toml` details. |
| Minimal stack evolution | HIGH | The repository already has the needed test, render, packaging, and isolation mechanisms; official docs support the proposed narrow use of pytest, `html.parser`, and extras. |
| Exact content validation matrix | MEDIUM | The project goal is clear, but the milestone’s detailed per-track acceptance checks are not part of this stack research. Finalize them with the content inventory and phase requirements. |

## Sources

- Repository baseline: `.planning/PROJECT.md`, `.planning/codebase/STACK.md`, `.planning/codebase/ARCHITECTURE.md`, and `pyproject.toml` (reviewed 2026-11-23).
- [Python 3.12 `html.parser` documentation](https://docs.python.org/3.12/library/html.parser.html); official scope and limitations of `HTMLParser`. **Confidence: MEDIUM** (official source, retrieved and cross-checked).
- [pytest: How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html); official parametrization guidance. **Confidence: MEDIUM** (official source, retrieved and cross-checked).
- [Python Packaging User Guide: Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) and [`pyproject.toml` specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/); official optional-dependency/extras guidance. **Confidence: MEDIUM** (official sources, retrieved and cross-checked).
