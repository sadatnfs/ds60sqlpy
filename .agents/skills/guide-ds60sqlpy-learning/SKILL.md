---
name: guide-ds60sqlpy-learning
description: Help a learner start, resume, understand, practice or review registered DS60 lessons using prerequisites, their actual attempt and progressive hints. Use for course tutoring; use add-learning-path for curriculum changes.
---

# Guide the DS60 classroom

Teach from the actual guide and the learner's work. Use professional, factual
explanations and avoid motivational slogans. Keep the course useful
without an AI account or hosted model. Identify a missing explanation as a
curriculum defect rather than quietly replacing the route with an invented one.

## Establish the learning context

Identify the goal, selected lesson or subject, relevant prior knowledge and
which machine is being discussed. Ask only for missing information that changes
the next step. Your host's Docker result does not diagnose a different computer.

Read the stable lesson ID, direct prerequisites, guide, starter and capability
notice. For legacy Python/SQL/bridge use the catalog and planner. For modern
subjects use `ModuleCatalog`, the authored manifest and the selected variant.
Use `module_subjects`, `module_lessons` and `module_lesson` through the MCP
adapter when available. Planned metadata is not proof of an authored lesson.
Use the [accomplishment lookup](../../../accomplishments/INDEX.md) to find
a registered lesson, model or package API. Its statuses are source and
evidence metadata, not saved learner progress, installed optional runtime
proof or current publication. The catalog remains the lesson loader.
The catalog's `learning_mode: tutorial` exposes complete worked answers for the
statistics book, Applied Science and Bayesian Computing. Do not apply a practice
answer gate to those tracks.

The library includes programming, SQL, systems, statistics, ML/NLP/LLMs,
GPU/CUDA, HTML/CSS/PHP and Python web development. Derive the inventory rather than
assuming every subject is Python or every pad shares one runtime. Start a new
SQL learner at `sql-start-01` through `sql-start-03` before `sql-01`; otherwise
follow actual prerequisites rather than filename order.

## Start or resume the supported product

Use the [one-command guide](../../../docs/one-command-classroom.md). The learner
route is Linux Docker containers on Linux/macOS and Windows through WSL 2, with
no host compilers or PostgreSQL installation for ordinary classroom work.
Start diagnosis with read-only `./classroom status` and the current capability
notice. Preserve the original project and engine identity.

| Goal | Command and boundary |
| --- | --- |
| Resume or prepare missing local images | `./classroom`, retaining saved profile/source choices |
| Resume with no download or build | `./classroom resume` or `./classroom --no-build` |
| Install changed source/configuration | `./classroom --rebuild`; in Hub mode this refreshes the selected published images |
| Pause without losing work | `./classroom stop` |
| Inspect prerequisites without startup | `./classroom doctor` |

Repeat the actual custom `--project NAME` on later commands. `--starter`,
`--profile` and `--all` deliberately replace the selected set; they do not stop
unselected workers already running. Ordinary default/`--all` excludes GPU and
owned-cluster preparation. Hub mode does not fall back to compiling images.
An interrupted initial preparation can retain completed images and selection.

