# Day 41: Complex Aggregations

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-41**. The
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
   `.learning/sql/sql-41/lesson/workspace/sql/postgres-60day/day41_complex_aggregations.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-41
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
- **Prerequisites:** [Day 40; advanced analytic functions](day40_analytic_functions_advanced.md)
- **Artifacts:** [learner SQL](../day41_complex_aggregations.sql) ·
  [solution reasoning](../solutions/day41_solutions.md) ·
  [executable solution](../solutions/day41_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is FILTER clause, Conditional aggregate, Ordered aggregation. Its worked SQL reads or creates `order_items`, `products`, `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `category` with columns `category`, `total_qty`, `qty_30d`, `qty_90d`, `revenue`, and `revenue_30d` from `order_items`, `products`, and `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `category`, `total_qty`, `qty_30d`, `qty_90d`, `revenue`, and `revenue_30d`. Independently group `order_items`, `products`, and `orders` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day41_complex_aggregations.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT
  p.category,
  SUM(oi.quantity) AS total_qty,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) FILTER (WHERE o.order_date >= now() - interval '30 days'), 2) AS revenue_30d
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
GROUP BY
  p.category
ORDER BY
  revenue DESC;
```

**How to read it:** Example 1: Start with `order_items`, `products`, and `orders` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `category`, `total_qty`, `qty_30d`, `qty_90d`, `revenue`, and `revenue_30d`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `category` with columns `category`, `total_qty`, `qty_30d`, `qty_90d`, `revenue`, and `revenue_30d` from `order_items`, `products`, and `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
SELECT
  c.country,
  SUM(
    CASE WHEN o.status IN ('paid', 'shipped', 'delivered') THEN
      1
    ELSE
      0
    END) AS successful_orders,
  SUM(
    CASE WHEN o.status = 'returned' THEN
      1
    ELSE
      0
    END) AS returned_orders,
  ROUND(SUM(
      CASE WHEN o.status <> 'returned' THEN
        o.total_amount
      ELSE
        0
      END), 2) AS net_revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
GROUP BY
  c.country
ORDER BY
  net_revenue DESC;
```

**How to read it:** Example 2: Start with `orders`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `country`, `successful_orders`, `returned_orders`, and `net_revenue`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `country` with columns `country`, `successful_orders`, `returned_orders`, and `net_revenue` from `orders`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Produce several conditional measures from one controlled fact grain.
- Build deterministic ordered labels after ranking within a partition.
- Generate detail rows, one-dimensional subtotals, and a grand total with
  `CUBE`.
- Use `GROUPING` to identify the grain of every subtotal row without confusing
  a generated subtotal marker with a stored SQL `NULL`.

## Vocabulary and concepts

- **FILTER clause:** a per-aggregate condition written after the aggregate.
- **Conditional aggregate:** a measure calculated only for qualifying rows.
- **Ordered aggregation:** concatenation or collection under a specified order.
- **Grouping set:** one explicit list of columns that defines an aggregate
  grain. `GROUPING SETS` asks PostgreSQL for several such grains in one query.
- **CUBE:** shorthand for every grouping set that can be formed from the listed
  dimensions. Two dimensions produce four levels.
- **GROUPING:** a function evaluated on grouping expressions. It returns `1`
  when an expression was omitted to create the current subtotal and `0` when
  the expression participates in that row's grouping key.
- **Grouping mask:** the integer returned by multi-argument `GROUPING`. Read its
  bits from right to left in the same order as the arguments.

## How to read a two-dimensional CUBE

`CUBE(country, category)` is equivalent to:

```sql
GROUP BY GROUPING SETS (
  (country, category), -- detail
  (country),           -- one country across all categories
  (category),          -- one category across all countries
  ()                   -- grand total
)
```

PostgreSQL encodes which expressions were omitted with
`GROUPING(country, category)`. The rightmost argument, `category`, is the
least-significant bit:

| `grouping_mask` | Included grouping key | Meaning |
|---:|---|---|
| `0` | `country, category` | detail |
| `1` | `country` | country subtotal |
| `2` | `category` | category subtotal |
| `3` | none | grand total |

This mask is a grain label, not a data-cleaning test. A stored `NULL` country
in a detail group still has a country grouping bit of `0`; a generated country
subtotal marker has that bit set to `1`. Test `GROUPING(country)`, not
`country IS NULL`, when you need to distinguish them.

## Worked example / walkthrough

Establish one order-line relation, then calculate 30-day revenue, 90-day
revenue, order count, and customer count in one category group using `FILTER`.
Reconcile each measure with a simpler single-purpose query before trusting the
combined dashboard.

## Exercises

Complete these in the [learner SQL](../day41_complex_aggregations.sql):

1. Build six category metrics with `FILTER`.
   **Inputs/evidence:** For sql-41 Exercise 1, read from `orders`, `order_items`, `products`, and `training.products`. Build the answer toward `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-41 Exercise 1, expected output: one row for each category in `training.products`, with six metric columns. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
   **Verify:** For sql-41 Exercise 1, independently aggregate `orders`, `order_items`, `products`, and `training.products` by `category`; require one output row for every distinct `category` tuple and compare `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_30d`, `revenue_90d`, and `orders_30d` for the existing `category` tuple and verify the new tuple appears exactly once.
2. List each country's top five products with `string_agg`.
   **Inputs/evidence:** For sql-41 Exercise 2, read from `customers`, `orders`, `order_items`, and `products`. First aggregate at (`country`, `product_id`, `name`) grain, then rank products within each country; build the answer toward `country` and `top_five_products`.
   **Expected result/shape:** For sql-41 Exercise 2, expected output: one row per represented country. `top_five_products` contains at most five product names ordered by `revenue DESC, product_id`; `product_id` is the deterministic tie-breaker. The final columns are `country` and `top_five_products`. The final order is `country`.
   **Verify:** For sql-41 Exercise 2, independently aggregate line revenue at (`country`, `product_id`, `name`) grain and rank with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)`. For every country, compare the ordered products used by `string_agg`, require no more than five ranked products, and confirm a country with fewer than five products is not padded.
