with
    expected as (
        select
            sum(
                case
                    when status = 'paid' then amount when status = 'refunded' then - amount else 0
                end
            ) as amount
        from {{ ref('raw_orders') }}
    ),
    actual as (select sum(net_amount) as amount from {{ ref('customer_revenue') }})
select expected.amount as expected_amount, actual.amount as actual_amount
from expected
cross join actual
where expected.amount is distinct from actual.amount
