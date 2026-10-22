# Add a track without rebuilding the course application

The catalog, prerequisite planner, reading library, coding lab, CLI, and MCP
tutor share lesson identities. An extension manifest registers new teaching
content in that shared system. It does not install a compiler, download a
model, create a cluster, or supply an execution command.

The current course remains usable while a future track is being authored.
Keep unfinished material outside `curriculum/extensions/` until its artifacts,
prerequisites, and teaching evidence are ready. The
[example manifest](examples/curriculum-extension.json) is deliberately outside
that active directory. It is a schema example, not a claim that its referenced
LLM lessons already exist.

## 1. Start with a learning gap and a bounded outcome

Read root [AGENTS.md](../AGENTS.md), the
[authoring contract](content-authoring.md), and the current catalog. Search
for existing lessons that teach the same mechanism before adding another one.
Record the gap, the learner's prerequisites, and an observable finish condition.
Choose the smallest useful sequence from beginner practice through a project;
do not create sixty empty placeholders to match the original directory names.

These are possible future subjects, not newly implemented execution features:

| Subject | Appropriate runner | What an author must establish |
| --- | --- | --- |
| C++ | `cpp` | Compiler and language version, deterministic local fixtures, compiler diagnostics, memory/lifetime reasoning, and a future reviewed adapter before in-app runs |
| Kubernetes | `kubernetes` | A named disposable local cluster/namespace, inspectable manifest outcomes, resource ownership, and cleanup after failure; no implicit current-context deployment |
| Deep learning | `python` | Python package group, CPU baseline or explicit GPU need, pinned small data/model assets, leakage checks, and disclosed first downloads |
| LLM theory | `none` | Worked reasoning, exact evaluation units, counterexamples, a written evidence rubric, and no invented requirement to call an online model |
| Scala/Spark | `scala` | JVM/Scala/Spark compatibility, a bounded local dataset and local mode, partition/order semantics, and an actual adapter before in-app execution |

The Python and SQL backends are implemented. C++, Scala, and Kubernetes are
registered planned capabilities, so their sources can be read and their work
can be preserved while execution remains unavailable. Reading mode (`none`)
has no execution requirement. Check `RUNNERS` in
`src/ds60sqlpy/curriculum_framework.py` for the actual capability descriptor;
do not infer readiness from a file extension or a dropdown label.

## 2. Author durable content first

Use `courses/<track>/` for a new subject, with a `README.md` learning plan and
a local `AGENTS.md` explaining its teaching and execution boundaries. A useful
layout is `guides/`, `lessons/`, `solutions/`, and `fixtures/`. Keep all manifest
paths relative to the repository, match filename case exactly, and use forward
slashes on every OS. Do not register absolute paths, hidden files, `.learning`,
symbolic links, junctions, or another user's data.

Each lesson needs a unique stable ID and a unique day/order value within its
track. Historical IDs and existing learner completion names stay unchanged.
Its guide and learner artifact must be separate files. Solutions remain closed
until an attempt or an explicit reveal request. A reading lesson needs at least
one separate explanatory solution; a code or operations lesson needs two
solution artifacts, including an explanation.

Meet the same depth and practice rules as the existing course. Define the
mental model, explain syntax or the reasoning process, give at least two worked
examples, and provide six distinct progressive exercises with exact inputs,
expected observations, and an independent verification. Use actual values,
small diagrams, proof steps, or counterexamples in a theory lesson. A generic
instruction to inspect evidence is not a useful acceptance check.

Include common mistakes, retrieval questions, a concrete next step, and the
exact `## Ask Codex about this lesson` block. Name the stable ID, actual guide
and learner paths, prerequisites, tutoring skill, solutions boundary, and
explain/predict/attempt/hint/evidence/retrieval sequence. Reading-only examples
may use fenced `text`; describe how the learner checks the reasoning instead
of pretending that a program runs.

## 3. Register the content additively

Use the [example JSON](examples/curriculum-extension.json) as a field reference.
After its real files exist, place your manifest under
`curriculum/extensions/<subject>.json` with `schema_version: 1`.

