# Content authoring guide

Course content must be correct, runnable, accessible to its intended learner,
and explicit about prerequisites. This guide defines the shared contract;
track-specific rules live in [python/AGENTS.md](../python/AGENTS.md),
[sql/AGENTS.md](../sql/AGENTS.md), and
[bridge/AGENTS.md](../bridge/AGENTS.md). The
[curriculum design references](curriculum-design-references.md) record the
external tutorial patterns that informed this contract.

## One classroom across every subject

The public browser entrypoint is `/classroom`. Python, PostgreSQL, the bridge
and module/book subjects share its home, navigation, saved-work conventions
and lesson workspace. A subject supplies identity, its individual theme and
learning sequence; a runtime profile supplies execution. Do not create a new
public application or hardcode an all-green theme for a new subject. Text labels
must identify subjects independently of color. Prerequisites and estimated
minutes support choice without imposing a study deadline.

Lead run instructions with the supported classroom workflow and its capability
notice. Keep contributor Jupyter, local SQL and separately prepared project
recipes under an explicit optional heading. Do not promise that a pad executes an entire notebook,
stateful SQL workflow or cluster operation unless that route implements the
artifact contract. Preserve stable lesson IDs and learner state when changing
navigation. The tutorial-book exception still has no exam or solution gate.

## Mathematical notation and code presentation

Author mathematical statements with explicit LaTeX delimiters: `\( ... \)`
for inline notation and `\[ ... \]` on separate lines for a displayed
formula. These delimiters avoid ambiguity with monetary dollar signs. The
reader converts supported notation into accessible native MathML using bundled
local dependencies. No CDN or network request is required to read a formula.

For example, write `\(\widehat{\delta}=\bar{x}_A-\bar{x}_B\)` for a mean
difference. Give the larger uncertainty expression its own paragraph:

```text
\[
\operatorname{SE}(\widehat{\delta})
=\sqrt{\frac{s_A^2}{n_A}+\frac{s_B^2}{n_B}}.
\]
```

Define each symbol, its units, indices and assumptions in nearby prose.
Distinguish a population parameter, an estimate and a numerical approximation.
Use `\frac`, `\sqrt`, subscripts and superscripts for actual mathematical
structure; do not leave formulas as `sqrt(sA^2/nA+sB^2/nB)` in teaching prose.
Keep program expressions inside code spans or fences when teaching literal
syntax. Source code must remain exact, including its operators and indentation.
Matrices, cases, sums, products and aligned derivations can use conventional
LaTeX. Check the rendered page for fallback source rather than assuming a
complicated macro is supported. Do not depend on custom macros or executable
HTML. A currency amount such as `$20` remains ordinary prose.

Every fenced code example needs an explicit language identifier. Use `python`,
`sql`, `cpp`, `java`, `javascript`, `typescript`, `scala`, `bash`, `sh`, `powershell`,
`yaml`, `json`, `dockerfile`, `makefile`, `html` or another supported lexer name.
Use `text` for console output, error transcripts, copied coaching prompts and
pseudocode that is intentionally not a real language. Syntax highlighting
must preserve selectable text and work without a CDN. Unknown languages should
remain readable escaped text; do not mislabel them as Python merely to obtain
colors. Adding a syntax lexer does not implement execution for a new language.

`curriculum/math-prose.json` is the reviewed migration source for older ASCII
formulas. `scripts/normalize_math_prose.py` applies only exact scoped mappings,
preserving existing math, links, inline code, fenced code, notebook code cells
and the supplied statistics outline. New lessons should use explicit LaTeX at
source. The consolidated `scripts/normalize_lesson_prose.py` pipeline also
applies `curriculum/prose-repairs.json` to reviewed display-text spacing, while
protecting code, math, IDs and runtime metadata. For legacy authoring generators, run the normalization step after
regeneration and before building readers:

```sh
python scripts/normalize_lesson_prose.py --write --report work/math-prose-audit.json
python scripts/build_lesson_readers.py
```

Without `--write`, the command checks whether a reviewed normalization is still
pending. Its candidate report is an editorial aid, not a claim that every match
is a mathematical error. Literal API calls and identifiers can resemble math.
Review those cases in context, and retain the report's code-preservation check.
Never solve a typography problem by changing an executable reference or hiding
a failed rendering test.

## Before authoring

1. Read the closest `AGENTS.md`.
2. Choose the existing authoring contract with the [extension playbook](curriculum-extension-playbook.md). Inspect the legacy catalog or subject plan and manifest as appropriate.
3. Run `python scripts/course.py catalog` for legacy content and `python scripts/check_modules.py` for authored modules.
4. Identify the learning gap and prerequisite chain.
5. Decide whether to revise an existing lesson or add a new stable lesson ID.

Do not add a lesson solely to increase the count.

Established Days 1–60 keep their IDs and filenames. New professional modules
use the stable named specifications in `src/ds60sqlpy/catalog_builder.py` and
live under the applicable `professional/` directory. Do not force a
foundation, elective, or specialization into a misleading sequential day.

## Lesson contract

Practice lessons should include:

1. **Title and level** - beginner, intermediate, or advanced
2. **Prerequisites** - concepts and environment
3. **Objectives** - observable abilities, not vague familiarity
4. **Motivation** - why the learner should care
5. **Vocabulary** - define new terms before use
6. **Worked examples** - small, runnable, and explained
7. **Exercises** - progress from recall to application
8. **Self-check** - expected behavior, assertions, or questions
9. **Common mistakes** - include how to diagnose them
10. **Next steps** - review or successor lessons
11. **Separate solution** - reasoning, alternatives, and edge cases

