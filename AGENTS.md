# Repository guidance for coding agents

## Mission and first steps

Maintain one local Docker classroom at `/classroom` for programming, data
science, statistics, machine learning and systems. The current library has 22
subjects; derive lesson IDs, variants and readiness from the catalog loaders,
not a copied inventory. Historical day numbers are stable labels, not a deadline.

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md), and the closest
subject `AGENTS.md`. Inspect `git status --short --branch` and preserve unrelated
work. Use the user's requested checkout and parallel agents with explicit file
ownership. Respect existing task authorization; do not add a separate approval
step for ordinary authorized edits. Git publication, image publication, history
rewrites and destructive cleanup have distinct scopes. Do not use em dashes.

## Choose the right role

- For explanation, placement, debugging or resuming study, use
  [Guide learning](.agents/skills/guide-ds60sqlpy-learning/SKILL.md).
- For new or extended lessons, subjects or runtimes, use
  [Add a learning path](.agents/skills/add-learning-path/SKILL.md).
- For application work, begin with the [repository tour](docs/repository-tour.md)
  and [current architecture](docs/implementation/CHECKPOINT.md).

A tutoring request is not automatically a request to implement curriculum,
replace a learner's attempt, run code or mark completion. Inspect the actual
lesson and learner-provided work, explain one mechanism, and offer progressive
hints. Reveal practice references when requested or when the chosen review
explicitly includes comparison. The statistics book exposes worked answers
without exams or solution gates. A read marker or reference run is not mastery.

The optional MCP adapter reads checked-in curriculum by default and does not
execute code. Its module tools do not read Docker-volume pads or results.
Do not claim to have inspected unseen learner state. Use a learner-provided
attempt or an authorized workspace/UI interface. Progress writes need the
adapter's opt-in and the learner's instruction. Preserve authorization already
given for the current task rather than asking repeatedly.

## Maintained sources

| Concern | Source |
| --- | --- |
| Startup, resume and image selection | `classroom`, `scripts/classroom.sh`, `scripts/classroom_images.sh`, `docker/classroom-images.tsv` |
| Product composition and runtime preparation | `compose.classroom.yaml`, `compose.modules.yaml`, `docker/workers/`, reviewed optional overlays |
| Unified directory, editor and preview | `classroom.py`, `assets/classroom.*`, `browser_runs.py` |
| Historical Python/SQL/bridge identity | `catalog_builder.py`, source artifacts, `curriculum/extensions/`, generated `curriculum/catalog.json` |
| Original five module plans | `module_plans.py`, `docs/expansion/plans/` |
| Additive subjects and variants | `courses/<subject>/track.json`, `lessons.json`, `modules.py`, `module_extensions.py` |
| Statistics tutorial | `courses/statistics-ml/manifest.json`, `coverage.json`, chapters and examples |
| Jobs, execution and results | `module_jobs.py`, `module_service.py`, `worker_operations.py`, `classroom_runs.py`, `lab.py` |
| Static/live reading | `lesson_reader.py`, `reader_math.py`, `reader_content.py`, `classroom_http.py`, `http_server.py` |
| Tutoring and legacy progress | `mcp_server.py`, `coaching.py`, `study_plan.py`, repository skills |
| Portable source packaging | `course_paths.py`, `scripts/course_payload.py`, `scripts/build_starter.py` |
| Authoring and verification | [content contract](docs/content-authoring.md), [module contract](docs/implementation/ADDING_A_MODULE.md), [validation](docs/validation.md) |

Python filenames without a full path are beneath `src/ds60sqlpy/`.
Do not recreate retired desktop executables, native editor-launch APIs or a
second Python/SQL/module UI. Local contributor `ds60 serve` uses the same
classroom shell; Docker remains the supported learner delivery route.

## Authoring and extension

Define the learner's starting point, direct prerequisites, observable outcome
and evidence before selecting a lesson count. Teach vocabulary and syntax before
using them. Include at least two explained worked cases, meaningful mistakes,
bounded fixtures and concrete next steps. Practice should progress from tracing
to modification, independent work, debugging and transfer. Avoid generic repeated
paragraphs that merely satisfy a heading or exercise counter.

Keep stable lesson IDs, prerequisite relationships, variant aliases and saved
state namespaces. The legacy practice baseline is immutable; additions use its
separate expansion registry. Modern modules use their own admission contracts.
The statistics book is a tutorial with complete examples and answered discussion,
not a practice module with hidden answers or mandatory problem sets.

Read the subject's `authoring/README.md` when present. Edit its durable source,
run only the relevant generator, format generated executable code, then refresh
shared readers. Directly authored subjects retain their documented artifact
sources. `make generate` refreshes shared metadata and readers; it does not run
every subject generator. Never hand-edit `START_HERE.html`, `lesson-pages/` or
`reference-pages/`.

Write mathematics with `\(...\)` or `\[...\]` and code in accurately tagged
fences. Preserve literal program characters. Rendering and highlighting must
work offline. Prose normalization and statistics-example fence synchronization
have reviewed contracts; they cannot change executable meaning or create new
runtime evidence. Use UTF-8 and LF for generated repository text.

A subject, language and runtime are different concepts. Prefer an existing
reviewed profile when it fits. New profiles need fixed operations, dependencies,
formatting/lint support, image/launcher registration, actual failure/success
checks and saved-work acceptance. A lexer or manifest alone does not create an
executor. See [the extension playbook](docs/curriculum-extension-playbook.md).

