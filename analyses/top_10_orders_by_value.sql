-- Top 10 Orders by Value

select
  order_id,
  customer_id,
  total_items_value,
  total_payment
from {{ ref('orders_mart') }}
order by total_items_value desc
limit 10;
