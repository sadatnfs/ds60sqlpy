# Day 27 — Solutions: Pivot and Unpivot

PostgreSQL has no `PIVOT` or `UNPIVOT` keyword. Conditional aggregation is the
portable pivot technique; a lateral `VALUES` list is a clear unpivot technique.

## Exercise 1 — Payment revenue by method across the latest four quarters

The result keeps quarters as rows and turns the four allowed payment methods
into columns. The window begins at the start of the quarter three quarters ago,
so it includes the current quarter plus the previous three.

```sql
SET search_path TO training, public;

WITH quarter_totals AS (
  SELECT date_trunc('quarter', payment_date)::date AS quarter,
         method,
         SUM(amount) AS revenue
  FROM payments
  WHERE payment_date
        >= date_trunc('quarter', CURRENT_DATE) - interval '9 months'
  GROUP BY date_trunc('quarter', payment_date), method
)
SELECT quarter,
       ROUND(
         SUM(revenue) FILTER (WHERE method = 'card'),
         2
       ) AS card,
       ROUND(
         SUM(revenue) FILTER (WHERE method = 'paypal'),
         2
       ) AS paypal,
       ROUND(
         SUM(revenue) FILTER (WHERE method = 'bank'),
         2
       ) AS bank,
       ROUND(
         SUM(revenue) FILTER (WHERE method = 'credit'),
         2
       ) AS credit
FROM quarter_totals
GROUP BY quarter
ORDER BY quarter;
```

Expected shape: up to four quarter rows and one column per method. A method with
no payment in a quarter is `NULL`; wrap each expression in `COALESCE(..., 0)` if
the report contract requires zeros.

## Exercise 2 — Unpivot budgets to period-category-amount rows

Ambiguity: `budgets` is already normalized as
`(period, category, amount)`. There is nothing to unpivot in its stored shape.
To practice the operation, this answer first makes a wide row per period and
then normalizes those columns with `CROSS JOIN LATERAL`.

```sql
SET search_path TO training, public;

WITH wide_budgets AS (
  SELECT period,
         SUM(amount) FILTER (
           WHERE category = 'COGS'
         ) AS cogs,
         SUM(amount) FILTER (
           WHERE category = 'Marketing'
         ) AS marketing,
         SUM(amount) FILTER (
           WHERE category = 'Payroll'
         ) AS payroll,
         SUM(amount) FILTER (
           WHERE category = 'Infrastructure'
         ) AS infrastructure,
         SUM(amount) FILTER (
           WHERE category = 'G&A'
         ) AS general_admin
  FROM budgets
  GROUP BY period
)
SELECT w.period,
       u.category,
       u.amount
FROM wide_budgets w
CROSS JOIN LATERAL (
  VALUES
    ('COGS', w.cogs),
    ('Marketing', w.marketing),
    ('Payroll', w.payroll),
    ('Infrastructure', w.infrastructure),
    ('G&A', w.general_admin)
) AS u(category, amount)
ORDER BY w.period, u.category;
```

Expected shape: five rows per budget period in the seeded data. For real
reporting, `SELECT period, category, amount FROM budgets` is already the desired
long-form answer.

## Pitfalls

- Hard-coded pivot columns do not adapt automatically when a new payment method
  or budget category appears.
- Pivoting can hide missing values. Decide deliberately between `NULL` and `0`.
- The optional `tablefunc.crosstab` extension is not needed for these answers
  and may be unavailable on managed or offline installations.
