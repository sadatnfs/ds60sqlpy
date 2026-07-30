# Day 02 — Aggregations, GROUP BY, HAVING, Grouping Sets (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 01 — SELECT, filtering, and ordering](day01_select_where_orderby.md)
- **Artifacts:** [learner SQL](../day02_aggregates_groupby_having.sql) ·
  [solution reasoning](../solutions/day02_solutions.md) ·
  [executable solution](../solutions/day02_solutions.sql)

## Learning objectives

- Aggregate rows at a declared grain with `GROUP BY`.
- Choose `WHERE` for row filters and `HAVING` for post-aggregation group filters.
- Produce subtotals without confusing subtotal `NULL`s with data `NULL`s.

## Vocabulary and concepts

- **Aggregate:** a function such as `SUM` or `COUNT` that summarizes rows.
- **Group grain:** the real-world meaning of one output row after grouping.
- **Grouping set:** one of several grouping-key combinations evaluated in one
  aggregate query.

## Worked example / walkthrough

In the category-revenue query, first identify one joined row as an order line.
Next group those rows by product category, calculate the revenue aggregate, and
only then apply `HAVING`. Compare that flow with a date predicate in `WHERE`,
which removes rows before the category totals are computed.

## Practice assumptions and review method

- **Focus:** Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
- **Assumptions:** Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
- **Failure to watch for:** Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Count customers by country and order countries by count then country.
   **Progressive hint:** The output grain is one row per country; include a deterministic secondary sort.
   **Expected shape:** One row per country.
2. **Query writing:** Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
   **Progressive hint:** Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
   **Expected shape:** One row per qualifying category.
3. **Query writing:** Summarize order count and average total by status, retaining statuses with at least 100 orders.
   **Progressive hint:** Filter groups after aggregation with `HAVING COUNT(*)`.
   **Expected shape:** One row per qualifying order status.
4. **Prediction:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
   **Progressive hint:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
   **Expected shape:** One row; present plus missing equals total.
5. **Debugging:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
   **Progressive hint:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
   **Expected shape:** One row per expense category over the threshold.
6. **Extension:** Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
   **Progressive hint:** Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
   **Expected shape:** Up to 12 month rows in chronological order.

## Self-check

- Can you state the grain of every result and explain why each selected
  non-aggregate belongs in `GROUP BY`?
- Do subtotal rows use `GROUPING(...)` rather than assuming every `NULL` is a
  subtotal marker?

## Next step

Continue to [Day 03 — inner joins](day03_inner_joins.md).

## Deep dive and reference

Learning objectives
- Master aggregate functions: COUNT/COUNT(DISTINCT), SUM, AVG, MIN/MAX, BOOL_AND/BOOL_OR
- Use GROUP BY on columns and expressions; understand functional dependencies
- Filter groups with HAVING; distinguish WHERE vs HAVING
- Apply advanced grouping: GROUPING SETS, ROLLUP, CUBE; handle NULLs in groups

Why this matters
Aggregations turn rows into insights. Correct use of GROUP BY, HAVING, and grouping sets is the backbone of reporting, dashboards, and dimensional analysis.

Core concepts and deep dive
- Aggregate functions
  - COUNT(*) counts rows; COUNT(col) counts non-null col values. COUNT(DISTINCT col) deduplicates within group.
  - AVG(col) = SUM(col)/COUNT(col) over non-null rows; watch type (integer division vs numeric).
  - BOOL_AND/BOOL_OR aggregate booleans; use for rule checks per group.
- Grouping scope
  - GROUP BY partitions the FROM result into groups; aggregates compute per group. SELECT may include only group keys and aggregates.
  - You may group by expressions: GROUP BY date_trunc('month', order_date).
  - Functional dependency (Postgres extension): In some modes, non-key columns can be selected if functionally dependent on the GROUP BY keys (e.g., primary key), but rely on explicit grouping for portability.
- WHERE vs HAVING
  - WHERE filters rows before grouping. HAVING filters groups after aggregation.
  - Example: WHERE order_date >= current_date - interval '90 days'; HAVING SUM(revenue) > 1000.
- NULL handling in groups
  - GROUP BY treats NULLs as equal, forming a single NULL group. Use COALESCE to bucket NULLs into labels.
- Grouping sets
  - GROUPING SETS((a,b), (a), ()) lets you compute multi-level totals in one pass. ROLLUP(a,b) is shorthand for ((a,b), (a), ()). CUBE(a,b) creates all combinations.
  - Use GROUPING(a) to detect subtotal rows (returns 1 when a is aggregated away).

Walkthrough of the day’s script (mapping to your data)
- Customer counts by `customers.country` introduce grouping and count aliases.
- Net line revenue by `products.category` uses `HAVING` to retain categories
  whose undiscounted line value exceeds 10,000.
- Monthly order counts and average `orders.total_amount` demonstrate grouping
  by `date_trunc('month', order_date)`.

Advanced patterns
- Conditional aggregation
  - `SUM(amount) FILTER (WHERE method = 'card') AS card_payments`
  - `COUNT(*) FILTER (WHERE status = 'returned') AS returned_orders`
- Distinct inside aggregates
  - SUM(DISTINCT amount) is allowed but costly. Prefer dedup in a subquery when needed.
- Multi-level totals
  - Use GROUPING SETS/ROLLUP/CUBE with GROUPING() indicator columns to format reports with subtotal rows.

Anti-patterns and pitfalls
- Selecting non-grouped, non-aggregated columns; results are undefined in standard SQL.
- Confusing WHERE and HAVING; using HAVING for row-level filters degrades performance.
- Relying on integer AVG without casting (integer division truncates). Cast to numeric: AVG(col::numeric).

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Check your understanding
- When do you use HAVING instead of WHERE? Give an example that would be wrong with WHERE.
- How does GROUPING SETS differ from running multiple queries with UNION ALL?

Further reading
- Postgres aggregation: https://www.postgresql.org/docs/current/functions-aggregate.html
- GROUPING SETS/ROLLUP/CUBE: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS
