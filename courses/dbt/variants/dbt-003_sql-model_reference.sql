-- One row per paid customer. Compare by customer_id, not display order.
select o.customer_id, c.name, c.region, sum(o.amount) as paid_amount, count(*) as paid_orders
from {{ ref('raw_orders') }} as o
join {{ ref('customers') }} as c on o.customer_id = c.customer_id
where o.status = '{{ var("status") }}'
group by o.customer_id, c.name, c.region
