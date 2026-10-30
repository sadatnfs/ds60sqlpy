# CQL access contract

Copy the owned Cassandra project as its README describes. These commands run
in that copied directory, never in an ordinary classroom Python pad.

```bash
bash run.sh prepare
bash run.sh start
bash run.sh check
```

Inspect `client.py` beside the commands: its customer/day partition query returns
order IDs 3 then 1; its unindexed filter must fail with a filtering diagnostic.
The read checks identity and values, so a coincidental sum cannot hide a missing row.

```sql
SELECT
  order_id,
  amount
FROM
  ds60_orders.by_customer
WHERE
  customer_id = 'alpha'
  AND day_bucket = '2026-01-01';
```

This SQL illustrates the actual query contract. Use the prepared client rather
than redirecting it to an external cluster. A cross-day question requires bounded
partition fanout or a separate table designed for that access pattern.