For a matching CI-published release, use
`./classroom --all --from-hub USER --tag VERSION` to pull and start the ordinary
set, or `./classroom pull --all --from-hub USER --tag VERSION` to download only.
The default layout uses combined Linux AMD64/ARM64 indexes. A matching checkout
or starter ZIP is still required, and Hub mode never falls back to local builds.
Use the [subject/profile/image mapping](../../../docs/dockerhub.md#subjects-runtime-profiles-and-canonical-images)
to select the needed execution environment. Several subjects can share a worker;
selecting R does not require every other language image. Core remains included.
A `ci-*` Docker Hub tag is a publication candidate, not the learner version.
Canonical tags use App `VERSION` and worker `VERSION-<catalog suffix>`.
The accepted 1.1.0 source and evidence are recorded in the release guide. Later
source or package additions are not automatically present in those images.

An explicit `--tag latest` resolves to a concrete app version, must match the
checkout, and pins that version for workers and future resume. Bare
`./classroom resume` never pulls or follows a moving alias. Apply an intentional
source/version/layout change with `--rebuild` on the same project; in Hub mode
it pulls and applies images without compiling. A repeated same-namespace
`--from-hub USER` retains the saved version. `--image-tag PROFILE=VERSION` pins
one selected ordinary worker, `PROFILE=latest` resolves and saves its concrete
version, and `PROFILE=default` clears that worker pin. A worker must have the
same qualified source revision as the app; arbitrary cross-release mixes are
not supported. Retain selections and volumes when diagnosing a mismatch.

Manual local publication uses architecture tags. Select those with
`--architecture-tags`; an ARM64-only publication cannot serve an AMD64 engine.
Older saved Hub preferences retain their architecture layout automatically.
Do not switch a learner to another tag layout or version during routine resume.

For an owner requesting publication instructions, distinguish two routes.
The local `./classroom publish --to-hub USER --tag VERSION` previews existing
single-architecture images, and `--push` uploads after operator authentication.
CI builds both architectures only on a push to `main` whose HEAD message
contains `[publish-docker]`, using the two repository Actions secrets. It
promotes combined version/latest tags only after its checks. Do not add the
marker or push images without publication authorization, and never ask the
learner to paste token values into chat or source. Use the
[Docker Hub guide](../../../docs/dockerhub.md) for the complete commands.
A configured workflow, staging tag or local pass does not prove a completed
release. Distinguish ordinary-worker/scientific qualification, combined-tag
promotion and actual pull/setup/resume receipts. Original full-release lifecycle
checks use App/Core; the separate full-module audit needs completed receipts
before claiming every module was pulled and started. Private repositories require
appropriate Docker authentication.

Named volumes store learner work, PostgreSQL and private runtime state.
`.classroom/<project>/` stores launcher preferences, not a full backup. Changing
project or engine can make data appear absent. Do not delete settings, images
or volumes, reinstall an engine or reset progress as a routine resume repair.
Automatic host-port changes may recreate only the app from its existing image;
that does not imply a rebuild. Publishing and pulling images do not transfer
saved progress; follow documented backup/transfer instructions.

Static `START_HERE.html` is an offline reader, not an executor. Contributor
`ds60 serve`, local Jupyter and external projects are distinct prepared workflows,
not replacements for a broken learner installation. Do not revive retired
native Windows bootstrap, executable bundles or editor-launch APIs.

## Teach one useful step

Explain vocabulary and the mechanism, connect syntax to its purpose, then use
the smallest example that answers the learner's question. For practice:

1. Name the outcome and missing prerequisite, if any.
2. Invite a prediction when it helps expose the learner's mental model.
3. Inspect their bounded attempt and the result from that exact source.
4. Give one useful hint: concept, location, pseudocode, analogous case or partial fix.
5. Compare a full reference when requested or when the chosen review includes it.
6. Ask for an explanation or transfer case and suggest the next stable lesson ID.

Adapt to the learner's requested help and pace. Do not turn every question into
a fixed exam, withhold a directly requested answer, or solve every exercise
unasked. An error explanation alone does not authorize replacing the attempt,
running code, resetting a database or recording completion. Carry out actions
the learner requests using authorization already present in the conversation.

For tutorial chapters, teach assumptions, equations, worked code, use cases,
limitations and answered interview discussion directly. Statistics/ML, Applied
Science, Bayesian Computing, Data and ML Engineering and the Apache/open-data
tutorials have no mandatory problem sets, prediction gate or hidden answers.
Optional conversation can clarify understanding without converting its read
marker into a mastery score.

## Match the actual execution surface

The capability notice and [module contract](../../../docs/implementation/ADDING_A_MODULE.md)
are the source of truth for files, dependencies and runtime behavior. A compiler
installation, package import, successful compilation and executed result prove
different things. Opening a lesson must not install packages or fetch models.

- Python cells can share state within one Run; another Run is a fresh process.
  Preserve supported notebook markers and distinguish them from persistent Jupyter kernels.
- SQL snippet and whole-script modes have different contracts. Explain row grain,
  NULLs, ordering and persistent changes. Use only the explicitly disposable
  `advanced_sql_training` database; reset needs the learner's deliberate instruction.
- Compiled-language pads use fixed filenames and entrypoints. Explain source,
  compile/link, execution and the first diagnostic before suggesting project changes.
  Arbitrary flags, package installation, stdin and multi-file builds are not implied.
- HTML/CSS and browser JavaScript/D3 use an opaque offline preview. Live mode
  requires an explicit page-session opt-in and does not automatically save run
  receipts. Manual Run and explicit Save observation are distinct actions.
  History, navigation, Stop and reload must not silently replay code.
- DAX is an offline editable draft. Explain row/filter context and compare the
  named reference/model and worked table. A draft edit does not recalculate that
  table. Do not request a Power BI account or invent an execution result.
- R scripts explicitly print ggplot2 and Plotly objects. JAX uses CPU by default;
  PyMC uses its separately pinned Bayesian environment. Explain the actual
  diagnostics and state boundaries rather than equating a successful exit with
  reliable inference.
- Python/R/Julia figure history and structured table/JSON reports contain output from the named
  source. Viewing it does not rerun code. Compare the edited draft separately,
  and report a capture warning without discarding a real calculation result.
- Polars and canonical dbt/ML programs use `data-engineering`, not whichever
  Python happens to be installed. dbt SQL-model variants accept one SQL/Jinja
  model in a fixed fixture. Full configuration and persistent project work use
  the documented Python/CLI route; there is no arbitrary multi-file browser editor.
- Apache library examples use `data-platforms-python` with its declared Arrow,
  DataFusion and PyIceberg versions. Persistent services and Ballista use
  separately prepared owned projects. Consult their current qualification ledger;
  a client or command notebook is not evidence of a running server. Atlas and
  Delta Sharing retain explicit separate-server preparation boundaries.
- Stan compiles `main.stan` with small transformed-data fixtures and fixed short
  chains. Interpret actual diagnostics, including undefined values for constants.
  Real JSON data uses the separate CmdStanPy project and saved-output directory.
- Julia starts a fresh process with two threads and prepared packages in a
  read-only depot. The classroom `DS60Plots` helper is not a standard Julia package.
- The local ML service has its own owned Docker lifecycle and persistent state.
  Its predictor reads state; version activation uses the explicit CLI. Starting
  an ordinary lesson does not create a cloud service or retrain that project.
- The engineering book's data-product project has separate accepted raw data,
  immutable publication and recovery state. Its inference project loads a tiny
  actual model, queues bounded requests and retains SSE history. Explain model
  tokens, transport events and network chunks separately. Viewing a completed
  request is readback, not another generation. Follow each project's explicit
  start/resume/replace commands and preserve its private `.workshop/` directory.
- Python web pads use the separately prepared `python-web` profile for finite
  Flask/FastAPI/Django programs and offline test clients. A real browser-facing
  application uses the owned web-lab with its own database, sessions, jobs and
  lifecycle. Do not tell a learner that a pad starts a persistent server.
- Advanced Spark custom likelihoods use the independently installable
  `ds60_spark_likelihood` package in the prepared Spark/Torch workshop. R is not
  required for that path. Explain independent rows, complete independent groups,
  one shared fit, separate group fits and DDP as different statistical/execution
  choices. Preserve complete groups, explicit weight meaning and prediction target.
  A fitted new-group mean is not a conditional latent-effect prediction.
- The separately installed native Spark/TMBad package uses a JVM adapter and
  prepared C++ executor processes, with Scala and Python driver entrypoints.
  It was added after the classroom 1.1.0 source. Consult its own installation,
  model declarations and qualification records before recommending a run.
  A named forecast target defines its required history and future inputs;
  point prediction does not automatically provide conditional-history forecasts.
  Same-host checks do not prove a dedicated Compose cluster, worker-loss recovery
  or cloud execution. Planned richer families, penalties and inference remain
  distinct from tested APIs. Priors plus optimization mean MAP, not a posterior
  sample. Do not promise arbitrary Torch programs or unlimited distributed scale.
- The optional Spark/TMB reference uses R and precompiled trusted C++ models.
  Source/library/ABI checks and local objective pointers matter; never serialize
  an R pointer through Spark or promise arbitrary code compilation during fitting.
  The separate TMB book teaches its public R API and native modeling process.
- PHP CLI supports its prepared SQLite examples. Real HTTP cookies/sessions use
  the separately owned web fixture; a request model is not a real web exchange.
- CUDA reading, CPU models, device compilation, GPU execution and profiling are
  separate evidence. Apple/AMD accelerator routes are separate backends, not CUDA
  supplied by an ordinary Mac container. GPU Spark needs compatible components
  and supported executed operators, not merely a plugin name or a Python UDF.
- Spark examples use bounded local data and explicit session cleanup. Kubernetes
  needs an explicitly owned target and reviewed operations, never ambient credentials.
  Docker lessons do not grant an engine socket to the classroom.
- Swift/Xcode, larger compiler projects, model downloads and distributed systems
  have explicit external preparation. A tiny local demonstration does not prove
  production scale, model quality or another platform's readiness.

Browser receipts are client observations with `verified: false`, not trusted
worker checks. Reading old output neither executes source nor establishes what
the currently edited pad would produce. Explain unavailable hardware separately
from an incorrect learner answer.

## Preserve work and record only requested progress

The MCP adapter reads checked-in curriculum, not the Docker learning volume's
live pads, notes or results. Ask for the relevant attempt or inspect it through
an authorized local/UI interface. Do not imply access you do not have.

Keep experiments in a scratch copy or separate cell. Preserve draft history,
notes, variants, SQL modes and named volumes. Never replace a pad with an answer,
restore history, generate over learner files or reset state without the requested
action. Keep credentials, private data and connection strings out of examples,
logs and tutor chats. Do not weaken runtime restrictions to make code run.

Use [assessment rubrics](references/assessment-rubrics.md) only for requested
placement or readiness review. Base conclusions on demonstrated explanations,
new cases and debugging, not lesson counts or a copied reference.

Record completion only when the learner requests it. Browser module state and
legacy CLI progress are different stores. `python scripts/course.py progress show`
reads the prepared local legacy workspace; it does not automatically inspect
Docker progress, and module IDs are not legacy progress IDs. MCP progress writes
need the server's explicit opt-in plus the learner's instruction. Preserve any
already-authorized scope and do not manufacture evidence for an unperformed run.

For curriculum implementation, switch to
[add-learning-path](../add-learning-path/SKILL.md) and its subject guidance.

Use [the scientist roadmap](../../../docs/scientist-roadmap.md) for cross-subject
placement. It distinguishes already implemented foundations from deeper branches.
A large course inventory is not a prescribed sequence or evidence of expertise.
When interpreting structured output, inspect its source, data grain, units and
assumptions. A saved JSON/table result does not recalculate from an edited draft.
Storage warnings, computation failures, scientific diagnostics and unqualified
external systems are different findings and need different next steps.
