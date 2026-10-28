# dbt-002: SQL-model reference

The SQL reference keeps paid orders 1, 2 and 5 with amounts 100, 50 and 120. Their total is 270. Removing the status filter returns the five-row population. Preserve the order key, inspect casts and compare the compiled predicate. The full-project parsing/quarantine exercise uses its separately declared source fixture.

```sql
-- Fixed var status is paid. Its three qualifying amounts sum to 270.
select id as order_id, customer_id, cast(amount as bigint) as amount
from {{ ref('raw_orders') }}
where status = '{{ var("status") }}'
```

This is actual dbt compilation and DuckDB materialization in the prepared fixture project. It does not execute the full project-editing exercises or deploy a cloud warehouse. Model tables have no row-order guarantee; use keys when comparing records.
