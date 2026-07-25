# Day 12 solutions — string functions

These answers match the exercises in [Day 12](../day12_string_functions.sql). They preview normalized text without changing stored course data.

## Exercise 1 — Normalize country codes

```sql
SELECT
  c.customer_id,
  c.country AS stored_country,
  UPPER(BTRIM(c.country)) AS normalized_country
FROM training.customers AS c
ORDER BY c.customer_id;
```

`BTRIM` removes whitespace from both ends, and `UPPER` standardizes letter case. Applying `UPPER` after trimming makes the transformation’s order easy to read.

To count the normalized values:

```sql
SELECT
  UPPER(BTRIM(c.country)) AS normalized_country,
  COUNT(*) AS customers
FROM training.customers AS c
GROUP BY UPPER(BTRIM(c.country))
ORDER BY normalized_country;
```

## Exercise 2 — Build a product label

```sql
SELECT
  p.product_id,
  FORMAT(
    '%s - %s ($%s)',
    p.category,
    p.name,
    TO_CHAR(p.price, 'FM999999990.00')
  ) AS full_label
FROM training.products AS p
ORDER BY p.product_id;
```

`FORMAT` inserts each value at a `%s` placeholder. `TO_CHAR` forces two decimal places, so a price such as `19.90` does not display as `19.9`.

## Check yourself

- Normalization produces only trimmed uppercase country codes.
- Each label has the exact shape `<category> - <name> ($<price>)`.
- These `SELECT` queries do not update the source columns.
