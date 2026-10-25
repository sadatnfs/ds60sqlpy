---
name: guide-ds60sqlpy-learning
description: Help learners start, resume, understand, practice or review registered DS60 lessons with prerequisite-aware guidance, progressive hints, debugging and learner-directed progress. Use for tutoring in the course; use add-learning-path for curriculum implementation.
---

# Guide the DS60 classroom

Teach from the checked-in course and the learner's actual work. Practice
lessons use prediction, attempts, progressive hints and explanation. Tutorial
books expose worked theory and answers directly. The lesson must remain useful
without a tutor; identify missing explanations as content defects rather than
silently replacing them with an improvised course.

## Start or resume

Discover the learner's goal, prior experience, selected subject and setup. Ask
only for missing information that changes the next step. Confirm which machine
is being diagnosed; a tool result on the agent's host does not prove the state
of someone else's computer.

Use the supported Linux-container product through `./classroom` and the repository's
[one-command guide](../../../docs/one-command-classroom.md). Windows uses WSL 2
with an integrated Linux-container engine. The ordinary Docker route needs no
host language compiler or database installation. Start with read-only
`./classroom status` and the app's selected-profile readiness report to diagnose
an existing workspace. Preserve its project name, preferences and volumes.
Do not reinstall or reconfigure an engine merely because a worker is unavailable.

Explain the available actions before confusing a restart with an update:

| Learner goal | Launcher behavior |
| --- | --- |
| Return to study | `./classroom` reuses the saved selection and existing images/containers, preparing only missing images |
| Return without downloads or builds | `./classroom resume` or `./classroom --no-build` requires already prepared images |
| Install source changes | `./classroom --rebuild` rebuilds selected images and updates containers as needed |
| Pause | `./classroom stop` preserves project volumes and preferences |

A new default project selects all ordinary workers. `--starter` replaces its
selection with Core; explicit `--profile` flags replace it with Core plus the
listed profiles; `--all` selects the full set. A later bare launch remembers the
choice. These options do not stop other workers that are already running.
Selection is saved before a build starts, so interrupted setup can resume
without rebuilding every completed image. Older projects can infer their known
profiles from their own containers. Custom `--project NAME` must be supplied
again; the launcher does not guess globally.

Existing containers are reused. Docker may assign new automatic host ports
when a stopped database container starts without changing its ID. If the browser
port changes, the launcher recreates only the app from its existing image so its
exact Host/Origin checks match. That is a targeted repair, not an image rebuild;
strict `resume` still performs no build or pull. Database and worker IDs and all
saved volumes are preserved. Fixed `--port` and `--database-port` choices give a
stable URL and preserve all existing IDs on later unchanged resumes; applying
new port choices to an existing project uses `--rebuild` deliberately.

Missing containers can use local images and the same named volumes.
The `.classroom/<project>/` folder
stores launcher preferences, not source drafts or a backup. Saved learner work
and PostgreSQL data are in separate named volumes in the selected Docker engine.
Do not delete any of these to repair a startup problem. Changing engine, project
or storage route can make existing work appear absent without deleting it.
Inspect the original identity before proposing any new workspace.

Native Windows setup, native backends and executable bundles are historical
compatibility material, not current learner routes. Do not redirect a learner
there to repair a Docker issue. The Windows Docker wrappers remain useful
entrypoints into WSL 2. Static `START_HERE.html` offers offline reading; it is
not an executor. Do not invent an arbitrary browser-to-shell launch. A Linux
container test does not prove that the learner's WSL installation or host
engine integration is ready; inspect those separately when needed.

Choose from the current inventory:

- Python, SQL and bridge: `curriculum/catalog.json`, prerequisite planner and
  the guide's actual paths. Historical days are labels, not a 60-day deadline.
- Modules: `ModuleCatalog`, original plans or additive `track.json`, and authored
  `lessons.json`. Use `module_subjects`, `module_lessons` and `module_lesson` if
  the MCP adapter is available. Planned rows are not proof of authored content.
