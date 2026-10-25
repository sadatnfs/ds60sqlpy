# Repository tour

DS60 is one local classroom for programming, data, statistics, machine learning
and systems. Start learning with [the front README](../README.md) and
`./classroom`. Start development with [CONTRIBUTING](../CONTRIBUTING.md), then
read the closest `AGENTS.md`. All learner subjects share `/classroom`; historical
day numbers and module IDs remain stable labels rather than a fixed schedule.

## Follow one lesson through the system

1. **Authoring sources** define teaching, metadata, learner code and references.
   Some subjects generate bundles from `courses/<subject>/authoring/`; others
   maintain artifacts directly. Read that subject's guidance before editing.
2. **Catalog loaders** validate identities, prerequisites, artifact paths and
   admitted runtimes. Python/SQL/bridge use the legacy catalog. Modern subjects
   use module plans and authored manifests. The statistics book has a separate
   tutorial contract.
3. **The shared classroom** derives its directory and navigation from those
   loaders. It loads guides, preserves independent pads/notes/variants, and
   exposes only the selected lesson's actual capabilities.
4. **Execution** uses a fixed prepared worker, a bounded legacy operation, or an
   opaque browser preview. Reading mode is a real learning mode without a Run
   operation. Content metadata cannot choose arbitrary commands.
5. **Results and progress** retain source identity. Reading a previous result
   never reruns it. Browser observations, worker verification and self-reported
   completion remain distinct evidence.
6. **Static readers** render the same material offline. They provide navigation
   and readable source; they do not install dependencies or launch host programs.

## Source map

| Area | Maintained files and directories |
| --- | --- |
| Learner entrypoint and resume | `classroom`, `scripts/classroom.sh`, `scripts/classroom_images.sh` |
| Linux container composition | `compose.classroom.yaml`, `compose.modules.yaml`, `docker/` |
| Image distribution catalog | `docker/classroom-images.tsv`, `scripts/publish-images`, [Docker Hub guide](dockerhub.md) |
| Shared UI and directory | `src/ds60sqlpy/classroom.py`, `src/ds60sqlpy/assets/classroom.*` |
| Browser observations | `src/ds60sqlpy/browser_runs.py` and the preview code in `classroom.js` |
| Python/SQL/bridge artifacts | `python/`, `sql/`, `bridge/` and their subject guidance |
| Legacy metadata | `catalog_builder.py`, `catalog.py`, `curriculum/extensions/`, generated `curriculum/catalog.json` |
| Core module plans | `module_plans.py`, [five maintained plan files](expansion/README.md) |
| Additive module routes | `courses/<subject>/track.json`, `lessons.json`, `modules.py`, `module_extensions.py` |
| Tutorial book | `courses/statistics-ml/manifest.json`, `coverage.json`, chapters and examples |
| Jobs, worker operations and limits | `module_jobs.py`, `module_service.py`, `worker_operations.py`, profile adapters |
| Legacy classroom execution | `lab.py`, `execution.py`, `classroom_runs.py` |
| State and learner exports | Runtime storage adapters, `state_files.py` and [backup instructions](one-command-classroom.md) |
| Reading and HTTP boundaries | `lesson_reader.py`, `reader_math.py`, `reader_content.py`, `classroom_http.py`, `http_server.py` |
| Contributor CLI and tutoring | `cli.py`, `mcp_server.py`, `coaching.py`, `study_plan.py`, `.agents/skills/` |
| Source/workspace packaging | `course_paths.py`, `scripts/course_payload.py`, `scripts/build_starter.py` |
| Quality and CI | `tests/`, `scripts/check_*`, formatting/lint wrappers, `.github/workflows/` |

Bare Python filenames in the table are under `src/ds60sqlpy/`. Inspect current
loaders instead of copying a historical lesson count:

```sh
python scripts/course.py catalog
python scripts/check_modules.py --json
```

The current library has 22 subjects, but execution profiles are not a subject
count. Several languages share a worker; CUDA combines reading, CPU and optional
GPU variants. HTML/CSS and JavaScript/D3 run in browser previews, while PHP CLI
and the separately prepared HTTP fixture have different contracts.

## Generated, maintained and private files

Do not hand-edit `START_HERE.html`, `lesson-pages/`, `reference-pages/` or the
legacy `curriculum/catalog.json`. Run a changed subject's documented generator
first, format its source output, then use `make generate` for shared views.
Read [content authoring](content-authoring.md) and [validation](validation.md)
for the complete order and check modes. Not every generator supports `--check`;
use only its documented command.

`.learning/` is local learner/contributor state; Docker uses named volumes for
its own learning data, PostgreSQL and private runtime state. `.classroom/`
records launcher selection and image preferences, not a full data backup.
Reuse the same project and engine to resume. Build outputs, caches, logs,
credentials and Git history do not belong in the portable source ZIP.
Historical runtime receipts are immutable observations. Formatting-equivalence
records explain reviewed source drift; they are not fresh execution receipts.

## Select a safe development loop

Use `./classroom` for prepared Docker behavior, `./classroom resume` for strict
no-build/no-pull startup, and `./classroom --rebuild` for deliberate source or
configuration updates. Optional GPU workers require compatible NVIDIA hardware
and explicit selection. Ordinary `--all` excludes them and the owned-cluster
adapter. A container build cannot prove hardware readiness.

A contributor can serve the same UI with
`python scripts/course.py serve --no-browser` in the prepared Python environment.
It reports actual local capabilities and does not create workers or import Docker
progress. The native desktop executable, private editor-launch API and separate
module/portal applications have been retired. Windows learners and contributors
use WSL 2 for the Linux Docker route.

Use focused behavioral tests first, then the relevant
[release gates](validation.md). The full Python suite uses
`python -m pytest -n 4 --dist loadgroup` so shared database tests remain grouped.
A UI or runtime change also needs actual prepared-worker/browser checks with
disposable state. Preserve learner volumes and unrelated containers.

For new learning paths, follow the [authoring skill](../.agents/skills/add-learning-path/SKILL.md).
For tutoring, use [learning with a companion](learning-with-an-ai-tutor.md).
The [implementation checkpoint](implementation/CHECKPOINT.md) records durable
architecture and operational constraints, not a past developer's session state.
