# Day 27 — Pivoting/Unpivoting: Crosstabs and Conditional Aggregation (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 26 — CTEs with window functions](day26_ctes_with_windows.md)
- **Artifacts:** [learner SQL](../day27_pivot_unpivot.sql) ·
  [solution reasoning](../solutions/day27_solutions.md) ·
  [executable solution](../solutions/day27_solutions.sql)

## Learning objectives

- Pivot controlled categories with portable conditional aggregation.
- Normalize wide values to a typed long-form relation.

## Vocabulary and concepts

- **Pivot:** turn row values into separate output columns.
- **Unpivot:** turn several columns into key/value rows.
- **Conditional aggregation:** aggregates restricted by `FILTER` or `CASE`.

## Worked example / walkthrough

At one row per quarter, calculate
`SUM(amount) FILTER (WHERE method = 'card')` and parallel columns for the other
known methods. Reconcile the sum of pivot columns to the long-form payment total
and decide whether absent combinations display as `NULL` or zero.

## Exercises

Complete the prompts in the [learner SQL](../day27_pivot_unpivot.sql). Add one
unrecognized category and document whether a static pivot intentionally omits
it or exposes an “other” column.

## Self-check

- Is the category domain controlled enough for fixed output columns?
- Do the wide and long forms reconcile without silently changing types?

## Next step

Continue to [Day 28 — JSONB and XML](day28_json_xml.md).

## Deep dive and reference

Learning objectives
- Build pivot tables from row-form data using two approaches in Postgres
  - Conditional aggregation (portable SQL)
  - tablefunc.crosstab (extension) for tidy pivot syntax
- Unpivot wide tables back to long form for analysis

Why this matters
Reports often require metrics by columns (months across columns, categories as columns). Knowing when to pivot/unpivot keeps data pipelines flexible and analytics straightforward.

Core concepts and deep dive
- Conditional aggregation (portable)
  - SELECT key, SUM(CASE WHEN bucket='A' THEN val END) AS a, ... GROUP BY key
  - Pros: no extension; dynamic columns require generating SQL
  - Cons: verbose for many buckets
- crosstab (tablefunc)
  - CREATE EXTENSION IF NOT EXISTS tablefunc;
  - crosstab(text source_sql, text category_sql) → returns setof record with specified column layout
  - Requires declaring the output column types (key, val for each category)
  - Extension installation requires sufficient database privileges; the
    portable course answer does not depend on it
  - Pros: concise; Cons: requires predeclared categories (static schema) or dynamic SQL
- Unpivot
  - Use UNION ALL over columns or use jsonb_each/text arrays to normalize wide to long
  - Example pattern: SELECT id, 'jan' AS month, jan_val AS val FROM t UNION ALL SELECT id, 'feb', feb_val FROM t ...
  - For many columns, convert row to JSON and jsonb_each_text to key/value rows

Design decisions
- For dashboards with fixed categories/months, crosstab is ergonomic
- For ad-hoc analysis or dynamic categories, prefer conditional aggregates or generate SQL in the application

Pitfalls
- crosstab requires sorted input and category queries; mismatches yield misaligned columns
- NULLs vs zeroes: decide whether to COALESCE NULL to 0 for metrics
- Unpivoting monetary/numeric columns: ensure data types are preserved

Exercises from the learner script
1) Pivot payment revenue by method across the latest four quarters.
2) Unpivot the budget table into category, period, and amount rows.

Ambiguity: `budgets` is already stored in exactly that long form. To practice
unpivoting, first pivot each period to category columns and then normalize those
columns with `CROSS JOIN LATERAL (VALUES ...)`. For actual reporting, selecting
`period, category, amount` from `budgets` is already sufficient.

The seeded payment methods are constrained to `card`, `paypal`, `bank`, and
`credit`; a static pivot must list them explicitly.

Further reading
- tablefunc: https://www.postgresql.org/docs/current/tablefunc.html
- Crosstab examples: https://wiki.postgresql.org/wiki/Tablefunc
