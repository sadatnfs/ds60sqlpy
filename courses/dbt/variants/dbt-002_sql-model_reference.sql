-- Fixed var status is paid. Its three qualifying amounts sum to 270.
select id as order_id, customer_id, cast(amount as bigint) as amount
from {{ ref('raw_orders') }}
where status = '{{ var("status") }}'
