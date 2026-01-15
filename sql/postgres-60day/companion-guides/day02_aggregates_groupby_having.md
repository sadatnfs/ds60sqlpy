# Day 02 — Aggregations, GROUP BY, HAVING, Grouping Sets (Companion Guide)

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
- Summaries by store/category/period using SUM(...) and COUNT(DISTINCT ...) showcase how to derive revenue, orders, and distinct customers.
- HAVING clauses restrict to meaningful segments (e.g., HAVING SUM(revenue) > 10_000) after aggregation.
- Grouping by expressions such as date_trunc('month', order_date) illustrates time bucketing.

Advanced patterns
- Conditional aggregation
  - SUM(CASE WHEN status='refunded' THEN amount ELSE 0 END) AS refunded_amount
  - COUNT(*) FILTER (WHERE status='completed') AS completed_orders (Postgres syntax)
- Distinct inside aggregates
  - SUM(DISTINCT amount) is allowed but costly. Prefer dedup in a subquery when needed.
- Multi-level totals
  - Use GROUPING SETS/ROLLUP/CUBE with GROUPING() indicator columns to format reports with subtotal rows.

Anti-patterns and pitfalls
- Selecting non-grouped, non-aggregated columns; results are undefined in standard SQL.
- Confusing WHERE and HAVING; using HAVING for row-level filters degrades performance.
- Relying on integer AVG without casting (integer division truncates). Cast to numeric: AVG(col::numeric).

Practice exercises (beyond the script)
1) Compute revenue, orders, AOV (avg order value) by country and month; include a country subtotal and a grand total using ROLLUP.
2) For each product category, compute share of total revenue: SUM(revenue)/SUM(SUM(revenue)) OVER ().
3) Use FILTER to count late shipments by region in the same query that computes total shipments.

Check your understanding
- When do you use HAVING instead of WHERE? Give an example that would be wrong with WHERE.
- How does GROUPING SETS differ from running multiple queries with UNION ALL?

Further reading
- Postgres aggregation: https://www.postgresql.org/docs/current/functions-aggregate.html
- GROUPING SETS/ROLLUP/CUBE: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS
