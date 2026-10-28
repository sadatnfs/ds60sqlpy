EXPLAIN
SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
WHERE
  day = '2026-01-01'
GROUP BY
  region;

SELECT
  region,
  SUM(amount)
FROM
  ds60.orders
WHERE
  day = '2026-01-01'
GROUP BY
  region
ORDER BY
  region;
