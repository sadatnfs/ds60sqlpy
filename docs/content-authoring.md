# Content authoring guide

Course content must be correct, runnable, accessible to its intended learner,
and explicit about prerequisites. This guide defines the shared contract;
track-specific rules live in [python/AGENTS.md](../python/AGENTS.md),
[sql/AGENTS.md](../sql/AGENTS.md), and
[bridge/AGENTS.md](../bridge/AGENTS.md). The
[curriculum design references](curriculum-design-references.md) record the
external tutorial patterns that informed this contract.

## Before authoring

1. Read the closest `AGENTS.md`.
2. Inspect the generated `curriculum/catalog.json` and the applicable rules in `src/ds60sqlpy/catalog_builder.py`.
3. Run `python scripts/course.py catalog`.
4. Identify the learning gap and prerequisite chain.
5. Decide whether to revise an existing lesson or add a new stable lesson ID.

Do not add a lesson solely to increase the count.

Established Days 1–60 keep their IDs and filenames. New professional modules
use the stable named specifications in `src/ds60sqlpy/catalog_builder.py` and
live under the applicable `professional/` directory. Do not force a
foundation, elective, or specialization into a misleading sequential day.

## Lesson contract

Every lesson should include:

1. **Title and level** — beginner, intermediate, or advanced
2. **Prerequisites** — concepts and environment
3. **Objectives** — observable abilities, not vague familiarity
4. **Motivation** — why the learner should care
5. **Vocabulary** — define new terms before use
6. **Worked examples** — small, runnable, and explained
7. **Exercises** — progress from recall to application
8. **Self-check** — expected behavior, assertions, or questions
9. **Common mistakes** — include how to diagnose them
10. **Next steps** — review or successor lessons
11. **Separate solution** — reasoning, alternatives, and edge cases

Prefer “write a query that returns…” or “implement and verify…” over “understand…”.
For a named professional module, list every direct catalog prerequisite by its
exact backticked stable ID inside `## Level and prerequisites`. Put transitive
background and merely helpful material in separately labeled prose so Codex
and learners do not mistake it for a hard gate.

## Complete-amateur depth standard

The section checklist above is necessary, but a heading with one sentence or a
list of unexplained terms is not a complete lesson. Write for a learner who has
never seen the topic and may not yet know what to type, where to type it, or
how to tell whether it worked.

Every companion guide in the Python, SQL, and bridge tracks must provide all
of the following:

1. **A plain-language purpose and mental model.** Explain what problem the
   concept solves and connect it to something the learner already knows.
2. **Definitions before use.** Define each new term in a complete sentence.
   Say what the thing is, what role it plays, and one important distinction
   from a nearby concept.
3. **Syntax or query anatomy.** Break a representative expression or statement
   into its meaningful parts. Do not assume punctuation, indentation, aliases,
   clauses, or evaluation order are self-explanatory.
4. **At least two focused worked examples.** One should demonstrate the normal
   case. The other should change one meaningful condition, expose an edge case,
   or contrast a common wrong approach. Annotate the important lines or clauses.
5. **An expected observation.** Show the bounded output, result columns and row
   grain, assertion, or precise behavior the learner should see. When output
   can vary, explain the invariant instead of inventing an exact value.
6. **A novice-safe run path.** Name the file or notebook, tool, kernel or
   database, command or button, where output appears, and what success looks
   like. SQL guides must lead with the guided SQL notebook route and retain
   separately labeled PowerShell and POSIX `psql` alternatives.
7. **A practice ramp.** Move from prediction and tracing to a guided change,
   independent construction, debugging, an edge case, and transfer to a new
   context. A long list of equally vague tasks is not progression.
8. **Diagnosis, not just warnings.** For each important mistake, show the
   symptom or likely error, explain its cause, and give the smallest useful
   investigation step.
9. **Retrieval and explanation.** End with questions that require the learner
   to explain the idea without copying syntax and identify what evidence would
   prove their work correct.

Avoid repeating a generic paragraph across lessons. Shared setup belongs in a
canonical setup document, but every lesson still needs a short, concrete
handoff to that workflow. Topic explanations, examples, mistakes, and expected
observations must be specific to the lesson.

