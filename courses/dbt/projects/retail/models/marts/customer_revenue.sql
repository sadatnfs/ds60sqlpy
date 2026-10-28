select
    c.customer_id,
    c.name,
    c.region,
    sum(o.recognized_amount)::decimal(18, 2) as net_amount,
    count(o.order_id)::bigint as order_count
from {{ ref('stg_customers') }} as c
left join {{ ref('stg_orders') }} as o on c.customer_id = o.customer_id
group by c.customer_id, c.name, c.region