## Runtime and learner-state invariants

Use Linux containers on Linux/macOS and Windows through WSL 2. Ordinary learners
need no host compilers or database installation. Keep the thin Docker launchers;
do not add native Windows backends, ACL machinery or executable-build gates.
Separately prepared contributor SQL/Jupyter tools and genuine external projects,
such as Swift/Xcode, have their own documented boundaries.

`./classroom` is resume-first: reuse saved selection and existing images and
containers, preparing only missing images. `resume` and `--no-build` never build
or pull. `--rebuild` deliberately installs source/configuration updates; `build`
prepares images without starting. Hub mode pulls its declared version and never
falls back to a local build. Keep the same custom `--project NAME` on later
commands. Do not change a project or engine to hide a startup defect.

Launcher preferences under `.classroom/<project>/` are separate from named
learning, PostgreSQL and private-runtime volumes. Preserve all learner state.
A normal resume reuses containers; an automatically changed browser port can
require recreating only the app from its existing image for exact Host/Origin
checks. That is not an image rebuild. Fixed port choices preserve a stable URL;
applying changed port settings uses the explicit update route.

Save or retain recoverable drafts before changing context. Keep source, notes,
results and history separate by lesson, language/variant and SQL mode. Reading
a past result must not rerun code or replace the current pad. Unknown job outcomes
must be reconciled without replay. A receipt-save failure must report the real
execution result and a storage warning.

HTML/CSS and JavaScript/D3 previews are opaque, offline browser observations.
Live preview requires an explicit current-page opt-in, debounces edits, preserves
editor focus and does not automatically create immutable receipts. Manual Run
or explicit Save observation captures submitted source. Navigation, Stop,
history selection and reload must not silently resume execution. PHP CLI uses
`main.php` and PDO SQLite; real HTTP/session work belongs to the separate owned
web fixture. Do not label request models as actual browser/server exchanges.

CUDA reading and CPU models are useful without NVIDIA hardware. Optional GPU
workers stay outside default/`--all`, require explicit device selection and a
real allocation/kernel/readback probe. Compilation, GPU correctness, profiling
and multi-GPU operation are separate evidence. A Mac container does not turn an
Apple GPU into CUDA. GPU Spark needs compatible components and actual supported
operator/plan evidence. Never reset a shared GPU automatically after a fault.

The classroom runs trusted local learner code, not arbitrary hosted tenants.
Preserve Host, origin, token, path, request/output-size, process and resource
checks. Publish ports to loopback; use `http_server.py` to avoid reverse-DNS
startup dependencies. Keep worker COPY lists aligned with imports. Manifests
cannot supply shell commands, compiler flags, endpoints or host paths.

Kubernetes needs explicitly owned resources, reviewed operations, no ambient
kubeconfig and bounded UID-aware cleanup. Ordinary workers never receive an
engine socket. Optional packages, external services and model/data downloads
require deliberate preparation; opening a lesson must not fetch them.

SQL automation targets only the explicitly disposable local
`advanced_sql_training` database, validates routing, uses a private credential
environment and invokes `psql -X -v ON_ERROR_STOP=1`. Resetting `training` is
destructive. Preserve declared stateful lesson sequences and never redirect
checks to shared or valuable data. Fakes prove policy, not PostgreSQL behavior.

## Verification and handoff

Use focused checks during implementation and [the release gates](docs/validation.md)
for the actual change. The shared entrypoints are:

```sh
./scripts/format-repo --check
./scripts/lint-repo
uv run --no-sync python scripts/check_modules.py
uv run --no-sync python scripts/course.py validate
uv run --no-sync python scripts/build_lesson_readers.py --check
uv run --no-sync python -m pytest -n 4 --dist loadgroup
git diff --check
```

These `uv` commands require the prepared contributor environment from
[CONTRIBUTING](CONTRIBUTING.md). Keep `--dist loadgroup` for shared database
fixtures. Bound parallelism and keep large Docker builds sequential when disk
or memory is constrained. Do not weaken assertions or rewrite expected behavior
to conceal a failure. Do not rerun expensive successful checks without a new
change or unresolved concern.

Report source checks, unit tests, actual runtime execution, browser delivery,
container recreation and hosted CI separately. Record exact source/revision and
platform; name skips and unavailable hardware. Historical receipts and
source-format parity records remain immutable. They do not qualify new behavior.
Do not place machine-specific image IDs, ports, temporary paths or test-session
counts into maintained onboarding instructions.

For a genuinely prose-only authorized push, GitHub's `[skip ci]` spelling is
available under the [documented constraints](docs/validation.md#optional-documentation-only-ci-skip).
It must not hide implementation, examples, dependencies, workflows or other
unvalidated commits. A skipped check is not a passed check.

Portable payloads exclude learner state, credentials, caches, local logs and Git
history. Preserve source licenses and use neutral public/synthetic examples.
Review the chosen repository-local public commit identity without exposing
private identity values. Git pushes do not authorize Docker Hub publication.
The publisher previews by default; the manual publication workflow requires all
image qualification before its protected publish phase. See [Docker Hub](docs/dockerhub.md).
Cleanup only owned task resources, and retain learner volumes unless their
deletion was explicitly requested. Do not prune unrelated resources or rewrite
history as incidental cleanup.
