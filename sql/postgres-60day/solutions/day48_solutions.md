# Day 48 Solutions — E-commerce Analytics, Part 3


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day48_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day48_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Market basket, Attribution window, Fractional credit. Its worked-model focus is:
Deduplicate products within each order, self-join with a.productid < b.productid, and count orders per pair. For attribution, deduplicate campaigns per purchase before dividing one credit by the distinct campaign count; verify allocated credit sums to one for every assisted purchase.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

The starter demonstrates market-basket pairs and first/last touch. The exercises
ask for seven-day assisted conversions and equal-credit multi-touch
attribution. The canonical file is
[`day48_solutions.sql`](day48_solutions.sql).

## Exercise 1 — Assisted conversions

```sql
SET search_path TO training, public;

WITH purchases AS (
  SELECT event_id AS purchase_event_id,
         customer_id,
         event_time AS purchase_time
  FROM events
  WHERE event_type = 'purchase'
), qualifying_touches AS (
  SELECT p.purchase_event_id,
         p.customer_id,
         COALESCE(t.metadata->>'campaign', 'none') AS campaign
  FROM purchases p
  JOIN events t
    ON t.customer_id = p.customer_id
   AND t.event_type <> 'purchase'
   AND t.event_time >= p.purchase_time - interval '7 days'
   AND t.event_time < p.purchase_time
)
SELECT campaign,
       COUNT(DISTINCT purchase_event_id) AS assisted_conversions,
       COUNT(DISTINCT customer_id) AS assisted_customers
FROM qualifying_touches
GROUP BY campaign
ORDER BY assisted_conversions DESC, campaign;
```

Expected grain: one row per campaign. A purchase can appear under several
campaigns, so `assisted_conversions` is not additive across rows.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 2 — Equal fractional multi-touch credit

```sql
SET search_path TO training, public;

WITH purchases AS (
  SELECT event_id AS purchase_event_id,
         customer_id,
         event_time AS purchase_time
  FROM events
  WHERE event_type = 'purchase'
), campaign_touches AS (
  SELECT DISTINCT
         p.purchase_event_id,
         p.customer_id,
         COALESCE(t.metadata->>'campaign', 'none') AS campaign
  FROM purchases p
  JOIN events t
    ON t.customer_id = p.customer_id
   AND t.event_type <> 'purchase'
   AND t.event_time >= p.purchase_time - interval '7 days'
   AND t.event_time < p.purchase_time
), credited AS (
  SELECT *,
         1.0 / COUNT(*) OVER (PARTITION BY purchase_event_id) AS fractional_credit
  FROM campaign_touches
)
SELECT campaign,
       ROUND(SUM(fractional_credit), 4) AS attributed_conversions,
       COUNT(DISTINCT purchase_event_id) AS touched_conversions
FROM credited
GROUP BY campaign
ORDER BY attributed_conversions DESC, campaign;
```

For every purchase that has at least one qualifying campaign, credits across
its distinct campaigns sum to 1.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Reasoning, safety, and pitfalls

- The conversion anchor here is a `purchase` event, not an order. State and test
  that business definition before comparing this result with order metrics.
- `DISTINCT` prevents repeated touches by the same campaign from receiving
  multiple shares.
- The half-open interval includes exactly seven days before the purchase but
  excludes the purchase timestamp itself.
- Campaign value `'none'` makes missing metadata visible; decide whether it
  should receive attribution in production.

## Exercise 3 — Credit distinct campaigns

The solution collapses repeated touches to `(purchase, campaign)` before
dividing. That implements equal credit per distinct campaign rather than per
event.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Compute basket association metrics

Distinct order/product membership defines baskets. Pair counts feed support;
single-product basket counts feed directional confidence; lift compares the
observed pair rate with independence.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Assign a touch only once

A LATERAL subquery chooses the earliest qualifying purchase after each touch.
`ORDER BY order_date, order_id LIMIT 1` prevents reuse and makes ties stable.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Reconcile direct purchases

The query starts from every order and left-joins its most recent qualifying
touch. Missing touches become `(direct)`, so bucket counts sum to purchases.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.