3. Predict explicit grouping sets versus a two-column `CUBE`.
   **Inputs/evidence:** For sql-41 Exercise 3, calculate line revenue from `orders`, `customers`, `order_items`, and `products`, then aggregate with `CUBE(country, category)`. Build the answer toward `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`.
   **Expected result/shape:** For sql-41 Exercise 3, expected output: every grouping level emitted by the two-dimensional cube. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
   **Verify:** For sql-41 Exercise 3, compare mask `0` with an independent (`country`, `category`) aggregate, mask `1` with a country aggregate, and mask `2` with a category aggregate; require exactly one mask `3` row. Within each mask, the sum of `revenue` must equal the independent all-lines revenue total.
4. Build country status/revenue/customer metrics with `FILTER`.
   **Inputs/evidence:** For sql-41 Exercise 4, read from `orders`, and `customers`. Build the answer toward `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-41 Exercise 4, expected output: one row per `country`. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
   **Verify:** For sql-41 Exercise 4, independently aggregate `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `orders`, `paid_orders`, and `paid_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
5. Distinguish stored NULLs from subtotal NULLs with `GROUPING`.
   **Inputs/evidence:** For sql-41 Exercise 5, read `customers.country` and append one controlled `NULL::text` input row in a `country_input` CTE. Apply `GROUPING(country)` to the grouped expression and build `country_label`, `is_subtotal`, and `customers`.
   **Expected result/shape:** For sql-41 Exercise 5, expected output: one detail row per distinct input country with `is_subtotal = 0`, including a `(stored null)` row, plus exactly one `ALL COUNTRIES` row with `is_subtotal = 1`. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
   **Verify:** For sql-41 Exercise 5, require exactly one row with `is_subtotal = 1`, require the `(stored null)` row to have `is_subtotal = 0`, and verify that detail-row `customers` sum to the grand-total `customers`. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
6. Return a typed empty array for an empty aggregate input.
   **Inputs/evidence:** For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)` and use a same-type `COALESCE` fallback. Build the answer toward `empty_email_array`.
   **Expected result/shape:** For sql-41 Exercise 6, expected output: exactly one scalar row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
   **Verify:** For sql-41 Exercise 6, assert that the uncoalesced filtered `array_agg` result is `NULL`, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`.

Decide explicitly when an absent measure should be `NULL` or zero.

## Self-check

- Are order and customer counts protected from line-level fanout?
- Is the top-five label order stable under metric ties?
- Can you expand `CUBE(country, category)` into its four explicit grouping
  sets without looking?
- Can you explain why masks `1` and `2` mean different subtotal grains even
  though each prints one NULL dimension?
- If `country` contains a stored NULL, can you prove why
  `GROUPING(country) = 0` for that detail row?
- Why does a scalar aggregate over no qualifying rows return one row, and why
  must the empty-array fallback be typed as `text[]`?

## Next step

Continue to [Day 42; data quality and validation](day42_data_quality_validation.md).

## Deep dive and reference

## What you will learn

- Calculate several conditional metrics in one grouped query with `FILTER`.
- Express equivalent conditional aggregates with `CASE`.
- Build ordered labels with `string_agg`.

## How the learner script uses the current schema

The starter calculates category units and revenue over all history, 30 days, and
90 days by joining `orders`, `order_items`, and `products`. It also reports
successful/returned orders by `customers.country`, then demonstrates
`string_agg(DISTINCT products.name, ...)` by category.

The valid successful status set used by the script is `paid`, `shipped`, and
`delivered`; `returned` is reported separately. Use only the statuses supplied
by the course setup.

## Multi-metric design

- Establish line-item grain before summing net revenue.
- Use `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT customer_id)` when a join
  has expanded each order to multiple item rows.
- Guard every denominator with `NULLIF`.
- Conditional sums can be `NULL` when no row qualifies; decide whether display
  policy should use `COALESCE`.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- Applying a global `LIMIT 5` does not produce five products per country; rank
  within country first.
- Do not sum `orders.total_amount` after joining to item rows.
- Add a deterministic tie-break such as `product_id`.
- Validate dashboard totals against a simpler single-metric query before
  trusting the combined report.

## Expanded practice lab

Prompts 3–6 make aggregate grain and subtotal identity explicit. A two-column
`CUBE` emits detail, both one-dimensional subtotals, and a grand total; the
listed `GROUPING SETS` intentionally omits detail. Use `GROUPING(column)` rather
than `column IS NULL` to detect a subtotal.

`FILTER` keeps several metric definitions readable in one grouped query.
Aggregates over no input rows often return NULL, so `COALESCE(array_agg(...),
'{}'::text[])` needs an explicit type matching the aggregate result.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-41 — Complex Aggregations.

I have completed the direct catalog prerequisite: `sql-40`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day41_complex_aggregations.sql

Key terms to teach in context: FILTER clause, Conditional aggregate, Ordered aggregation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-41/ working copy. Never point setup, reset, DDL, or DML
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
