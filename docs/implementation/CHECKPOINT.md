# Expansion implementation checkpoint

Last updated: 22 October 2026. Starting commit: `19b2396`.
Human-managed HEAD advanced to `650d8b1` during implementation; agent work
continues directly on that checkout without staging, commits or pushes.

## Active expansion beyond the previous checkpoint

The user has requested a new implementation phase: complete all five planned
tracks, expand Python/NumPy/pandas/algorithms and SQL, add Java and JavaScript /
TypeScript, and build a detailed statistics/ML tutorial book from the supplied
40-section, 1,005-method outline. The book has worked examples and explained
interview answers, with no exams or problem sets. It requires deeper theory,
assumptions, derivations and failure analysis throughout, not definition cards.

Current ownership: statistics lead owns chapters 1-24, manifest, coverage and
book tests. Systems author finishes and freezes C++ then owns book chapters
25-40. ML author owns remaining TensorFlow/LLM bodies. Root owns new runtimes,
shared catalog/UI/readers/MCP integration, Docker and final acceptance.
Kubernetes/Scala-Spark remaining bodies, Java/JavaScript full authoring and the
18 Python/SQL deeper lessons remain queued. Consult live agents before assigning.
Use main checkout only. Human owns Git staging/commits. Preserve all learner
volumes and unrelated containers. No image publication.

Root added fixed Java21, Node24 and strictly compiled TypeScript5.9 worker
profiles and Docker recipes, and `-pthread` for C++ compilation/linking. Their
runtime acceptance is still in progress. New book integration uses tutorial
mode and never turns reading into an exam or automatic mastery event.

Bounded hourly continuation is configured as heartbeat
`continue-ds60-overnight-implementation`. Inspect this checkpoint and active
agents before resuming; disable it after the entire requested scope passes.
The acceptance numbers below describe the prior checkpoint, not these new
changes. Do not claim the expanded project is fully tested from those numbers.

## PyTorch parity scope addition

The user explicitly requested equally substantial PyTorch and TensorFlow
teaching. Root added the36lesson `deep-learning-pytorch` route and paired
comparison guide. It reuses the prepared `llm-torch-cpu` worker. The ML author
paused Java after001-020 and is now authoring torch-001 through torch-036.
Java021-036 and all JavaScript/TypeScript lessons remain required afterward.

A temporary validation classroom is currently running on localhost58770,
Compose project `ds60-classroom-validation`, with test database port58434.
Only this project may be replaced or stopped; preserve named volumes. The
personal PostgreSQL and unrelated Valkey continue running untouched. Stop the
validation HTTP service and workers after browser checks. No kind cluster exists.

The first expanded image served208authored lessons/chapters across10subjects.
Browser inspection caught nested section headings omitted from the chapter
selector. The shared renderer/UI fix now preserves coverage IDs while showing
human method names, includes nested headings in navigation, and offers a
full-width reading view. Its28JSbehavior checks and2newreader checks pass;
updated image rebuild/browser readback is pending. The latest focused suite
before those two extra checks passed261tests with6host-onlyPyTorch skips, all
of which have separate successful Docker runtime receipts.

## Latest verified implementation checkpoint

The40chapter statistics book is authored with all1,005source methods mapped.
Its82focusedtests pass, including all40offline example programs and embedded
code parity. The24lesson applied LLM route is authored; all23default runnable
references passed actual Docker (17Core,6Torch). The optional pretrained recipe
is documented but no model weights were downloaded or trained.

All27TensorFlow and15LLM-theory PyTorch reference cases now pass in Docker after
repairing three fresh-process examples. Java001-012 all compile/run in Java21.
All41runnable C++ references pass GCC inside Docker using the current adapter
mounted over the previous image; final image rebuild remains required. Both
C++ multi-file CMake/CTest/install fixtures passed as well.

Root owns shared runtime/catalog/reader/UI integration and final acceptance.
NLP001-004 are authored and have8focusedpassingtests; systems author now owns
NLP005-024 after finishing statistics25-40. The ML author finishes applied
status/tests then resumes Java013-036, with JS/TS42 to follow. Statistics author
owns18deeperPythonSQLlessons and its additive manifest. Kubernetes38missing and
Scala/Spark38missing remain queued and required. No one should mark the overall
requested expansion complete until those remaining bodies and full integration
are finished. User's newest priority is very detailed LLM/NLP instruction.

