# Learn with an AI companion

The classroom works without an AI account. A companion can explain a difficult
paragraph, help diagnose your code, review an answer or plan a learning route.
It should work from the actual lesson and your attempt, preserving your pace and
saved work rather than replacing the course with an unrelated tutorial.

## Start with the same classroom

Clone or unpack the source and follow the [front README](../README.md).
Run `./classroom` in the repository to reuse your saved selection and prepare
only missing images. Use `./classroom resume` when you want no download or build,
`./classroom stop` to pause, and the same `--project NAME` for a custom workspace.
Windows uses WSL 2 and a Linux-container engine. Ordinary lessons need no host
compiler or PostgreSQL installation.

All subjects share the classroom home. Select the subject, lesson and variant
you want, read its capability notice, and use its separate pad, notes and result
history. Reading a saved result never reruns code. The static `START_HERE.html`
library is useful for offline reading, but it does not execute your programs.
See [the launcher guide](one-command-classroom.md) for storage and recovery.

## Give a companion useful context

Open this repository in your coding assistant and ask it to use the checked-in
[learning skill](../.agents/skills/guide-ds60sqlpy-learning/SKILL.md). Assistants with
repository skill support can use it directly; other tutors can read the same Markdown.
Subject guidance and lesson-specific tutor prompts supply the teaching contract.
A companion should respect authorization you already gave for the current task.

For example:

```text
Use $guide-ds60sqlpy-learning for sql-start-01. I am new to SQL and am using
./classroom in Docker. Read the guide and prerequisites, explain row grain,
and help me interpret my attempt below. Give one hint at a time and keep my
work unchanged unless I ask for an edit.
```

For a CUDA chapter:

```text
Use $guide-ds60sqlpy-learning for cuda-001. I am on a CPU-only machine.
Explain the GPU execution model in detail and use the reading/CPU route.
Distinguish a CPU model, successful compilation and real device execution.
```

Include the stable lesson ID, selected runtime/variant, your question, the
relevant source and exact output or error. Remove credentials and private data.
The guide's “Ask an AI tutor” panel already provides paths and prerequisites.
A screenshot may help with layout; code and errors are usually easier to inspect
as text. A companion cannot see an unshared pad just because it can read the repo.

## Choose the amount of help

Ask for an explanation, conceptual hint, line-by-line review, analogous example,
full worked solution or readiness discussion. A useful practice sequence is to
predict a result, try a small change, inspect the observed evidence and explain
why it happened. A full reference is available when you ask; the tutor should
not overwrite your attempt or mark completion merely because the reference runs.

Statistics/ML, Applied Science and Bayesian Computing use tutorial mode:
theory, complete examples, use cases and answered discussions remain available
without exams or hidden answers. Ask questions at any depth. Reading progress is a personal marker,
not a claim of mastery.

If you are missing a prerequisite, ask for its stable lesson ID and one concrete
reason it will help. You can switch paths at any time. Historical day numbers
are labels, not a required timetable. A learner starting SQL from nothing should
use `sql-start-01` through `sql-start-03` before `sql-01`.

## Know what a result establishes

- Compiled languages have distinct source, compilation/linking, execution and
  diagnostic stages. The pad has fixed filenames and prepared dependencies;
  larger projects follow their explicit external instructions.
- HTML/CSS and JavaScript/D3 previews are real isolated browser documents.
  Their saved observations are client evidence, not trusted server verification.
  Live preview is opt-in for the current page and does not create receipts for
  every edit. Manual Run and Save observation have explicit meanings.
- PHP CLI examples and the separate local HTTP/session project teach different
  execution environments. An HTML string printed by PHP is not an HTTP response.
- CUDA reading and CPU models work without NVIDIA hardware. GPU execution,
  profiling and multi-GPU behavior require a separately qualified environment.
  Apple/AMD accelerators use other backends; they are not CUDA in a Mac container.
- Local Spark, CPU training and tiny language-model examples explain mechanisms.
  They do not establish cluster performance, pretrained-model quality or useful
  subject-matter answers. Ask what would have to be measured next.
- SQL changes can persist, and Kubernetes operations affect explicitly owned
  resources. A tutor must not reset data or use ambient cluster credentials to
  repair an ordinary lesson error.

## Optional MCP integration

The local MCP server exposes checked-in curriculum, guides, prerequisites and
reference discovery. Its module tools are read-only and do not execute code.
It does **not** automatically read Docker-volume drafts, notes or saved jobs.
Share the relevant attempt, or explicitly authorize an available workspace/UI
interface to inspect it. Do not confuse catalog access with access to your work.

Prepare the contributor Python environment only if you want this integration;
it is not a prerequisite for learning in Docker. Follow [MCP setup](mcp-tutor.md) for
the exact executable and server arguments. The server defaults to read-only.
Optional legacy progress writes require its explicit opt-in and your instruction.
Legacy CLI/MCP progress and Docker module progress are separate stores.

## Preserve your learning history

Ask the companion to keep experiments in a scratch copy or separate cell, retain
notes and drafts, and explain any proposed reset or cleanup. Named volumes hold
Docker learning data; `.classroom/` only stores launcher preferences. Switching
project or engine can make existing state appear missing. Use the documented
backup/export workflow before moving machines.

If the explanation is missing from the course itself, report the stable lesson
ID and the gap. For a requested curriculum improvement, the companion can switch
to the [authoring skill](../.agents/skills/add-learning-path/SKILL.md), update the
durable source and verify it. Tutoring and course implementation remain distinct
roles, and the course should become clearer for the next learner too.

For scientific placement, use [the maintained roadmap](scientist-roadmap.md).
A companion should distinguish PyMC from the native Stan pad, the Stan JSON-data
project from its single-source pad, dbt SQL models from a full project, and the
ML service's persisted state from classroom progress. Ask it to identify the
actual source and evidence behind a saved chart, table or JSON report. None of
these tools grants automatic access to your private project state.