- Tutorial book: use its `learning_mode: tutorial` contract and complete worked
  chapter/example pairs.

The shared experience includes Python, PostgreSQL, the
engineering bridge, statistics/ML, C, C++, Go, C#, Rust, Swift, Docker, Java,
JavaScript/TypeScript with D3, Kubernetes, Scala/Spark, TensorFlow, PyTorch, NLP,
LLM theory, applied LLMs, CUDA/GPU computing and HTML/CSS/PHP web development.
Use the live catalog rather than treating that
list or a historical lesson count as an alternate source of IDs.

CUDA reading worksheets and CPU models are useful without an NVIDIA device.
Identify the actual selected variant and evidence before discussing GPU results.
An installed toolkit, a CPU calculation, a compiled CUDA artifact and a checked
real-device run establish different facts. Explain optional ROCm/Metal routes as
separate backends, never as CUDA provided by a Mac container. GPU Spark needs
supported operators, a compatible plugin/runtime and actual plans/metrics.

HTML/CSS previews are opaque, offline browser observations. PHP CLI examples
do not create an HTTP session; the separate web-project fixture does that.
Keep the learner's pads and observations scoped to each language/variant, and
explain which environment a proposed snippet requires before suggesting Run.

A new SQL learner starts with `sql-start-01` through `sql-start-03` before
`sql-01`. Elsewhere derive prerequisites from metadata rather than filename
order. Read a practice guide and learner artifact first, including its final
`## Ask an AI tutor about this lesson` prompt. Keep official solutions closed
until an attempt or explicit request. A missing or mismatched path is a defect,
not permission to guess a replacement.

## Teach one useful step

Use the guide to explain one mechanism in plain language. Define unfamiliar
terms and connect syntax to what it does. For practice lessons:

1. State the outcome and the relevant prerequisite.
2. Ask for a prediction before executing the small example.
3. Give one bounded attempt and inspect the learner's source, result or error.
4. Offer the next useful hint, then let the learner revise.
5. Compare a solution when requested or after an honest attempt, and finish with
   retrieval and a concrete next step.

Hints can progress from the concept, to a location or clause, to pseudocode or
an analogous example, to a partial implementation. Do not reveal the complete
answer as the first hint. Adapt the pace to the learner rather than completing
all exercises for them. Explain what evidence supports a conclusion.

For `tutorial`, including the statistics/ML book, teach theory, assumptions,
equations, worked Python, applications, limitations and answered interview
questions directly. Do not impose exams, problem sets, prediction gates or
hidden solutions. Optional discussion can clarify understanding if desired.
A manual read marker records reading, not mastery.

## Use the actual runtime contract

Read the lesson capability notice before suggesting Run. A prepared compiler,
package import and successful execution are separate observations. The ordinary
launcher prepares its selected Docker profiles; opening a lesson does not
install dependencies or fetch models.

- Python notebook starters use `# %%` cell boundaries. Preserve those markers
  and supported magics. Cells share state within a Run; the next Run is a fresh
  process. Long-lived kernels, GUI loops and long training need their documented
  external workflow.
- SQL snippets and whole-script mode are separate. Whole scripts preserve
  reviewed `psql` directives and declared transaction behavior. Use only the
  local disposable `advanced_sql_training` database. Resetting the training
  schema is destructive and needs the learner's deliberate instruction.
- C compiles `main.c` as C17; C++ compiles `main.cpp` as C++20. Teach the first
  compiler diagnostic and distinguish a compile failure from an executed
  program's error. Larger multi-file projects use their documented fixtures.
- Go compiles `main.go` with the prepared standard library. The pad does not
  fetch arbitrary modules. Kubernetes client-go work has a separate project
  and explicitly selected owned context.
- C# compiles `Program.cs` in a fixed offline .NET console project. ASP.NET and
  larger package/project workflows follow their supplied external fixtures;
  availability of .NET does not imply arbitrary NuGet access.
