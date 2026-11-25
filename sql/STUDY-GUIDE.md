# How to run and study a SQL lesson

This page holds the operating routine that every PostgreSQL lesson shares: the
PostgreSQL 60-day course in [postgres-60day](postgres-60day/README.md) and the
professional on-ramp and depth lessons in [professional](professional/README.md).
Each lesson guide links here instead of repeating it, so the guide itself can
spend its words on that lesson's concept, data and traps.

## Run a lesson in the classroom

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin `START_DOCKER_CLASSROOM.cmd`
wrapper. Choose **PostgreSQL** on the shared `/classroom` home, then open the
lesson by its id (for example `sql-01` or `sql-start-01`). The
[launcher guide](../docs/one-command-classroom.md) covers first preparation,
strict resume and the saved project selection. No host Python or PostgreSQL
installation is required for this browser route.

1. Read the lesson's prerequisite and fixture notes before running anything.
   Use only the local disposable `advanced_sql_training` database.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   keeps the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is fine for ordinary statements, but
   it does not replace a whole script's setup.
3. The **Course database** panel above the code shows whether the course
   training tables are loaded. Missing tables load automatically before your
   first run (or choose **Load course tables**) and stay loaded for later
   lessons. **Reset training data** restores the original rows only when your
   own changes made results differ; it keeps your saved code and notes.
4. Edit the learner copy in the classroom and save your prediction before
   running. The whole-script workspace lives at
   `.learning/sql/<lesson-id>/lesson/workspace/<lesson path>` inside the
   Docker learning volume, not in a new folder beside your checkout. The
   checked-in source stays the answer-free starting artifact.
5. Run the whole script and read the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL and DML print command tags; intentional checks may print NOTICE
   messages. An unexpected ERROR or a nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements. The
   warehouse sequence and other explicitly stateful exercises say when state
   is committed. Read saved output without rerunning it when you review an
   earlier attempt.

If a relation is missing, inspect the lesson's required fixture and its
predecessor lesson rather than guessing a new table definition. If
authentication or runtime readiness fails, use `./classroom status` and the
setup guide. Keep credentials out of SQL, notebooks, screenshots and committed
files. Repair the first error before trusting partial output.

## Optional contributor notebook route

For notebook work, prepare the Linux or WSL contributor environment from
[CONTRIBUTING.md](../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate a lesson's private workspace through the
maintained CLI, replacing the id:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-01
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout and executes the complete script
through psql. Its host-side state is separate from the Docker browser's named
volume. Follow [guided SQL notebooks](../docs/guided-sql-notebooks.md) for
explicit local connection selection and kernel setup. Notebook generation does
not execute SQL or authorize a reset.

## Work an exercise

Attempt each prompt in a scratch SQL file before opening the solution. Every
exercise carries three contract lines:

- **Inputs/evidence** names the relations and output columns to build toward.
- **Expected result/shape** states the grain, row bound, columns and order.
- **Verify** (or **Independent verification**) describes a check that does
  not trust the query you just wrote.

Write the expected grain and shape before you run anything. Then run, inspect
a bounded sample, and reconcile counts or totals against an independent
control query before you accept the result.

## Read a solution

Open a solution only after an honest attempt. Each lesson ships a Markdown
explanation and an executable companion. Run the companion only against the
disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day01_solutions.sql
```

`psql` prints each result or command tag. Stop at the first unexpected
`ERROR`; later output cannot repair an earlier failed invariant. Compare your
row grain, column names, row counts, `NULL` policy and ordering with the
explanation before you compare syntax.

The executable companions wrap each answer in `BEGIN` and `ROLLBACK` unless the
lesson declares a committed stateful step, and the snippets assume the
lesson's `SET search_path TO training, public;` statement. Run the complete
companion when you want a self-contained check.

### Reading any query in logical order

- Start at `FROM` and `JOIN` and state the intermediate row grain. Inspect join
  keys before adding aggregates; a one-to-many join may multiply rows only when
  the later contract accounts for it.
- `WHERE` filters input rows, `GROUP BY` forms buckets and `HAVING` filters
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- The `SELECT` list is the public result contract: keys establish grain,
  measures state calculations and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee, so add a unique tie-breaker before `LIMIT`.
- Treat every common table expression (CTE) as a temporary named relation.
  Inspect one stage at a time while debugging, then compare the final result
  with an independent control rather than trusting stage names.
- Keep SQL `NULL` as missing, unknown or not applicable until the metric
  contract chooses another representation. Guard division with `NULLIF`,
  disclose exclusions, and distinguish zero from no row.
- For DDL and DML, a command tag proves only that PostgreSQL accepted a
  statement. Catalog checks, negative cases, row-count reconciliation and the
  declared transaction boundary prove behavior and cleanup.

The published query is not the only valid syntax. A join, subquery, CTE,
window or conditional aggregate is an acceptable alternative when it keeps the
same grain, `NULL` semantics, deterministic ordering and safety. Prefer the
form whose intermediate relations a reviewer can verify, and optimize only
after correctness is established with evidence.

## Recover from common failures

- **Unexpected row count:** display keys before aggregates, count rows after
  each join or filter stage, and find the first stage whose grain differs from
  the contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top, first or last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows and aggregates.
- **`psql` stops on an error:** fix the first error shown by `ON_ERROR_STOP`,
  restore the declared transaction or setup state, and rerun the complete
  file. A later successful statement does not validate a partial run.

## Use an AI tutor (optional)

Each guide ends with a copyable tutor prompt. The guide, learner SQL,
PostgreSQL and the expected checks are enough to finish a lesson offline. If
you use the tutor, it follows the checked-in `guide-ds60sqlpy-learning` skill:
guide, then prediction, then your attempt, then one progressive hint at a
time, and only then a solution comparison. Paths under `solutions/` stay closed
until you ask after an attempt, and you never paste a password.
