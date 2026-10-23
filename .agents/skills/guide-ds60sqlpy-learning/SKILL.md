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

Prefer `./classroom` and the repository's
[one-command guide](../../../docs/one-command-classroom.md). Windows uses WSL 2
with an integrated Linux-container engine. The ordinary Docker route needs no
host Python, PostgreSQL, Java or Node installation. Use `./classroom status`
and the app's selected-profile readiness report to diagnose an existing
workspace. Preserve its project name and volumes. Do not reinstall or
reconfigure an engine merely because a worker is unavailable.

For an explicitly chosen native route, use the documented repository interpreter
and `scripts/course.py doctor`. Static `START_HERE.html` offers offline reading;
it is not an executor. The optional native portal has a fixed action allowlist.
Do not invent an arbitrary browser-to-shell launch.

Choose from the current inventory:

- Python, SQL and bridge: `curriculum/catalog.json`, prerequisite planner and
  the guide's actual paths. Historical days are labels, not a 60-day deadline.
- Modules: `ModuleCatalog`, original plans or additive `track.json`, and authored
  `lessons.json`. Use `module_subjects`, `module_lessons` and `module_lesson` if
  the MCP adapter is available. Planned rows are not proof of authored content.
- Tutorial book: use its `learning_mode: tutorial` contract and complete worked
  chapter/example pairs.

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
- C++ compiles `main.cpp`; Java compiles `Main.java` with public `Main` and no
  package; Node runs `main.mjs`; TypeScript compiles `main.mts`; Scala uses
  `Main.scala` and `object Main`. Use the profile's prepared dependencies.
  Browser DOM APIs are not available in Node.
- Spark requires bounded local data and explicit session cleanup. Kubernetes
  requires an explicitly owned disposable target; never use ambient cluster
  context or credentials.
- Reading-only lessons use reasoning and notes, with no invented execution
  action. Framework and pretrained work needs the declared runtime and local
  assets; tiny offline demonstrations do not establish production quality.

For bridge work, separate parameter binding, transaction ownership, retries,
idempotency and cleanup. Provided fakes test policy; only an explicit disposable
PostgreSQL check proves server behavior. Do not reveal connection strings.

## Preserve the learner's work

Use their current saved source and notes when they ask to resume. Do not replace
a pad with a reference, regenerate a learner-local notebook, delete a volume or
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
progress IDs. For a legacy lesson, the prepared interpreter can run:

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
