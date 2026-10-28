# dbt-007: SQL-model reference

The SQL reference demonstrates Jinja variable resolution and source() in a prepared model. It produces total_orders 5, paid_orders 3 and paid_order_rate 0.6. Setting accepted_status explicitly to refunded yields one qualifying order and rate 0.2. Custom macro files and packages require the full-project route; this variant does not pretend to create them.

```sql
-- This variant uses Jinja variables and source(), not a custom macro file.
{% set accepted_status = var('status') %}
with
    counts as (
        select
            count(*) as total_orders,
            sum(case when status = '{{ accepted_status }}' then 1 else 0 end) as paid_orders
        from {{ source('raw', 'orders') }}
    )
select
    total_orders,
    paid_orders,
    case
        when total_orders = 0 then null else cast(paid_orders as double) / total_orders
    end as paid_order_rate
from counts
```

This is actual dbt compilation and DuckDB materialization in the prepared fixture project. It does not execute the full project-editing exercises or deploy a cloud warehouse. Model tables have no row-order guarantee; use keys when comparing records.
