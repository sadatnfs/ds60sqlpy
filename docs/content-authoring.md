# Content authoring guide

Course content must be correct, runnable, accessible to its intended learner,
and explicit about prerequisites. This guide defines the shared contract;
track-specific rules live in [python/AGENTS.md](../python/AGENTS.md),
[sql/AGENTS.md](../sql/AGENTS.md), and
[bridge/AGENTS.md](../bridge/AGENTS.md).

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
Read `DS60_DATABASE_URL`, select SQLAlchemy's explicit Psycopg 3 dialect, pass
the engine object to `%sql`, disable connection display, bound results, and use
named binding for values. Never add `%pip`, a credential, or an untrusted Jinja
fragment to a lesson notebook.

## PostgreSQL

- Target PostgreSQL 16+ and test canonical automation on PostgreSQL 17.
- Use PostgreSQL syntax in runnable files.
- Keep normal lessons transactional and rollback-safe.
- Declare persistent project fixtures.
- Explain NULL, ordering, time zone, and money assumptions.
- Use `psql -X -v ON_ERROR_STOP=1` for file validation.
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
.\.venv\Scripts\python.exe scripts\course.py doctor
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
- Generated artifacts and secrets are absent.

Run [repository validation](validation.md) before handoff.
