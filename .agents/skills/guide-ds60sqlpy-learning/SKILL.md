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
The statistics book's `learning_mode: tutorial` exposes complete worked answers.

The library includes programming, SQL, systems, statistics, ML/NLP/LLMs,
GPU/CUDA and HTML/CSS/PHP web development. Derive the inventory rather than
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

Named volumes store learner work, PostgreSQL and private runtime state.
`.classroom/<project>/` stores launcher preferences, not a full backup. Changing
project or engine can make data appear absent. Do not delete settings, images
or volumes, reinstall an engine or reset progress as a routine resume repair.
Automatic host-port changes may recreate only the app from its existing image;
that does not imply a rebuild. Follow documented backup/transfer instructions.

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

For tutorial chapters, teach assumptions, equations, worked Python, use cases,
limitations and answered interview discussion directly. The statistics book
has no mandatory problem sets, prediction gate or hidden answers. Optional
conversation can clarify understanding without converting its read marker into
a mastery score.

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
- Python/R figure history contains captured images or chart data from the named
  source. Viewing it does not rerun code. Compare the edited draft separately,
  and report a capture warning without discarding a real calculation result.
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