- `tracks` maps each new track ID to its title and Markdown plan path.
- `lessons` contains the complete catalog fields plus an explicit `runner` and
  optional `topics` list. Topics are search labels, not execution tools.
- `learning_paths` maps a goal ID to a title, description, and target lesson
  IDs. The planner expands prerequisites; do not duplicate the whole sequence.
- `prerequisites` can refer to existing Python, SQL, bridge, or extension IDs.
  Every target must exist, and the combined graph must be acyclic.
- `network` states real download behavior. Keep the default path offline after
  its disclosed setup. `dependency_group` must match the actual packaged Python
  dependencies when relevant; external tools still need explicit run guidance.

Manifests are additive. Duplicate IDs, replacement tracks, duplicate track/day
pairs, missing files, invalid prerequisites, and unsafe paths are errors to fix,
not reasons to relax validation. Do not edit `curriculum/catalog.json` by hand.
The manifest has no command, shell, image-pull, or cluster-action field.

Use a Markdown companion guide. Supported learner source formats follow the
runner: Python uses `.py` or `.ipynb`, SQL uses `.sql`, C++ uses `.cpp`, `.cc`,
`.cxx`, `.h`, or `.hpp`, Scala uses `.scala`, and Kubernetes uses `.yaml` or
`.yml`. Only Python notebooks are supported currently; a Scala notebook needs
an actual kernel adapter before registration. Reading mode and explanatory
artifacts use the supported authored-text formats, including Markdown and text
notes. A `.txt` worksheet uses an explicit `## Exercises` section with numbered
tasks, or plain `Exercise 1:` labels; repeated labels count once. JSON, TOML,
CSV, and shell text can be displayed safely when declared or
linked; display support does not enable execution. Keep a Markdown explanatory
solution for the app and tutor's explicit reveal workflow. See
`TEXT_ARTIFACT_SUFFIXES` and `RUNNER_SOURCE_SUFFIXES` in the framework for the
exact current allowlists.

Add every new lesson ID to `curriculum/practice_expansion.json` with
`{"baseline": 0, "target": 6}`. Do not modify the historical baseline or let
registration automatically waive quality checks. Number C++ and Scala source
prompts with `// Exercise 1:` comments; YAML uses `# Exercise 1:`. A repeated
label counts once. Guides and every explanatory solution need the same actual
exercise set, not six copies of one task.

## 4. Verify the learner journey

From the repository root, use the course's configured Python interpreter:

```text
python scripts/build_catalog.py
python scripts/course.py catalog
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/build_course_guide.py
python scripts/build_lesson_readers.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
```

Run the relevant tests after the generators. Verify that search finds the new
ID and topic, its goal includes the correct prerequisites, and its declared
time estimate is understandable. Open its generated lesson reader, track plan,
and linked references both through the app and as static files. The app must
describe a planned adapter honestly and preserve notes/work when run is
unavailable. Check that the read-only MCP catalog/search/plan/resource/prompt
path reaches the same lesson without revealing solutions by default.

The generated dashboard derives track filters and progress summaries from the
catalog. Track plans seed reference generation, so a new plan does not depend
on a link from the original three tracks. The original route shortcuts remain
useful entry points for the built-in course; all registered tracks remain
discoverable through catalog search and filtering.

## 5. Implement an execution adapter only when needed

Registering `runner: "cpp"`, `"scala"`, or `"kubernetes"` does not make it
runnable. A real adapter belongs in reviewed backend code. Update the central
capability descriptor only after implementing a non-shell command boundary,
controlled working directory, bounded runtime and output, process termination,
invalid-input handling, and learner-file preservation. Test failures and cleanup
as carefully as successful execution.

For operations lessons, require an explicit disposable target and prevent
ambient credentials or the user's current cluster context from selecting it.
For model lessons, verify a small offline/default path and report any optional
download separately. Never turn a manifest into an arbitrary shell launcher.
Package the authored content in source, native, and Docker distributions, then
verify the actual distribution on its target OS before claiming that its tools
are installed and ready.

Finish by reviewing the changed lesson with a beginner's perspective: what they
should predict, what they can observe, which failure teaches a useful idea,
and what they can now explain without the solution.