Do not paste mechanically shortened prompt text such as
`For task "Build a pipeli..."` into learner-facing prose. Name the operation
directly, and state its complete expected evidence. Likewise, placeholders
such as “the key named in the prompt,” “the operation being learned,” or “the
declared object” must be resolved to the actual key, concept, or object before
review.

### Exercise contracts

An exercise must be specific enough that a learner and a reviewer can agree on
whether it is complete. Include:

- the supplied input, table, or starting code;
- the requested output or behavior;
- meaningful constraints, such as “do not mutate the input” or “one row per
  customer”;
- at least one concrete normal case and one boundary or failure case; and
- a verification method that does not require opening the official solution.

For example, do not write:

> Replace a loop that appends filtered values with a list comprehension.

Write a bounded contract instead:

> Given `temperatures = [18, -3, 25, 0, 14, -8]`, first run an ordinary loop
> that appends only values greater than or equal to zero. Rewrite that behavior
> as one list comprehension named `non_freezing`. Preserve input order, do not
> modify `temperatures`, and verify that the result is
> `[18, 25, 0, 14]`. Then test an empty list and a list containing only
> negative values.

The second version names the input, filter boundary, result name, ordering and
mutation constraints, expected value, and edge cases without revealing the
comprehension itself.

An `**Expected:**` or `**Verify:**` label is not evidence by itself. Its body
must name something the learner can inspect: an assertion and value, an exact
exception, output columns and row grain, a bounded count, a file and hash, a
metric and tolerance, a command and exit status, a transcript, or another
topic-specific artifact. Do not copy the exercise behind a generic wrapper
such as “a deterministic result demonstrates the requirement,” and do not
apply every possible control to every task. A one-row aggregate does not need a
ranking tie-breaker; a simple projection does not need a CTE-stage audit; a
configuration parser does not need a database query. Verification must follow
the actual mechanism and failure modes of that exercise.

More prose is not automatically more teaching. Do not inflate a lesson with a
generated “independent verification,” “edge case,” or “alternative” paragraph
whose test does not apply to that exact query or program. A wrong scalar,
join, window, DML, limit, or time-boundary checklist is worse than omitting the
check. Keep the exercise-specific explanation and remove boilerplate whenever
the artifact cannot name literal inputs, keys, measures, expected values, and
the independent evidence that proves them.

### Notebook teaching flow

Historical Python notebooks should no longer be four-cell summaries. A
tutorial notebook should normally separate:

1. goal, prerequisites, and how to run;
2. mental model and vocabulary;
3. first explained example;
4. a prediction or trace before execution;
5. second contrasting example;
6. guided practice with a starter cell;
7. independent and debugging practice with scratch cells;
8. checks and expected observations; and
9. retrieval questions and next steps.

The exact number of cells may vary, but each cell should have one teaching job.
Do not hide all examples in one large code cell or all instructions in one
large Markdown cell. A learner must be able to run top to bottom from a fresh
kernel without relying on state created out of order.

### Ask Codex about this lesson

Every companion guide must end with an optional `## Ask Codex about this
lesson` section containing a copy-ready fenced `text` prompt. The course prose
must remain sufficient without it.

The prompt must be specific rather than “explain this topic.” Include:

- the stable lesson ID and title;
- the exact companion-guide and learner-artifact paths;
- the checked-in `$guide-ds60sqlpy-learning` skill;
- the declared prerequisite boundary and beginner-appropriate depth;
- the key concepts or decisions this particular lesson emphasizes;
- an instruction not to read `solutions/` until the learner asks or has made
  an honest attempt;
- the explain → predict → attempt → one-hint-at-a-time → evidence-review loop;
- the exact environment safety boundary for live SQL; and
- a done condition based on working evidence and retrieval in the learner's
  own words.

The generated lesson reader extracts this exact fenced prompt into a dedicated,
copyable coaching panel; it does not maintain a second hand-authored prompt.
Keep the Markdown block complete so the same source remains usable in VS Code,
plain text, static HTML, and private portal modes.

## Difficulty and pacing

- A beginner lesson should not silently require an intermediate concept.
- Introduce one primary idea at a time.
- Reuse vocabulary consistently.
- Advanced lessons may survey a broad system, but must say what mastery is out of scope.
- Project lessons can span multiple sessions and should provide checkpoints.

## Exercises and solutions