Root UI now has26behavior checks including exact Java/TS diagnostics, tutorial
read markers and topic search. Full expanded image/browser/suite acceptance is
still pending. Build logs and perlesson runtime receipts are in ignored work/.

## Latest LLM and NLP scope addition

The user explicitly requested much more LLM and NLP detail, especially
fine-tuning, RAG, use in data science and training subject-matter assistants.
The ML writer completed TF36/36 and LLM42/42, then paused Java authoring to own
`courses/llm-applied/` with an expanded practical route. Root is preparing
`courses/nlp/` for the systems writer after book25-40. Java36 and JS/TS42 plans
are registered but their content remains queued. They are not finished lessons.
All older requested Python/SQL, Kubernetes and Spark scope remains required.

New runtime evidence: Java, JavaScript and TypeScript compiled/executed and
passed failure/cancellation cases in local Linux arm64 Docker. C++ multi-file
CMake, CTest and install examples passed in the prepared image. The focused
four-worker suite passed139tests before the latest UI/LLM additions. Book
navigation now includes search, section selection and an explicit saved read
marker, with no mastery inference. Additional UI regression checks are pending.

The first real TensorFlow fullreference pass had25successes out of27. Fresh
subprocess checkpoint/export lessons028/032 revealed indentation bugs, now
assigned to the content owner for correction. Do not call that pass all-green.
PyTorch CPU image is built; all15reference cases are running. See ignored
`work/*-all-lessons-acceptance.jsonl`, not prior host skips, for runtime evidence.

## Scope and current result

Work happens directly in `~/workspace/ds60sqlpy`. There are no additional
clones, worktrees, agent commits, pushes or published container images. The
human owns Git staging and commits. Read `git status --short` before resuming.

The five-course design contains 204 planned lessons. The first implementation
batch has **29 authored lesson sets**, with guides, learner sources or
worksheets, separate explained solutions, fixtures and track authoring rules:

| Track | Authored IDs | Still planned |
| --- | --- | --- |
| TensorFlow | `tf-001` through `tf-008` | 28 |
| LLM theory in Python | `llm-001` through `llm-009` | 33 |
| C++ | `cpp-001`, `cpp-002`, `cpp-003`, `cpp-009` | 38 |
| Kubernetes | `k8s-001`, `k8s-002`, `k8s-003`, `k8s-008` | 38 |
| Scala and Spark | `spark-001`, `spark-002`, `spark-003`, `spark-013` | 38 |

The PySpark variant of `spark-013` has its own source, solution and saved pad;
it is not an extra lesson in the count. There are **175 planned lesson bodies
remaining**. Some systems pilots therefore have planned prerequisites. They
are clearly marked pilots, not a complete beginner-to-advanced publication.
The existing 168 published Python/SQL/engineering lessons remain available.

## Implemented application

- `/journeys` renders the authored course guides beside editable pads, prediction
  and explanation notes, explicit solution reveal, structured verification,
  compiler diagnostics, bounded logs and attempt history.
- `/journey-preview` retains the complete planned route. Planned lessons have
  no fake execution or completion action.
- Module state is separate from existing progress: `.learning/modules/` holds
  source, notes, sessions and persisted job receipts on the host. Empty source
  is a valid saved draft. Scala and PySpark drafts remain separate.
- Authenticated same-origin `/api/modules` requests have a separate bounded
  body allowance. Legacy API limits stay unchanged. Runtime endpoints and
  operations are fixed by the host preparation and lesson manifest.
- The optional stdio MCP tutor has four read-only beta tools: subject discovery,
  authored-by-default lesson search, bounded guide/source reads and explicit
  solution reveal. It does not start workers or inspect private pads.
- Jobs are asynchronous and idempotent. Reconnection polls an accepted job;
  it does not replay source. Uncertain cleanup holds admission. A proved new
  CPU worker instance can close an unavailable old receipt as failed; external
  Kubernetes cleanup requires explicit owned recovery.
- The optional local launcher selects profiles, builds sequentially with
  foreground logs, checks local engine/disk prerequisites and reuses host
  learner state. Windows has `START_MODULE_LAB.cmd`; base engine setup remains
  in `START_DOCKER_LAB.cmd` with its WSL 2 walkthrough.

## Runtime boundaries and evidence

See [runtime instructions](../modules-runtime.md), [worker status](worker-status.md),
[ML content status](ml-content-status.md), and
[systems content status](systems-content-status.md).

