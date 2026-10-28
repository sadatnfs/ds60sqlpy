-- Enrich identified orders before defining an aggregate grain.
select o.id, o.customer_id, c.name, c.region, o.amount, o.status
from {{ ref('raw_orders') }} as o
left join {{ ref('customers') }} as c on o.customer_id = c.customer_id
