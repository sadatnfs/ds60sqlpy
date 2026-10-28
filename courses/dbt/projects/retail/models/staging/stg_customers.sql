select customer_id::bigint as customer_id, name::varchar as name, region::varchar as region
from {{ ref('customers') }}