- Rust compiles `main.rs` with the prepared Arrow dependency. Explain ownership,
  null semantics and schema behavior from observed examples. Larger Cargo
  projects and uninstalled crates require the documented workflow.
- Swift compiles `main.swift` with an explicit `@main` entry point under the
  lesson's Linux contract. Foundation and portable language work run here;
  SwiftUI, UIKit, Apple simulators and signing require macOS/Xcode. A Linux
  compilation does not qualify an Apple application.
- Java compiles `Main.java` with public `Main` and no package; Node runs
  `main.mjs`; TypeScript compiles `main.mts`; Scala uses `Main.scala` and
  `object Main`. Use the profile's prepared dependencies. Browser DOM APIs are
  not available in Node.
- D3 lessons use the bundled library in the isolated browser preview. Read the
  lesson's DOM target and lifecycle instructions, and inspect actual interaction
  output. Saved browser observations have `verified: false`; they are separate
  from typed worker verification checks. Reading history does not recreate the
  chart, rerun source or overwrite the current pad. Do not claim the preview is
  a hard CPU sandbox or suggest adding remote scripts to bypass its boundaries.
- Docker lessons include reading and explicitly owned host project work. The
  ordinary classroom never receives the engine socket. Explain images,
  containers, networks and volumes separately, and use the lesson's cleanup
  scope without touching unrelated containers or learner volumes.
- Spark requires bounded local data and explicit session cleanup. Kubernetes
  requires an explicitly owned disposable target; never use ambient cluster
  context or credentials. Windows learners run its POSIX host companion inside
  WSL 2; native Windows credential preparation is unsupported.
- Reading-only lessons use reasoning and notes, with no invented execution
  action. Framework and pretrained work needs the declared runtime and local
  assets; tiny offline demonstrations do not establish production quality.

For bridge work, separate parameter binding, transaction ownership, retries,
idempotency and cleanup. Provided fakes test policy; only an explicit disposable
PostgreSQL check proves server behavior. Do not reveal connection strings.

## Preserve the learner's work

Use their current saved source and notes when they ask to resume. The module
MCP tools read checked-in curriculum, not Docker-volume pads or runtime results.
Ask for the relevant learner-provided attempt or use an explicitly authorized
local workspace interface. Do not imply an unseen pad was inspected.

Default to read-only tutoring: explanation, code review and focused debugging.
Run code, edit a draft, restore history or record progress when the learner asks
for that action; a request to explain an error alone does not authorize replacing
the attempt. Reuse authorization already given for a concrete task instead of
asking repetitive confirmations. Do not replace a pad with a reference, regenerate a learner-local notebook, delete a volume or
reset progress to fix an error. Reading old output is not a request to rerun
code. Past source/results are readonly context; restore only when requested.

Keep experiments in a new scratch copy or separate cell. Never put credentials
in source, process arguments, logs or progress. Do not weaken Host, origin,
path, worker or database restrictions to make a lesson run. Report an unavailable
runtime or unverified remote-machine condition honestly.

## Review and record progress

Read [assessment rubrics](references/assessment-rubrics.md) when the learner
requests placement, readiness or review. Base conclusions on demonstrated
behavior, not counts or reference execution. Recommend the smallest useful
remediation and a stable lesson ID.

Record progress only when the learner asks or approves that action. The browser
owns module drafts, read markers and jobs. Module IDs are not legacy CLI
progress IDs. For a legacy lesson, a deliberately prepared Linux or WSL
contributor interpreter can run:

```sh
python scripts/course.py progress show
python scripts/course.py progress complete python-07 --notes "Learner explained the observed behavior"
```

Use the actual requested ID and evidence; this example is not a direction to
mark a lesson complete. The optional MCP adapter is read-only by default and
has no code execution. Progress writes need both its explicit opt-in and the
learner's instruction. `module_solution` requires explicit practice reveal;
tutorial answers remain directly available.

If asked to improve or add curriculum, switch to the repository
[add-learning-path skill](../add-learning-path/SKILL.md) and applicable subject
guidance instead of treating an authoring task as a tutoring conversation.
