# Day 48 — E-commerce Project, Part 3: Affinity and Attribution

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 47 — cohort retention](day47_project1_ecommerce_part2.md)
- **Artifacts:** [learner SQL](../day48_project1_ecommerce_part3.sql) ·
  [solution reasoning](../solutions/day48_solutions.md) ·
  [executable solution](../solutions/day48_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-48 — Project1 Ecommerce Part3** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-48/lesson/workspace/sql/postgres-60day/day48_project1_ecommerce_part3.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day48_project1_ecommerce_part3.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day48_project1_ecommerce_part3.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Market basket, Attribution window, Fractional credit. Its worked SQL reads or creates `order_items`, `products`, `events`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `order_id`, and `product_id`, capped at 50 rows with columns `order_id`, `product_id`, `p1`, `p2`, `together`, and `product_a` from `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `product_a`, `product_b`, and `together`. Independently group `order_items`, `items`, `pairs`, and `products` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day48_project1_ecommerce_part3.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH items AS (
  SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id
), pairs AS (
  SELECT a.product_id AS p1, b.product_id AS p2, COUNT(*) AS together
  FROM items a
  JOIN items b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
)
SELECT p1.name AS product_a, p2.name AS product_b, together
FROM pairs
JOIN products p1 ON p1.product_id = pairs.p1
JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY together DESC
LIMIT 50;
```

**How to read it:** Example 1: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `product_a`, `product_b`, and `together`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `order_id`, and `product_id`, capped at 50 rows with columns `order_id`, `product_id`, `p1`, `p2`, `together`, and `product_a` from `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH ev AS (
  SELECT e.customer_id, e.event_time, coalesce(e.metadata->>'campaign','none') AS campaign
  FROM events e
), first_last AS (
  SELECT customer_id,
         (ARRAY_AGG(campaign ORDER BY event_time ASC))[1] AS first_touch,
         (ARRAY_AGG(campaign ORDER BY event_time DESC))[1] AS last_touch
  FROM ev
  GROUP BY customer_id
)
SELECT first_touch, last_touch, COUNT(*)
FROM first_last
GROUP BY first_touch, last_touch
ORDER BY COUNT(*) DESC
LIMIT 50;
```

**How to read it:** Example 2: Start with `events` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `first_touch`, and `last_touch`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `customer_id`, capped at 50 rows with columns `customer_id`, `event_time`, `campaign`, `first_touch`, and `last_touch` from `events`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Count each undirected basket pair once per order.
- Attribute a purchase event across distinct qualifying campaigns under an
  explicit lookback rule.

## Vocabulary and concepts

- **Market basket:** the distinct products associated with one order.
- **Attribution window:** the time interval in which a touch can qualify for
  conversion credit.
- **Fractional credit:** one conversion divided across several qualifying
  touches or campaigns.

## Worked example / walkthrough

Deduplicate products within each order, self-join with
`a.product_id < b.product_id`, and count orders per pair. For attribution,
deduplicate campaigns per purchase before dividing one credit by the distinct
campaign count; verify allocated credit sums to one for every assisted purchase.

## Exercises

Complete these in the [learner SQL](../day48_project1_ecommerce_part3.sql):

1. Calculate seven-day assisted conversions.
   **Inputs/evidence:** For sql-48 Exercise 1, read from `events`. Build the answer toward `campaign`, `assisted_conversions`, and `assisted_customers`; keep `campaign` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 1, expected output: one row per campaign. The final columns are `campaign`, `assisted_conversions`, and `assisted_customers`. The final order is `assisted_conversions DESC, campaign`.
   **Verify:** For sql-48 Exercise 1, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `assisted_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `assisted_customers` for the existing `campaign` tuple and verify the new tuple appears exactly once.
2. Allocate equal fractional multi-touch credit.
   **Inputs/evidence:** For sql-48 Exercise 2, read from `events`. Build the answer toward `campaign`, `attributed_conversions`, and `touched_conversions`; keep `campaign` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 2, expected output: one row per `campaign`. The final columns are `campaign`, `attributed_conversions`, and `touched_conversions`. The final order is `attributed_conversions DESC, campaign`.
   **Verify:** For sql-48 Exercise 2, independently aggregate `events` by `campaign`; require one output row for every distinct `campaign` tuple and compare `attributed_conversions`, and `touched_conversions` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `attributed_conversions`, and `touched_conversions` for the existing `campaign` tuple and verify the new tuple appears exactly once.
3. Predict repeated-campaign behavior at touch versus campaign grain.
   **Inputs/evidence:** For sql-48 Exercise 3, read from `events`. Build the answer toward `purchase_id`, `campaign`, and `campaign_credit`; keep `purchase_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 3, expected output: one row per `purchase_id`. The final columns are `purchase_id`, `campaign`, and `campaign_credit`. The final order is `purchase_id, campaign`.
   **Verify:** For sql-48 Exercise 3, choose one complete partition from `events`; hand-calculate its first, middle, and final window values for `campaign`, and `campaign_credit`, then verify output keys remain `purchase_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. Calculate product-pair support, bidirectional confidence, and lift.
   **Inputs/evidence:** For sql-48 Exercise 4, read from `order_items`. Build the answer toward `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`; keep `order_item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 4, expected output: at most 20 rows keyed by `order_item_id`. The final columns are `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift`. The final order is `lift DESC, product_a, product_b`.
   **Verify:** For sql-48 Exercise 4, assert no more than 20 rows, no duplicate `order_item_id`, and no adjacent pair that violates `lift DESC, product_a, product_b`. Rejoin the returned keys to `order_items` to confirm `product_a`, `product_b`, `support`, `confidence_a_to_b`, `confidence_b_to_a`, and `lift` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `lift DESC, product_a, product_b`.
5. Assign a touch only to the next purchase.
   **Inputs/evidence:** For sql-48 Exercise 5, read from `events`, and `orders`. Build the answer toward `touch_id`, `campaign`, `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 5, expected output: one row per `order_id`. The final columns are `touch_id`, `campaign`, `order_id`, and `order_date`. The final order is `e.event_id`.
   **Verify:** For sql-48 Exercise 5, project `order_id` plus the raw source columns from `events`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `touch_id`, `campaign`, `order_id`, and `order_date` values match those staged rows without unintended fanout or loss. Add one row for which `(e.metadata ? 'campaign')` is true and one for which it is false; verify only the matching `order_id` value is returned.
6. Add a direct bucket and reconcile credit to eligible purchases.
   **Inputs/evidence:** For sql-48 Exercise 6, read from `orders`, and `events`. Build the answer toward `attribution_bucket`, and `purchases`; keep `attribution_bucket`, and `purchases` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-48 Exercise 6, expected output: one row per `attribution_bucket`, and `purchases`. The final columns are `attribution_bucket`, and `purchases`. The final order is `purchases DESC, attribution_bucket`.
   **Verify:** For sql-48 Exercise 6, independently aggregate `orders`, and `events` by `attribution_bucket`, and `purchases`; require one output row for every distinct `attribution_bucket`, and `purchases` tuple and compare `row_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `attribution_bucket`, and `purchases` tuple and verify the new tuple appears exactly once.

Test touches exactly at both seven-day boundaries.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Enforce productid ordering to avoid self-pairs and reversed duplicates.
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

- Are reversed pairs, self-pairs, and repeat quantities excluded as intended?
- Does fractional credit reconcile to assisted conversions without implying
  causal impact?

## Next step

Continue to [Day 49 — revenue forecasting](day49_project2_finance_part1.md).

## Deep dive and reference

## Project focus

- Form undirected market-basket product pairs.
- Count campaign-assisted purchase events in a seven-day lookback.
- Allocate equal fractional credit across distinct qualifying campaigns.

## How the learner script uses the current schema

The starter deduplicates products within each order and pairs them with
`a.product_id < b.product_id`. It also extracts campaign from
`events.metadata->>'campaign'` and demonstrates each customer's first and last
touch by `events.event_time`.

The setup provides event types `page_view`, `add_to_cart`, `checkout`,
`purchase`, and `support`. It has no separate sessions or experiment assignment
table.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Attribution reasoning

- The conversion anchor is a purchase event, not an order. State that definition
  before comparing results with order revenue.
- Assisted counts are not additive because one purchase can have several
  assisting campaigns.
- Equal credit for a qualifying purchase should sum to exactly one across its
  distinct campaigns.
- Decide whether missing campaign metadata, represented as `none`, should
  receive credit.

## Validation and limits

- Enforce `product_id` ordering to avoid self-pairs and reversed duplicates.
- The exercise does not establish causal marketing impact.
- The seven-day half-open window needs explicit boundary tests.
- Without session IDs, do not imply session-level journeys.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-48 — Project1 Ecommerce Part3.

I have completed the direct catalog prerequisite: `sql-47`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day48_project1_ecommerce_part3.md
- Answer-free learner SQL: sql/postgres-60day/day48_project1_ecommerce_part3.sql

Key terms to teach in context: Market basket, Attribution window, Fractional credit. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-48/ working copy. Never point setup, reset, DDL, or DML
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
