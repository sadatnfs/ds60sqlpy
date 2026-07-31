# Day 41 Solutions — Complex Aggregations


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day41_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day41_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are FILTER clause, Conditional aggregate, Ordered aggregation. Its worked-model focus is:
Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.

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

The learner script introduces `FILTER`, conditional aggregation, and
`string_agg`. The two exercises turn those techniques into a category dashboard
and a country-level top-product label. The canonical runnable answer is also in
[`day41_solutions.sql`](day41_solutions.sql).

## Exercise 1 — Six category dashboard metrics

Build one row per product category containing:

1. revenue in the last 30 days;
2. revenue in the last 90 days;
3. distinct orders in the last 30 days;
4. units in the last 30 days;
5. distinct customers in the last 90 days; and
6. revenue per order in the last 30 days.

```sql
SET search_path TO training, public;

WITH lines AS (
  SELECT p.category,
         o.order_id,
         o.customer_id,
         o.order_date,
         oi.quantity,
         oi.unit_price * oi.quantity * (1 - oi.discount) AS revenue
  FROM orders o
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
)
SELECT category,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ), 2) AS revenue_30d,
       ROUND(SUM(revenue) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ), 2) AS revenue_90d,
       COUNT(DISTINCT order_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS orders_30d,
       SUM(quantity) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
       ) AS units_30d,
       COUNT(DISTINCT customer_id) FILTER (
         WHERE order_date >= CURRENT_TIMESTAMP - interval '90 days'
       ) AS customers_90d,
       ROUND(
         SUM(revenue) FILTER (
           WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
         )
         / NULLIF(
             COUNT(DISTINCT order_id) FILTER (
               WHERE order_date >= CURRENT_TIMESTAMP - interval '30 days'
             ),
             0
           ),
         2
       ) AS revenue_per_order_30d
FROM lines
GROUP BY category
ORDER BY revenue_30d DESC NULLS LAST, category;
```

Expected shape: one row for each category in `training.products`, with six
metric columns. A category with no qualifying recent activity can have `NULL`
windowed sums. `NULLIF` makes revenue per order `NULL` instead of raising a
division-by-zero error.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
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

## Exercise 2 — Top five product names per country

Rank at `(country, product)` grain before aggregating names. This avoids the
common mistake of applying `LIMIT 5` to the entire result instead of five
products per country.

```sql
SET search_path TO training, public;

WITH product_revenue AS (
  SELECT c.country,
         p.product_id,
         p.name,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM customers c
  JOIN orders o USING (customer_id)
  JOIN order_items oi USING (order_id)
  JOIN products p USING (product_id)
  GROUP BY c.country, p.product_id, p.name
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY country ORDER BY revenue DESC, product_id
         ) AS product_rank
  FROM product_revenue
)
SELECT country,
       string_agg(name, ', ' ORDER BY product_rank) AS top_five_products
FROM ranked
WHERE product_rank <= 5
GROUP BY country
ORDER BY country;
```

Expected shape: one row per represented country and one comma-separated label
ordered from highest to lowest product revenue.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A different window or subquery shape is valid only with the same partition, peer, frame, tie, and output-order semantics.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Reasoning, safety, and pitfalls

- Compute line revenue from `order_items`; do not multiply `orders.total_amount`
  after joining to items because that would repeat the order total per line.
- Use `DISTINCT` inside counts when the input is at line-item grain.
- Add a deterministic tie-breaker (`product_id`) to `ROW_NUMBER`.
- Both answers are read-only and safe to run repeatedly.

## Exercise 3 — Compare grouping sets and CUBE

The `CUBE(country, category)` answer emits detail, both one-dimensional
subtotals, and the grand total. `GROUPING(country, category)` identifies each
generated level.

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

## Exercise 4 — State metric populations with FILTER

Each status/time population appears beside its aggregate, making several
country metrics readable without repeating the whole grouped relation.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
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

## Exercise 5 — Distinguish stored and generated NULLs

`GROUPING(country)` is one only for the generated subtotal. A stored NULL, if
allowed by the model, keeps grouping flag zero and receives a different label.

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

## Exercise 6 — Return a typed empty collection

`array_agg` over no qualifying inputs is NULL. The answer uses
`COALESCE(..., '{}'::text[])`; the explicit type must match the aggregate type.

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
