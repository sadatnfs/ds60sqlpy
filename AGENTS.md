# Repository guidance for coding agents

## Mission and scope

Maintain a self-contained, beginner-friendly learning library and one local
Docker classroom at `/classroom`. Teach programming, data science, statistics,
machine learning and systems through accurate explanations and reproducible
examples. Historical day numbers are stable labels, not a curriculum limit.

Read [README.md](README.md), [CONTRIBUTING.md](CONTRIBUTING.md) and the closest
nested `AGENTS.md` before editing. Run `git status --short --branch` and preserve
unrelated changes. Work in the requested checkout. Do not stage, commit, push,
create another checkout or publish images unless that is part of the request.
Use parallel agents for independent work with explicit file ownership. Do not
use em dashes in authored prose.

## Find the maintained source

| Concern | Source |
| --- | --- |
| Learner setup and persistence | `classroom`, `scripts/classroom.sh`, `compose.classroom.yaml`, `docs/one-command-classroom.md` |
| Unified UI and subject directory | `src/ds60sqlpy/classroom.py`, `src/ds60sqlpy/assets/classroom.html`, `.css`, `.js` |
| Legacy Python, SQL and bridge identity | `catalog_builder.py`, lesson artifacts, `curriculum/extensions/`, generated `curriculum/catalog.json` |
| Module route and prerequisites | Original five plans in `docs/expansion/plans/`; additive subjects in `courses/<subject>/track.json` |
| Authored module admission | `courses/<subject>/lessons.json`, `modules.py`, `module_extensions.py` |
| Statistics tutorial book | `courses/statistics-ml/manifest.json`, `coverage.json`, chapters and examples |
| Saved work and execution | `lab.py`, `classroom_runs.py`, `module_service.py`, `module_jobs.py`, `worker_operations.py`, `browser_runs.py` |
| Static and live document rendering | `lesson_reader.py`, `reader_math.py`, `reader_content.py` |
| Read-only tutoring context | `mcp_server.py`, `coaching.py`, `study_plan.py` |
| Content rules and expansion | `docs/content-authoring.md`, `docs/implementation/ADDING_A_MODULE.md` |
| Architecture and current limits | `docs/implementation/CHECKPOINT.md` |
| Verification and CI | `docs/validation.md`, `.github/workflows/`, focused tests |

Python module filenames in this table are beneath `src/ds60sqlpy/` unless a
full path is given. Derive inventories from the loaders. Do not maintain a
second lesson list in UI code or documentation that could be generated.

Two repository skills are available:

- [Guide learning](.agents/skills/guide-ds60sqlpy-learning/SKILL.md) for tutoring,
  placement, explanation and learner-directed progress.
- [Add a learning path](.agents/skills/add-learning-path/SKILL.md) for adding or
  extending a subject, language or tutorial sequence.

## Act as a learning companion

For a learner's question, use the repository learning skill before proposing
curriculum or application changes. Read the current guide, prerequisites and
learner-provided attempt. Start with explanation and read-only diagnosis; do not
turn a request for help into edits, execution, a reference-solution reveal or a
completion write. Carry out actions the learner actually requests, while
preserving their source, notes, history and chosen pace. Give progressive hints
and the smallest useful next step. Read markers and successful reference runs
are not mastery assessments.

All twenty registered subjects share this companion approach: Python,
PostgreSQL, the engineering bridge, statistics/ML, C, C++, Go, C#, Rust, Swift,
Docker, Java, JavaScript/TypeScript with D3, Kubernetes, Scala/Spark, TensorFlow,
PyTorch, NLP, LLM theory and applied LLMs. Derive exact lesson IDs and capability
notices from the current loaders and guides. Keep tutorial-book discussion free
of mandatory exams or withheld worked answers. Do not assume the MCP adapter
can read the Docker classroom's saved pads or execute code; its module tools
read checked-in curriculum only. Ask the learner to share the relevant attempt,
or inspect the workspace through an authorized local interface.

## Teaching and authoring

Keep lessons useful without an AI tutor. Define vocabulary before use, explain
syntax and mechanisms, show at least two focused worked examples and their
expected observations, diagnose common mistakes, and provide concrete next steps.
Practice lessons progress from prediction to guided change, independent work,
debugging and transfer. Keep learner artifacts, executable references and
explanatory solutions separate. Give progressive hints before revealing answers,
unless the learner explicitly requests the solution.

