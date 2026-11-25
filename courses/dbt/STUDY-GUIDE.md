# dbt study guide

Every dbt lesson guide links here for the routine that is the same in all 26 lessons:
how a lesson runs, what the shared case harness does, how the SQL model pad works, how to
practice, how the explained answers are laid out and how a tutor should help. The lesson
guides keep only what is specific to their own projects and results.

## Run a lesson

Open the lesson in `/classroom`. Its starter `main.py` contains both worked cases and
prints the dictionary each case returns. The prepared `data-engineering` worker runs it
in a fresh temporary directory. Each case writes its dbt project and DuckDB database into its own temporary directory, runs real dbt commands through dbt's Python entry point and removes the directory when it returns. No account, warehouse, network request or package download is involved.

Each lesson's run section says which values should print and what they mean. An
`AssertionError` means that an observation differs from the case's stated contract. Read
its message, then compare the printed dictionary with the guide's **Expected evidence**
before you change code. Never delete or weaken an assertion to get a clean run: the
assertion is the evidence. Save source and notes before switching lessons.

In dbt-001, dbt-002, dbt-003 and dbt-007 the run section is titled "Full-project Python workspace", because those
lessons also offer the SQL model pad described below.

## Case harness

Every program uses the same small helpers. dbt-001 shows them in full in its first worked
case, and each starter repeats them at the top so that it runs on its own. Later guides
show only each case's own functions.

- `project(directory, models, seeds, schema, snapshots, macros)` creates `project/` with
  `models/`, `seeds/`, `snapshots/` and `macros/` folders. It writes `dbt_project.yml`
  with the profile `classroom` and `profiles.yml` with one `dev` output: DuckDB in
  `warehouse.duckdb`, schema `main`, one dbt thread and a 256MB memory limit. It then
  writes each model, seed CSV and macro, plus `models/schema.yml` and
  `snapshots/snapshots.yml` when they are given. Without models it writes the single
  model `answer`.
- `invoke(root, *arguments, succeeds=True)` runs dbt in the same process through
  `dbtRunner` with `--quiet`, `--no-use-colors` and `--no-send-anonymous-usage-stats`,
  then adds `--project-dir` and `--profiles-dir` (both the temporary project) and
  `--no-partial-parse`. It asserts success, or with `succeeds=False` asserts that dbt
  rejected a deliberately invalid fixture.
- `rows(root, sql)` queries the DuckDB file directly and returns a list of tuples.
- `artifact(root, name)` reads a JSON artifact such as `manifest.json` or
  `run_results.json` from `target/`.
- `relation(root, unique_id)` reads a node's `relation_name` from the manifest. Only
  dbt-010 uses it.

Lesson-specific helpers, such as `targets` in dbt-019 to dbt-021, appear in that
lesson's own program.

A worked case lists its **Project files** before its commands. YAML is shown in
conventional key order; the harness writes it with `yaml.safe_dump`, which sorts keys,
and dbt reads the same mappings either way. Under **Commands, in order**, each `dbt`
line is one `invoke(...)` call. The harness adds `--project-dir` and `--profiles-dir`
for the temporary project, so the listed commands omit them. Text between command
blocks names the file the program changes before its next command.

## SQL model pad

Choose **SQL model** in the language selector to write a model directly. The separate `dbt-duckdb` profile compiles and builds it in a prepared local project. It provides `ref('raw_orders')`, `ref('customers')` and `source('raw', 'orders')`. The five fixed orders have amounts 100, 50, 25, 80 and 120; statuses are paid, paid, refunded, pending and paid. The fixed status variable is paid, and report_date is 2024-01-06. Paid amount totals 270. Customers 10/20/30 are Ada/north, Ben/south and Cy/north. This fixture differs deliberately from the full-project examples below. Compare returned rows by their keys: a materialized relation has no guaranteed row order.

The SQL pad changes one model. Project configuration, custom macros, seeds, tests, snapshots and incremental state are taught through the complete Python/CLI projects; the model-only pad does not pretend to edit those files.

## Practice routine

The six numbered tasks in each guide change one of its two worked cases, and the
starter contains both. Make each change in a saved copy, run it, and compare the
printed result with the task's **Check** before opening the explained answers. If a
check fails, use the task's **Hint** first, then the guide's section on diagnosing
errors and misleading results.

## Answers and references

Each lesson has an explained answer file in `solutions/` and a complete program in
`references/`. The answer file opens with the lesson outcome and a statement of what the
reference proves and what it does not. Each numbered answer explains the change; where
the guide asks for code or reasoning, it adds the code and the labels **Why it holds
here**, **Plausible wrong approach** and **How to verify**. It ends with the task's
**Expected** check. The file closes with the complete reference program, whose two
worked cases carry the assertions, and an interpretation for independent work.

## Tutor guidance

Tutors use the repository's `$guide-ds60sqlpy-learning` skill
(`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`). Inspect the learner's own source
and printed output first. Ask the learner to explain the lesson's concepts in their own
words, then give one focused hint at a time. Keep an assertion on a synthetic fixture
separate from a claim about an external dataset or deployed service. Each lesson's tutor
section adds the questions that matter for its own cases.
