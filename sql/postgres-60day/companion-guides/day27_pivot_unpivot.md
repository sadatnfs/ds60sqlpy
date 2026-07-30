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

## Practice assumptions and review method

- **Focus:** Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.
- **Assumptions:** PostgreSQL core has no portable dynamic PIVOT keyword. `FILTER`, `CASE`, `VALUES`, JSON objects, or optional `tablefunc` serve different needs.
- **Failure to watch for:** Replacing missing category combinations with zero is a business decision; dynamic columns are difficult for stable downstream schemas.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Pivot with conditional aggregation when output categories are known, and unpivot with explicit typed rows while preserving missing-value meaning.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Pivot order counts by status into one summary row.
   **Progressive hint:** Use one filtered count per known status and keep an all-orders denominator.
   **Expected shape:** Exactly one row.
2. **Query writing:** Pivot customer counts for US, CA, GB, and DE by segment.
   **Progressive hint:** Group at segment grain and use filtered counts for known country columns.
   **Expected shape:** One row per segment.
3. **Query writing:** Unpivot a wide quarterly sample into quarter/amount rows.
   **Progressive hint:** Use a lateral `VALUES` relation with one output row per source column.
   **Expected shape:** Eight rows from two source rows and four quarters.
4. **Prediction:** Compare a missing pivot combination with a real zero and preserve the distinction.
   **Progressive hint:** Filtered `SUM` returns NULL when no rows contribute; `COALESCE` should be used only when the report defines absence as zero.
   **Expected shape:** One row per expense category with nullable/zero-aware columns.
5. **Debugging:** Produce a dynamic category report as a JSONB object instead of generating unstable SQL columns.
   **Progressive hint:** Aggregate category/value pairs into data values so the result schema remains stable.
   **Expected shape:** One row per UTC month with a JSON object of category revenue.
6. **Extension:** Round-trip a wide sample to long form and back, verifying values and NULLs.
   **Progressive hint:** Unpivot with lateral values, then use conditional aggregation keyed by company.
   **Expected shape:** Two reconstructed rows matching the source.

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

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- tablefunc: https://www.postgresql.org/docs/current/tablefunc.html
- Crosstab examples: https://wiki.postgresql.org/wiki/Tablefunc