- Treat `curriculum/practice_baseline.json` as immutable audit evidence, not a
  target to edit downward. Every cataloged lesson must contain at least
  `max(6, 2 × baseline)` distinct numbered prompts on the learner, guide, and
  every explanatory-solution artifact.
- Run `python scripts/audit_practice.py` after changing practice content. The
  generated `docs/practice-coverage.md` must agree with the live audit.
- Count real learner actions, questions, predictions, diagnoses, and
  explanations. Repeated sub-bullets, headings, hints, and answer steps do not
  become separate exercises merely to satisfy the count.
- Sequence practice from retrieval and prediction through implementation,
  debugging, edge cases, and transfer to a new context.
- Keep learner exercises answer-free.
- Provide hints that do not collapse immediately into the answer.
- Make solution reasoning more important than syntax.
- Give each exercise one authoritative numbered solution section. Integrate
  legacy explanations and later clause/line maps beneath it; do not leave two
  sections with the same exercise number, different function names, or
  conflicting edge-case policies.
- Include at least one edge case or alternative.
- Avoid brittle assertions tied to random or time-dependent output.
- Do not use the official solution as the only test of correctness.

## Python and notebooks

- Target Python 3.11–3.12; use Python 3.12 as the canonical environment.
- Keep a valid notebook structure and repository kernelspec.
- Use clean-kernel execution to detect hidden state.
- Prefer `pathlib`, local data, explicit seeds, and small cells.
- Do not embed environment setup in dozens of notebooks; link to canonical setup.
- Tag heavy, manual, and network cells.
- Tag non-Python magic cells `skip-static-validation`; tag live PostgreSQL
  cells `live-postgres` as well.
- Keep generated output and models in ignored directories.
- Add direct imports to the appropriate dependency group.

For PostgreSQL-in-Jupyter lessons, use JupySQL from the selected course kernel.
Read `DS60_DATABASE_URL` and validate it with
`ds60sqlpy.sql_notebook.validate_course_database_target()` before passing it to
SQLAlchemy. This keeps every notebook on the exact course boundary: the
disposable `advanced_sql_training` database through a native local socket or
loopback host, with remote/multi-host targets and routing, service,
file-reading, or unsupported query overrides rejected. Then select
SQLAlchemy's explicit Psycopg 3 dialect, pass the engine object to `%sql`,
disable connection display, bound results, and use named binding for values.
Never add `%pip`, a credential, or an untrusted Jinja fragment to a lesson
notebook.

## PostgreSQL

- Target PostgreSQL 16+ and test canonical automation on PostgreSQL 17.
- Use PostgreSQL syntax in runnable files.
- State the outer result grain with its real identity columns. Do not infer
  grain from the last selected alias, treat a measure such as `count` or
  `ranking` as a unique key, or use placeholders such as “the answer's named
  identity.”
- List the final projected columns explicitly in exercise contracts instead
  of saying `*`. If order matters, state only the outer query's final
  `ORDER BY`; never copy a window frame, nested subquery, CTE body, or
  truncated SQL fragment into the result-order description.
- Keep normal lessons transactional and rollback-safe.
- Declare persistent project fixtures.
- Explain NULL, ordering, time zone, and money assumptions.
- Use `psql -X -v ON_ERROR_STOP=1` for file validation.
- Keep `psql` meta-commands deliberate and repository-relative. Guided SQL
  notebooks preserve the official meta-command lines and mirror fixed
  recursive `\ir` dependencies; do not add shell escape commands or dynamic
  include paths to learner content.
- Never use a production or shared database for examples.

## Python and PostgreSQL bridge

- Preserve both sides of the contract: typed Python boundaries and explicit
  PostgreSQL semantics.
- Use Psycopg 3 parameter binding for values and `psycopg.sql.Identifier` for
  dynamic identifiers; never interpolate user input into SQL.
- Keep core logic testable with Protocol-based fakes and add optional live
  integration only where server behavior matters.
- Read connection information from `DS60_DATABASE_URL`; never commit
  credentials.
- Make transaction ownership, retryable errors, idempotency keys, concurrency
  limits, and failure cleanup visible in examples.

## Cross-platform commands

When commands differ, give separately labeled blocks:

```powershell
# Windows PowerShell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py doctor
```