Fixed private workers implement Python/NumPy, C++20, TensorFlow CPU, standalone
Scala, Spark Scala and PySpark. CPU PyTorch has a separate locked image recipe;
its image/runtime has not been qualified in this batch. The current LLM pilot
uses NumPy and does not require PyTorch. Single-file C++ compilation is
implemented; a browser multi-file CMake project workflow is still future work.

Kubernetes uses an explicitly prepared owned kind cluster, scoped expiring
credentials, pinned fixture image and exact namespace identity. The browser
and workers have no Docker socket or ambient kubeconfig. The one-shot operation
accepts only the fixed bounded hello Deployment and optional Service. It
checks real controller/Pod readiness, matching EndpointSlice Pod UIDs, a fresh
in-cluster version client, and UID-precondition cleanup. Stateful rolling
changes, arbitrary commands and the entire six-task pilot are not automatically
graded. Host preparation/release are separate visible operations.

Actual Linux arm64 Docker proofs and image IDs are recorded in ignored
`work/modules-acceptance/*.json`. Positive and misconception cases have passed
for Python, TensorFlow, C++, Scala and both Spark variants. Kubernetes positive
routing and Deployment-only checks now pass together with unready timeout,
wrong-selector timeout, namespace escape refusal, privilege refusal and active
cancellation, all with the appropriate owned cleanup evidence. A real SIGTERM
test observed four owned objects before stop, zero afterward and exit status
zero in 6.837 seconds. Final image: `sha256:75313e305d1dd216b20e4fc74fa5e7c23fe6ba821cf7833f3f42a01292224200`.
The explicit host release has also passed against a real cluster using its
recorded immutable Docker container ID. No by-name destructive reselection is
used. Test sources and receipts preserve both positive and rejected cases.

This machine's Docker Hub download certificate validation failed. Trusted
cached/GCR inputs were selected with TLS verification retained. Standard
upstream defaults remain portable build inputs; optional base overrides are
supported. No engine trust, VM configuration, unrelated cache or service was
changed. Builds and acceptance are Linux arm64 on this engine, not proof of
Windows, Linux amd64 or native Windows ACL behavior.

## Acceptance resources and stop policy

The user's temporary native preview and personal Docker HTTP app were stopped
at their request. Preserve their `.learning`, personal PostgreSQL volume,
native PostgreSQL 5432 and unrelated containers.

Current test resources belong only to Compose project
`ds60-modules-validation`: browser port 58769, PostgreSQL port 58433 and ignored
host learner folder `work/modules-acceptance/learning`. Private runtime tokens
and Kubernetes receipts are outside `.learning` in a private temporary session.
Never print or package credentials. Read the last non-secret record in
`work/kubernetes-owned-preparation.log` to find the owned session; do not adopt
an ambient cluster or create another session without checking that record.

Stop test HTTP and workers after verification, then explicitly release only
the recorded owned kind session using `scripts/prepare_kubernetes.py release`.
Keep the user's personal HTTP app stopped. Never restart the engine, prune
unrelated resources, delete learner state or stop the user's personal database.

## Resume and next authoring batch

1. Read this checkpoint, owner status files, `git status` and the final receipts.
2. Inspect actual owned test services before starting more. Source/configuration
   alone is not runtime evidence. Check host and engine free disk before builds.
3. Finish any recorded acceptance gap, then run the grouped four-worker suite
   with isolated caches and the disposable PostgreSQL on port 58432. The
   host-only TensorFlow opt-in test is expected to skip when TensorFlow is not
   installed; actual TensorFlow execution must still pass in its worker.
4. Regenerate/check readers and the journey preview after authoring changes.
   Never hand-edit generated HTML or the original published catalog.
5. Fill the missing systems foundations before expanding their intermediate
   stages. Follow `courses/<track>/AGENTS.md`, the per-track `lessons.json`,
   `docs/expansion/architecture.md`, [the module authoring contract](ADDING_A_MODULE.md)
   and publication gates. Each new lesson needs
   a full explanation, vocabulary, worked examples, graded practice, separate
   solutions, meaningful fixtures and appropriate execution checks.
6. Promote a module into the published catalog only after its prerequisite
   chain, runtime and supported platform rows pass their publication gates.
   Do not mark all 204 lessons complete because five pilots execute.

