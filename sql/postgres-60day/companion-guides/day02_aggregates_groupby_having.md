# Day 02: Aggregations, GROUP BY, HAVING, Grouping Sets (Companion Guide)

## How to run this lesson

From the repository root, run `./classroom`, select PostgreSQL and **sql-02**, then choose **Whole SQL lesson (psql)**. The file connects to `advanced_sql_training`, sets `search_path` to `training` inside a transaction that ends in `ROLLBACK`, and prints three grouped summaries: customers per country, net revenue per product category, and order count with average order total per calendar month.

You edit
`.learning/sql/sql-02/lesson/workspace/sql/postgres-60day/day02_aggregates_groupby_having.sql`.
To see what `GROUP BY` does, temporarily add `c.segment` to the first `SELECT` without adding it to `GROUP BY`. PostgreSQL refuses with `column "c.segment" must appear in the GROUP BY clause or be used in an aggregate function`, because one country row has no single segment to show.

The study guide's [classroom quick start](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom) covers what to do when the classroom will not launch. There are also [contributors' notebook instructions](../../STUDY-GUIDE.md#optional-contributor-notebook-route), which learners can skip.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 01; SELECT, filtering, and ordering](day01_select_where_orderby.md)
- **Artifacts:** [learner SQL](../day02_aggregates_groupby_having.sql) ·
  [solution reasoning](../solutions/day02_solutions.md) ·
  [executable solution](../solutions/day02_solutions.sql)

## A beginner's mental model for this lesson

Day 01 returned stored rows one at a time. Today each output row summarizes many input rows. `GROUP BY c.country` sorts the 500 customers into buckets that share a country, and an **aggregate** such as `COUNT(*)`, `SUM(...)` or `AVG(...)` reduces each bucket to one value. The result has one row per bucket, so the first query prints eight rows, not 500.

The **group grain** is what one of those rows stands for: one country, one product category, one calendar month. Every column in the `SELECT` list must either be a grouping key or sit inside an aggregate, because a country row has one country but 62 or 63 different emails. A **grouping set** is one particular list of grouping keys; this lesson uses one set per query, and `ROLLUP` or `GROUPING SETS` later ask for several at once, such as per category and grand total.

Two filters act at different moments. `WHERE` runs first and removes input rows before any bucket exists, so it cannot mention `SUM(amount)`; PostgreSQL answers `aggregate functions are not allowed in WHERE`. `HAVING` runs after the aggregates and keeps or drops whole groups. `ORDER BY` comes last, which is why it may sort by an output alias such as `customers` while `HAVING` may not.

## Two worked SQL examples

### Example 1

```sql
SELECT
  c.country,
  COUNT(*) AS customers
FROM
  customers c
GROUP BY
  c.country
ORDER BY
  customers DESC,
  c.country;
```

**How to read it:** `FROM customers c` reads all 500 customers. `GROUP BY c.country` forms one bucket per country and `COUNT(*) AS customers` counts the rows in each. Because `ORDER BY` runs after the `SELECT` list, it can sort by the alias `customers`, largest first, and then by `c.country` so countries with the same count appear alphabetically.

**Expected result/shape:** Eight rows. CA, DE, GB and US come first with 63 customers each, followed by AU, BR, FR and IN with 62 each; the counts add up to 500. Without `c.country` as the second sort key, the four countries tied at 63 could print in any order from one run to the next.

### Example 2

```sql
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
HAVING
  SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY
  revenue DESC,
  p.category;
```

**How to read it:** Order lines are joined to `products` to learn each line's category, then grouped by `p.category`. The `SELECT` list reports net revenue, discounts included, rounded to cents. The `HAVING` clause tests a different number, `SUM(oi.unit_price * oi.quantity)`, which ignores discounts, and keeps a category only if that gross total exceeds 10,000. `ORDER BY revenue DESC, p.category` puts the best seller first.

**Expected result/shape:** Six rows: Sports 397,427.70, Electronics 394,424.39, Home 393,760.42, Beauty 393,436.90, Apparel 390,404.94 and Books 386,192.77. The `HAVING` threshold removes nothing, because every category's gross total is near 400,000. It still shows the mechanics: the expression in `HAVING` need not match the one displayed, which is easy to miss when a report filters on one figure and shows another.

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

In Example 2, one row of `order_items JOIN products` is one order line with its product's category: 13,085 rows. `GROUP BY p.category` turns them into six buckets of 2,145 to 2,192 lines. `SUM(unit_price * quantity * (1 - discount))` then gives each bucket its net revenue, and only after that does `HAVING SUM(unit_price * quantity) > 10000` test each category's undiscounted total. All six pass easily, since the smallest, Books, is 391,855.58 before discounts. Had the condition been a row test such as `oi.discount = 0`, it would belong in `WHERE` and would change every total by removing lines before grouping.

## Practice assumptions and review method

- **Focus:** Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
- **Assumptions:** Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
- **Failure to watch for:** Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
- **Review loop:** after each grouped query, add up the group counts or totals and compare them with one ungrouped `COUNT(*)` or `SUM(...)` over the same rows: the eight country counts should add to 500, the five expense totals to 50,483,850.00.

## Exercises

Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.

Before writing each query, say in one phrase what an output row stands for (one country, one status, one month) and guess how many rows there will be. Then decide whether each condition tests single rows, which means `WHERE`, or finished groups, which means `HAVING`.

1. **Query writing:** Count customers by country and order countries by count then country.
   **Commit to a guess:** how many countries tie at the top count?
   **Progressive hint:** The output grain is one row per country; include a deterministic secondary sort.
   **Inputs/evidence:** For sql-02 Exercise 1, read all 500 `customers` rows; `country` is `NOT NULL` and takes 8 values. Return `country` and `customer_count`.
   **Expected result/shape:** For sql-02 Exercise 1, return 8 rows, one per country: `CA`, `DE`, `GB`, and `US` with 63 customers each, then `AU`, `BR`, `FR`, and `IN` with 62 each. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
   **Verify:** For sql-02 Exercise 1, confirm the 8 counts sum to 500, matching `SELECT COUNT(*) FROM customers`, and that the four-way tie at 63 is listed alphabetically. Inside a rolled-back transaction, move customer 1 from `US` to `NZ`; the result must grow to 9 rows, with `US` falling to 62 and `NZ` appearing last with 1.
2. **Query writing:** Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
   **Commit to a guess:** with 300 products spread over six categories, will any category fall below 100,000?
   **Progressive hint:** Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
   **Inputs/evidence:** For sql-02 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; every item finds its product, and the 6 categories hold between 2,145 and 2,192 items each. Return `category`, `net_revenue`, and `average_unit_price`.
   **Expected result/shape:** For sql-02 Exercise 2, return 6 rows, because every category clears the 100,000 `HAVING` threshold; `Sports` leads at 397427.70 and `Books` is last at 386192.77. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
   **Verify:** For sql-02 Exercise 2, confirm the 6 `net_revenue` values sum to 2355647.12, the same total that `SUM(unit_price * quantity * (1 - discount))` gives over all of `order_items`. Raise the threshold to 395000 and only `Sports` must remain, which proves `HAVING` filters groups after they are summed.
3. **Query writing:** Summarize order count and average total by status, retaining statuses with at least 100 orders.
   **Commit to a guess:** 4,362 orders spread over five statuses; how many statuses clear the bar of 100?
   **Progressive hint:** Filter groups after aggregation with `HAVING COUNT(*)`.
   **Inputs/evidence:** For sql-02 Exercise 3, read all 4,362 `orders` rows across 5 `status` values. Return `status`, `order_count`, and `average_order_total`.
   **Expected result/shape:** For sql-02 Exercise 3, return 5 rows, since every status has far more than 100 orders: `placed` and `shipped` with 873 each, then `delivered`, `paid`, and `returned` with 872 each. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
   **Verify:** For sql-02 Exercise 3, confirm the 5 counts sum to 4,362 and that `paid` has the highest average at 548.24. Change the filter to `HAVING COUNT(*) >= 873`; only `placed` and `shipped` must remain, so the tie at 873 is broken by `status` name.
4. **Prediction:** Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
   **Commit to a guess:** write down all three numbers before running.
   **Progressive hint:** `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
   **Inputs/evidence:** For sql-02 Exercise 4, read from `customers` and count, in one aggregate query, all rows as `all_rows`, rows with a non-null `email` as `nonnull_email_rows`, and rows whose `email` is NULL as `missing_email_rows`.
   **Expected result/shape:** For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
   **Verify:** For sql-02 Exercise 4, confirm `nonnull_email_rows + missing_email_rows = all_rows`; the seed returns 500, 500, and 0 because every seeded customer has an email. In a transaction you roll back, set one customer's `email` to NULL and rerun: expect 500, 499, and 1.
5. **Debugging:** Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
   **Commit to a guess:** run the broken version first and note the exact error text.
   **Progressive hint:** `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
   **Inputs/evidence:** For sql-02 Exercise 5, read the 10,000 `expenses` rows, 2,000 in each of 5 categories, with amounts from 100.51 to 9998.28. Return `category` and `total_expense`.
   **Expected result/shape:** For sql-02 Exercise 5, return 5 rows, because every category total is above 1,000,000: `Marketing` first at 10108910.00 and `Infrastructure` last at 10080670.00. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
   **Verify:** For sql-02 Exercise 5, rerun the grouping without `HAVING` and confirm the same 5 totals, each over 2,000 rows. Raise the threshold to 10100000; only `Marketing` and `COGS` (10103230.00) must remain.
6. **Extension:** Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
   **Commit to a guess:** will the current month have about as many orders as the month before it?
   **Progressive hint:** Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
   **Inputs/evidence:** For sql-02 Exercise 6, read from `orders` placed on or after `date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`, group them by `date_trunc('month', order_date)`, and return each month's order count, summed `total_amount`, and count of `returned` orders.
   **Expected result/shape:** For sql-02 Exercise 6, return 12 month rows in chronological order, since every month of the window has orders; the first `order_month` is the first day of the month eleven months before the current one, and the last is the current month. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
   **Verify:** For sql-02 Exercise 6, confirm that `order_month` values are unique and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`; for one month, recount its `returned` orders directly and compare the result with `returned_orders`.

## Common mistakes and how to recover

- **A column that is neither grouped nor aggregated:** `SELECT c.country, c.segment, COUNT(*) ... GROUP BY c.country` fails, because each country holds customers from several segments. Either add `c.segment` to `GROUP BY` (one row per country and segment) or wrap it in an aggregate.
- **An aggregate in `WHERE`:** `WHERE SUM(amount) > 1000000` raises `aggregate functions are not allowed in WHERE`. Move the test to `HAVING`, as Exercise 5 does.
- **An alias in `HAVING`:** `HAVING customer_count > 62` fails with `column "customer_count" does not exist`. `HAVING` runs before the `SELECT` list names its columns, so repeat the expression: `HAVING COUNT(*) > 62`.
- **Treating `COUNT(email)` as a row count:** it skips `NULL` emails. Here both give 500, but on data with gaps they differ, and Exercise 4 shows how to count the gaps directly.
- **Expecting zero from an empty group:** `SUM(amount)` over no rows is `NULL`, not 0, and a grouped query over no rows returns no groups at all. `SELECT SUM(amount) FROM expenses WHERE amount < 0` prints one empty cell.

When `ON_ERROR_STOP` halts the file, read the first error only, fix it, and rerun the whole lesson; the study guide's [error-recovery advice](../../STUDY-GUIDE.md#recover-from-common-failures) walks through the steps.

## Self-check

- Can you state the grain of every result and explain why each selected
  non-aggregate belongs in `GROUP BY`?
- Do subtotal rows use `GROUPING(...)` rather than assuming every `NULL` is a
  subtotal marker?

## Next step

Continue to [Day 03; inner joins](day03_inner_joins.md).

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
- Dividing integers by hand: `SUM(quantity) / COUNT(*)` truncates the fraction. `AVG(quantity)` does not, because PostgreSQL returns `numeric` from `AVG` of an integer column (3.0002 for `order_items`).

Check your understanding
- When do you use HAVING instead of WHERE? Give an example that would be wrong with WHERE.
- How does GROUPING SETS differ from running multiple queries with UNION ALL?

Further reading
- Postgres aggregation: https://www.postgresql.org/docs/17/functions-aggregate.html
- GROUPING SETS/ROLLUP/CUBE: https://www.postgresql.org/docs/17/queries-table-expressions.html#QUERIES-GROUPING-SETS

## Ask an AI tutor about this lesson

No tutor is needed for this lesson. If you try one, ask it to explain why `ORDER BY customers` works in Example 1 while `HAVING customer_count > 62` fails, then confirm its explanation by running both in `psql`. The study guide's [notes on tutoring with AI](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) describe how to keep a tutor asking questions rather than handing over finished SQL.

```text
Tutor me through sql-02: Aggregates, GROUP BY, and HAVING.

I have completed the direct catalog prerequisite: `sql-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day02_aggregates_groupby_having.md
- Answer-free learner SQL: sql/postgres-60day/day02_aggregates_groupby_having.sql

Key terms to teach in context: Aggregate, Group grain, Grouping set. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: In the category-revenue query, first identify one joined row as an order line. Next group those rows by product category, calculate the revenue aggregate, and only then apply `HAVING`. Compare that flow with a date predicate in `WHERE`, which removes rows before the category totals are computed.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-02/ working copy. Never point setup, reset, DDL, or DML
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