The statistics/ML book has `learning_mode: tutorial`. It teaches theory,
assumptions, worked code, use cases and answered interview discussion without
exams, problem sets, prediction gates or hidden solutions. Its read marker is
not a mastery assessment. Use coverage and numerical-example checks for this
book, not practice exercise-count rules.

Preserve stable lesson IDs, prerequisite graph, variant IDs and saved-state
namespaces. The legacy practice baseline is immutable. New legacy catalog
lessons use `curriculum/practice_expansion.json`; module subjects use their own
content gates. Do not apply the legacy registry to every module or tutorial.
Every practice guide has a lesson-specific `## Ask an AI tutor about this lesson`
block; the source prompt must match its actual ID and artifact paths.

Find an existing subject's `authoring/README.md` before editing generated
content. Edit the durable authoring source as well as its published artifact,
then run only the relevant subject generator. `make generate` refreshes shared
catalogs, reports and readers; it does not regenerate every subject's prose.
Never hand-edit `START_HERE.html`, `lesson-pages/` or `reference-pages/`.

Use explicit `\(...\)` or `\[...\]` LaTeX for mathematics and tagged code fences.
Keep literal program syntax in code. Rendering must preserve copied characters,
escape source, and work without a CDN. After authoring generation, run the
reviewed prose normalization before building HTML. A typography edit must not
change executable reference behavior or manufacture new runtime evidence.

## Execution and learner state

Docker with Linux containers and Compose is the supported delivery route.
Windows uses WSL 2; macOS and Linux use the same Bash launcher.

Treat `./classroom` as resume-first: use the saved per-project selection and
existing containers/images, building only missing images. `resume` and
`--no-build` must never build or pull; `--rebuild` deliberately installs changed
source/configuration. `build` updates images without starting services. The
launcher saves selection before preparation, so an interrupted initial build
retains its intended profiles. `--starter`, explicit `--profile` flags and
`--all` replace the selection; unselected running workers remain running.
Repeat the learner's custom `--project` on every command. Never guess another
project or silently change the project to repair startup.

Distinguish `.classroom/<project>/` launcher preferences from Docker learning,
PostgreSQL and private-runtime volumes. They are different storage layers.
Inspect `./classroom status` and current engine state before acting. Normal
resume reuses existing containers. Docker may reassign automatic host ports
when the stopped database starts while retaining its ID. If the browser port
changes, only the app is recreated from its existing image to preserve exact
Host/Origin checks; no image build or pull is needed. Database and workers
retain their IDs and all volumes remain intact. Fixed browser and database
ports allow all existing IDs and the URL to remain stable on later unchanged
resumes. Deliberately changing port settings needs `--rebuild`. Missing
containers can be recreated from existing images while retaining volumes.
A configuration mismatch needs the explicit update path. Do not recommend rebuilding every image, deleting
settings, pruning containers or deleting volumes as a routine restart.

No host language compiler is required for ordinary classroom profiles. Validate contributor
setup on Linux, including WSL 2. Retained native setup scripts and executable
builders are unsupported compatibility tooling, not release gates. Do not add
native Windows backend, ACL or executable qualification requirements. Keep the
Windows Docker wrappers that delegate to WSL. Supply OS-specific engine setup
commands only when needed; never label Bash commands as PowerShell.

The classroom executes trusted local learner code. It is not a hosted security
sandbox for arbitrary users. Preserve exact Host, origin, token, request-size,
output-size and filesystem checks. Native servers bind loopback; container
ports publish to loopback. Manifests cannot supply shell commands, endpoints,
compiler flags, cluster identities or host paths. Reviewed backend code owns
runtime profiles and bounded execution.
Use `http_server.py` for local and private-worker HTTP servers so startup does
not depend on reverse DNS. Keep minimal worker Docker COPY lists aligned with
shared imports. Repository text generators must write explicit UTF-8 and LF
newlines so byte-level fixture and regeneration checks remain portable.

Kubernetes host preparation and private credential handling require POSIX paths
and permissions. Windows users run the companion inside WSL 2; native Windows
credential APIs and named-pipe cluster endpoints are unsupported.

A profile name, installed compiler, successful parse and executed lesson are
different evidence. Report the actual capability and never enable Run based
only on metadata. Kubernetes needs an explicitly owned disposable target, no
ambient kubeconfig, and bounded UID-aware cleanup. Model downloads and external
services need deliberate setup; opening a lesson must not fetch them.

Preserve learner pads, source history, notes, progress, saved runs and named
Docker volumes. Save or retain recoverable drafts before changing context.
Keep results scoped by lesson, language and SQL mode. Reading a past result
must not replace current source or run it again. If execution succeeds but
saving its receipt fails, return the actual result and a storage warning.

SQL automation must validate the exact local disposable
`advanced_sql_training` database, reject remote or routing overrides, pass
credentials through a private child environment, and use
`psql -X -v ON_ERROR_STOP=1`. Resetting `training` is destructive even in a
teaching project. Never reset a shared database or erase learner state as a
repair step. Preserve declared multi-lesson transaction and fixture contracts.

The optional stdio MCP adapter has a read-only default and no code execution.
Practice solutions require explicit reveal. Progress writes require the
adapter's opt-in and the learner's instruction. Tutorial worked answers are
available directly. Native portal actions remain a fixed catalog-derived
allowlist; a static page cannot start arbitrary programs.

## Check the work

Use focused checks while iterating, then the relevant integration gates in
[validation](docs/validation.md). Typical commands from a prepared environment:

```sh
python scripts/check_modules.py
python scripts/normalize_lesson_prose.py
python scripts/check_content_rendering.py
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
python scripts/check_published_links.py
node scripts/check_classroom_ui.mjs
python -m pytest -n 4 --dist loadgroup
python scripts/scan_secrets.py --history
python scripts/check_public_release.py
git diff --check
```

Keep `--dist loadgroup` with parallel tests so shared PostgreSQL fixtures stay
serialized. Bound worker count to available resources; keep Docker builds
sequential on constrained machines. Do not suppress failures, relax assertions
or replace expected behavior to obtain a green run.

Report source validation, unit tests, live runtime execution, browser delivery,
and Linux-container CI separately. The release matrix covers Ubuntu core and
contributor checks, PostgreSQL, ordinary Docker workers, Chromium, owned Linux
Kubernetes and the portable source ZIP. A local pass does not prove hosted CI,
WSL installation, a different engine configuration or a different architecture. Record skipped or unavailable surfaces. Never describe
a scan as proof that the repository is bug free. Keep machine-specific logs,
image IDs, ports and temporary paths out of maintained onboarding documents.

## Optional documentation-only CI skip

For an authorized push containing only prose and its regenerated readers, use
GitHub's native `[skip ci]` token, with a space. `[skip-ci]` is unsupported by
this native feature; do not add a custom workflow gate. Never include
unvalidated code, executable lesson examples, tests, runtime/configuration,
dependencies or workflow changes in that push. A skip marker in one pushed
commit must not hide implementation changes in another.

Regenerate readers locally and run prose, rendering, link and whitespace
checks first. See [the exact commands and limitations](docs/validation.md#optional-documentation-only-ci-skip)
and [commit example](CONTRIBUTING.md#optional-ci-skip-for-a-prose-only-push).
The marker affects push/PR triggers, not scheduled/manual or already-running
jobs. Required PR checks may remain Pending; use an unmarked follow-up or an
appropriate manual run under repository policy. Do not report a skip as a pass.

## Publication and cleanup

Portable payloads must exclude `.learning/`, runtime session credentials,
`.classroom/`, model caches, environment files, local logs and Git history.
Preserve public source licenses and required third-party notices. Use neutral
examples without workplace identifiers or private infrastructure references.

Before authorized commits, review the intended public Git identity without
copying private identity values into reports. See the repository-local setup in
[CONTRIBUTING.md](CONTRIBUTING.md). Source and ZIP sanitation do not rewrite
existing author/committer metadata or Git history. Do not change global Git
configuration, rewrite history or publish rewritten branches without a separate
explicit instruction from the repository owner.

Cleanup must be scoped to resources created for this project. Remove containers
and images only when authorized, and inspect ownership first. Keep progress
volumes unless their deletion is explicitly requested. Do not stop unrelated
services, reconfigure an engine or run broad pruning as an incidental cleanup.