Useful checks: `scripts/check_modules.py`, `scripts/check_module_ui.mjs`,
`build_journey_preview.py --check`, `build_course_guide.py --check`,
`build_lesson_readers.py --check`, Ruff, strict MyPy and `pytest -n 4 --dist
loadgroup`. Build logs use `work/build-*.log`; narrow runtime helpers and
non-secret evidence use `work/modules-acceptance/`.

## Final integration verification

Before the Docker-only entrypoint refinement, the grouped four-worker suite passed **1123 tests**, with **one expected
host-only TensorFlow opt-in skip**, zero failures and zero errors in **89.18
seconds**. All ten recorded subtests passed. Actual TensorFlow import, gradient
verification and rejected update-sign execution passed in its Docker worker.
The disposable PostgreSQL 16 test instance on 58432 was stopped afterward.

The earlier integration run exposed a synthetic-track fixture collision, two
startup-timing assumptions and late generated-reader drift. The fixtures now
preserve the real authored inventory, cancellation waits for observed startup,
normal-parent exit has a real child-readiness/PID handshake, and generated
readers match their sources. No short-timeout proof was removed.

Strict MyPy, Ruff, 22 inline-JavaScript UI behavior
checks, structural validation and notebook syntax checks pass. The first Docker HTTP
audit served 394 HTML pages and 86 canonical/variant module documents,
checking 15584 internal links with zero failures. Browser execution has passed
all five subjects and the separate PySpark variant, with actual typed feedback.
See ignored `work/modules-full-tests*` and `work/modules-acceptance/` for the
exact non-secret runtime receipts. Native Windows execution, Linux amd64 and
the optional PyTorch image remain unqualified.

## Docker-first entrypoint refinement

The user confirmed that an installed Docker engine is the operating-system
prerequisite and PowerShell should be optional. `compose.classroom.yaml` is
therefore the primary ordinary-course entrypoint. It uses no host Python,
PostgreSQL, Bash or PowerShell backend. A no-network one-shot Docker initializer
creates private credentials and local learning volumes, preserving the token
and existing learner files on later starts. Six ordinary qualified profiles
reuse the reviewed worker images. Kubernetes still uses its separate explicit
owned-cluster preparation; opening the classroom does not provision it.

`START_DOCKER_CLASSROOM.cmd` and `.command` are thin optional Docker launchers.
The old host-folder launchers and setup helpers remain compatible and optional.
Classroom progress lives in the machine-local `classroom-learning` Docker
volume; it is separate from the old host `.learning` workflow. Credentials live
in another private volume and are excluded from progress backups. See
[the Docker-only guide](../docker-classroom.md) for build/start/stop, profile
selection and shell-independent backup commands.

Final Docker-only runtime, replacement/backup and image-integrity receipts use
`work/classroom-acceptance/`. The latest grouped suite summary remains in
`work/modules-full-tests-summary.json`; preserve earlier runs when repeating
it. Only actual receipts qualify an OS/architecture or engine mode. Stop the
owned validation project after acceptance and retain its learner volumes.

## Docker-only acceptance result

The complete grouped suite including Docker classroom initialization passed
**1157 tests**, with **one expected host TensorFlow opt-in skip** and no failures
in **62.53 seconds**. All ten recorded subtests passed. Strict MyPy checked
162 files. The initializer/UI review added 35 focused passing cases; the
22 inline JavaScript behavior checks remain green.

Actual Docker Compose 5.3.1 on Linux arm64 started all six ordinary profiles
using only named credential and learning volumes. Every profile became healthy
and passed a reference execution through the browser application's API. A
second initializer run preserved the private token. App, PostgreSQL and worker
containers were replaced; all six lesson sources, notes, accepted job IDs and
hashes remained intact, along with the database marker row. The private token
kept its inode, UID 1000 ownership and mode 0400.

The documented Docker-only learning archive and pg_dump exports passed against
this isolated project. The archive contains sessions and job receipts and
excludes the private runtime token; its source volume was read-only. The dump
contains the marker table. The temporary export helper was removed. Exact
receipts live in `work/classroom-acceptance/`.

The preceding Docker-first HTML audit covered 395 served pages and 86 canonical/variant
module documents, checking 15603 internal links with no failures. The thin
Windows launcher checks for the PostgreSQL image and pulls it on a fresh engine
before offline-only startup. Native Windows launch execution remains untested;
its prepared Docker commands and storage contract are the primary interface.
Kubernetes was qualified separately and all owned kind sessions have been
explicitly released. No unrelated container, personal database or learner
folder was removed.
