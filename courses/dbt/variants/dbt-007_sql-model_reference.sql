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
