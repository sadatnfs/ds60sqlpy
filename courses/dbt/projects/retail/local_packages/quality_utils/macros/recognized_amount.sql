{% macro recognized_amount(amount, status) %}
    case
        when {{ status }} = 'paid'
        then {{ amount }}
        when {{ status }} = 'refunded'
        then -{{ amount }}
        else 0
    end
{% endmacro %}
