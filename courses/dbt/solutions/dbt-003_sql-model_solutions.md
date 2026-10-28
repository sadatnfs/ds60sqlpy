# dbt-003: SQL-model reference

The SQL reference joins the two fixed refs and groups paid amounts by customer identity. Customer 10/Ada/north has 100 from one paid order; customer 20/Ben/south has 170 from two. Compare by customer_id rather than the displayed row order. The full-project route additionally controls model dependencies and materialization files.

```sql
-- One row per paid customer. Compare by customer_id, not display order.
select o.customer_id, c.name, c.region, sum(o.amount) as paid_amount, count(*) as paid_orders
from {{ ref('raw_orders') }} as o
join {{ ref('customers') }} as c on o.customer_id = c.customer_id
where o.status = '{{ var("status") }}'
group by o.customer_id, c.name, c.region
```

This is actual dbt compilation and DuckDB materialization in the prepared fixture project. It does not execute the full project-editing exercises or deploy a cloud warehouse. Model tables have no row-order guarantee; use keys when comparing records.
