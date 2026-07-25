# Day 14 solutions — numeric functions and casting

These answers match the exercises in [Day 14](../day14_numeric_and_casting.sql).

## Exercise 1 — Create price boundaries with FLOOR and CEIL

```sql
SELECT
  p.product_id,
  p.name,
  p.price,
  FLOOR(p.price) AS lower_whole_dollar,
  CEIL(p.price) AS upper_whole_dollar,
  FLOOR(p.price / 10) * 10 AS lower_ten_dollar_boundary,
  CEIL(p.price / 10) * 10 AS upper_ten_dollar_boundary
FROM training.products AS p
ORDER BY p.price, p.product_id;
```

`FLOOR` rounds toward negative infinity and `CEIL` rounds toward positive infinity. Course prices are nonnegative, so these act as the lower and upper boundaries learners usually expect.

## Exercise 2 — Group by JSON channel as text

```sql
SELECT
  COALESCE((c.attributes ->> 'channel')::text, 'unknown') AS channel,
  COUNT(*) AS customers
FROM training.customers AS c
GROUP BY COALESCE((c.attributes ->> 'channel')::text, 'unknown')
ORDER BY customers DESC, channel;
```

The `->>` operator already extracts JSON as text, so the explicit `::text` cast is redundant in this schema but demonstrates casting as requested. `COALESCE` gives missing channels a visible group instead of hiding their meaning behind `NULL`.

## Check yourself

- Every price lies between its lower and upper boundaries.
- Exercise 2 returns one row per normalized channel value.
- `attributes -> 'channel'` returns JSONB; `attributes ->> 'channel'` returns text.
