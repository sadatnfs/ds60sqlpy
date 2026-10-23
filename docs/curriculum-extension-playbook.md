# Extend the curriculum

A subject is a learning sequence. A runtime is the tool that executes its code.
A lesson can reuse a runtime or be reading-only. All subjects join the same
`/classroom` home, workspace, navigation and saved-work experience.

Start with the learner's goal and a real gap, then choose the existing content
contract. Do not register empty lessons just to reach a desired count. The
[add-learning-path skill](../.agents/skills/add-learning-path/SKILL.md) turns
this playbook into a reusable contributor-agent workflow.

## Choose the correct registration route

| Change | Durable registration | Validation |
| --- | --- | --- |
| Extend existing Python, SQL or bridge material | Existing artifacts and `catalog_builder.py`; additive legacy manifests when appropriate | Legacy catalog, practice and depth gates |
| Add a new subject to the classroom | `courses/<subject>/track.json` and `lessons.json` | `ModuleCatalog`, subject tests and browser/runtime checks |
| Extend one of the original five module subjects | Existing plan under `docs/expansion/plans/` and its `courses/<subject>/lessons.json` | Same module gates, existing design checks |
| Extend the statistics tutorial | `courses/statistics-ml/manifest.json`, chapters, examples and coverage | Tutorial coverage, numerical examples and rendering |
| Add a new execution language or external operation | Reviewed backend adapter, profile and image in addition to content | Actual runtime success, failure, cleanup and persistence evidence |

The original five module subjects are Kubernetes, TensorFlow, LLM theory, C++
and Scala/Spark. Their plans supply live route metadata; authored admission
still comes from `lessons.json`. Additive subjects use `track.json`. Do not
migrate an existing subject between these contracts as an incidental edit.

The statistics loader is currently specific to that book. A different tutorial
book requires a deliberate loader/schema extension and tests, or a proposal
kept outside active registration until supported. Do not assume any arbitrary
`manifest.json` is automatically discovered.

## Design a useful progression

Define the starting knowledge, observable independent project and prerequisites.
Build the shortest sequence that teaches the mechanisms needed for that project:

1. Orient the learner: where code lives, what Run does, where output appears,
   and how to read an ordinary error.
2. Teach values, representations, control flow or query composition with small
   traces and exact observations.
3. Introduce abstraction, data structures, contracts, state and error handling.
4. Connect multiple pieces through tests, debugging, files or bounded data.
5. Explain performance, concurrency, ownership or distributed semantics where
   they matter to the subject.
6. Finish with an independently designed project and explicit tradeoffs,
   limitations and recovery behavior.

A beginner does not need every advanced topic immediately. Cross-subject
prerequisites should name stable IDs, not hide a whole language inside a
single introductory lesson. See the skill's
[progression reference](../.agents/skills/add-learning-path/references/progression.md)
for Python, SQL, C++, Java, JavaScript/TypeScript and Scala/Spark examples.

## Author and integrate a module

Follow [ADDING_A_MODULE.md](implementation/ADDING_A_MODULE.md) for exact route,
manifest, variant and runtime boundaries. Inspect an existing subject and the
loader instead of guessing fields. There is no universal scaffold command in
this repository. Create only the files needed for the chosen subject and use
an existing subject's documented authoring command only for that subject.

Write the self-contained guide, learner artifact, reference and explanatory
solution under `courses/<subject>/`. Define vocabulary, show worked examples,
include expected observations and misconceptions, and provide progressive
practice. Reading-only practice uses reasoning and a separate explanation.
The statistics tutorial has no exercise quota or hidden answer gate.

Preserve IDs, variant aliases and state ownership. Add accessible subject
colors and a text label to the existing UI; do not add another public page.
Review the declared runtime before promising a Run action. A syntax lexer or
file extension does not install a compiler.

## Legacy catalog extensions

Use `curriculum/extensions/<subject>.json` only when deliberately extending the
legacy catalog contract. [The inactive example](examples/curriculum-extension.json)
shows its schema. It is not a template for modern `track.json`/`lessons.json`
module registration and does not assert that its referenced files exist.

Legacy manifests use `schema_version: 1`, `tracks`, complete `lessons`, and
optional `learning_paths`. Their runner and allowed suffixes come from
`src/ds60sqlpy/curriculum_framework.py`. Preserve historical track/day pairs,
IDs and the acyclic prerequisite graph. Add new legacy IDs to
`curriculum/practice_expansion.json` with baseline zero and target six; do not
change the historical baseline. Do not add module or tutorial IDs to that
registry simply because they are new lessons.

The legacy capability descriptors can differ from module workers. Existing C++
and Scala module execution does not imply that a legacy extension entry using
the same language has its own adapter. Report the capability of the actual
route, not the availability of a different route's compiler.

## Verify and publish

From a prepared development environment at the repository root:

```sh
python scripts/check_modules.py
python scripts/normalize_lesson_prose.py --write
make generate
python scripts/normalize_lesson_prose.py
python scripts/check_content_rendering.py
python scripts/course.py validate
python scripts/audit_practice.py
python scripts/audit_lesson_depth.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
node scripts/check_classroom_ui.mjs
```

Use the documented subject authoring command before this sequence where one
exists. Review all generated changes. Test changed reference programs and
misconceptions in the intended worker; use a disposable classroom project for
writes. Verify guide rendering, source loading, explicit solution reveal,
subject/variant switching, saved drafts, result history and fresh-container
restoration. Check read-only tutor discovery when registration changes.

Keep first-download preparation, offline execution and optional external
resources distinct. Record exact checks and unresolved platform limits.
[Validation](validation.md) describes the grouped parallel suite and CI gates.
A count check, build or reference execution alone does not establish a complete
learning experience or independent learner competence.
