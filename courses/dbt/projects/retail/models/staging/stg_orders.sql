select
    id::bigint as order_id,
    customer_id::bigint as customer_id,
    amount::decimal(12, 2) as amount,
    status::varchar as status,
    updated_at::date as updated_at,
    {{ quality_utils.recognized_amount('amount', 'status') }}::decimal(12, 2) as recognized_amount
from {{ ref('raw_orders') }}
