# Day 53: Data Warehouse Project, Part 2: SCD Type 2

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-53**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-53/lesson/workspace/sql/postgres-60day/day53_project3_dwh_part2_scd.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-53
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Run and verify committed
  [Day 52; star-schema warehouse](day52_project3_dwh_part1.md) in the same
  database.
- **Artifacts:** [learner SQL](../day53_project3_dwh_part2_scd.sql) ·
  [solution reasoning](../solutions/day53_solutions.md) ·
  [executable solution](../solutions/day53_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is SCD Type 2, Business key, Validity interval. Its worked SQL reads or creates `training.customers`, `dim_customer`, `training.products`, `dim_product`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For one changed customer, locate exactly one current row, set its validto to the day before the new version, and insert the successor at CURRENTDATE. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key, not zero and not two.
The first runnable example has a concrete contract: Example 1 returns one row per `customer_id`, `full_name`, and `country`, capped at 10 rows with columns `customer_id`, `full_name`, `country`, and `segment` from `training.customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `customer_id`, `full_name`, `country`, and `segment`. Reselect the returned key columns from `training.customers`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day53_project3_dwh_part2_scd.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
CREATE TEMP TABLE changed_customers AS
SELECT c.customer_id,
       c.full_name,
       c.country,
       CASE WHEN c.segment = 'platinum' THEN 'gold' ELSE 'platinum' END AS segment
FROM training.customers c
ORDER BY c.customer_id
LIMIT 10;
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 returns one row per `customer_id`, `full_name`, and `country`, capped at 10 rows with columns `customer_id`, `full_name`, `country`, and `segment` from `training.customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH current_dim AS (
  SELECT dc.*
  FROM dim_customer dc
  WHERE dc.is_current
), diffs AS (
  SELECT s.customer_id,
         s.full_name,
         s.country,
         s.segment
  FROM changed_customers s
  JOIN current_dim dc ON dc.customer_id = s.customer_id
  WHERE coalesce(s.full_name,'') <> coalesce(dc.full_name,'')
     OR coalesce(s.country,'')   <> coalesce(dc.country,'')
     OR coalesce(s.segment,'')   <> coalesce(dc.segment,'')
), closed AS (
  UPDATE dim_customer dc
  SET valid_to = CURRENT_DATE - 1,
      is_current = FALSE
  FROM diffs d
  WHERE dc.customer_id = d.customer_id
    AND dc.is_current
  RETURNING dc.customer_id
)
INSERT INTO dim_customer(customer_id, full_name, country, segment, valid_from, valid_to, is_current)
SELECT d.customer_id, d.full_name, d.country, d.segment, CURRENT_DATE, NULL, TRUE
FROM diffs d;
```

**How to read it:** Example 2 is a data-changing CTE chain, not a displayed query result. The CTEs `current_dim`, `diffs`, and `closed` identify changed customers, close each former current row, and insert one successor into `dim_customer`. Read the command tag for the inserted-row count, then verify one current version per customer and non-overlapping validity periods; a successful command tag alone does not prove Type-2 history is correct.

**Expected result/shape:** Example 2 prints a DML command tag for `dim_customer`, and `changed_customers`. Capture the target key set at `customer_id`, `full_name`, and `country` grain before the write, compare it with affected/returned keys, and use a follow-up `SELECT` to prove the before/after invariant and transaction cleanup.

## Learning objectives

- Close one current dimension version and insert its successor atomically.
- Resolve facts to the dimension version valid on their event date.

## Vocabulary and concepts

- **SCD Type 2:** slowly changing dimension design that preserves version
  history as new rows.
- **Business key:** stable source identity shared by all versions.
- **Validity interval:** the dates or timestamps for which one version applies.

## Worked example / walkthrough

For one changed customer, locate exactly one current row, set its `valid_to` to
the day before the new version, and insert the successor at `CURRENT_DATE`.
Then as-of join a fact date using inclusive bounds and verify it resolves to one
surrogate key, not zero and not two.

## Exercises

Complete these in the [learner SQL](../day53_project3_dwh_part2_scd.sql):

1. Map facts to the effective SCD Type 2 version.
   **Inputs/evidence:** For sql-53 Exercise 1, read from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`. Build the answer toward `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-53 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`.
   **Verify:** For sql-53 Exercise 1, project `order_id` plus the raw source columns from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
2. Add/set audit columns on inserts and closes.
   **Inputs/evidence:** For sql-53 Exercise 2, change only `dim_customer`, and `dim_product` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `information_schema.columns` rows.
   **Expected result/shape:** For sql-53 Exercise 2, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `updated_by`, and `day53_solution`.
   **Verify:** For sql-53 Exercise 2, inspect `information_schema.columns` for `dim_customer`, and `dim_product`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
3. Diagnose same-day date-grain version closure.
   **Inputs/evidence:** For sql-53 Exercise 3, read from `dim_customer`. Build the answer toward `customer_id`, `valid_from`, `valid_to`, and `invalid_range`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-53 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `valid_from`, `valid_to`, and `invalid_range`. The final order is `valid_from`.
   **Verify:** For sql-53 Exercise 3, run an anti-check that counts rows where NOT ((customer_id = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `valid_from`, `valid_to`, and `invalid_range` against `dim_customer`. Add one row for which `(customer_id = 1)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
4. Detect overlapping effective ranges per natural key.
   **Inputs/evidence:** For sql-53 Exercise 4, read from `dim_customer`. Build the answer toward `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-53 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`. The final order is `a.customer_id, version_a, version_b`.
   **Verify:** For sql-53 Exercise 4, project `customer_id` plus the raw source columns from `dim_customer` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
5. Make an unchanged-source rerun idempotent.
   **Inputs/evidence:** For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
   **Expected result/shape:** For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
   **Verify:** For sql-53 Exercise 5, rerun the nullable-safe attribute comparison against `desired_customer_state`; the result must report zero differences. Then alter one staged attribute and require a result of exactly one difference before applying any close/insert statements.
6. Define a same-day change sequence policy.
   **Inputs/evidence:** For sql-53 Exercise 6, read from `training.customers`, `dim_customer`, and `changed_customers`. Compute `first_version`, and `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-53 Exercise 6, expected output: exactly one aggregate summary row. The final columns are `first_version`, and `ROLLBACK`.
   **Verify:** For sql-53 Exercise 6, evaluate each of `first_version`, and `ROLLBACK` in a separate control `SELECT` over `training.customers`, `dim_customer`, and `changed_customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

Check multiple-current versions, gaps, and overlaps.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Temporal fact mapping count must equal source item count.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Are close and insert operations in one atomic transaction?
- Does temporal fact mapping preserve the source fact count exactly?

## Next step

Continue in the same database to
[Day 54; warehouse aggregates](day54_project3_dwh_part3_aggregations.md).

## Deep dive and reference

## Project focus

- Detect changed customer and product attributes.
- Close the old current row and insert a new version.
- Map historical facts to the dimension version valid on the fact date.

## Preconditions and state

Run Day 52 first in the same database. Day 53 reads the committed `dwh` schema
but performs its changes inside a transaction and rolls them back.

The learner stages deterministic changes for ten customers and ten products.
For each changed business key, the current row closes at `CURRENT_DATE - 1`,
and the replacement starts at `CURRENT_DATE`.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## SCD reasoning

- Close and insert are one atomic transaction.
- `customer_id` and `product_id` are business keys; their surrogate keys identify
  versions.
- Inclusive bounds require the old row to end one day before the new row starts.
- A production dimension should prevent more than one current row per business
  key and overlapping validity ranges.

## Validation and limits

- Temporal fact mapping count must equal source item count.
- A lower count signals a date/version gap; a higher count signals overlapping
  versions.
- Audit defaults cover inserts but do not explain update actors; set them on
  close operations too.
- The course uses date-grain validity. Timestamp-effective changes require a
  different boundary model.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-53 — Project3 DWH Part2 SCD.

I have completed the direct catalog prerequisite: `sql-52`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day53_project3_dwh_part2_scd.md
- Answer-free learner SQL: sql/postgres-60day/day53_project3_dwh_part2_scd.sql

Key terms to teach in context: SCD Type 2, Business key, Validity interval. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For one changed customer, locate exactly one current row, set its validto to the day before the new version, and insert the successor at CURRENTDATE. Then as-of join a fact date using inclusive bounds and verify it resolves to one surrogate key—not zero and not two.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-53/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
