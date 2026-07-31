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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-48/day48_project1_ecommerce_part3.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Market basket, Attribution window, Fractional credit. Its worked SQL reads or creates `order_items`, `products`, `events`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Allocate equal fractional multi-touch credit.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict repeated-campaign behavior at touch versus campaign grain.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Calculate product-pair support, bidirectional confidence, and lift.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Assign a touch only to the next purchase.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Add a direct bucket and reconcile credit to eligible purchases.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Test touches exactly at both seven-day boundaries.

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

## Practice — match the learner prompts exactly

1. For every `purchase` event, find non-purchase campaign touches for the same
   customer from seven days before the purchase up to, but not including, the
   purchase timestamp. Count distinct assisted purchases by campaign.
2. Deduplicate repeated campaign touches per purchase, divide one conversion
   equally across its distinct campaigns with a window count, and sum
   fractional credit by campaign.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day48_project1_ecommerce_part3.md
- Answer-free learner SQL: sql/postgres-60day/day48_project1_ecommerce_part3.sql

The lesson concepts include Market basket, Attribution window, Fractional credit. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-48/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