Prefer “write a query that returns…” or “implement and verify…” over “understand…”.
For a named professional module, list every direct catalog prerequisite by its
exact backticked stable ID inside `## Level and prerequisites`. Put transitive
background and merely helpful material in separately labeled prose so an AI tutor
and learners do not mistake it for a hard gate.

The statistics/ML tutorial has a different contract: detailed theory, assumptions,
worked examples, use cases, failure modes and answered interview discussions.
It has no exams, problem sets, exercise quota or hidden-solution gate. Its
coverage and executable-example checks replace practice-count gates. Reading
markers record reading rather than mastery.

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
   like. SQL guides must lead with the classroom capability notice. Optional
   contributor notebooks and local `psql` commands belong in a separately
   prepared route; ordinary Windows learners use the same WSL 2 Docker commands.
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

The notebook cell, code-cell, and teaching-text minimums apply to every
Python-runner learner notebook, including a new track or a lesson numbered
beyond sixty. A new topic name must not bypass notebook depth checks.

The exact number of cells may vary, but each cell should have one teaching job.
Do not hide all examples in one large code cell or all instructions in one
large Markdown cell. A learner must be able to run top to bottom from a fresh
kernel without relying on state created out of order.

### Ask an AI tutor about this lesson

Every companion guide must end with an optional `## Ask an AI tutor about this
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
plain text, static HTML and the unified classroom.

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

The learner route uses the same Bash launcher on Linux, macOS and Windows
through WSL 2. Link to the [one-command guide](one-command-classroom.md) for
engine installation and preparation instead of duplicating installers:

```sh
./classroom
./classroom stop
./classroom resume
```

A custom project requires the same `--project NAME` on each command. `resume`
does not pull or build; `--rebuild` deliberately applies source/configuration
updates. Do not reset learner state to demonstrate startup.

For explicitly prepared contributor commands, use the environment documented in
[CONTRIBUTING](../CONTRIBUTING.md), for example:

```sh
uv run --no-sync python scripts/course.py validate
```

Keep host toolchain work, real external projects and classroom execution
separate. Do not reintroduce native Windows installers, private editor-launch
APIs or a second UI merely to provide an alternative command block.

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
3. an honest handoff to the coding lab's declared capability, or a documented
   separately prepared contributor Jupyter/SQL or external-project workflow; and
4. visibly separated solutions after the attempt.

Reader generation must remain offline and self-contained. Escape source,
reject unsafe URL schemes, render no untrusted notebook HTML, load no remote
fonts/scripts/analytics, and rewrite known course links to the matching reader
section. Static pages display source and links; they do not start native
editors, terminals or servers. The unified classroom owns authenticated execution
through its declared runtime contracts.

Every learner-visible local Markdown or SQL link from the dashboard, lesson
readers, or rendered references must point to generated HTML. The generator
derives a deterministic recursive closure from explicit dashboard references
and links rendered from catalog artifacts; do not replace it with a scan of
arbitrary untracked files. Seed each registered track's plan from catalog
metadata, including plans that the original three tracks never link to. Keep
completion on the dashboard in static mode. Classroom-served readers link
back to that lesson's saved-evidence workflow. Reading progress and source-bound
execution receipts remain different evidence, and opening a reader never runs code.

Do not create hand-maintained SQL notebooks for every lesson. For a cataloged SQL lesson,
the explicitly invoked contributor notebook command derives an ignored working
notebook and editable SQL copy
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

## Extending subjects, languages, and learning modes

Follow [the extension playbook](curriculum-extension-playbook.md) to choose
between a legacy catalog extension, an authored module and the tutorial book.
New classroom subjects normally use `courses/<subject>/track.json` and
`lessons.json`; the original five modules retain their existing plans. Follow
[the module contract](implementation/ADDING_A_MODULE.md) for exact admission,
profile and variant rules. Do not put every new subject into
`curriculum/extensions/` or count module lessons in legacy practice audits.

A subject describes what learners study; a runtime describes how its code runs.
C++, Java, Node, TypeScript, Scala/Spark and framework modules have fixed reviewed
workers. Use the actual lesson capability report, because legacy descriptors
and module runtimes are separate routes. A registered profile or highlighted
source alone does not establish execution readiness.

For legacy catalog additions, preserve `curriculum/practice_baseline.json` and
register new IDs in `curriculum/practice_expansion.json`. Ordinary module
practice uses the subject's depth and six-exercise contract. Reading-only
practice still needs worked reasoning and a separate explanation. The tutorial
book has no practice requirement or answer gate.

For C++/Scala learner sources, label prompts `// Exercise 1:` through the final
number. Kubernetes YAML uses `# Exercise 1:` comments. Count distinct learner
tasks, not repeated labels or answer steps. Keep guide and solution tasks
aligned. A new execution adapter requires reviewed backend code, bounded runs,
cleanup, saved-work protection and actual runtime evidence.

List any compiler, JVM, cluster, GPU, model or first download beside the run
instructions, and distinguish Docker-provided tools from optional host setup.
External operations need a deliberately owned local target. Keep the default
path offline after its documented preparation.

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

## New-lesson practice evidence

Do not rewrite historical enrichment counts. Register genuinely new legacy catalog lesson IDs
in `curriculum/practice_expansion.json` with baseline zero and target six; the
audit merges this disjoint registry with the immutable historical baseline.
The new legacy guides still need distinct inspectable exercises, and the depth
and shared guide-contract checks both apply. Module subjects and tutorial books
use their separate contracts described above.
