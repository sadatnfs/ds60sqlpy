-- Jinja runs during compilation; the database evaluates the emitted SQL.
{% set multiplier = 2 %}
select id, amount * {{ multiplier }} as scaled_amount
from {{ source('raw', 'orders') }}
