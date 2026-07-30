# Curriculum map

DS60 contains two substantial 60-lesson cores, an eight-lesson engineering
bridge, and 26 named foundation, professional, and specialization modules. The
day number is an ordering key, not a promise that every learner should finish
in that many calendar days.

Use:

```text
python scripts/course.py catalog
```

for the checked-in generated inventory in `curriculum/catalog.json`. The index is built from lesson artifact filenames plus metadata rules in `src/ds60sqlpy/catalog_builder.py`; do not edit the JSON by hand.

## Choose a path

### New to programming and databases

1. Complete Python Days 1–15.
2. Complete `sql-found-01` and `sql-found-02`, then begin SQL Days 1–15.
3. Continue Python Days 16–30.
4. Continue SQL Days 16–30.
5. Add the engineering bridge after Python Day 15 and SQL Day 15 when you want
   application-oriented integration practice.
6. Choose advanced data science, advanced SQL, or alternate both.

### Comfortable with another programming language

Review Python Days 1–9, then focus on testing, tooling, data work, and
projects. Complete the two SQL foundations before Day 1 unless you can already
design constraints and explain a versioned migration workflow.

### Comfortable with SQL

Use the SQL companion guides and project lessons as a diagnostic. Do not skip PostgreSQL setup, transaction behavior, or query-plan lessons merely because SELECT syntax is familiar.

### Focused on data science

Follow the Python track in order through Day 45. Days 46–60 introduce larger optional dependencies and production topics; inspect the catalog and environment doctor before installing heavy extras.

### Focused on data or backend engineering

Complete Python Days 1–15 and SQL Days 1–15, then follow the
[engineering bridge](../bridge/README.md). Continue the main tracks alongside
it when a bridge lesson identifies a deeper Python or PostgreSQL prerequisite.
Use the [professional paths](professional-paths.md) after the shared bridge.

## Python and data-science track

Primary plan: [python/PYTHON_TRAINING.md](../python/PYTHON_TRAINING.md)  
Track guide: [python/ds-60day/README.md](../python/ds-60day/README.md)

| Range | Phase | Main outcomes |
| --- | --- | --- |
| Days 1–15 | Core Python and engineering habits | Syntax, functions, collections, files, modules, tests, debugging, OOP, tooling, and a CLI project |
| Days 16–30 | Data manipulation and visualization | NumPy, pandas, pipelines, EDA, visualization, feature engineering, validation, and a preprocessing project |
| Days 31–45 | Statistics and machine learning | Probability, inference, linear algebra, scikit-learn, evaluation, model families, interpretation, deployment, and an end-to-end project |
| Days 46–60 | Advanced and production topics | Deep learning, NLP, forecasting, scale, MLOps, monitoring, containers, orchestration, ethics, refactoring, and a capstone |

Artifacts currently present:

- Learner notebooks: Days 1–60
- Companion guides: Days 1–60
- Markdown solutions: Days 1–60
- Solution notebooks: Days 1–60
- Named professional learner modules: 10, each with a guide and two solution
  artifacts

The track is a practical Python-for-data-science curriculum. It does not replace the complete Python language reference, and some advanced topics are surveys rather than mastery in one session.

## PostgreSQL track

Primary plan: [sql/ADVANCED_SQL_60DAY_PLAN.md](../sql/ADVANCED_SQL_60DAY_PLAN.md)  
Track guide: [sql/postgres-60day/README.md](../sql/postgres-60day/README.md)

| Range | Phase | Main outcomes |
| --- | --- | --- |
| Days 1–15 | Relational querying | SELECT, filtering, aggregation, joins, set operations, subqueries, DML, CASE, functions, and a report project |
| Days 16–30 | Analytical SQL | Window functions, CTEs, recursion, pivots, JSON/XML, patterns, and a project |
| Days 31–45 | Performance and operations | Plans, indexes, optimization, partitioning, transactions, locks, data quality, backup concepts, monitoring, and an optimization project |
| Days 46–60 | Applied projects | E-commerce, finance, data warehousing, BI, and a final integrated capstone |

Artifacts currently present:

- Lesson scripts: Days 1–60
- Companion guides: Days 1–60
- Markdown solutions: Days 1–60
- Executable solution SQL: Days 1–60
- Relational foundations: 2 named modules before Day 1
- Professional and specialization SQL: 10 named modules after the shared core

Runnable material and the maintained high-level plan both target PostgreSQL
16 or newer.

## Python + PostgreSQL engineering bridge

Track guide: [bridge/README.md](../bridge/README.md)

| Day | Main outcome |
| --- | --- |
| 1 | Typed configuration, structured logging, and command-line boundaries |
| 2 | Protocols, context managers, and decorators for testable infrastructure |
| 3 | Safe Psycopg 3 parameters, rows, and dynamic identifiers |
| 4 | Transaction boundaries, idempotency, retry classification, and backoff |
| 5 | Database tests, fixtures, fakes, and integration-test boundaries |
| 6 | Bounded bulk ETL with validation and reject accounting |
| 7 | Async database work with bounded concurrency and cancellation safety |
| 8 | Production capstone with observability, security, and recovery evidence |

Bridge Day 1 requires `python-15` and `sql-15`; later bridge lessons are
sequential. Every lesson includes a learner `.py` file, companion guide,
executable reference solution, and reasoning guide. Default tests use fakes and
run offline. Optional live PostgreSQL work uses `DS60_DATABASE_URL` and the
disposable course database.

Four named bridge modules add PostgreSQL notebook magics, migration delivery
and observability, AI application boundaries, and analytics engineering.

## Artifact roles

- **Plan:** broad learning sequence and goals
- **Companion guide:** concepts, mental models, pitfalls, and preparation
- **Learner notebook or SQL file:** examples and exercises
- **Bridge learner module:** application-engineering exercises with testable
  boundaries and optional live integration
- **Named professional module:** a stable-ID foundation, cumulative lab, or
  elective that does not renumber an established day
- **Solution:** worked reasoning after an honest attempt
- **Generated catalog:** machine-readable mapping of artifact names plus authoring metadata such as prerequisites, dependency groups, network behavior, and solution availability

Do not infer that a solution format exists because another format exists. Ask the catalog.

## Pacing

A useful lesson rhythm is:

1. 10–20 minutes: recall prerequisites and read
2. 20–40 minutes: predict and run examples
3. 30–60 minutes: exercises
4. 10 minutes: self-check and notes

Project lessons often need multiple sessions. Heavy machine-learning setup may need a separate connected preparation session.

## Readiness checkpoints

Before moving from a phase:

- Explain the phase’s core ideas without copying definitions.
- Recreate one small example from a blank file.
- Complete the phase project or an equivalent.
- Review failed exercises after a delay.
- Run the relevant local validation.

Use Codex for a diagnostic quiz with [Learning with Codex](learning-with-codex.md), or create your own retrieval questions.

## Adding lessons beyond 60

The repository may grow beyond the historical numbering. New material should close a documented gap, declare prerequisites, and receive a stable catalog ID. Do not renumber established lessons merely to preserve a marketing total.

See [Content authoring](content-authoring.md).

For the audited gap record and implementation criteria, see the
[curriculum gap backlog](curriculum-gap-backlog.md).

The implemented named modules and recommended lanes are in
[Professional and specialization paths](professional-paths.md).