Do not put Bash operators in PowerShell examples. Prefer a cross-platform Python helper when the procedure is more than a few commands.

## Offline-first design

The default contract is one connected bootstrap followed by offline study.

For every external asset:

1. Identify its source and license.
2. Decide whether it is tracked, generated, or cached.
3. Record network behavior in the catalog.
4. Provide a local fallback where practical.
5. Make a missing cache fail with an instructive message.

Seaborn first-use downloads are accepted when disclosed. Pretrained weights or models must not download silently.

## Catalog and navigation

`curriculum/catalog.json` is a checked-in generated index. Do not edit it by hand. Update the lesson artifact filename or `src/ds60sqlpy/catalog_builder.py` authoring metadata whenever a lesson’s:

- Path
- Title
- Order
- Level
- Prerequisite
- Dependency group
- Network behavior
- Solution availability
- Validation status

changes.

Then regenerate and validate:

```text
python scripts/build_catalog.py
python scripts/course.py validate
```

Do not guess the catalog schema; inspect the builder and checked-in generated output.

Use relative Markdown links for repository navigation. Avoid plain-text file paths when a clickable link is clearer.

## Generated learner readers

`START_HERE.html`, `lesson-pages/<lesson-id>.html`, and
`reference-pages/<source>.html` are checked-in, deterministic course
artifacts, not hand-authored pages. The dashboard comes from
`scripts/build_course_guide.py`; the lesson/reference readers come from
`src/ds60sqlpy/lesson_reader.py` through
`scripts/build_lesson_readers.py`. Never edit any generated HTML surface by
hand.

Each reader must keep this learner journey:

1. rendered companion guide;
2. read-only learner-artifact preview with a path to the real file;
3. execution in VS Code, JupyterLab, or the guided SQL workspace; and
4. visibly separated solutions after the attempt.

Reader generation must remain offline and self-contained. Escape source,
reject unsafe URL schemes, render no untrusted notebook HTML, load no remote
fonts/scripts/analytics, and rewrite known course links to the matching reader
section. A static `file://` page may offer a best-effort registered VS Code
URL, but only the authenticated loopback launcher may start allowlisted native
actions.

Every learner-visible local Markdown or SQL link from the dashboard, lesson
readers, or rendered references must point to generated HTML. The generator
derives a deterministic recursive closure from explicit dashboard references
and links rendered from catalog artifacts; do not replace it with a scan of
arbitrary untracked files. Keep completion on the dashboard in static mode and
show the per-lesson checkbox only when the private launcher token is present.

Do not create 154 hand-maintained SQL notebooks. For a cataloged SQL lesson,
the private launcher derives an ignored working notebook and editable SQL copy
under `.learning/sql/<lesson-id>/` through
`src/ds60sqlpy/sql_notebook.py`. The generator must preserve existing learner
files, accept only stable catalog identities, keep paths below `.learning/sql/`,
run fixed non-shell `psql -f` commands, detect changed meta-commands even when
they follow SQL on the same line, hide connection values, and require explicit
confirmation before resetting the disposable course schema.

After lesson artifacts, paths, or catalog metadata change, regenerate and
check both navigation layers:

```text
python scripts/build_course_guide.py
python scripts/build_lesson_readers.py
python scripts/build_course_guide.py --check
python scripts/build_lesson_readers.py --check
```

## Accessibility and tone

- Use plain language without talking down to the learner.
- Expand acronyms on first use.
- Do not communicate meaning through color alone.
- Add alt text to meaningful images.
- Keep tables readable on a narrow editor pane.
- Explain error messages and recovery, not only the happy path.
- Avoid culture-specific examples when a neutral example works.

## Review checklist

- Objectives match exercises.
- Prerequisites are sufficient.
- Examples run from documented setup.
- No hidden notebook state exists.
- Default execution works offline after bootstrap.
- Windows and POSIX commands are valid.
- Direct dependencies are declared.
- Solution paths are truthful.
- Catalog and internal links validate.
- Generated dashboard, lesson readers, and reference pages have no drift and
  still open the real artifact rather than raw source in a browser tab.
- Guided SQL notebook tests prove catalog/path/reset/no-overwrite boundaries;
  no `.learning/sql/` workspace is tracked.
- Unexpected machine-generated artifacts and secrets are absent.

Run [repository validation](validation.md) before handoff.
