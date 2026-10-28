-- The prepared raw_orders seed has five rows, not the full-project fixture.
-- Start by inspecting the input, then select paid orders using the guide.
select id, customer_id, amount, status, updated_at from {{ ref('raw_orders') }}
